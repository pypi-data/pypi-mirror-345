import json
import re
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, TypedDict, cast

from dataclasses_json import DataClassJsonMixin
from random_word import RandomWords

from ezbatch.job import submit_job
from ezbatch.job_definition import (
    create_ezbatch_job_definition,
    deregister_job_definition,
)
from ezbatch.s3 import S3Mounts

from .preload_scripts import PRELOAD_COMMAND


class EZBatchJobDefinition(TypedDict):
    job_name: str
    container_name: str
    command: list[str]
    image: str
    environment: dict[str, str]
    vcpus: int
    memory: int
    storage_size: int
    platform: Literal["FARGATE", "EC2"]
    tags: dict[str, str]


def sanitize_name(name: str) -> str:
    """Sanitize a name for use in AWS Batch.

    Parameters
    ----------
    name : str
        The name to sanitize.

    Returns
    -------
    str
        Sanitized name.
    """
    return re.sub(r"[^a-zA-Z0-9]", "_", name)


@dataclass
class EZBatchJob(DataClassJsonMixin):
    """A class representing a single EZBatch job in an EZBatch workflow.

    The Job class will be translated into an AWS Batch job definition.

    Attributes
    ----------
    image : str
        The Docker image to use for the job.
    command : str
        The command to run in the container.
    environment : dict[str, str]
        The environment variables to set in the container.
    mounts: S3Mounts
        The S3 mounts to mount in the container.
    vcpus : int
        The number of vCPUs to allocate for the job.
    memory : int
        The amount of memory to allocate for the job.
    storage_size : int, optional
        The amount of storage to allocate for the job, by default None.
    platform : Literal["FARGATE", "EC2"]
        The platform to run the job on.
    tags : dict[str, str]
        The tags to associate with the job.
    queue: str | None
        The name or ARN of the job queue to submit the job to. Overrides the workflow
        level queue if provided.
    preloader : bool
        Whether to preload the job with the EZBatch preloader script. This script will allow you to use the
        mounts variable to download/upload S3 data to the running container. If False, it's up to the user to
        manage s3 downloads/uploads. By default, this is False.
    """

    image: str
    command: str
    environment: dict[str, str] = field(default_factory=dict)
    mounts: S3Mounts = field(default_factory=S3Mounts)
    vcpus: int = 1
    memory: int = 2048
    storage_size: int | None = None
    platform: Literal["FARGATE", "EC2"] = "FARGATE"
    tags: dict[str, str] = field(default_factory=dict)
    queue: str | None = None
    preloader: bool = False

    # internal variables
    _job_name: str = ""

    def __post_init__(self):
        """Set the job name and validate mounts."""
        self._job_name = f"{self.image.split('/')[-1]}-job"
        self.mounts.validate()

    def to_definition(self) -> EZBatchJobDefinition:
        """Convert the Job to a job definition.

        Returns
        -------
        EZBatchJobDefinition
            The job definition.
        """
        # if preloader is True, setup preloader execution
        if self.preloader:
            # store command in EZBATCH_COMMAND environment variable
            self.environment["EZBATCH_COMMAND"] = self.command
            # add mounts to environment
            self.environment["EZBATCH_S3_MOUNTS"] = self.mounts.to_json()
            command = PRELOAD_COMMAND
        else:  # just use the command as is
            command = self.command.split(" ")
        ezbatch_job_definition = {
            "job_name": self._job_name,
            "container_name": sanitize_name(self.image.split("/")[-1]),
            "image": self.image,
            "command": command,
            "environment": self.environment,
            "vcpus": self.vcpus,
            "memory": self.memory,
            "platform": self.platform,
            "tags": self.tags,
        }
        if self.storage_size is not None:
            ezbatch_job_definition["storage_size"] = self.storage_size
        return ezbatch_job_definition  # type: ignore


