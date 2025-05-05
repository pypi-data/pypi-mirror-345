from dataclasses import dataclass, field
from unittest.mock import MagicMock, patch

import pytest

from ezbatch.job_definition import (
    Container,
    ECSProperties,
    EnvironmentProperty,
    EphemeralStorageProperty,
    MemoryRequirement,
    TaskProperty,
    VCpuRequirement,
    create_ezbatch_job_definition,
    create_job_definition,
    deregister_job_definition,
)


@pytest.fixture
def mock_batch_client():
    with patch("ezbatch.job_definition.BATCH_CLIENT") as mock:
        yield mock


@pytest.fixture
def mock_config():
    with patch("ezbatch.job_definition.CONFIG") as mock:
        mock.Settings.executionRoleArn = "arn:aws:iam::123456789012:role/execution-role"
        mock.Settings.taskRoleArn = "arn:aws:iam::123456789012:role/task-role"
        yield mock


class TestCreateJobDefinition:
    def test_create_job_definition_new(self, mock_batch_client, mock_config):
        """Test creating a new job definition."""
        # Setup mock responses
        mock_batch_client.describe_job_definitions.return_value = {"jobDefinitions": []}  # No existing job definitions
        mock_batch_client.register_job_definition.return_value = {
            "jobDefinitionName": "test-job-def",
            "jobDefinitionArn": "arn:aws:batch:region:account:job-definition/test-job-def:1",
            "revision": 1,
        }

        # Create test ECSProperties
        ecs_properties = ECSProperties(
            taskProperties=[
                TaskProperty(
                    containers=[
                        Container(
                            name="test-container",
                            command=["echo", "hello"],
                            image="test-image",
                        )
                    ],
                )
            ]
        )

        # Test
        response = create_job_definition(
            name="test-job-def",
            ecs_properties=ecs_properties,
            tags={"tag1": "value1"},
        )

        # Verify
        assert response["jobDefinitionName"] == "test-job-def"
        assert response["jobDefinitionArn"] == "arn:aws:batch:region:account:job-definition/test-job-def:1"
        assert response["revision"] == 1

        mock_batch_client.describe_job_definitions.assert_called_once_with(jobDefinitionName="test-job-def")
        mock_batch_client.register_job_definition.assert_called_once_with(
            jobDefinitionName="test-job-def",
            type="container",
            tags={"tag1": "value1"},
            platformCapabilities=["FARGATE"],
            ecsProperties=ecs_properties.as_dict(),
            propagateTags=True,
        )

    def test_create_job_definition_existing_active(self, mock_batch_client, mock_config):
        """Test creating a job definition when an active one already exists."""
        # Setup mock responses for existing active job definition
        mock_batch_client.describe_job_definitions.return_value = {
            "jobDefinitions": [
                {
                    "jobDefinitionName": "test-job-def",
                    "jobDefinitionArn": "arn:aws:batch:region:account:job-definition/test-job-def:1",
                    "revision": 1,
                    "status": "ACTIVE",
                }
            ]
        }
        mock_batch_client.register_job_definition.return_value = {
            "jobDefinitionName": "test-job-def",
            "jobDefinitionArn": "arn:aws:batch:region:account:job-definition/test-job-def:2",
            "revision": 2,
        }

        # Create test ECSProperties
        ecs_properties = ECSProperties(
            taskProperties=[
                TaskProperty(
                    containers=[
                        Container(
                            name="test-container",
                            command=["echo", "hello"],
                            image="test-image",
                        )
                    ],
                )
            ]
        )

        # Test
        response = create_job_definition(
            name="test-job-def",
            ecs_properties=ecs_properties,
            tags={"tag1": "value1"},
        )

        # Verify
        assert response["jobDefinitionName"] == "test-job-def"
        assert response["jobDefinitionArn"] == "arn:aws:batch:region:account:job-definition/test-job-def:2"
        assert response["revision"] == 2

        mock_batch_client.describe_job_definitions.assert_called_once_with(jobDefinitionName="test-job-def")
        mock_batch_client.deregister_job_definition.assert_called_once_with(
            jobDefinition="arn:aws:batch:region:account:job-definition/test-job-def:1"
        )
        mock_batch_client.register_job_definition.assert_called_once_with(
            jobDefinitionName="test-job-def",
            type="container",
            tags={"tag1": "value1"},
            platformCapabilities=["FARGATE"],
            ecsProperties=ecs_properties.as_dict(),
            propagateTags=True,
        )

    def test_create_job_definition_existing_inactive(self, mock_batch_client, mock_config):
        """Test creating a job definition when an inactive one already exists."""
        # Setup mock responses for existing inactive job definition
        mock_batch_client.describe_job_definitions.return_value = {
            "jobDefinitions": [
                {
                    "jobDefinitionName": "test-job-def",
                    "jobDefinitionArn": "arn:aws:batch:region:account:job-definition/test-job-def:1",
                    "revision": 1,
                    "status": "INACTIVE",
                }
            ]
        }
        mock_batch_client.register_job_definition.return_value = {
            "jobDefinitionName": "test-job-def",
            "jobDefinitionArn": "arn:aws:batch:region:account:job-definition/test-job-def:2",
            "revision": 2,
        }

        # Create test ECSProperties
        ecs_properties = ECSProperties(
            taskProperties=[
                TaskProperty(
                    containers=[
                        Container(
                            name="test-container",
                            command=["echo", "hello"],
                            image="test-image",
                        )
                    ],
                )
            ]
        )

        # Test
        response = create_job_definition(
            name="test-job-def",
            ecs_properties=ecs_properties,
            tags={"tag1": "value1"},
        )

        # Verify
        assert response["jobDefinitionName"] == "test-job-def"
        assert response["jobDefinitionArn"] == "arn:aws:batch:region:account:job-definition/test-job-def:2"
        assert response["revision"] == 2

        mock_batch_client.describe_job_definitions.assert_called_once_with(jobDefinitionName="test-job-def")
        mock_batch_client.deregister_job_definition.assert_not_called()
        mock_batch_client.register_job_definition.assert_called_once_with(
            jobDefinitionName="test-job-def",
            type="container",
            tags={"tag1": "value1"},
            platformCapabilities=["FARGATE"],
            ecsProperties=ecs_properties.as_dict(),
            propagateTags=True,
        )


