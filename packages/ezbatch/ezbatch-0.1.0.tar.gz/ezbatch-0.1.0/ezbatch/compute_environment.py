import re
from typing import Literal

from mypy_boto3_batch.type_defs import (
    CreateComputeEnvironmentResponseTypeDef,
    UpdateComputeEnvironmentResponseTypeDef,
)
from pandas import DataFrame

from .client import BATCH_CLIENT, IAM_CLIENT
from .conf import CONFIG


def create_compute_environment(
    name: str,
    service_role: str = CONFIG.Settings.serviceRole,
    instance_role: str = CONFIG.Settings.instanceRole,
    type: Literal["FARGATE", "EC2"] = "FARGATE",
    max_vcpus: int = CONFIG.Settings.maxvCpus,
    subnets: list[str] = CONFIG.Settings.subnets,
    security_group_ids: list[str] = CONFIG.Settings.securityGroupIds,
    tags: dict[str, str] = {},
) -> CreateComputeEnvironmentResponseTypeDef:
    """Create a new compute environment.

    Parameters
    ----------
    name : str
        The name of the compute environment.
    service_role : str, optional
        The service role to use for the compute environment. Default is the service role in the configuration
    instance_role : str, optional
        The instance role to use for the compute environment. Default is the instance role in the configuration
    type : Literal["FARGATE", "EC2"], optional
        The type of compute environment to create. Default is "FARGATE".
    max_vcpus : int, optional
        The maximum number of vCPUs for the compute environment. Default is the maximum vCPUs in the configuration
    subnets : list[str], optional
        The subnets to use for the compute environment. Default is the subnets in the configuration.
    security_group_ids : list[str], optional
        The security group IDs to use for the compute environment. Default is the security group IDs in the configuration.
    tags : dict[str, str]
        The tags to apply to the compute environment.

    Returns
    -------
    ComputeEnvironmentDetailTypeDef
        The response from the AWS Batch API.
    """
    # check that the service role exists
    if "Role" not in IAM_CLIENT.get_role(RoleName=service_role.split("/")[-1]):
        raise ValueError(f"Service role {service_role} does not exist.")

    if type == "FARGATE":
        # create the compute environment
        return BATCH_CLIENT.create_compute_environment(
            computeEnvironmentName=name,
            type="MANAGED",
            state="ENABLED",
            serviceRole=service_role,
            computeResources={
                "type": type,
                "maxvCpus": max_vcpus,
                "subnets": subnets,
                "securityGroupIds": security_group_ids,
                "tags": tags,
            },
        )
    elif type == "EC2":
        return BATCH_CLIENT.create_compute_environment(
            computeEnvironmentName=name,
            type="MANAGED",
            state="ENABLED",
            serviceRole=service_role,
            computeResources={
                "type": type,
                "instanceTypes": ["optimal"],
                "minvCpus": 0,
                "desiredvCpus": 0,
                "maxvCpus": max_vcpus,
                "allocationStrategy": "BEST_FIT_PROGRESSIVE",
                "instanceRole": instance_role,
                "subnets": subnets,
                "securityGroupIds": security_group_ids,
                "tags": tags,
            },
        )
    else:
        raise ValueError(f"Invalid type {type}.")


def list_compute_environments() -> DataFrame:
    """List all compute environments.

    Returns
    -------
    DataFrame
        A DataFrame containing the compute environments.
    """
    table_dict = {
        "Name": [],
        "ARN": [],
        "State": [],
        "Type": [],
        "Max vCPUs": [],
        "Subnets": [],
        "Security Group IDs": [],
        "Tags": [],
    }
    compute_environments = BATCH_CLIENT.describe_compute_environments()
    for compute_environment in compute_environments["computeEnvironments"]:
        # check that the non-required fields is in the response
        if "state" not in compute_environment:
            continue
        if "computeResources" not in compute_environment:
            continue
        if "securityGroupIds" not in compute_environment["computeResources"]:
            continue
        if "tags" not in compute_environment:
            continue
        table_dict["Name"].append(compute_environment["computeEnvironmentName"])
        table_dict["ARN"].append(compute_environment["computeEnvironmentArn"])
        table_dict["State"].append(compute_environment["state"])
        table_dict["Type"].append(compute_environment["computeResources"]["type"])
        table_dict["Max vCPUs"].append(compute_environment["computeResources"]["maxvCpus"])
        table_dict["Subnets"].append(compute_environment["computeResources"]["subnets"])
        table_dict["Security Group IDs"].append(compute_environment["computeResources"]["securityGroupIds"])
        table_dict["Tags"].append(compute_environment["tags"])
    return DataFrame(table_dict)


def toggle_compute_environment(
    name: str,
) -> tuple[UpdateComputeEnvironmentResponseTypeDef, Literal["ENABLED", "DISABLED"]]:
    """Toggle the state of a compute environment.

    Parameters
    ----------
    name : str
        The name or ARN of the compute environment to toggle

    Returns
    -------
    UpdateComputeEnvironmentResponseTypeDef
        The response from the AWS Batch API.
    Literal["ENABLED", "DISABLED"]
        The new state of the compute environment.
    """
    # get the current state
    compute_environments = BATCH_CLIENT.describe_compute_environments(computeEnvironments=[name])
    # check if computeEnvironment field is empty
    if not compute_environments["computeEnvironments"]:
        raise ValueError(f"Compute environment {name} does not exist.")
    # check if state in the response
    if "state" not in compute_environments["computeEnvironments"][0]:
        raise ValueError(f"State of compute environment {name} is not available.")
    state = "ENABLED" if compute_environments["computeEnvironments"][0]["state"] == "DISABLED" else "DISABLED"
    return BATCH_CLIENT.update_compute_environment(computeEnvironment=name, state=state), state


def delete_compute_environment(name: str):
    """Delete a compute environment.

    Parameters
    ----------
    name : str
        The name or ARN of the compute environment to delete
    """
    BATCH_CLIENT.delete_compute_environment(computeEnvironment=name)
