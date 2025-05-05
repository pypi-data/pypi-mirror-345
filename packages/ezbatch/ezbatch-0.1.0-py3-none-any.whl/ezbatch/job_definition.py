from dataclasses import dataclass, field
from typing import Literal, cast

from dataclasses_json import DataClassJsonMixin
from mypy_boto3_batch.type_defs import (
    EcsPropertiesTypeDef,
    RegisterJobDefinitionResponseTypeDef,
)

from .client import BATCH_CLIENT
from .conf import CONFIG


@dataclass
class LogConfigurationProperty(DataClassJsonMixin):
    logDriver: Literal["awslogs"] = "awslogs"


@dataclass
class EphemeralStorageProperty(DataClassJsonMixin):
    sizeInGiB: int = 30


@dataclass
class EnvironmentProperty(DataClassJsonMixin):
    name: str
    value: str


@dataclass
class DependsOnProperty(DataClassJsonMixin):
    containerName: str
    condition: Literal["START", "COMPLETE", "SUCCESS"] = "SUCCESS"


@dataclass
class RuntimePlatform(DataClassJsonMixin):
    operatingSystemFamily: Literal["LINUX"] = "LINUX"
    cpuArchitecture: Literal["X86_64"] = "X86_64"


@dataclass
class NetworkConfiguration(DataClassJsonMixin):
    assignPublicIp: Literal["ENABLED", "DISABLED"] = "DISABLED"


@dataclass
class MemoryRequirement(DataClassJsonMixin):
    type: Literal["MEMORY"] = "MEMORY"
    value: str = "2048"


@dataclass
class VCpuRequirement(DataClassJsonMixin):
    type: Literal["VCPU"] = "VCPU"
    value: str = "1"


@dataclass
class Container(DataClassJsonMixin):
    name: str
    command: list[str]
    image: str
    dependsOn: list[DependsOnProperty] = field(default_factory=list)
    environment: list[EnvironmentProperty] = field(default_factory=list)
    essential: bool = True
    resourceRequirements: list[VCpuRequirement | MemoryRequirement] = field(
        default_factory=lambda: [VCpuRequirement(), MemoryRequirement()]
    )
    logConfiguration: LogConfigurationProperty = field(default_factory=lambda: LogConfigurationProperty())


@dataclass
class TaskProperty(DataClassJsonMixin):
    containers: list[Container]
    ephemeralStorage: EphemeralStorageProperty = field(default_factory=lambda: EphemeralStorageProperty())
    executionRoleArn: str = CONFIG.Settings.executionRoleArn
    taskRoleArn: str = CONFIG.Settings.taskRoleArn
    platformVersion: str = "LATEST"
    networkConfiguration: NetworkConfiguration = field(default_factory=lambda: NetworkConfiguration())
    runtimePlatform: RuntimePlatform = field(default_factory=lambda: RuntimePlatform())


@dataclass
class ECSProperties(DataClassJsonMixin):
    taskProperties: list[TaskProperty]

    def as_dict(self) -> EcsPropertiesTypeDef:
        """Return the ECSProperties object as a dictionary."""
        return cast(EcsPropertiesTypeDef, self.to_dict(encode_json=True))


def create_job_definition(
    name: str,
    ecs_properties: ECSProperties | EcsPropertiesTypeDef,
    platform: Literal["FARGATE", "EC2"] = "FARGATE",
    tags: dict[str, str] = {},
) -> RegisterJobDefinitionResponseTypeDef:
    """Create a job definition.

    Parameters
    ----------
    name : str
        The name of the job definition.
    ecs_properties : ECSProperties | EcsPropertiesTypeDef
        The ECS properties for the job definition.
    platform : Literal["FARGATE", "EC2"], optional
        The platform capabilities, by default "FARGATE".
    tags : dict[str, str], optional
        The tags to associate with the job definition, by default

    Returns
    -------
    RegisterJobDefinitionResponseTypeDef
        The response from the register job definition operation
    """
    # first check if the job definition already exists
    job_definitions = BATCH_CLIENT.describe_job_definitions(jobDefinitionName=name)["jobDefinitions"]
    if len(job_definitions) > 0:
        # check if any job definitions are active
        active_job_definitions = [
            job_def for job_def in job_definitions if "status" in job_def and job_def["status"] == "ACTIVE"
        ]
        # deregister all active job definitions with the same name
        for job_definition in active_job_definitions:
            if job_definition["jobDefinitionName"] == name:
                deregister_job_definition(job_definition["jobDefinitionArn"])

    # register the new job definition
    return BATCH_CLIENT.register_job_definition(
        jobDefinitionName=name,
        type="container",
        tags=tags,
        platformCapabilities=[platform],
        ecsProperties=ecs_properties.as_dict() if isinstance(ecs_properties, ECSProperties) else ecs_properties,
        propagateTags=True,
    )


