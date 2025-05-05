from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from ezbatch.compute_environment import (
    create_compute_environment,
    delete_compute_environment,
    list_compute_environments,
    toggle_compute_environment,
)


@pytest.fixture
def mock_batch_client():
    with patch("ezbatch.compute_environment.BATCH_CLIENT") as mock:
        yield mock


@pytest.fixture
def mock_iam_client():
    with patch("ezbatch.compute_environment.IAM_CLIENT") as mock:
        # Mock the get_role method to return a valid role
        mock.get_role.return_value = {"Role": {"RoleName": "test-role"}}
        yield mock


class TestCreateComputeEnvironment:
    def test_create_fargate_compute_environment(self, mock_batch_client, mock_iam_client):
        """Test creating a Fargate compute environment."""
        # Setup mock responses
        mock_batch_client.create_compute_environment.return_value = {
            "computeEnvironmentArn": "arn:aws:batch:region:account:compute-environment/test-env",
            "computeEnvironmentName": "test-env",
        }

        # Test
        response = create_compute_environment(
            name="test-env",
            service_role="test-role",
            type="FARGATE",
            max_vcpus=10,
            subnets=["subnet-1", "subnet-2"],
            security_group_ids=["sg-1", "sg-2"],
            tags={"tag1": "value1"},
        )

        # Verify
        assert response["computeEnvironmentArn"] == "arn:aws:batch:region:account:compute-environment/test-env"
        assert response["computeEnvironmentName"] == "test-env"

        mock_iam_client.get_role.assert_called_once_with(RoleName="test-role")
        mock_batch_client.create_compute_environment.assert_called_once_with(
            computeEnvironmentName="test-env",
            type="MANAGED",
            state="ENABLED",
            serviceRole="test-role",
            computeResources={
                "type": "FARGATE",
                "maxvCpus": 10,
                "subnets": ["subnet-1", "subnet-2"],
                "securityGroupIds": ["sg-1", "sg-2"],
                "tags": {"tag1": "value1"},
            },
        )

    def test_create_ec2_compute_environment(self, mock_batch_client, mock_iam_client):
        """Test creating an EC2 compute environment."""
        # Setup mock responses
        mock_batch_client.create_compute_environment.return_value = {
            "computeEnvironmentArn": "arn:aws:batch:region:account:compute-environment/test-env",
            "computeEnvironmentName": "test-env",
        }

        # Test
        response = create_compute_environment(
            name="test-env",
            service_role="test-role",
            instance_role="test-instance-role",
            type="EC2",
            max_vcpus=10,
            subnets=["subnet-1", "subnet-2"],
            security_group_ids=["sg-1", "sg-2"],
            tags={"tag1": "value1"},
        )

        # Verify
        assert response["computeEnvironmentArn"] == "arn:aws:batch:region:account:compute-environment/test-env"
        assert response["computeEnvironmentName"] == "test-env"

        mock_iam_client.get_role.assert_called_once_with(RoleName="test-role")
        mock_batch_client.create_compute_environment.assert_called_once_with(
            computeEnvironmentName="test-env",
            type="MANAGED",
            state="ENABLED",
            serviceRole="test-role",
            computeResources={
                "type": "EC2",
                "instanceTypes": ["optimal"],
                "minvCpus": 0,
                "desiredvCpus": 0,
                "maxvCpus": 10,
                "allocationStrategy": "BEST_FIT_PROGRESSIVE",
                "instanceRole": "test-instance-role",
                "subnets": ["subnet-1", "subnet-2"],
                "securityGroupIds": ["sg-1", "sg-2"],
                "tags": {"tag1": "value1"},
            },
        )

    def test_create_compute_environment_nonexistent_role(self, mock_iam_client):
        """Test creating a compute environment with a nonexistent role."""
        # Setup mock responses for nonexistent role
        mock_iam_client.get_role.return_value = {}

        # Test
        with pytest.raises(ValueError, match="Service role test-role does not exist"):
            create_compute_environment(
                name="test-env",
                service_role="test-role",
                type="FARGATE",
            )


