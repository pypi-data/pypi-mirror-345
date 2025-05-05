# Machine Learning Training with ezbatch

This tutorial demonstrates how to use ezbatch to train a machine learning model on AWS Batch. We'll create a workflow that downloads training data from S3, trains a model, and uploads the trained model back to S3.

## Prerequisites

Before you begin, make sure you have:

1. Installed ezbatch (`pip install ezbatch`)
2. Set up your AWS credentials
3. Created a compute environment and job queue (see the [Getting Started](../user-guide/01-getting-started.md) guide)
4. An S3 bucket with training data
5. Permissions to read from and write to the S3 bucket

## Step 1: Prepare Your Training Data

For this tutorial, we'll assume you have training data in an S3 bucket. Let's say the data is located at `s3://my-bucket/training-data/`.

## Step 2: Create a Docker Image

We need a Docker image that contains the tools we need to train the model. For this tutorial, we'll use a Python image and install scikit-learn for machine learning.

Create a Dockerfile:

```dockerfile
FROM python:3.9-slim

# Install dependencies
RUN pip install scikit-learn pandas joblib

# Set the working directory
WORKDIR /app

# Copy the training script
COPY train.py .

# Set the entrypoint
ENTRYPOINT ["python", "train.py"]
```

Create a training script (`train.py`):

```python
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import sys

def train_model(data_dir, model_dir):
    """Train a machine learning model and save it."""
    print(f"Loading data from {data_dir}...")
    
    # Load the data
    data_file = os.path.join(data_dir, "data.csv")
    df = pd.read_csv(data_file)
    
    # Prepare the data
    X = df.drop("target", axis=1)
    y = df["target"]
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the model
    print("Training the model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.4f}")
    
    # Save the model
    model_file = os.path.join(model_dir, "model.joblib")
    joblib.dump(model, model_file)
    print(f"Model saved to {model_file}")

if __name__ == "__main__":
    # Get the data and model directories from the command line
    data_dir = sys.argv[1]
    model_dir = sys.argv[2]
    
    # Create the model directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)
    
    # Train the model
    train_model(data_dir, model_dir)
```

Build and push the Docker image to a registry (e.g., Amazon ECR):

```bash
# Build the image
docker build -t ml-trainer .

# Tag the image
docker tag ml-trainer:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/ml-trainer:latest

# Push the image
docker push <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/ml-trainer:latest
```

## Step 3: Create a Job to Train the Model

Now we'll create a job that uses our Docker image to train the model:

```python
from ezbatch.workflow import EZBatchJob, EZBatchWorkflow
from ezbatch.s3 import S3Mounts

# Create a job to train the model
job = EZBatchJob(
    image="<your-account-id>.dkr.ecr.<your-region>.amazonaws.com/ml-trainer:latest",
    command="/mnt/data /mnt/model",  # Pass data and model directories to the script
    mounts=S3Mounts(
        read=[
            {
                "source": "s3://my-bucket/training-data",
                "destination": "/mnt/data",
                "recursive": True,
            }
        ],
        write=[
            {
                "source": "/mnt/model",
                "destination": "s3://my-bucket/models",
                "recursive": True,
            }
        ],
    ),
    vcpus=4,
    memory=8192,
    platform="EC2",  # Use EC2 for more compute power
    preloader=True,  # Enable the preloader to use S3 mounts
)

# Create a workflow with the job
workflow = EZBatchWorkflow(
    name="ml-training-workflow",
    jobs={
        "train-model": job,
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

# Create a job to train the model
job = EZBatchJob(
    image="<your-account-id>.dkr.ecr.<your-region>.amazonaws.com/ml-trainer:latest",
    command="/mnt/data /mnt/model",  # Pass data and model directories to the script
    mounts=S3Mounts(
        read=[
            {
                "source": "s3://my-bucket/training-data",
                "destination": "/mnt/data",
                "recursive": True,
            }
        ],
        write=[
            {
                "source": "/mnt/model",
                "destination": "s3://my-bucket/models",
                "recursive": True,
            }
        ],
    ),
    vcpus=4,
    memory=8192,
    platform="EC2",  # Use EC2 for more compute power
    preloader=True,  # Enable the preloader to use S3 mounts
)

# Create a workflow with the job
workflow = EZBatchWorkflow(
    name="ml-training-workflow",
    jobs={
        "train-model": job,
    },
)

# Submit the workflow to a job queue
workflow.submit(queue="my-job-queue")
```

Save this code to a file (e.g., `train_model.py`) and run it:

```bash
python train_model.py
```

## Explanation

Let's break down what's happening in this example:

1. We create a Docker image that contains the tools we need to train the model. The image includes a Python script that loads training data, trains a random forest classifier, and saves the trained model.

2. We create an `EZBatchJob` with the following parameters:
   - `image`: The Docker image to use for the job. We're using the image we built and pushed to Amazon ECR.
   - `command`: The command to run in the container. We're passing the data and model directories to the script.
   - `mounts`: The S3 mounts to mount in the container. We're mounting the training data from S3 to `/mnt/data` and the model directory from `/mnt/model` to S3.
   - `vcpus`: The number of vCPUs to allocate for the job. We're using 4 vCPUs for faster training.
   - `memory`: The amount of memory to allocate for the job, in MiB. We're using 8192 MiB (8 GB) for larger datasets.
   - `platform`: The platform to run the job on. We're using EC2 for more compute power.
   - `preloader`: Whether to preload the job with the EZBatch preloader script. We're enabling this to use S3 mounts.

3. We create an `EZBatchWorkflow` with the following parameters:
   - `name`: The name of the workflow. We're calling it "ml-training-workflow".
   - `jobs`: A dictionary of job names to `EZBatchJob` objects. We're adding our job with the name "train-model".

4. We submit the workflow to a job queue using the `submit` method, specifying the name of the job queue.

## Using GPU Instances

If your machine learning workload can benefit from GPU acceleration, you can use GPU instances by specifying the appropriate instance type in your compute environment.

When creating your compute environment, specify the instance type:

```bash
ezbatch-cli compute-environment create --name gpu-compute-environment --type EC2 --maxvCpus 256 --instance-type p3.2xlarge
```

Then, when creating your job queue, specify the GPU compute environment:

```bash
ezbatch-cli job-queue create --name gpu-job-queue --compute-environment gpu-compute-environment
```

Finally, when submitting your workflow, specify the GPU job queue:

```python
workflow.submit(queue="gpu-job-queue")
```

## Next Steps

Now that you've trained a machine learning model on AWS Batch, you can try more advanced features:

- [Running a parameter sweep using AWS Batch](parameter-sweep.md)
- [Creating a multi-stage pipeline using AWS Batch](multi-stage-pipeline.md)

You can also explore the [Advanced Usage](../user-guide/03-advanced-usage.md) guide to learn more about the advanced features of ezbatch.
