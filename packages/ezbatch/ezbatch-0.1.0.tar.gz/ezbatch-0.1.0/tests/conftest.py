import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# Set AWS environment variables for tests
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SECURITY_TOKEN"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"


# Patch STS_CLIENT.get_caller_identity before importing any ezbatch modules
mock_sts_client = MagicMock()
mock_sts_client.get_caller_identity.return_value = {"Account": "123456789012"}
sys.modules["boto3"] = MagicMock()
sys.modules["boto3"].client.return_value = mock_sts_client


@pytest.fixture(autouse=True)
def mock_boto3_client():
    """Mock boto3.client to prevent AWS API calls during tests."""
    mock_client = MagicMock()
    with patch("boto3.client", return_value=mock_client):
        yield mock_client


@pytest.fixture
def mock_batch_client():
    """Mock AWS Batch client."""
    with patch("ezbatch.client.BATCH_CLIENT") as mock_client:
        yield mock_client


@pytest.fixture
def mock_s3_client():
    """Mock AWS S3 client."""
    with patch("ezbatch.client.S3_CLIENT") as mock_client:
        yield mock_client


@pytest.fixture
def mock_sts_client():
    """Mock AWS STS client."""
    with patch("ezbatch.client.STS_CLIENT") as mock_client:
        yield mock_client


@pytest.fixture
def mock_iam_client():
    """Mock AWS IAM client."""
    with patch("ezbatch.client.IAM_CLIENT") as mock_client:
        yield mock_client


@pytest.fixture
def mock_logs_client():
    """Mock AWS Logs client."""
    with patch("ezbatch.client.LOGS_CLIENT") as mock_client:
        yield mock_client


@pytest.fixture
def mock_all_clients(mock_batch_client, mock_s3_client, mock_sts_client, mock_iam_client, mock_logs_client):
    """Mock all AWS clients."""
    return {
        "batch": mock_batch_client,
        "s3": mock_s3_client,
        "sts": mock_sts_client,
        "iam": mock_iam_client,
        "logs": mock_logs_client,
    }


@pytest.fixture
def sample_s3_mount():
    """Sample S3Mount object for testing."""
    from ezbatch.s3 import S3Mount

    return S3Mount(
        source="s3://source-bucket/path",
        destination="/container/path",
        recursive=True,
        sse="AES256",
    )


@pytest.fixture
def sample_s3_mounts():
    """Sample S3Mounts object for testing."""
    from ezbatch.s3 import S3Mount, S3Mounts

    read_mount = S3Mount(
        source="s3://source-bucket/read-path",
        destination="/container/read-path",
        recursive=True,
    )
    write_mount = S3Mount(
        source="/container/write-path",
        destination="s3://destination-bucket/write-path",
        recursive=True,
        sse="AES256",
    )
    return S3Mounts(read=[read_mount], write=[write_mount])


@pytest.fixture
def sample_job():
    """Sample EZBatchJob object for testing."""
    from ezbatch.workflow import EZBatchJob

    return EZBatchJob(
        image="python:3.9",
        command="python -c 'print(\"Hello, World!\")'",
        environment={"ENV_VAR": "value"},
        vcpus=2,
        memory=4096,
        platform="FARGATE",
        tags={"tag1": "value1"},
    )


@pytest.fixture
def sample_workflow():
    """Sample EZBatchWorkflow object for testing."""
    from ezbatch.workflow import EZBatchJob, EZBatchWorkflow

    job1 = EZBatchJob(
        image="python:3.9",
        command="python -c 'print(\"Job 1\")'",
        vcpus=1,
        memory=2048,
    )
    job2 = EZBatchJob(
        image="python:3.9",
        command="python -c 'print(\"Job 2\")'",
        vcpus=1,
        memory=2048,
    )
    return EZBatchWorkflow(
        name="test-workflow",
        jobs={"job1": job1, "job2": job2},
        dependencies={"job2": ["job1"]},
    )
