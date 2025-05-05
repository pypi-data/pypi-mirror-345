import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from dataclasses_json import DataClassJsonMixin
from toml import dump, load

from ezbatch.defaults import (
    CURRENT_AWS_ACCOUNT,
    DEFAULT_CONFIG_PATH,
    DEFAULT_MAX_VCPUS,
    DEFAULT_SSE,
    DEFAULT_SSE_KMS_KEY_ID,
)


@dataclass
class EZBatchSettings(DataClassJsonMixin):
    """Settings class for EZBatch.

    Attributes
    ----------
    executionRoleArn : str
        The default execution role to use for jobs.
    maxvCpus : int
        The default maximum number of vCPUs for Compute Environments.
    serviceRole : str
        The service role to use for AWS Batch.
    securityGroupIds : list[str]
        The default security group IDs to use for Compute Environments.
    subnets : list[str]
        The default subnets to use for Compute Environments.
    taskRoleArn : str
        The default task role to use for jobs.
    """

    executionRoleArn: str = f"arn:aws:iam::{CURRENT_AWS_ACCOUNT}:role/ecsTaskExecutionRole"
    maxvCpus: int = DEFAULT_MAX_VCPUS
    serviceRole: str = (
        f"arn:aws:iam::{CURRENT_AWS_ACCOUNT}:role/aws-service-role/batch.amazonaws.com/AWSServiceRoleForBatch"
    )
    instanceRole: str = f"arn:aws:iam::{CURRENT_AWS_ACCOUNT}:role/ecsInstanceRole"
    securityGroupIds: list[str] = field(default_factory=lambda: [])
    sse: Literal["AES256", "aws:kms", "aws:kms:dsse"] = DEFAULT_SSE
    sseKmsKeyId: str = DEFAULT_SSE_KMS_KEY_ID
    subnets: list[str] = field(default_factory=lambda: [])
    taskRoleArn: str = f"arn:aws:iam::{CURRENT_AWS_ACCOUNT}:role/ecsTaskExecutionRole"


@dataclass
class EZBatchConfig(DataClassJsonMixin):
    """Configuration class for EZBatch.

    Attributes
    ----------
    settings : EZBatchSettings
        The settings for EZBatch.
    """

    Settings: EZBatchSettings = field(default_factory=lambda: EZBatchSettings())

    @classmethod
    def load(cls, filename: Path | str):
        """Load the configuration file.

        Parameters
        ----------
        filename : Path | str
            The configuration file path.
        """
        filename = Path(filename)
        with filename.open("r") as f:
            config = load(f)
        return cls.from_dict(config)


# Use Configuration file path, if not set in environment variable
CONFIG_PATH = Path(os.environ.get("EZBATCH_CONFIG_PATH", str(DEFAULT_CONFIG_PATH)))

# Create a new configuration file if it does not exist
if not CONFIG_PATH.exists():
    print(f"Configuration file not found at: {CONFIG_PATH}")
    print("Creating a new configuration file...")
    # creating a new configuration file
    with CONFIG_PATH.open("w") as config_file:
        dump(EZBatchConfig().to_dict(encode_json=True), config_file)
    print(f"Configuration file created at: {CONFIG_PATH}")

# Load the configuration file
CONFIG = EZBatchConfig.load(CONFIG_PATH)
