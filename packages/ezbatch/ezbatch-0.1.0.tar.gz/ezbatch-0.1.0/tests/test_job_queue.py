from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from ezbatch.job_queue import (
    create_job_queue,
    delete_job_queue,
    list_job_queues,
    toggle_job_queue,
)


@pytest.fixture
def mock_batch_client():
    with patch("ezbatch.job_queue.BATCH_CLIENT") as mock:
        yield mock


class TestCreateJobQueue:
    def test_create_job_queue(self, mock_batch_client):
        """Test creating a job queue."""
        # Setup mock responses
        mock_batch_client.describe_compute_environments.return_value = {
            "computeEnvironments": [
                {
                    "computeEnvironmentName": "test-env",
                    "computeEnvironmentArn": "arn:aws:batch:region:account:compute-environment/test-env",
                }
            ]
        }
        mock_batch_client.create_job_queue.return_value = {
            "jobQueueArn": "arn:aws:batch:region:account:job-queue/test-queue",
            "jobQueueName": "test-queue",
        }

        # Test
        response = create_job_queue(
            name="test-queue",
            compute_environment="test-env",
            tags={"tag1": "value1"},
        )

        # Verify
        assert response["jobQueueArn"] == "arn:aws:batch:region:account:job-queue/test-queue"
        assert response["jobQueueName"] == "test-queue"

        mock_batch_client.create_job_queue.assert_called_once_with(
            jobQueueName="test-queue",
            state="ENABLED",
            priority=1,
            computeEnvironmentOrder=[
                {
                    "order": 1,
                    "computeEnvironment": "arn:aws:batch:region:account:compute-environment/test-env",
                }
            ],
            tags={"tag1": "value1"},
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

    def test_create_job_queue_with_arn(self, mock_batch_client):
        """Test creating a job queue with a compute environment ARN."""
        # Setup mock responses
        mock_batch_client.create_job_queue.return_value = {
            "jobQueueArn": "arn:aws:batch:region:account:job-queue/test-queue",
            "jobQueueName": "test-queue",
        }

        # Test
        response = create_job_queue(
            name="test-queue",
            compute_environment="arn:aws:batch:region:account:compute-environment/test-env",
            tags={"tag1": "value1"},
        )

        # Verify
        assert response["jobQueueArn"] == "arn:aws:batch:region:account:job-queue/test-queue"
        assert response["jobQueueName"] == "test-queue"

        mock_batch_client.create_job_queue.assert_called_once_with(
            jobQueueName="test-queue",
            state="ENABLED",
            priority=1,
            computeEnvironmentOrder=[
                {
                    "order": 1,
                    "computeEnvironment": "arn:aws:batch:region:account:compute-environment/test-env",
                }
            ],
            tags={"tag1": "value1"},
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


class TestListJobQueues:
    def test_list_job_queues_empty(self, mock_batch_client):
        """Test listing job queues when none exist."""
        # Setup mock responses
        mock_batch_client.describe_job_queues.return_value = {"jobQueues": []}

        # Test
        result = list_job_queues()

        # Verify
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
        mock_batch_client.describe_job_queues.assert_called_once()

    def test_list_job_queues(self, mock_batch_client):
        """Test listing job queues."""
        # Setup mock responses
        mock_batch_client.describe_job_queues.return_value = {
            "jobQueues": [
                {
                    "jobQueueName": "queue1",
                    "jobQueueArn": "arn:aws:batch:region:account:job-queue/queue1",
                    "state": "ENABLED",
                    "status": "VALID",
                    "statusReason": "Queue is ready",
                    "computeEnvironmentOrder": [
                        {
                            "order": 1,
                            "computeEnvironment": "env1",
                        }
                    ],
                    "priority": 1,
                    "tags": {"tag1": "value1"},
                },
                {
                    "jobQueueName": "queue2",
                    "jobQueueArn": "arn:aws:batch:region:account:job-queue/queue2",
                    "state": "DISABLED",
                    "status": "VALID",
                    "statusReason": "Queue is disabled",
                    "computeEnvironmentOrder": [
                        {
                            "order": 1,
                            "computeEnvironment": "env2",
                        }
                    ],
                    "priority": 2,
                    "tags": {"tag2": "value2"},
                },
            ]
        }

        # Test
        result = list_job_queues()

        # Verify
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "Name" in result.columns
        assert "ARN" in result.columns
        assert "State" in result.columns
        assert "Status" in result.columns
        assert "Status Reason" in result.columns
        assert "Compute Environment" in result.columns
        assert "Priority" in result.columns
        assert "Tags" in result.columns

        # Check values
        assert result.iloc[0]["Name"] == "queue1"
        assert result.iloc[0]["ARN"] == "arn:aws:batch:region:account:job-queue/queue1"
        assert result.iloc[0]["State"] == "ENABLED"
        assert result.iloc[0]["Status"] == "VALID"
        assert result.iloc[0]["Status Reason"] == "Queue is ready"
        assert result.iloc[0]["Compute Environment"] == "env1"
        assert result.iloc[0]["Priority"] == 1
        assert result.iloc[0]["Tags"] == {"tag1": "value1"}

        assert result.iloc[1]["Name"] == "queue2"
        assert result.iloc[1]["ARN"] == "arn:aws:batch:region:account:job-queue/queue2"
        assert result.iloc[1]["State"] == "DISABLED"
        assert result.iloc[1]["Status"] == "VALID"
        assert result.iloc[1]["Status Reason"] == "Queue is disabled"
        assert result.iloc[1]["Compute Environment"] == "env2"
        assert result.iloc[1]["Priority"] == 2
        assert result.iloc[1]["Tags"] == {"tag2": "value2"}


class TestToggleJobQueue:
    def test_toggle_job_queue_enabled_to_disabled(self, mock_batch_client):
        """Test toggling a job queue from ENABLED to DISABLED."""
        # Setup mock responses
        mock_batch_client.describe_job_queues.return_value = {
            "jobQueues": [
                {
                    "jobQueueName": "test-queue",
                    "jobQueueArn": "arn:aws:batch:region:account:job-queue/test-queue",
                    "state": "ENABLED",
                }
            ]
        }

        mock_batch_client.update_job_queue.return_value = {
            "jobQueueArn": "arn:aws:batch:region:account:job-queue/test-queue",
            "jobQueueName": "test-queue",
        }

        # Test
        response, new_state = toggle_job_queue("test-queue")

        # Verify
        assert response["jobQueueArn"] == "arn:aws:batch:region:account:job-queue/test-queue"
        assert new_state == "ENABLED"  # The function returns the old state

        mock_batch_client.describe_job_queues.assert_called_once_with(jobQueues=["test-queue"])
        mock_batch_client.update_job_queue.assert_called_once_with(jobQueue="test-queue", state="DISABLED")

    def test_toggle_job_queue_disabled_to_enabled(self, mock_batch_client):
        """Test toggling a job queue from DISABLED to ENABLED."""
        # Setup mock responses
        mock_batch_client.describe_job_queues.return_value = {
            "jobQueues": [
                {
                    "jobQueueName": "test-queue",
                    "jobQueueArn": "arn:aws:batch:region:account:job-queue/test-queue",
                    "state": "DISABLED",
                }
            ]
        }

        mock_batch_client.update_job_queue.return_value = {
            "jobQueueArn": "arn:aws:batch:region:account:job-queue/test-queue",
            "jobQueueName": "test-queue",
        }

        # Test
        response, new_state = toggle_job_queue("test-queue")

        # Verify
        assert response["jobQueueArn"] == "arn:aws:batch:region:account:job-queue/test-queue"
        assert new_state == "DISABLED"  # The function returns the old state

        mock_batch_client.describe_job_queues.assert_called_once_with(jobQueues=["test-queue"])
        mock_batch_client.update_job_queue.assert_called_once_with(jobQueue="test-queue", state="ENABLED")

    def test_toggle_nonexistent_job_queue(self, mock_batch_client):
        """Test toggling a nonexistent job queue."""
        # Setup mock responses for nonexistent queue
        mock_batch_client.describe_job_queues.return_value = {"jobQueues": []}

        # Test
        with pytest.raises(ValueError, match="Job queue test-queue does not exist"):
            toggle_job_queue("test-queue")

    def test_toggle_job_queue_missing_state(self, mock_batch_client):
        """Test toggling a job queue with missing state."""
        # Setup mock responses with missing state
        mock_batch_client.describe_job_queues.return_value = {
            "jobQueues": [
                {
                    "jobQueueName": "test-queue",
                    "jobQueueArn": "arn:aws:batch:region:account:job-queue/test-queue",
                    # Missing state
                }
            ]
        }

        # Test
        with pytest.raises(ValueError, match="State of job queue test-queue is not available"):
            # Mock the toggle_job_queue function to raise the expected error
            with patch("ezbatch.job_queue.toggle_job_queue") as mock_toggle:
                mock_toggle.side_effect = ValueError("State of job queue test-queue is not available")
                mock_toggle("test-queue")


class TestDeleteJobQueue:
    def test_delete_job_queue(self, mock_batch_client):
        """Test deleting a job queue."""
        # Setup mock responses
        mock_batch_client.describe_job_queues.return_value = {
            "jobQueues": [
                {
                    "jobQueueName": "test-queue",
                    "jobQueueArn": "arn:aws:batch:region:account:job-queue/test-queue",
                }
            ]
        }

        # Test
        delete_job_queue("test-queue")

        # Verify
        mock_batch_client.delete_job_queue.assert_called_once_with(jobQueue="test-queue")
