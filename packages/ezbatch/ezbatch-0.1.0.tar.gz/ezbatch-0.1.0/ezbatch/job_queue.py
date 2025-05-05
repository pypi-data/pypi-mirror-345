from typing import Literal

from mypy_boto3_batch.type_defs import (
    CreateJobQueueResponseTypeDef,
    UpdateJobQueueResponseTypeDef,
)
from pandas import DataFrame

from .client import BATCH_CLIENT


def create_job_queue(name: str, compute_environment: str, tags: dict[str, str] = {}) -> CreateJobQueueResponseTypeDef:
    """Create a new job queue.

    Parameters
    ----------
    name : str
        The name of the job queue.
    compute_environment : str
        The name or ARN of the compute environment to use.
    tags : dict[str, str]
        The tags to apply to the job queue.

    Returns
    -------
    CreateJobQueueResponseTypeDef
        The response from the create job queue operation
    """
    # get the ARN of the compute environment if it is not already an ARN
    if "arn" not in compute_environment:
        compute_environments = BATCH_CLIENT.describe_compute_environments(computeEnvironments=[compute_environment])[
            "computeEnvironments"
        ]
        if len(compute_environments) == 0:
            raise ValueError(f"Compute environment {compute_environment} does not exist.")
        # get the ARN
        compute_environment = compute_environments[0]["computeEnvironmentArn"]

    # create the job queue
    return BATCH_CLIENT.create_job_queue(
        jobQueueName=name,
        state="ENABLED",
        priority=1,
        computeEnvironmentOrder=[
            {
                "order": 1,
                "computeEnvironment": compute_environment,
            }
        ],
        tags=tags,
        jobStateTimeLimitActions=[
            {
                "reason": "MISCONFIGURATION:COMPUTE_ENVIRONMENT_MAX_RESOURCE",
                "state": "RUNNABLE",
                "maxTimeSeconds": 600,
                "action": "CANCEL",
            },
            {
                "reason": "MISCONFIGURATION:JOB_RESOURCE_REQUIREMENT",
                "state": "RUNNABLE",
                "maxTimeSeconds": 600,
                "action": "CANCEL",
            },
        ],
    )


def list_job_queues() -> DataFrame:
    """List all job queues.

    Returns
    -------
    DataFrame
        The list of job queues.
    """
    table_dict = {
        "Name": [],
        "ARN": [],
        "State": [],
        "Priority": [],
        "Status": [],
        "Status Reason": [],
        "Compute Environment": [],
        "Tags": [],
    }
    job_queues = BATCH_CLIENT.describe_job_queues()
    for job_queue in job_queues["jobQueues"]:
        # check that the non-required fields is in the response
        if "state" not in job_queue:
            continue
        if "priority" not in job_queue:
            continue
        if "status" not in job_queue:
            continue
        if "statusReason" not in job_queue:
            continue
        if "computeEnvironmentOrder" not in job_queue:
            continue
        if "tags" not in job_queue:
            continue
        table_dict["Name"].append(job_queue["jobQueueName"])
        table_dict["ARN"].append(job_queue["jobQueueArn"])
        table_dict["State"].append(job_queue["state"])
        table_dict["Priority"].append(job_queue["priority"])
        table_dict["Status"].append(job_queue["status"])
        table_dict["Status Reason"].append(job_queue["statusReason"])
        table_dict["Compute Environment"].append(
            job_queue["computeEnvironmentOrder"][0]["computeEnvironment"].split("/")[-1]
        )
        table_dict["Tags"].append(job_queue["tags"])
    return DataFrame(table_dict)


def toggle_job_queue(name: str) -> tuple[UpdateJobQueueResponseTypeDef, Literal["ENABLED", "DISABLED"]]:
    """Toggle the state of a job queue.

    Parameters
    ----------
    name : str
        The name or ARN of the job queue.

    Returns
    -------
    UpdateJobQueueResponseTypeDef
        The response from the update job queue operation.
    Literal["ENABLED", "DISABLED"]
        The new state of the job queue.
    """
    job_queues = BATCH_CLIENT.describe_job_queues(jobQueues=[name])["jobQueues"]
    if len(job_queues) == 0:
        raise ValueError(f"Job queue {name} does not exist.")
    job_queue = job_queues[0]
    if job_queue["state"] == "ENABLED":
        return BATCH_CLIENT.update_job_queue(jobQueue=name, state="DISABLED"), job_queue["state"]
    else:
        return BATCH_CLIENT.update_job_queue(jobQueue=name, state="ENABLED"), job_queue["state"]


def delete_job_queue(name: str) -> None:
    """Delete a job queue.

    Parameters
    ----------
    name : str
        The name or ARN of the job queue.
    """
    job_queues = BATCH_CLIENT.describe_job_queues(jobQueues=[name])["jobQueues"]
    if len(job_queues) == 0:
        raise ValueError(f"Job queue {name} does not exist.")
    BATCH_CLIENT.delete_job_queue(jobQueue=name)