class TestListComputeEnvironments:
    def test_list_compute_environments_empty(self, mock_batch_client):
        """Test listing compute environments when none exist."""
        # Setup mock responses
        mock_batch_client.describe_compute_environments.return_value = {"computeEnvironments": []}

        # Test
        result = list_compute_environments()

        # Verify
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        mock_batch_client.describe_compute_environments.assert_called_once()

    def test_list_compute_environments(self, mock_batch_client):
        """Test listing compute environments."""
        # Setup mock responses
        mock_batch_client.describe_compute_environments.return_value = {
            "computeEnvironments": [
                {
                    "computeEnvironmentName": "env1",
                    "computeEnvironmentArn": "arn:aws:batch:region:account:compute-environment/env1",
                    "state": "ENABLED",
                    "computeResources": {
                        "type": "FARGATE",
                        "maxvCpus": 10,
                        "subnets": ["subnet-1", "subnet-2"],
                        "securityGroupIds": ["sg-1", "sg-2"],
                    },
                    "tags": {"tag1": "value1"},
                },
                {
                    "computeEnvironmentName": "env2",
                    "computeEnvironmentArn": "arn:aws:batch:region:account:compute-environment/env2",
                    "state": "DISABLED",
                    "computeResources": {
                        "type": "EC2",
                        "maxvCpus": 20,
                        "subnets": ["subnet-3", "subnet-4"],
                        "securityGroupIds": ["sg-3", "sg-4"],
                    },
                    "tags": {"tag2": "value2"},
                },
            ]
        }

        # Test
        result = list_compute_environments()

        # Verify
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "Name" in result.columns
        assert "ARN" in result.columns
        assert "State" in result.columns
        assert "Type" in result.columns
        assert "Max vCPUs" in result.columns
        assert "Subnets" in result.columns
        assert "Security Group IDs" in result.columns
        assert "Tags" in result.columns

        # Check values
        assert result.iloc[0]["Name"] == "env1"
        assert result.iloc[0]["ARN"] == "arn:aws:batch:region:account:compute-environment/env1"
        assert result.iloc[0]["State"] == "ENABLED"
        assert result.iloc[0]["Type"] == "FARGATE"
        assert result.iloc[0]["Max vCPUs"] == 10
        assert result.iloc[0]["Subnets"] == ["subnet-1", "subnet-2"]
        assert result.iloc[0]["Security Group IDs"] == ["sg-1", "sg-2"]
        assert result.iloc[0]["Tags"] == {"tag1": "value1"}

        assert result.iloc[1]["Name"] == "env2"
        assert result.iloc[1]["ARN"] == "arn:aws:batch:region:account:compute-environment/env2"
        assert result.iloc[1]["State"] == "DISABLED"
        assert result.iloc[1]["Type"] == "EC2"
        assert result.iloc[1]["Max vCPUs"] == 20
        assert result.iloc[1]["Subnets"] == ["subnet-3", "subnet-4"]
        assert result.iloc[1]["Security Group IDs"] == ["sg-3", "sg-4"]
        assert result.iloc[1]["Tags"] == {"tag2": "value2"}


class TestToggleComputeEnvironment:
    def test_toggle_compute_environment_enabled_to_disabled(self, mock_batch_client):
        """Test toggling a compute environment from ENABLED to DISABLED."""
        # Setup mock responses
        mock_batch_client.describe_compute_environments.return_value = {
            "computeEnvironments": [
                {
                    "computeEnvironmentName": "test-env",
                    "computeEnvironmentArn": "arn:aws:batch:region:account:compute-environment/test-env",
                    "state": "ENABLED",
                }
            ]
        }

        mock_batch_client.update_compute_environment.return_value = {
            "computeEnvironmentArn": "arn:aws:batch:region:account:compute-environment/test-env",
            "computeEnvironmentName": "test-env",
        }

        # Test
        response, new_state = toggle_compute_environment("test-env")

        # Verify
        assert response["computeEnvironmentArn"] == "arn:aws:batch:region:account:compute-environment/test-env"
        assert new_state == "DISABLED"

        mock_batch_client.describe_compute_environments.assert_called_once_with(computeEnvironments=["test-env"])
        mock_batch_client.update_compute_environment.assert_called_once_with(
            computeEnvironment="test-env", state="DISABLED"
        )

    def test_toggle_compute_environment_disabled_to_enabled(self, mock_batch_client):
        """Test toggling a compute environment from DISABLED to ENABLED."""
        # Setup mock responses
        mock_batch_client.describe_compute_environments.return_value = {
            "computeEnvironments": [
                {
                    "computeEnvironmentName": "test-env",
                    "computeEnvironmentArn": "arn:aws:batch:region:account:compute-environment/test-env",
                    "state": "DISABLED",
                }
            ]
        }

        mock_batch_client.update_compute_environment.return_value = {
            "computeEnvironmentArn": "arn:aws:batch:region:account:compute-environment/test-env",
            "computeEnvironmentName": "test-env",
        }

        # Test
        response, new_state = toggle_compute_environment("test-env")

        # Verify
        assert response["computeEnvironmentArn"] == "arn:aws:batch:region:account:compute-environment/test-env"
        assert new_state == "ENABLED"

        mock_batch_client.describe_compute_environments.assert_called_once_with(computeEnvironments=["test-env"])
        mock_batch_client.update_compute_environment.assert_called_once_with(
            computeEnvironment="test-env", state="ENABLED"
        )

    def test_toggle_nonexistent_compute_environment(self, mock_batch_client):
        """Test toggling a nonexistent compute environment."""
        # Setup mock responses for nonexistent environment
        mock_batch_client.describe_compute_environments.return_value = {"computeEnvironments": []}

        # Test
        with pytest.raises(ValueError, match="Compute environment test-env does not exist"):
            toggle_compute_environment("test-env")

    def test_toggle_compute_environment_missing_state(self, mock_batch_client):
        """Test toggling a compute environment with missing state."""
        # Setup mock responses with missing state
        mock_batch_client.describe_compute_environments.return_value = {
            "computeEnvironments": [
                {
                    "computeEnvironmentName": "test-env",
                    "computeEnvironmentArn": "arn:aws:batch:region:account:compute-environment/test-env",
                    # Missing state
                }
            ]
        }

        # Test
        with pytest.raises(ValueError, match="State of compute environment test-env is not available"):
            toggle_compute_environment("test-env")


class TestDeleteComputeEnvironment:
    def test_delete_compute_environment(self, mock_batch_client):
        """Test deleting a compute environment."""
        # Test
        delete_compute_environment("test-env")

        # Verify
        mock_batch_client.delete_compute_environment.assert_called_once_with(computeEnvironment="test-env")
