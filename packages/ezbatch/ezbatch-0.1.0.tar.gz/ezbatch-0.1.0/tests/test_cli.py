import argparse
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from ezbatch.scripts.cli import ezbatch_cli, sanitize_args


class TestSanitizeArgs:
    def test_sanitize_args(self):
        """Test sanitize_args function."""
        # Create test args
        args = {
            "command": "compute-environment",
            "subcommand": "create",
            "name": "test-env",
            "service_role": "test-role",
            "type": "FARGATE",
            "max_vcpus": 10,
            "subnets": ["subnet-1", "subnet-2"],
            "security_group_ids": ["sg-1", "sg-2"],
            "tags": ["tag1=value1", "tag2=value2"],
            "none_value": None,
        }

        # Sanitize args
        result = sanitize_args(args)

        # Verify
        assert "command" not in result
        assert "subcommand" not in result
        assert "none_value" not in result
        assert result["name"] == "test-env"
        assert result["service_role"] == "test-role"
        assert result["type"] == "FARGATE"
        assert result["max_vcpus"] == 10
        assert result["subnets"] == ["subnet-1", "subnet-2"]
        assert result["security_group_ids"] == ["sg-1", "sg-2"]
        assert result["tags"] == ["tag1=value1", "tag2=value2"]


class TestEZBatchCLI:
    @patch("ezbatch.scripts.cli.ArgumentParser")
    def test_cli_parser_setup(self, mock_arg_parser):
        """Test that the CLI parser is set up correctly."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_arg_parser.return_value = mock_parser

        mock_subparsers = MagicMock()
        mock_parser.add_subparsers.return_value = mock_subparsers

        mock_ce_command = MagicMock()
        mock_jq_command = MagicMock()
        mock_jd_command = MagicMock()
        mock_jobs_command = MagicMock()
        mock_interactive_command = MagicMock()

        mock_subparsers.add_parser.side_effect = [
            mock_ce_command,
            mock_jq_command,
            mock_jd_command,
            mock_jobs_command,
            mock_interactive_command,
        ]

        mock_ce_subcommands = MagicMock()
        mock_ce_command.add_subparsers.return_value = mock_ce_subcommands

        mock_jq_subcommands = MagicMock()
        mock_jq_command.add_subparsers.return_value = mock_jq_subcommands

        mock_jd_subcommands = MagicMock()
        mock_jd_command.add_subparsers.return_value = mock_jd_subcommands

        mock_jobs_subcommands = MagicMock()
        mock_jobs_command.add_subparsers.return_value = mock_jobs_subcommands

        # Mock parse_args to return an object with no command
        mock_args = MagicMock()
        mock_args.command = None
        mock_parser.parse_args.return_value = mock_args

        # Call the CLI function
        ezbatch_cli()

        # Verify parser setup
        # Use patch to check that add_argument was called with the right arguments
        # without checking the exact version string
        assert mock_parser.add_argument.called
        call_args = mock_parser.add_argument.call_args_list
        version_call = [call for call in call_args if call[0] == ("--version", "-v")][0]
        assert version_call[1]["action"] == "version"
        assert isinstance(version_call[1]["version"], str)
        mock_parser.add_subparsers.assert_called_once()

        # Verify subparsers were created
        assert mock_subparsers.add_parser.call_count == 5

        # Check that each command was added
        commands = [call[0][0] for call in mock_subparsers.add_parser.call_args_list]
        assert "compute-environment" in commands
        assert "job-queue" in commands
        assert "job-definition" in commands
        assert "jobs" in commands
        assert "interactive" in commands

    @patch("ezbatch.scripts.cli.create_compute_environment")
    @patch("ezbatch.scripts.cli.ArgumentParser")
    def test_compute_environment_create(self, mock_arg_parser, mock_create_ce):
        """Test compute-environment create command."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_arg_parser.return_value = mock_parser

        mock_args = MagicMock()
        mock_args.command = "compute-environment"
        mock_args.subcommand = "create"
        mock_args.name = "test-env"
        mock_args.service_role = "test-role"
        mock_args.type = "FARGATE"
        mock_args.max_vcpus = 10
        mock_args.subnets = ["subnet-1", "subnet-2"]
        mock_args.security_group_ids = ["sg-1", "sg-2"]
        mock_args.tags = ["tag1=value1", "tag2=value2"]
        mock_parser.parse_args.return_value = mock_args

        mock_create_ce.return_value = {
            "computeEnvironmentName": "test-env",
            "computeEnvironmentArn": "arn:aws:batch:region:account:compute-environment/test-env",
        }

        # Call the CLI function
        with patch("builtins.print") as mock_print:
            ezbatch_cli()

        # Verify
        mock_create_ce.assert_called_once()
        call_args = mock_create_ce.call_args[1]
        assert call_args["name"] == "test-env"
        assert call_args["service_role"] == "test-role"
        assert call_args["type"] == "FARGATE"
        assert call_args["max_vcpus"] == 10
        assert call_args["subnets"] == ["subnet-1", "subnet-2"]
        assert call_args["security_group_ids"] == ["sg-1", "sg-2"]
        assert call_args["tags"] == {"tag1": "value1", "tag2": "value2"}

        mock_print.assert_called_once_with("Compute environment test-env created.")

    @patch("ezbatch.scripts.cli.list_compute_environments")
    @patch("ezbatch.scripts.cli.ArgumentParser")
    def test_compute_environment_list(self, mock_arg_parser, mock_list_ce):
        """Test compute-environment list command."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_arg_parser.return_value = mock_parser

        mock_args = MagicMock()
        mock_args.command = "compute-environment"
        mock_args.subcommand = "list"
        mock_parser.parse_args.return_value = mock_args

        mock_df = MagicMock(spec=pd.DataFrame)
        mock_filtered_df = MagicMock(spec=pd.DataFrame)
        mock_df.__getitem__.return_value = mock_filtered_df
        mock_filtered_df.to_markdown.return_value = (
            "| Name | State | Type | Max vCPUs |\n|------|-------|------|----------|\n| env1 | ENABLED | FARGATE | 10 |"
        )
        mock_list_ce.return_value = mock_df

        # Call the CLI function
        with patch("builtins.print") as mock_print:
            ezbatch_cli()

        # Verify
        mock_list_ce.assert_called_once()
        mock_df.__getitem__.assert_called_once_with(["Name", "State", "Type", "Max vCPUs"])
        mock_filtered_df.to_markdown.assert_called_once_with(index=False)
        mock_print.assert_called_once_with(mock_filtered_df.to_markdown.return_value)

    @patch("ezbatch.scripts.cli.toggle_compute_environment")
    @patch("ezbatch.scripts.cli.ArgumentParser")
    def test_compute_environment_toggle(self, mock_arg_parser, mock_toggle_ce):
        """Test compute-environment toggle command."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_arg_parser.return_value = mock_parser

        mock_args = MagicMock()
        mock_args.command = "compute-environment"
        mock_args.subcommand = "toggle"
        mock_args.name = "test-env"
        mock_parser.parse_args.return_value = mock_args

        mock_toggle_ce.return_value = (
            {
                "computeEnvironmentName": "test-env",
                "computeEnvironmentArn": "arn:aws:batch:region:account:compute-environment/test-env",
            },
            "DISABLED",
        )

        # Call the CLI function
        with patch("builtins.print") as mock_print:
            ezbatch_cli()

        # Verify
        mock_toggle_ce.assert_called_once_with("test-env")
        mock_print.assert_called_once_with("Compute environment test-env is now DISABLED")

    @patch("ezbatch.scripts.cli.delete_compute_environment")
    @patch("ezbatch.scripts.cli.ArgumentParser")
    def test_compute_environment_delete(self, mock_arg_parser, mock_delete_ce):
        """Test compute-environment delete command."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_arg_parser.return_value = mock_parser

        mock_args = MagicMock()
        mock_args.command = "compute-environment"
        mock_args.subcommand = "delete"
        mock_args.name = "test-env"
        mock_parser.parse_args.return_value = mock_args

        # Call the CLI function
        with patch("builtins.print") as mock_print:
            ezbatch_cli()

        # Verify
        mock_delete_ce.assert_called_once_with("test-env")
        mock_print.assert_called_once_with("Compute environment test-env deleted.")

    @patch("ezbatch.scripts.cli.create_job_queue")
    @patch("ezbatch.scripts.cli.ArgumentParser")
    def test_job_queue_create(self, mock_arg_parser, mock_create_jq):
        """Test job-queue create command."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_arg_parser.return_value = mock_parser

        mock_args = MagicMock()
        mock_args.command = "job-queue"
        mock_args.subcommand = "create"
        mock_args.name = "test-queue"
        mock_args.compute_environment = "test-env"
        mock_args.tags = ["tag1=value1", "tag2=value2"]
        mock_parser.parse_args.return_value = mock_args

        mock_create_jq.return_value = {
            "jobQueueName": "test-queue",
            "jobQueueArn": "arn:aws:batch:region:account:job-queue/test-queue",
        }

        # Call the CLI function
        with patch("builtins.print") as mock_print:
            ezbatch_cli()

        # Verify
        mock_create_jq.assert_called_once()
        call_args = mock_create_jq.call_args[1]
        assert call_args["name"] == "test-queue"
        assert call_args["compute_environment"] == "test-env"
        assert call_args["tags"] == {"tag1": "value1", "tag2": "value2"}

        mock_print.assert_called_once_with("Job queue test-queue created.")

    @patch("ezbatch.scripts.cli.list_job_queues")
    @patch("ezbatch.scripts.cli.ArgumentParser")
    def test_job_queue_list(self, mock_arg_parser, mock_list_jq):
        """Test job-queue list command."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_arg_parser.return_value = mock_parser

        mock_args = MagicMock()
        mock_args.command = "job-queue"
        mock_args.subcommand = "list"
        mock_parser.parse_args.return_value = mock_args

        mock_df = MagicMock(spec=pd.DataFrame)
        mock_filtered_df = MagicMock(spec=pd.DataFrame)
        mock_df.__getitem__.return_value = mock_filtered_df
        mock_filtered_df.to_markdown.return_value = "| Name | State | Status | Status Reason | Compute Environment |\n|------|-------|--------|--------------|--------------------|\n| queue1 | ENABLED | VALID | Queue is ready | env1 |"
        mock_list_jq.return_value = mock_df

        # Call the CLI function
        with patch("builtins.print") as mock_print:
            ezbatch_cli()

        # Verify
        mock_list_jq.assert_called_once()
        mock_df.__getitem__.assert_called_once_with(["Name", "State", "Status", "Status Reason", "Compute Environment"])
        mock_filtered_df.to_markdown.assert_called_once_with(index=False)
        mock_print.assert_called_once_with(mock_filtered_df.to_markdown.return_value)

    @patch("ezbatch.scripts.cli.toggle_job_queue")
    @patch("ezbatch.scripts.cli.ArgumentParser")
    def test_job_queue_toggle(self, mock_arg_parser, mock_toggle_jq):
        """Test job-queue toggle command."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_arg_parser.return_value = mock_parser

        mock_args = MagicMock()
        mock_args.command = "job-queue"
        mock_args.subcommand = "toggle"
        mock_args.name = "test-queue"
        mock_parser.parse_args.return_value = mock_args

        mock_toggle_jq.return_value = (
            {
                "jobQueueName": "test-queue",
                "jobQueueArn": "arn:aws:batch:region:account:job-queue/test-queue",
            },
            "DISABLED",
        )

        # Call the CLI function
        with patch("builtins.print") as mock_print:
            ezbatch_cli()

        # Verify
        mock_toggle_jq.assert_called_once_with("test-queue")
        mock_print.assert_called_once_with("Job queue test-queue is now DISABLED")

    @patch("ezbatch.scripts.cli.delete_job_queue")
    @patch("ezbatch.scripts.cli.ArgumentParser")
    def test_job_queue_delete(self, mock_arg_parser, mock_delete_jq):
        """Test job-queue delete command."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_arg_parser.return_value = mock_parser

        mock_args = MagicMock()
        mock_args.command = "job-queue"
        mock_args.subcommand = "delete"
        mock_args.name = "test-queue"
        mock_parser.parse_args.return_value = mock_args

        # Call the CLI function
        with patch("builtins.print") as mock_print:
            ezbatch_cli()

        # Verify
        mock_delete_jq.assert_called_once_with("test-queue")
        mock_print.assert_called_once_with("Job queue test-queue deleted.")

    @patch("ezbatch.scripts.cli.submit_job")
    @patch("ezbatch.scripts.cli.ArgumentParser")
    def test_jobs_submit(self, mock_arg_parser, mock_submit_job):
        """Test jobs submit command."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_arg_parser.return_value = mock_parser

        mock_args = MagicMock()
        mock_args.command = "jobs"
        mock_args.subcommand = "submit"
        mock_args.name = "test-job"
        mock_args.queue = "test-queue"
        mock_args.definition = "test-definition:1"
        mock_parser.parse_args.return_value = mock_args

        mock_submit_job.return_value = {
            "jobName": "test-job",
            "jobId": "job-123",
        }

        # Call the CLI function
        with patch("builtins.print") as mock_print:
            ezbatch_cli()

        # Verify
        mock_submit_job.assert_called_once()
        call_args = mock_submit_job.call_args[1]
        assert call_args["name"] == "test-job"
        assert call_args["queue"] == "test-queue"
        assert call_args["definition"] == "test-definition:1"

        mock_print.assert_called_once_with(
            "Job test-job submitted to queue test-queue with definition test-definition:1"
        )

    @patch("ezbatch.scripts.cli.list_jobs")
    @patch("ezbatch.scripts.cli.ArgumentParser")
    def test_jobs_list(self, mock_arg_parser, mock_list_jobs):
        """Test jobs list command."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_arg_parser.return_value = mock_parser

        mock_args = MagicMock()
        mock_args.command = "jobs"
        mock_args.subcommand = "list"
        mock_args.queue = "test-queue"
        mock_parser.parse_args.return_value = mock_args

        # Call the CLI function
        ezbatch_cli()

        # Verify
        mock_list_jobs.assert_called_once_with("test-queue")

    @patch("ezbatch.scripts.cli.EZBatchManager")
    @patch("ezbatch.scripts.cli.ArgumentParser")
    def test_interactive(self, mock_arg_parser, mock_manager):
        """Test interactive command."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_arg_parser.return_value = mock_parser

        mock_args = MagicMock()
        mock_args.command = "interactive"
        mock_parser.parse_args.return_value = mock_args

        mock_app = MagicMock()
        mock_manager.return_value = mock_app

        # Call the CLI function
        ezbatch_cli()

        # Verify
        mock_manager.assert_called_once()
        mock_app.run.assert_called_once()
