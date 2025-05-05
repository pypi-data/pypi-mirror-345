from typing import Literal

from mypy_boto3_batch.type_defs import JobDependencyTypeDef, SubmitJobResponseTypeDef
from pandas import DataFrame

from .client import BATCH_CLIENT


def submit_job(
    name: str,
    queue: str,
    definition: str,
    depends_on: list[JobDependencyTypeDef] | None = None,
    tags: dict[str, str] = {},
) -> SubmitJobResponseTypeDef:
    """Submit a job to the job queue.

    Parameters
    ----------
    name : str
        The name of the job.
    queue : str
        The name or ARN of the job queue.
    definition : str
        The job definition to use (can be Name, Name:Revision or ARN).
    depends_on : list, optional
        A list of job IDs on which this job depends, by default None
    tags : dict, optional
        The tags to associate with the job, by default {}

    Returns
    -------
    SubmitJobResponseTypeDef
        The response from the submit job operation.
    """
    # default depends_on to empty list
    if depends_on is None:
        depends_on = []

    # check if job name already exists in queue
    for job in BATCH_CLIENT.list_jobs(jobQueue=queue)["jobSummaryList"]:
        if job["jobName"] == name:
            raise ValueError(f"Job {name} already exists in queue {queue}")

    # submit the job
    return BATCH_CLIENT.submit_job(
        jobName=name, jobQueue=queue, jobDefinition=definition, dependsOn=depends_on, tags=tags
    )


def list_jobs(
    queue: str,
    status: Literal["SUBMITTED", "PENDING", "RUNNABLE", "STARTING", "RUNNING", "SUCCEEDED", "FAILED"] = "RUNNING",
) -> DataFrame:
    """List jobs in queue.

    Parameters
    ----------
    queue : str
        The name or ARN of the job queue.

    Returns
    -------
    DataFrame
        The list of jobs in the queue.
    """
    job_list = {
        "Name": [],
        "JobId": [],
        "TaskId": [],
        "Status": [],
        "Tags": [],
    }
    for job in BATCH_CLIENT.list_jobs(jobQueue=queue, jobStatus=status, maxResults=10)["jobSummaryList"]:
        if "status" not in job:
            continue
        # get taskID
        jobs_descriptions = BATCH_CLIENT.describe_jobs(jobs=[job["jobId"]])["jobs"]
        for job_desp in jobs_descriptions:
            if "ecsProperties" not in job_desp:
                continue
            if "taskProperties" not in job_desp["ecsProperties"]:
                continue
            if "taskArn" not in job_desp["ecsProperties"]["taskProperties"][0]:
                continue
            if "tags" not in job_desp:
                tags = {}
            else:
                tags = job_desp["tags"]
            task_arn = job_desp["ecsProperties"]["taskProperties"][0]["taskArn"]
            task_id = task_arn.split("/")[-1]
            job_list["Name"].append(job["jobName"])
            job_list["JobId"].append(job["jobId"])
            job_list["TaskId"].append(task_id)
            job_list["Status"].append(job["status"])
            job_list["Tags"].append(tags)
    job_df = DataFrame(job_list)
    return job_df
