# Workflows and Jobs

## Overview

In `ezbatch`, a *job* is a basic unit of work that can be run on AWS Batch.
A *job* is defined by a Docker container image to run, as well as the resources required to run the *job*.

A *workflow* is a collection of jobs that depend on each other and can be set to run in a specific order. 
A *workflow* contains a list of jobs and the dependencies between them.

## Creating a job

To create a job in `ezbatch`, you need to define the following:

1. **Docker Image**: Specify the Docker container image that contains the code and dependencies for the job.
2. **Command**: Provide the command to execute within the container.
3. **Resources**: Define the CPU, memory, and storage requirements for the job.
4. **Environment Variables**: Set any environment variables required by the job.
5. **S3 Mounts** (optional): Specify S3 paths to read from or write to during the job execution.

Example Python code to define a job:
```python
from ezbatch.s3 import S3Mounts
from ezbatch.workflow import EZBatchJob

job = EZBatchJob(
    image="public.ecr.aws/ubuntu/ubuntu:22.04",
    command="echo hello, world!",
    environment={"EXAMPLE_VAR": "value"},
    mounts=S3Mounts(
        read=[
            {"source": "s3://my-bucket/input", "destination": "/mnt/input", "recursive": True}
        ],
        write=[
            {"source": "/mnt/output", "destination": "s3://my-bucket/output", "recursive": True}
        ],
    ),
    vcpus=2,
    memory=4096,
    platform="FARGATE",
)
```

## Creating a Workflow

A workflow is a collection of jobs with defined dependencies. You can create a workflow by specifying the jobs and their dependencies.

Example Python code to define a workflow:
```python
from ezbatch.workflow import EZBatchWorkflow

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

## Running a Workflow

To run a workflow, use the `submit` method of the `EZBatchWorkflow` class. You can optionally specify a job queue.

Example Python code to run a workflow:
```python
workflow.submit(queue="my-job-queue")
```

You can also save the workflow to a file for reuse:
```python
workflow.save("workflow.json")
```

To load and run a saved workflow:
```python
from ezbatch.workflow import EZBatchWorkflow

loaded_workflow = EZBatchWorkflow.load("workflow.json")
loaded_workflow.submit(queue="my-job-queue")
```
