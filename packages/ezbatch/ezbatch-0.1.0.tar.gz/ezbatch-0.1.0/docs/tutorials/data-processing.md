# Data Processing with ezbatch

This tutorial demonstrates how to use ezbatch to process data using AWS Batch. We'll create a workflow that downloads data from S3, processes it, and uploads the results back to S3.

## Prerequisites

Before you begin, make sure you have:

1. Installed ezbatch (`pip install ezbatch`)
2. Set up your AWS credentials
3. Created a compute environment and job queue (see the [Getting Started](../user-guide/01-getting-started.md) guide)
4. An S3 bucket with some data to process
5. Permissions to read from and write to the S3 bucket

## Step 1: Prepare Your Data

For this tutorial, we'll assume you have a CSV file in an S3 bucket that you want to process. Let's say the file is located at `s3://my-bucket/input/data.csv`.

## Step 2: Create a Docker Image

We need a Docker image that contains the tools we need to process the data. For this tutorial, we'll use a Python image and install pandas for data processing.

Create a Dockerfile:

```dockerfile
FROM python:3.9-slim

# Install dependencies
RUN pip install pandas

# Set the working directory
WORKDIR /app

# Copy the processing script
COPY process.py .

# Set the entrypoint
ENTRYPOINT ["python", "process.py"]
```

Create a processing script (`process.py`):

```python
import os
import pandas as pd
import sys

def process_data(input_file, output_file):
    """Process the data and save the results."""
    print(f"Processing {input_file}...")
    
    # Read the data
    df = pd.read_csv(input_file)
    
    # Process the data (example: calculate mean of each column)
    result = df.mean().to_frame().T
    
    # Save the results
    result.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    # Get the input and output directories from the command line
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Process all CSV files in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith(".csv"):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, f"processed_{filename}")
            process_data(input_file, output_file)
```

Build and push the Docker image to a registry (e.g., Amazon ECR):

```bash
# Build the image
docker build -t data-processor .

# Tag the image
docker tag data-processor:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/data-processor:latest

# Push the image
docker push <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/data-processor:latest
```

## Step 3: Create a Job to Process the Data

Now we'll create a job that uses our Docker image to process the data:

```python
from ezbatch.workflow import EZBatchJob, EZBatchWorkflow
from ezbatch.s3 import S3Mounts

# Create a job to process the data
job = EZBatchJob(
    image="<your-account-id>.dkr.ecr.<your-region>.amazonaws.com/data-processor:latest",
    command="/mnt/input /mnt/output",  # Pass input and output directories to the script
    mounts=S3Mounts(
        read=[
            {
                "source": "s3://my-bucket/input",
                "destination": "/mnt/input",
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
    vcpus=2,
    memory=4096,
    platform="FARGATE",
    preloader=True,  # Enable the preloader to use S3 mounts
)

# Create a workflow with the job
workflow = EZBatchWorkflow(
    name="data-processing-workflow",
    jobs={
        "process-data": job,
    },
)
```

## Step 4: Submit the Workflow

Now that we have created a workflow with our job, we can submit it to AWS Batch:

```python
# Submit the workflow to a job queue
workflow.submit(queue="my-job-queue")
```

Replace `"my-job-queue"` with the name of your job queue.

## Step 5: Monitor the Job

You can monitor the job using the AWS Management Console or the ezbatch CLI:

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
from ezbatch.s3 import S3Mounts

# Create a job to process the data
job = EZBatchJob(
    image="<your-account-id>.dkr.ecr.<your-region>.amazonaws.com/data-processor:latest",
    command="/mnt/input /mnt/output",  # Pass input and output directories to the script
    mounts=S3Mounts(
        read=[
            {
                "source": "s3://my-bucket/input",
                "destination": "/mnt/input",
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
    vcpus=2,
    memory=4096,
    platform="FARGATE",
    preloader=True,  # Enable the preloader to use S3 mounts
)

# Create a workflow with the job
workflow = EZBatchWorkflow(
    name="data-processing-workflow",
    jobs={
        "process-data": job,
    },
)

# Submit the workflow to a job queue
workflow.submit(queue="my-job-queue")
```

Save this code to a file (e.g., `process_data.py`) and run it:

```bash
python process_data.py
```

## Explanation

Let's break down what's happening in this example:

1. We create a Docker image that contains the tools we need to process the data. The image includes a Python script that reads CSV files, processes them, and saves the results.

2. We create an `EZBatchJob` with the following parameters:
   - `image`: The Docker image to use for the job. We're using the image we built and pushed to Amazon ECR.
   - `command`: The command to run in the container. We're passing the input and output directories to the script.
   - `mounts`: The S3 mounts to mount in the container. We're mounting the input directory from S3 to `/mnt/input` and the output directory from `/mnt/output` to S3.
   - `vcpus`: The number of vCPUs to allocate for the job. We're using 2 vCPUs.
   - `memory`: The amount of memory to allocate for the job, in MiB. We're using 4096 MiB (4 GB).
   - `platform`: The platform to run the job on. We're using Fargate.
   - `preloader`: Whether to preload the job with the EZBatch preloader script. We're enabling this to use S3 mounts.

3. We create an `EZBatchWorkflow` with the following parameters:
   - `name`: The name of the workflow. We're calling it "data-processing-workflow".
   - `jobs`: A dictionary of job names to `EZBatchJob` objects. We're adding our job with the name "process-data".

4. We submit the workflow to a job queue using the `submit` method, specifying the name of the job queue.

## Next Steps

Now that you've processed data using AWS Batch, you can try more advanced features:

- [Training a machine learning model on AWS Batch](ml-training.md)
- [Running a parameter sweep using AWS Batch](parameter-sweep.md)
- [Creating a multi-stage pipeline using AWS Batch](multi-stage-pipeline.md)

You can also explore the [Advanced Usage](../user-guide/03-advanced-usage.md) guide to learn more about the advanced features of ezbatch.