def create_ezbatch_job_definition(
    job_name: str,
    container_name: str,
    command: list[str],
    image: str,
    environment: dict[str, str] = {},
    vcpus: int = 1,
    memory: int = 2048,
    storage_size: int | None = None,
    platform: Literal["FARGATE", "EC2"] = "FARGATE",
    tags: dict[str, str] = {},
) -> RegisterJobDefinitionResponseTypeDef:
    """Create a job definition with a single container for EZBatch.

    Parameters
    ----------
    job_name : str
        The name of the job definition.
    container_name : str
        The name of the container.
    command : list[str]
        The command to run in the container.
    image : str
        The image to use for the container.
    environment : dict[str, str], optional
        The environment variables to set in the container, by default {}
    vcpus : int, optional
        The number of vCPUs to allocate to the container, by default 1
    memory : int, optional
        The amount of memory to allocate to the container, by default 2048
    storage_size : int, optional
        The amount of storage to allocate to the container, by default None
    platform : Literal["FARGATE", "EC2"], optional
        The platform capabilities, by default "FARGATE".
    tags : dict[str, str], optional
        The tags to associate with the job definition, by default {}

    Returns
    -------
    RegisterJobDefinitionResponseTypeDef
        The response from the register job definition operation
    """
    if platform == "FARGATE":
        # create ecs_properties
        ecs_properties: ECSProperties = ECSProperties(  # type: ignore
            taskProperties=[
                TaskProperty(
                    containers=[
                        Container(
                            name=container_name,
                            command=command,
                            image=image,
                            environment=[
                                EnvironmentProperty(name=str(key), value=str(value))
                                for key, value in environment.items()
                            ],
                            resourceRequirements=[
                                VCpuRequirement(value=str(vcpus)),
                                MemoryRequirement(value=str(memory)),
                            ],
                        )
                    ],
                    ephemeralStorage=(
                        EphemeralStorageProperty(sizeInGiB=storage_size)
                        if storage_size is not None
                        else EphemeralStorageProperty()
                    ),
                ),
            ]
        )
    elif platform == "EC2":
        # format environment
        environment_field = [
            EnvironmentProperty(name=str(key), value=str(value)).to_dict() for key, value in environment.items()
        ]

        # format resource requirements
        resource_requirements = [
            VCpuRequirement(value=str(vcpus)).to_dict(),
            MemoryRequirement(value=str(memory)).to_dict(),
        ]

        # create ecs_properties
        ecs_properties: EcsPropertiesTypeDef = {
            "taskProperties": [
                {  # type: ignore
                    "containers": [
                        {
                            "name": container_name,
                            "command": command,
                            "image": image,
                            "environment": environment_field,
                            "resourceRequirements": resource_requirements,
                        }
                    ],
                }
            ]
        }

        # add storage size if provided
        if storage_size is not None:
            ecs_properties["taskProperties"][0]["ephemeralStorage"] = {"sizeInGiB": storage_size}  # type: ignore
    else:
        raise ValueError(f"Invalid platform {platform}")

    # create the job definition
    job_definition = create_job_definition(
        name=job_name,
        ecs_properties=ecs_properties,
        platform=platform,
        tags=tags,
    )

    # return the job definition
    return job_definition


def deregister_job_definition(job_definition: str) -> None:
    """Deregister a job definition.

    Parameters
    ----------
    job_definition : str
        The name:revision or ARN of the job definition.
    """
    BATCH_CLIENT.deregister_job_definition(jobDefinition=job_definition)
