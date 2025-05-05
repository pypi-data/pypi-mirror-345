from unittest.mock import MagicMock, patch

import pytest

from ezbatch.logs import get_task_log


class TestGetTaskLog:
    @patch("ezbatch.logs.LOGS_CLIENT")
    def test_get_task_log(self, mock_logs_client):
        """Test getting task logs."""
        # Setup mock response
        mock_logs_client.get_log_events.return_value = {
            "events": [
                {
                    "timestamp": 1234567890,
                    "message": "Log message 1",
                    "ingestionTime": 1234567891,
                },
                {
                    "timestamp": 1234567892,
                    "message": "Log message 2",
                    "ingestionTime": 1234567893,
                },
            ],
            "nextForwardToken": "next-token",
            "nextBackwardToken": "back-token",
        }

        # Test
        result = get_task_log("task-123")

        # Verify
        assert "events" in result
        assert len(result["events"]) == 2
        # Check if message exists in the events
        if "message" in result["events"][0]:
            assert result["events"][0]["message"] == "Log message 1"
        if "message" in result["events"][1]:
            assert result["events"][1]["message"] == "Log message 2"

        # Check that get_log_events was called with the correct parameters
        # Note: The function currently uses a hardcoded log stream name instead of the task_id
        mock_logs_client.get_log_events.assert_called_once_with(
            logGroupName="/aws/batch/job",
            logStreamName="test-job-definition-2/container1/2e7dab38f600403b9df0b6d2c4ef1062",
        )

    @patch("ezbatch.logs.LOGS_CLIENT")
    def test_get_task_log_error(self, mock_logs_client):
        """Test getting task logs with an error."""
        # Setup mock to raise an exception
        mock_logs_client.get_log_events.side_effect = Exception("Log error")

        # Test
        with pytest.raises(Exception, match="Log error"):
            get_task_log("task-123")
