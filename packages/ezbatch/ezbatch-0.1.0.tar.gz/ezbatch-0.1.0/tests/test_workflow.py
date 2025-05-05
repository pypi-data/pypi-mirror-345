import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ezbatch.s3 import S3Mounts
from ezbatch.workflow import (
    EZBatchJob,
    EZBatchJobDefinition,
    EZBatchWorkflow,
    sanitize_name,
)


class TestSanitizeName:
    def test_sanitize_name(self):
        """Test sanitizing a name."""
        # Test
        result = sanitize_name("test-name")

        # Verify
        assert result == "test_name"

        # Test with special characters
        result = sanitize_name("test@name!123")

        # Verify
        assert result == "test_name_123"


class TestEZBatchJob:
    def test_ezbatch_job_init(self):
        """Test initializing an EZBatchJob."""
        # Test
        job = EZBatchJob(
            image="test-image",
            command="echo hello",
            environment={"ENV_VAR": "value"},
            vcpus=2,
            memory=4096,
            storage_size=50,
            platform="FARGATE",
            tags={"tag1": "value1"},
            queue="test-queue",
            preloader=False,
        )

        # Verify
        assert job.image == "test-image"
        assert job.command == "echo hello"
        assert job.environment == {"ENV_VAR": "value"}
        assert job.vcpus == 2
        assert job.memory == 4096
        assert job.storage_size == 50
        assert job.platform == "FARGATE"
        assert job.tags == {"tag1": "value1"}
        assert job.queue == "test-queue"
        assert job.preloader is False
        assert job._job_name == "test-image-job"

    def test_ezbatch_job_init_defaults(self):
        """Test initializing an EZBatchJob with default values."""
        # Test
        job = EZBatchJob(
            image="test-image",
            command="echo hello",
        )

        # Verify
        assert job.image == "test-image"
        assert job.command == "echo hello"
        assert job.environment == {}
        assert isinstance(job.mounts, S3Mounts)
        assert job.vcpus == 1
        assert job.memory == 2048
        assert job.storage_size is None
        assert job.platform == "FARGATE"
        assert job.tags == {}
        assert job.queue is None
        assert job.preloader is False
        assert job._job_name == "test-image-job"

    @patch("ezbatch.workflow.S3Mounts.validate")
    def test_ezbatch_job_post_init(self, mock_validate):
        """Test post-initialization of an EZBatchJob."""
        # Test
        job = EZBatchJob(
            image="test-image",
            command="echo hello",
        )

        # Verify
        assert job._job_name == "test-image-job"
        mock_validate.assert_called_once()

    @patch("ezbatch.workflow.PRELOAD_COMMAND", ["preload", "command"])
    def test_ezbatch_job_to_definition_no_preloader(self):
        """Test converting an EZBatchJob to a job definition without preloader."""
        # Test
        job = EZBatchJob(
            image="test-image",
            command="echo hello",
            environment={"ENV_VAR": "value"},
            vcpus=2,
            memory=4096,
            storage_size=50,
            platform="FARGATE",
            tags={"tag1": "value1"},
            queue="test-queue",
            preloader=False,
        )

        definition = job.to_definition()

        # Verify
        assert definition["job_name"] == "test-image-job"
        assert definition["container_name"] == "test_image"
        assert definition["image"] == "test-image"
        assert definition["command"] == ["echo", "hello"]
        assert definition["environment"] == {"ENV_VAR": "value"}
        assert definition["vcpus"] == 2
        assert definition["memory"] == 4096
        assert definition["storage_size"] == 50
        assert definition["platform"] == "FARGATE"
        assert definition["tags"] == {"tag1": "value1"}

    @patch("ezbatch.workflow.PRELOAD_COMMAND", ["preload", "command"])
    def test_ezbatch_job_to_definition_with_preloader(self):
        """Test converting an EZBatchJob to a job definition with preloader."""
        # Test
        job = EZBatchJob(
            image="test-image",
            command="echo hello",
            environment={"ENV_VAR": "value"},
            vcpus=2,
            memory=4096,
            storage_size=50,
            platform="FARGATE",
            tags={"tag1": "value1"},
            queue="test-queue",
            preloader=True,
        )

        definition = job.to_definition()

        # Verify
        assert definition["job_name"] == "test-image-job"
        assert definition["container_name"] == "test_image"
        assert definition["image"] == "test-image"
        assert definition["command"] == ["preload", "command"]
        assert "ENV_VAR" in definition["environment"]
        assert "EZBATCH_COMMAND" in definition["environment"]
        assert definition["environment"]["EZBATCH_COMMAND"] == "echo hello"
        assert "EZBATCH_S3_MOUNTS" in definition["environment"]
        assert definition["vcpus"] == 2
        assert definition["memory"] == 4096
        assert definition["storage_size"] == 50
        assert definition["platform"] == "FARGATE"
        assert definition["tags"] == {"tag1": "value1"}


