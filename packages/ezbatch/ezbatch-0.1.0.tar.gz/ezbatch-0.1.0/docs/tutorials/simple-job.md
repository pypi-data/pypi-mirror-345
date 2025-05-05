# Running a Simple Job

This tutorial demonstrates how to run a simple job on AWS Batch using ezbatch.

## Prerequisites

Before you begin, make sure you have:

1. Installed ezbatch (`pip install ezbatch`)
2. Set up your AWS credentials
3. Created a compute environment and job queue (see the [Getting Started](../user-guide/01-getting-started.md) guide)

## Step 1: Create a Simple Job

Let's create a simple job that runs a basic command in a container. We'll use the public Ubuntu image from Amazon ECR.

```python
from ezbatch.workflow import EZBatchJob, EZBatchWorkflow

# Create a simple job
job = EZBatchJob(
    image="public.ecr.aws/ubuntu/ubuntu:22.04",
    command="echo 'Hello, World!' && date",
    vcpus=1,
    memory=2048,
    platform="FARGATE",
)

# Create a workflow with the job
workflow = EZBatchWorkflow(
    name="hello-world-workflow",
    jobs={
        "hello-world": job,
    },
)
```

## Step 2: Submit the Workflow

Now that we have created a workflow with our job, we can submit it to AWS Batch.

```python
# Submit the workflow to a job queue
workflow.submit(queue="my-job-queue")
```

Replace `"my-job-queue"` with the name of your job queue.

## Step 3: Monitor the Job

You can monitor the job using the AWS Management Console or the ezbatch CLI.

```bash
# List jobs in the queue
ezbatch-cli jobs list --queue my-job-queue
```

You can also use the interactive mode to monitor jobs:

```bash
ezbatch-cli interactive
```

## Complete Example

Here's a complete example that you can run:

```python
from ezbatch.workflow import EZBatchJob, EZBatchWorkflow

# Create a simple job
job = EZBatchJob(
    image="public.ecr.aws/ubuntu/ubuntu:22.04",
    command="echo 'Hello, World!' && date",
    vcpus=1,
    memory=2048,
    platform="FARGATE",
)

# Create a workflow with the job
workflow = EZBatchWorkflow(
    name="hello-world-workflow",
    jobs={
        "hello-world": job,
    },
)

# Submit the workflow to a job queue
workflow.submit(queue="my-job-queue")
```

Save this code to a file (e.g., `hello_world.py`) and run it:

```bash
python hello_world.py
```

## Explanation

Let's break down what's happening in this example:

1. We create an `EZBatchJob` with the following parameters:
   - `image`: The Docker image to use for the job. We're using the public Ubuntu image from Amazon ECR.
   - `command`: The command to run in the container. We're running a simple command that prints "Hello, World!" and the current date.
   - `vcpus`: The number of vCPUs to allocate for the job. We're using 1 vCPU.
   - `memory`: The amount of memory to allocate for the job, in MiB. We're using 2048 MiB (2 GB).
   - `platform`: The platform to run the job on. We're using Fargate, which is a serverless compute engine for containers.

2. We create an `EZBatchWorkflow` with the following parameters:
   - `name`: The name of the workflow. We're calling it "hello-world-workflow".
   - `jobs`: A dictionary of job names to `EZBatchJob` objects. We're adding our job with the name "hello-world".

3. We submit the workflow to a job queue using the `submit` method, specifying the name of the job queue.

## Next Steps

Now that you've run a simple job, you can try more advanced features:

- [Processing data using AWS Batch](data-processing.md)
- [Training a machine learning model on AWS Batch](ml-training.md)
- [Running a parameter sweep using AWS Batch](parameter-sweep.md)
- [Creating a multi-stage pipeline using AWS Batch](multi-stage-pipeline.md)

You can also explore the [Advanced Usage](../user-guide/03-advanced-usage.md) guide to learn more about the advanced features of ezbatch.