@dataclass
class EZBatchWorkflow(DataClassJsonMixin):
    """A class representing an EZBatch workflow.

    An EZBatch workflow is a collection of EZBatch jobs that are executed in a specific order.

    Attributes
    ----------
    name : str
        The name of the workflow.
    jobs : dict[str, EZBatchJob]
        A dictionary of job names to EZBatchJob objects.
    dependencies : dict[str, list[str]]
        A dictionary of job names to lists of job names that they depend on.
    """

    name: str
    jobs: dict[str, EZBatchJob]
    dependencies: dict[str, list[str]] = field(default_factory=dict)

    # internal variables
    _job_map: dict[str, EZBatchJob] = field(default_factory=dict)
    _job_def_map: dict[str, str] = field(default_factory=dict)
    _job_name_map: dict[str, str] = field(default_factory=dict)
    _job_dependency_map: dict[str, list[str]] = field(default_factory=dict)
    _job_id_map: dict[str, str] = field(default_factory=dict)

    @staticmethod
    def job_submission_queue(jobs: list[str], dependency_map: dict[str, list[str]]) -> list[str]:
        """Create a queue of job submissions based on job dependencies.

        Parameters
        ----------
        dependency_map : dict[str, list[str]]
            A dictionary mapping job names to lists of job names that they depend on.

        Returns
        -------
        list[str]
            A list of job names in the order that they should be submitted.
        """
        # create job queue
        job_queue = []

        # number of iterations
        num_iter = 0

        # loop until all jobs are in the queue
        while len(job_queue) != len(jobs):

            # loop over dependency map
            for job_name in jobs:
                # if job is already in queue, skip
                if job_name in job_queue:
                    continue
                # if job name is not in dependency_map, no dependencies, add to queue
                if job_name not in dependency_map:
                    job_queue.append(job_name)
                    continue
                # if all of job's dependencies are in queue, add job to queue
                if all(dep in job_queue for dep in dependency_map[job_name]):
                    job_queue.append(job_name)

            # increment number of iterations
            num_iter += 1

            # if number of iterations is greater than 100, raise error
            if num_iter > 100:
                raise ValueError("Dependency loop detected.")

        # return job queue
        return job_queue

    def submit(self, queue: str | None = None):
        """Submit the workflow to AWS Batch.

        Parameters
        ----------
        queue : str | None
            The name or ARN of the job queue to submit the workflow to.
        """
        try:
            # initialize random word generator
            rwg = RandomWords()

            # make ezbatch workflow id
            ezbatch_workflow_id = f"{rwg.get_random_word().capitalize()}{rwg.get_random_word().capitalize()}"

            # first register all the job definitions
            for job_basename, job in self.jobs.items():
                # make a copy of the job so we don't modify the original
                job = deepcopy(job)
                # make ezbatch job id
                ezbatch_job_id = f"{rwg.get_random_word().capitalize()}{rwg.get_random_word().capitalize()}"
                # set the job name/job definition name
                job._job_name = f"{self.name}-{ezbatch_workflow_id}-{job_basename}-{ezbatch_job_id}"
                # set tags
                job.tags["workflowName"] = self.name
                job.tags["job"] = job_basename
                job.tags["ezbatchWorkflowId"] = str(ezbatch_workflow_id)
                job.tags["ezbatchJobId"] = str(ezbatch_job_id)
                # register the job definition
                job_def_response = create_ezbatch_job_definition(**job.to_definition())
                # update the job map
                self._job_map[job._job_name] = job
                # store the job definition ARN
                self._job_def_map[job._job_name] = job_def_response["jobDefinitionArn"]
                # update map between job basename and job name
                self._job_name_map[job_basename] = job._job_name

            # get job queue, translating the job basenames to the full job names
            job_queue = [
                self._job_name_map[job] for job in self.job_submission_queue(list(self.jobs.keys()), self.dependencies)
            ]

            # translate the job dependencies to the full job names
            for job_name, deps in self.dependencies.items():
                self._job_dependency_map[self._job_name_map[job_name]] = [self._job_name_map[dep] for dep in deps]

            # loop over the job queue
            for job in job_queue:
                print(f"Submitting job: {job}")
                # get the job dependencies
                depends_on = self._job_dependency_map.get(job, [])
                # get ezbatch job object
                ezbatch_job = self._job_map[job]
                # raise error if both queue and ezbatch_job.queue are None
                if queue is None and ezbatch_job.queue is None:
                    raise ValueError("Queue must be provided at the workflow or job level.")
                queue = cast(str, queue)
                # submit the job
                response = submit_job(
                    name=job,
                    queue=queue if ezbatch_job.queue is None else ezbatch_job.queue,
                    definition=self._job_def_map[job],
                    depends_on=[{"jobId": self._job_id_map[d]} for d in depends_on],
                    tags=self._job_map[job].tags,
                )
                # save the job id
                self._job_id_map[job] = response["jobId"]

        finally:
            # deregister all the job definitions
            for job_def_arn in self._job_def_map.values():
                deregister_job_definition(job_def_arn)

    def save(self, path: Path | str):
        """Save the workflow to a JSON file.

        Parameters
        ----------
        path : Path | str
            The path to save the workflow to.
        """
        # get self as json dict
        json_dict = self.to_dict(encode_json=True)

        # loop through all keys and remove anything beginning with an underscore
        def remove_underscore(json_dict):
            new_dict = {}
            for key, value in json_dict.items():
                if key.startswith("_"):
                    continue
                if isinstance(value, dict):
                    new_dict[key] = remove_underscore(value)
                else:
                    new_dict[key] = value
            return new_dict

        json_dict = remove_underscore(json_dict)

        # write to file
        with open(path, "w") as f:
            json.dump(json_dict, f, indent=4)

    @classmethod
    def load(cls, path: Path | str):
        """Load the workflow from a JSON file.

        Parameters
        ----------
        path : Path | str
            The path to load the workflow from.
        """
        # read from file
        with open(path) as f:
            json_dict = json.load(f)

        # load from json
        return cls.from_dict(json_dict)