class TestEZBatchWorkflow:
    def test_ezbatch_workflow_init(self):
        """Test initializing an EZBatchWorkflow."""
        # Test
        job1 = EZBatchJob(
            image="test-image-1",
            command="echo hello 1",
        )

        job2 = EZBatchJob(
            image="test-image-2",
            command="echo hello 2",
        )

        workflow = EZBatchWorkflow(
            name="test-workflow",
            jobs={"job1": job1, "job2": job2},
            dependencies={"job2": ["job1"]},
        )

        # Verify
        assert workflow.name == "test-workflow"
        assert len(workflow.jobs) == 2
        assert "job1" in workflow.jobs
        assert "job2" in workflow.jobs
        assert workflow.dependencies == {"job2": ["job1"]}
        assert workflow._job_map == {}
        assert workflow._job_def_map == {}
        assert workflow._job_name_map == {}
        assert workflow._job_dependency_map == {}
        assert workflow._job_id_map == {}

    def test_job_submission_queue_no_dependencies(self):
        """Test creating a job submission queue with no dependencies."""
        # Test
        jobs = ["job1", "job2", "job3"]
        dependency_map = {}

        # Test
        result = EZBatchWorkflow.job_submission_queue(jobs, dependency_map)

        # Verify
        assert len(result) == 3
        assert set(result) == set(jobs)

    def test_job_submission_queue_with_dependencies(self):
        """Test creating a job submission queue with dependencies."""
        # Test
        jobs = ["job1", "job2", "job3"]
        dependency_map = {
            "job2": ["job1"],
            "job3": ["job2"],
        }

        # Test
        result = EZBatchWorkflow.job_submission_queue(jobs, dependency_map)

        # Verify
        assert len(result) == 3
        assert result.index("job1") < result.index("job2")
        assert result.index("job2") < result.index("job3")

    def test_job_submission_queue_with_complex_dependencies(self):
        """Test creating a job submission queue with complex dependencies."""
        # Test
        jobs = ["job1", "job2", "job3", "job4", "job5"]
        dependency_map = {
            "job2": ["job1"],
            "job3": ["job1"],
            "job4": ["job2", "job3"],
            "job5": ["job4"],
        }

        # Test
        result = EZBatchWorkflow.job_submission_queue(jobs, dependency_map)

        # Verify
        assert len(result) == 5
        assert result.index("job1") < result.index("job2")
        assert result.index("job1") < result.index("job3")
        assert result.index("job2") < result.index("job4")
        assert result.index("job3") < result.index("job4")
        assert result.index("job4") < result.index("job5")

    def test_job_submission_queue_with_dependency_loop(self):
        """Test creating a job submission queue with a dependency loop."""
        # Test
        jobs = ["job1", "job2", "job3"]
        dependency_map = {
            "job1": ["job3"],
            "job2": ["job1"],
            "job3": ["job2"],
        }

        # Test
        with pytest.raises(ValueError, match="Dependency loop detected"):
            EZBatchWorkflow.job_submission_queue(jobs, dependency_map)

    @patch("ezbatch.workflow.RandomWords")
    @patch("ezbatch.workflow.create_ezbatch_job_definition")
    @patch("ezbatch.workflow.submit_job")
    @patch("ezbatch.workflow.deregister_job_definition")
    def test_submit_workflow(self, mock_deregister, mock_submit, mock_create, mock_random_words):
        """Test submitting a workflow."""
        # Setup mock responses
        mock_random = MagicMock()
        # Need to provide enough random words for all calls in the workflow.submit method
        mock_random.get_random_word.side_effect = [
            "word1",
            "word2",
            "word3",
            "word4",
            "word5",
            "word6",
            "word7",
            "word8",
        ]
        mock_random_words.return_value = mock_random

        mock_create.side_effect = [
            {"jobDefinitionArn": "arn:aws:batch:region:account:job-definition/job1:1"},
            {"jobDefinitionArn": "arn:aws:batch:region:account:job-definition/job2:1"},
        ]

        mock_submit.side_effect = [
            {"jobId": "job-id-1"},
            {"jobId": "job-id-2"},
        ]

        # Test
        job1 = EZBatchJob(
            image="test-image-1",
            command="echo hello 1",
            queue="test-queue",
        )

        job2 = EZBatchJob(
            image="test-image-2",
            command="echo hello 2",
            queue="test-queue",
        )

        workflow = EZBatchWorkflow(
            name="test-workflow",
            jobs={"job1": job1, "job2": job2},
            dependencies={"job2": ["job1"]},
        )

        workflow.submit()

        # Verify
        assert mock_create.call_count == 2
        assert mock_submit.call_count == 2
        assert mock_deregister.call_count == 2

        # Check that job1 was submitted before job2
        job1_name = "test-workflow-Word1Word2-job1-Word3Word4"
        job2_name = "test-workflow-Word1Word2-job2-Word5Word6"

        # First job submission should be job1
        mock_submit.assert_any_call(
            name=job1_name,
            queue="test-queue",
            definition="arn:aws:batch:region:account:job-definition/job1:1",
            depends_on=[],
            tags={
                "workflowName": "test-workflow",
                "job": "job1",
                "ezbatchWorkflowId": "Word1Word2",
                "ezbatchJobId": "Word3Word4",
            },
        )

        # Second job submission should be job2 with dependency on job1
        mock_submit.assert_any_call(
            name=job2_name,
            queue="test-queue",
            definition="arn:aws:batch:region:account:job-definition/job2:1",
            depends_on=[{"jobId": "job-id-1"}],
            tags={
                "workflowName": "test-workflow",
                "job": "job2",
                "ezbatchWorkflowId": "Word1Word2",
                "ezbatchJobId": "Word5Word6",
            },
        )

    @patch("ezbatch.workflow.RandomWords")
    @patch("ezbatch.workflow.create_ezbatch_job_definition")
    @patch("ezbatch.workflow.submit_job")
    @patch("ezbatch.workflow.deregister_job_definition")
    def test_submit_workflow_with_queue_override(self, mock_deregister, mock_submit, mock_create, mock_random_words):
        """Test submitting a workflow with queue override."""
        # Setup mock responses
        mock_random = MagicMock()
        # Need to provide enough random words for all calls in the workflow.submit method
        mock_random.get_random_word.side_effect = [
            "word1",
            "word2",
            "word3",
            "word4",
            "word5",
            "word6",
            "word7",
            "word8",
        ]
        mock_random_words.return_value = mock_random

        mock_create.side_effect = [
            {"jobDefinitionArn": "arn:aws:batch:region:account:job-definition/job1:1"},
            {"jobDefinitionArn": "arn:aws:batch:region:account:job-definition/job2:1"},
        ]

        mock_submit.side_effect = [
            {"jobId": "job-id-1"},
            {"jobId": "job-id-2"},
        ]

        # Test
        job1 = EZBatchJob(
            image="test-image-1",
            command="echo hello 1",
        )

        job2 = EZBatchJob(
            image="test-image-2",
            command="echo hello 2",
            queue="job2-queue",  # Override the queue for job2
        )

        workflow = EZBatchWorkflow(
            name="test-workflow",
            jobs={"job1": job1, "job2": job2},
            dependencies={"job2": ["job1"]},
        )

        workflow.submit(queue="workflow-queue")

        # Verify
        assert mock_create.call_count == 2
        assert mock_submit.call_count == 2
        assert mock_deregister.call_count == 2

        # Check that job1 was submitted before job2
        job1_name = "test-workflow-Word1Word2-job1-Word3Word4"
        job2_name = "test-workflow-Word1Word2-job2-Word5Word6"

        # First job submission should be job1 with workflow queue
        mock_submit.assert_any_call(
            name=job1_name,
            queue="workflow-queue",
            definition="arn:aws:batch:region:account:job-definition/job1:1",
            depends_on=[],
            tags={
                "workflowName": "test-workflow",
                "job": "job1",
                "ezbatchWorkflowId": "Word1Word2",
                "ezbatchJobId": "Word3Word4",
            },
        )

        # Second job submission should be job2 with job2 queue
        mock_submit.assert_any_call(
            name=job2_name,
            queue="job2-queue",
            definition="arn:aws:batch:region:account:job-definition/job2:1",
            depends_on=[{"jobId": "job-id-1"}],
            tags={
                "workflowName": "test-workflow",
                "job": "job2",
                "ezbatchWorkflowId": "Word1Word2",
                "ezbatchJobId": "Word5Word6",
            },
        )

    @patch("ezbatch.workflow.RandomWords")
    @patch("ezbatch.workflow.create_ezbatch_job_definition")
    @patch("ezbatch.workflow.submit_job")
    @patch("ezbatch.workflow.deregister_job_definition")
    def test_submit_workflow_no_queue(self, mock_deregister, mock_submit, mock_create, mock_random_words):
        """Test submitting a workflow with no queue."""
        # Setup mock responses
        mock_random = MagicMock()
        # Need to provide enough random words for all calls in the workflow.submit method
        mock_random.get_random_word.side_effect = [
            "word1",
            "word2",
            "word3",
            "word4",
            "word5",
            "word6",
            "word7",
            "word8",
        ]
        mock_random_words.return_value = mock_random

        mock_create.side_effect = [
            {"jobDefinitionArn": "arn:aws:batch:region:account:job-definition/job1:1"},
            {"jobDefinitionArn": "arn:aws:batch:region:account:job-definition/job2:1"},
        ]

        # Test
        job1 = EZBatchJob(
            image="test-image-1",
            command="echo hello 1",
        )

        job2 = EZBatchJob(
            image="test-image-2",
            command="echo hello 2",
        )

        workflow = EZBatchWorkflow(
            name="test-workflow",
            jobs={"job1": job1, "job2": job2},
            dependencies={"job2": ["job1"]},
        )

        # Test
        with pytest.raises(ValueError, match="Queue must be provided at the workflow or job level"):
            workflow.submit()

    def test_save_workflow(self):
        """Test saving a workflow to a file."""
        # Test
        job1 = EZBatchJob(
            image="test-image-1",
            command="echo hello 1",
        )

        job2 = EZBatchJob(
            image="test-image-2",
            command="echo hello 2",
        )

        workflow = EZBatchWorkflow(
            name="test-workflow",
            jobs={"job1": job1, "job2": job2},
            dependencies={"job2": ["job1"]},
        )

        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".json") as temp_file:
            # Save the workflow
            workflow.save(temp_file.name)

            # Read the file
            with open(temp_file.name) as f:
                data = json.load(f)

            # Verify
            assert data["name"] == "test-workflow"
            assert "jobs" in data
            assert "job1" in data["jobs"]
            assert "job2" in data["jobs"]
            assert data["dependencies"] == {"job2": ["job1"]}

            # Check that internal variables are not saved
            assert "_job_map" not in data
            assert "_job_def_map" not in data
            assert "_job_name_map" not in data
            assert "_job_dependency_map" not in data
            assert "_job_id_map" not in data

    def test_load_workflow(self):
        """Test loading a workflow from a file."""
        # Create a temporary file with workflow data
        workflow_data = {
            "name": "test-workflow",
            "jobs": {
                "job1": {
                    "image": "test-image-1",
                    "command": "echo hello 1",
                },
                "job2": {
                    "image": "test-image-2",
                    "command": "echo hello 2",
                },
            },
            "dependencies": {
                "job2": ["job1"],
            },
        }

        with tempfile.NamedTemporaryFile(suffix=".json", mode="w") as temp_file:
            # Write the workflow data
            json.dump(workflow_data, temp_file)
            temp_file.flush()

            # Load the workflow
            workflow = EZBatchWorkflow.load(temp_file.name)

            # Verify
            assert workflow.name == "test-workflow"
            assert len(workflow.jobs) == 2
            assert "job1" in workflow.jobs
            assert "job2" in workflow.jobs
            assert workflow.dependencies == {"job2": ["job1"]}

            # Check job properties
            assert workflow.jobs["job1"].image == "test-image-1"
            assert workflow.jobs["job1"].command == "echo hello 1"
            assert workflow.jobs["job2"].image == "test-image-2"
            assert workflow.jobs["job2"].command == "echo hello 2"
