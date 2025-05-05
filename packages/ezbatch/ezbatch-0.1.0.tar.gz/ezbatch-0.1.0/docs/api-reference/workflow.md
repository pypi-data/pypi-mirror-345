# Workflow Module

The `workflow` module provides classes for creating and submitting workflows to AWS Batch. A workflow consists of one or more jobs with optional dependencies between them.

## EZBatchJob

```python
class EZBatchJob(DataClassJsonMixin):
    """A class representing a single EZBatch job in an EZBatch workflow.

    The Job class will be translated into an AWS Batch job definition.

    Attributes
    ----------
    image : str
        The Docker image to use for the job.
    command : str
        The command to run in the container.
    environment : dict[str, str]
        The environment variables to set in the container.
    mounts: S3Mounts
        The S3 mounts to mount in the container.
    vcpus : int
        The number of vCPUs to allocate for the job.
    memory : int
        The amount of memory to allocate for the job.
    storage_size : int, optional
        The amount of storage to allocate for the job, by default None.
    platform : Literal["FARGATE", "EC2"]
        The platform to run the job on.
    tags : dict[str, str]
        The tags to associate with the job.
    queue: str | None
        The name or ARN of the job queue to submit the job to. Overrides the workflow
        level queue if provided.
    preloader : bool
        Whether to preload the job with the EZBatch preloader script. This script will allow you to use the
        mounts variable to download/upload S3 data to the running container. If False, it's up to the user to
        manage s3 downloads/uploads. By default, this is False.
    """
```

### Parameters

- **image** (`str`): The Docker image to use for the job. This can be a public image from Docker Hub or a private image from Amazon ECR.
- **command** (`str`): The command to run in the container. This is the command that will be executed when the container starts.
- **environment** (`dict[str, str]`, optional): The environment variables to set in the container. Default is an empty dictionary.
- **mounts** (`S3Mounts`, optional): The S3 mounts to mount in the container. Default is an empty `S3Mounts` object.
- **vcpus** (`int`, optional): The number of vCPUs to allocate for the job. Default is 1.
- **memory** (`int`, optional): The amount of memory to allocate for the job, in MiB. Default is 2048.
- **storage_size** (`int`, optional): The amount of storage to allocate for the job, in GiB. Default is None.
- **platform** (`Literal["FARGATE", "EC2"]`, optional): The platform to run the job on. Default is "FARGATE".
- **tags** (`dict[str, str]`, optional): The tags to associate with the job. Default is an empty dictionary.
- **queue** (`str | None`, optional): The name or ARN of the job queue to submit the job to. Overrides the workflow level queue if provided. Default is None.
- **preloader** (`bool`, optional): Whether to preload the job with the EZBatch preloader script. This script will allow you to use the mounts variable to download/upload S3 data to the running container. If False, it's up to the user to manage s3 downloads/uploads. Default is False.

### Methods

#### to_definition

```python
def to_definition(self) -> EZBatchJobDefinition:
    """Convert the Job to a job definition.

    Returns
    -------
    EZBatchJobDefinition
        The job definition.
    """
```

Converts the `EZBatchJob` to a job definition that can be used to create an AWS Batch job definition.

## EZBatchWorkflow

```python
class EZBatchWorkflow(DataClassJsonMixin):
    """A class representing an EZBatch workflow.

    An EZBatch workflow is a collection of EZBatch jobs that are executed in a specific order.

    Attributes
    ----------
    name : str
        The name of the workflow.
    jobs : dict[str, EZBatchJob]
        A dictionary of job names to EZBatchJob objects.
    dependencies : dict[str, list[str]]
        A dictionary of job names to lists of job names that they depend on.
    """
```

### Parameters

- **name** (`str`): The name of the workflow.
- **jobs** (`dict[str, EZBatchJob]`): A dictionary of job names to `EZBatchJob` objects.
- **dependencies** (`dict[str, list[str]]`, optional): A dictionary of job names to lists of job names that they depend on. Default is an empty dictionary.

### Methods

#### job_submission_queue

```python
@staticmethod
def job_submission_queue(jobs: list[str], dependency_map: dict[str, list[str]]) -> list[str]:
    """Create a queue of job submissions based on job dependencies.

    Parameters
    ----------
    dependency_map : dict[str, list[str]]
        A dictionary mapping job names to lists of job names that they depend on.

    Returns
    -------
    list[str]
        A list of job names in the order that they should be submitted.
    """
```

Creates a queue of job submissions based on job dependencies. This is used internally by the `submit` method to determine the order in which jobs should be submitted.

#### submit

```python
def submit(self, queue: str | None = None):
    """Submit the workflow to AWS Batch.

    Parameters
    ----------
    queue : str | None
        The name or ARN of the job queue to submit the workflow to.
    """
```

Submits the workflow to AWS Batch. This method:

1. Registers job definitions for all jobs in the workflow
2. Determines the order in which jobs should be submitted based on dependencies
3. Submits the jobs to the specified job queue
4. Deregisters the job definitions when the workflow is complete

#### save

```python
def save(self, path: Path | str):
    """Save the workflow to a JSON file.

    Parameters
    ----------
    path : Path | str
        The path to save the workflow to.
    """
```

Saves the workflow to a JSON file. This allows you to create workflow templates that can be reused and shared with others.

#### load

```python
@classmethod
def load(cls, path: Path | str):
    """Load the workflow from a JSON file.

    Parameters
    ----------
    path : Path | str
        The path to load the workflow from.
    """
```

Loads a workflow from a JSON file. This allows you to reuse workflow templates that have been saved using the `save` method.

## Examples

### Creating a Simple Job

```python
from ezbatch.workflow import EZBatchJob

job = EZBatchJob(
    image="public.ecr.aws/ubuntu/ubuntu:22.04",
    command="echo hello, world!",
    vcpus=1,
    memory=2048,
    platform="FARGATE",
)
```

### Creating a Job with S3 Mounts

```python
from ezbatch.workflow import EZBatchJob
from ezbatch.s3 import S3Mounts

job = EZBatchJob(
    image="public.ecr.aws/ubuntu/ubuntu:22.04",
    command="echo hello, world!; ls -l /mnt/data;",
    environment={"TEST": "test"},
    mounts=S3Mounts(
        read=[
            {
                "source": "s3://my-bucket/input",
                "destination": "/mnt/data",
                "recursive": True,
            }
        ],
        write=[
            {
                "source": "/mnt/output",
                "destination": "s3://my-bucket/output",
                "recursive": True,
            }
        ],
    ),
    platform="EC2",
    preloader=True,
)
```

### Creating a Workflow

```python
from ezbatch.workflow import EZBatchWorkflow, EZBatchJob

workflow = EZBatchWorkflow(
    name="example-workflow",
    jobs={
        "job1": EZBatchJob(
            image="public.ecr.aws/ubuntu/ubuntu:22.04",
            command="echo Job 1",
            vcpus=1,
            memory=2048,
        ),
        "job2": EZBatchJob(
            image="public.ecr.aws/ubuntu/ubuntu:22.04",
            command="echo Job 2",
            vcpus=1,
            memory=2048,
        ),
    },
    dependencies={
        "job2": ["job1"],  # job2 depends on job1
    },
)
```

### Submitting a Workflow

```python
workflow.submit(queue="my-job-queue")
```

### Saving and Loading a Workflow

```python
# Save a workflow to a file
workflow.save("workflow.json")

# Load a workflow from a file
loaded_workflow = EZBatchWorkflow.load("workflow.json")
loaded_workflow.submit(queue="my-job-queue")
```