class TestCreateEzbatchJobDefinition:
    def test_create_ezbatch_job_definition_fargate(self, mock_batch_client, mock_config):
        """Test creating an EZBatch job definition with Fargate platform."""
        # Setup mock responses
        mock_batch_client.describe_job_definitions.return_value = {"jobDefinitions": []}  # No existing job definitions
        mock_batch_client.register_job_definition.return_value = {
            "jobDefinitionName": "test-job-def",
            "jobDefinitionArn": "arn:aws:batch:region:account:job-definition/test-job-def:1",
            "revision": 1,
        }

        # Test
        response = create_ezbatch_job_definition(
            job_name="test-job-def",
            container_name="test-container",
            command=["echo", "hello"],
            image="test-image",
            environment={"ENV_VAR": "value"},
            vcpus=2,
            memory=4096,
            storage_size=50,
            tags={"tag1": "value1"},
        )

        # Verify
        assert response["jobDefinitionName"] == "test-job-def"
        assert response["jobDefinitionArn"] == "arn:aws:batch:region:account:job-definition/test-job-def:1"
        assert response["revision"] == 1

        mock_batch_client.describe_job_definitions.assert_called_once_with(jobDefinitionName="test-job-def")

        # Verify the ECSProperties structure
        call_args = mock_batch_client.register_job_definition.call_args[1]
        assert call_args["jobDefinitionName"] == "test-job-def"
        assert call_args["type"] == "container"
        assert call_args["tags"] == {"tag1": "value1"}
        assert call_args["platformCapabilities"] == ["FARGATE"]
        assert call_args["propagateTags"] == True

        # Check the ECSProperties structure
        ecs_properties = call_args["ecsProperties"]
        assert len(ecs_properties["taskProperties"]) == 1
        task_property = ecs_properties["taskProperties"][0]

        # Check container properties
        assert len(task_property["containers"]) == 1
        container = task_property["containers"][0]
        assert container["name"] == "test-container"
        assert container["command"] == ["echo", "hello"]
        assert container["image"] == "test-image"

        # Check environment variables
        assert len(container["environment"]) == 1
        env_var = container["environment"][0]
        assert env_var["name"] == "ENV_VAR"
        assert env_var["value"] == "value"

        # Check resource requirements
        assert len(container["resourceRequirements"]) == 2
        vcpu_req = next(r for r in container["resourceRequirements"] if r["type"] == "VCPU")
        mem_req = next(r for r in container["resourceRequirements"] if r["type"] == "MEMORY")
        assert vcpu_req["value"] == "2"
        assert mem_req["value"] == "4096"

        # Check ephemeral storage
        assert task_property["ephemeralStorage"]["sizeInGiB"] == 50

    def test_create_ezbatch_job_definition_ec2(self, mock_batch_client, mock_config):
        """Test creating an EZBatch job definition with EC2 platform."""
        # Setup mock responses
        mock_batch_client.describe_job_definitions.return_value = {"jobDefinitions": []}  # No existing job definitions
        mock_batch_client.register_job_definition.return_value = {
            "jobDefinitionName": "test-job-def",
            "jobDefinitionArn": "arn:aws:batch:region:account:job-definition/test-job-def:1",
            "revision": 1,
        }

        # Test
        response = create_ezbatch_job_definition(
            job_name="test-job-def",
            container_name="test-container",
            command=["echo", "hello"],
            image="test-image",
            environment={"ENV_VAR": "value"},
            vcpus=2,
            memory=4096,
            storage_size=50,
            platform="EC2",
            tags={"tag1": "value1"},
        )

        # Verify
        assert response["jobDefinitionName"] == "test-job-def"
        assert response["jobDefinitionArn"] == "arn:aws:batch:region:account:job-definition/test-job-def:1"
        assert response["revision"] == 1

        mock_batch_client.describe_job_definitions.assert_called_once_with(jobDefinitionName="test-job-def")

        # Verify the ECSProperties structure
        call_args = mock_batch_client.register_job_definition.call_args[1]
        assert call_args["jobDefinitionName"] == "test-job-def"
        assert call_args["type"] == "container"
        assert call_args["tags"] == {"tag1": "value1"}
        assert call_args["platformCapabilities"] == ["EC2"]
        assert call_args["propagateTags"] == True

        # Check the ECSProperties structure
        ecs_properties = call_args["ecsProperties"]
        assert len(ecs_properties["taskProperties"]) == 1
        task_property = ecs_properties["taskProperties"][0]

        # Check container properties
        assert len(task_property["containers"]) == 1
        container = task_property["containers"][0]
        assert container["name"] == "test-container"
        assert container["command"] == ["echo", "hello"]
        assert container["image"] == "test-image"

        # Check environment variables
        assert len(container["environment"]) == 1
        env_var = container["environment"][0]
        assert env_var["name"] == "ENV_VAR"
        assert env_var["value"] == "value"

        # Check resource requirements
        assert len(container["resourceRequirements"]) == 2
        vcpu_req = next(r for r in container["resourceRequirements"] if r["type"] == "VCPU")
        mem_req = next(r for r in container["resourceRequirements"] if r["type"] == "MEMORY")
        assert vcpu_req["value"] == "2"
        assert mem_req["value"] == "4096"

        # Check ephemeral storage
        assert task_property["ephemeralStorage"]["sizeInGiB"] == 50

    def test_create_ezbatch_job_definition_invalid_platform(self, mock_batch_client, mock_config):
        """Test creating an EZBatch job definition with an invalid platform."""
        # Test
        with pytest.raises(ValueError, match="Invalid platform INVALID"):
            create_ezbatch_job_definition(
                job_name="test-job-def",
                container_name="test-container",
                command=["echo", "hello"],
                image="test-image",
                platform="INVALID",  # type: ignore
            )


class TestDeregisterJobDefinition:
    def test_deregister_job_definition(self, mock_batch_client):
        """Test deregistering a job definition."""
        # Test
        deregister_job_definition("test-job-def:1")

        # Verify
        mock_batch_client.deregister_job_definition.assert_called_once_with(jobDefinition="test-job-def:1")
