# Advanced Usage

This section covers advanced features and techniques for using ezbatch.

## Preloader Functionality

ezbatch includes a preloader script that can be used to download data from S3 before job execution and upload data to S3 after job execution. This is particularly useful for jobs that need to process large amounts of data.

To use the preloader, set the `preloader` parameter to `True` when creating an `EZBatchJob`:

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
    preloader=True,  # Enable the preloader
)
```

When the preloader is enabled, ezbatch will:

1. Download data from the specified S3 paths to the specified local paths before executing the command
2. Execute the command
3. Upload data from the specified local paths to the specified S3 paths after executing the command

The preloader script automatically installs the AWS CLI if it's not already installed in the container, so you don't need to include it in your Docker image.

## Job Dependencies

ezbatch allows you to create complex workflows with dependencies between jobs. This is useful for creating multi-stage pipelines where the output of one job is used as input for another job.

To create a workflow with dependencies, specify the dependencies when creating the workflow:

```python
from ezbatch.workflow import EZBatchWorkflow, EZBatchJob

workflow = EZBatchWorkflow(
    name="example-workflow",
    jobs={
        "job1": EZBatchJob(
            image="public.ecr.aws/ubuntu/ubuntu:22.04",
            command="echo Job 1; mkdir -p /mnt/output; echo 'Hello from Job 1' > /mnt/output/job1.txt",
            mounts=S3Mounts(
                write=[
                    {
                        "source": "/mnt/output",
                        "destination": "s3://my-bucket/output/job1",
                        "recursive": True,
                    }
                ],
            ),
            preloader=True,
        ),
        "job2": EZBatchJob(
            image="public.ecr.aws/ubuntu/ubuntu:22.04",
            command="echo Job 2; cat /mnt/input/job1.txt",
            mounts=S3Mounts(
                read=[
                    {
                        "source": "s3://my-bucket/output/job1",
                        "destination": "/mnt/input",
                        "recursive": True,
                    }
                ],
            ),
            preloader=True,
        ),
    },
    dependencies={
        "job2": ["job1"],  # job2 depends on job1
    },
)
```

In this example, `job2` depends on `job1`, so `job1` will be executed first, and `job2` will only be executed after `job1` has completed successfully.

You can create more complex dependency graphs by specifying multiple dependencies:

```python
dependencies={
    "job2": ["job1"],  # job2 depends on job1
    "job3": ["job1"],  # job3 depends on job1
    "job4": ["job2", "job3"],  # job4 depends on job2 and job3
}
```

## Resource Configuration

ezbatch allows you to configure the resources allocated to each job. This includes CPU, memory, and storage.

```python
job = EZBatchJob(
    image="public.ecr.aws/ubuntu/ubuntu:22.04",
    command="echo hello, world!",
    vcpus=4,  # Allocate 4 vCPUs
    memory=8192,  # Allocate 8 GB of memory
    storage_size=100,  # Allocate 100 GB of storage
)
```

The resource requirements depend on the platform:

- **Fargate**: Supports specific combinations of vCPUs and memory. See the [AWS Fargate documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-cpu-memory-error.html) for details.
- **EC2**: Supports a wider range of vCPUs and memory combinations, depending on the instance types available in your compute environment.

## Platform Selection

ezbatch supports two platforms for running jobs:

- **Fargate**: A serverless compute engine for containers. You don't need to provision or manage servers.
- **EC2**: Traditional EC2 instances that you can configure and manage.

To specify the platform, use the `platform` parameter when creating an `EZBatchJob`:

```python
# Fargate job
fargate_job = EZBatchJob(
    image="public.ecr.aws/ubuntu/ubuntu:22.04",
    command="echo hello, world!",
    platform="FARGATE",
)

# EC2 job
ec2_job = EZBatchJob(
    image="public.ecr.aws/ubuntu/ubuntu:22.04",
    command="echo hello, world!",
    platform="EC2",
)
```

### When to Use Fargate

Fargate is a good choice when:

- You want to avoid managing EC2 instances
- Your jobs have predictable resource requirements
- Your jobs are relatively short-lived
- You want to pay only for the resources you use

### When to Use EC2

EC2 is a good choice when:

- You need more control over the instances running your jobs
- Your jobs have specific hardware requirements
- Your jobs are long-running
- You want to take advantage of Spot Instances for cost savings

## Tags

ezbatch allows you to add tags to jobs, which can be useful for tracking and organizing your jobs.

```python
job = EZBatchJob(
    image="public.ecr.aws/ubuntu/ubuntu:22.04",
    command="echo hello, world!",
    tags={
        "Project": "MyProject",
        "Environment": "Development",
        "Owner": "JohnDoe",
    },
)
```

These tags will be applied to the AWS Batch job and can be used for filtering and reporting.

## Queue Selection

ezbatch allows you to specify the job queue to use when submitting a workflow. You can specify the queue at the workflow level or at the job level.

```python
# Specify the queue at the workflow level
workflow = EZBatchWorkflow(
    name="example-workflow",
    jobs={
        "job1": EZBatchJob(
            image="public.ecr.aws/ubuntu/ubuntu:22.04",
            command="echo Job 1",
        ),
        "job2": EZBatchJob(
            image="public.ecr.aws/ubuntu/ubuntu:22.04",
            command="echo Job 2",
        ),
    },
)
workflow.submit(queue="my-job-queue")

# Specify the queue at the job level
workflow = EZBatchWorkflow(
    name="example-workflow",
    jobs={
        "job1": EZBatchJob(
            image="public.ecr.aws/ubuntu/ubuntu:22.04",
            command="echo Job 1",
            queue="job1-queue",
        ),
        "job2": EZBatchJob(
            image="public.ecr.aws/ubuntu/ubuntu:22.04",
            command="echo Job 2",
            queue="job2-queue",
        ),
    },
)
workflow.submit()
```

If you specify the queue at both the workflow level and the job level, the job-level queue takes precedence.

## Saving and Loading Workflows

ezbatch allows you to save workflows to a file and load them later. This is useful for creating reusable workflow templates.

```python
# Save a workflow to a file
workflow = EZBatchWorkflow(
    name="example-workflow",
    jobs={
        "job1": EZBatchJob(
            image="public.ecr.aws/ubuntu/ubuntu:22.04",
            command="echo Job 1",
        ),
        "job2": EZBatchJob(
            image="public.ecr.aws/ubuntu/ubuntu:22.04",
            command="echo Job 2",
        ),
    },
    dependencies={
        "job2": ["job1"],
    },
)
workflow.save("workflow.json")

# Load a workflow from a file
loaded_workflow = EZBatchWorkflow.load("workflow.json")
loaded_workflow.submit(queue="my-job-queue")
```

This allows you to create workflow templates that can be reused and shared with others.
