# Parameter Sweep with ezbatch

This tutorial demonstrates how to use ezbatch to perform a parameter sweep on AWS Batch. A parameter sweep is a technique where you run the same algorithm multiple times with different parameter values to find the optimal configuration.

## Prerequisites

Before you begin, make sure you have:

1. Installed ezbatch (`pip install ezbatch`)
2. Set up your AWS credentials
3. Created a compute environment and job queue (see the [Getting Started](../user-guide/01-getting-started.md) guide)
4. An S3 bucket with training data
5. Permissions to read from and write to the S3 bucket

## Step 1: Prepare Your Data

For this tutorial, we'll assume you have training data in an S3 bucket. Let's say the data is located at `s3://my-bucket/training-data/`.

## Step 2: Create a Docker Image

We need a Docker image that contains the tools we need to train the model with different parameters. For this tutorial, we'll use a Python image and install scikit-learn for machine learning.

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
import json

def train_model(data_dir, model_dir, params):
    """Train a machine learning model with the given parameters and save it."""
    print(f"Loading data from {data_dir}...")
    
    # Load the data
    data_file = os.path.join(data_dir, "data.csv")
    df = pd.read_csv(data_file)
    
    # Prepare the data
    X = df.drop("target", axis=1)
    y = df["target"]
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the model with the given parameters
    print(f"Training the model with parameters: {params}")
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.4f}")
    
    # Save the model
    model_file = os.path.join(model_dir, f"model_{params['n_estimators']}_{params['max_depth']}.joblib")
    joblib.dump(model, model_file)
    print(f"Model saved to {model_file}")
    
    # Save the results
    results = {
        "parameters": params,
        "accuracy": accuracy,
        "model_file": model_file,
    }
    results_file = os.path.join(model_dir, f"results_{params['n_estimators']}_{params['max_depth']}.json")
    with open(results_file, "w") as f:
        json.dump(results, f)
    print(f"Results saved to {results_file}")
    
    return accuracy

if __name__ == "__main__":
    # Get the data and model directories from the command line
    data_dir = sys.argv[1]
    model_dir = sys.argv[2]
    n_estimators = int(sys.argv[3])
    max_depth = int(sys.argv[4]) if sys.argv[4] != "None" else None
    
    # Create the model directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)
    
    # Set the parameters
    params = {
        "n_estimators": n_estimators,
        "max_depth": max_depth,
        "random_state": 42,
    }
    
    # Train the model
    train_model(data_dir, model_dir, params)
```

Build and push the Docker image to a registry (e.g., Amazon ECR):

```bash
# Build the image
docker build -t param-sweep .

# Tag the image
docker tag param-sweep:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/param-sweep:latest

# Push the image
docker push <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/param-sweep:latest
```

## Step 3: Create Jobs for the Parameter Sweep

Now we'll create multiple jobs, each with a different set of parameters:

```python
from ezbatch.workflow import EZBatchJob, EZBatchWorkflow
from ezbatch.s3 import S3Mounts

# Define the parameter grid
n_estimators_list = [10, 50, 100, 200]
max_depth_list = [None, 5, 10, 15, 20]

# Create jobs for each parameter combination
jobs = {}
for n_estimators in n_estimators_list:
    for max_depth in max_depth_list:
        # Create a unique job name
        job_name = f"train-n{n_estimators}-d{max_depth if max_depth is not None else 'None'}"
        
        # Create the job
        job = EZBatchJob(
            image="<your-account-id>.dkr.ecr.<your-region>.amazonaws.com/param-sweep:latest",
            command=f"/mnt/data /mnt/model {n_estimators} {max_depth if max_depth is not None else 'None'}",
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
                        "destination": f"s3://my-bucket/models/n{n_estimators}-d{max_depth if max_depth is not None else 'None'}",
                        "recursive": True,
                    }
                ],
            ),
            vcpus=2,
            memory=4096,
            platform="EC2",
            preloader=True,
        )
        
        # Add the job to the jobs dictionary
        jobs[job_name] = job

# Create a workflow with all the jobs
workflow = EZBatchWorkflow(
    name="parameter-sweep-workflow",
    jobs=jobs,
)
```

## Step 4: Submit the Workflow

Now that we have created a workflow with all our jobs, we can submit it to AWS Batch:

```python
# Submit the workflow to a job queue
workflow.submit(queue="my-job-queue")
```

Replace `"my-job-queue"` with the name of your job queue.

## Step 5: Monitor the Jobs

You can monitor the jobs using the AWS Management Console or the ezbatch CLI:

```bash
# List jobs in the queue
ezbatch-cli jobs list --queue my-job-queue
```

You can also use the interactive mode to monitor jobs:

```bash
ezbatch-cli interactive
```

## Step 6: Analyze the Results

After all the jobs have completed, you can analyze the results to find the best parameters:

```python
import boto3
import json
import pandas as pd

# Initialize the S3 client
s3 = boto3.client('s3')

# Define the parameter grid
n_estimators_list = [10, 50, 100, 200]
max_depth_list = [None, 5, 10, 15, 20]

# Create a list to store the results
results = []

# Get the results for each parameter combination
for n_estimators in n_estimators_list:
    for max_depth in max_depth_list:
        # Define the S3 path
        s3_path = f"models/n{n_estimators}-d{max_depth if max_depth is not None else 'None'}/results_{n_estimators}_{max_depth if max_depth is not None else 'None'}.json"
        
        try:
            # Download the results file
            response = s3.get_object(Bucket='my-bucket', Key=s3_path)
            result = json.loads(response['Body'].read().decode('utf-8'))
            
            # Add the result to the list
            results.append(result)
        except Exception as e:
            print(f"Error getting results for n_estimators={n_estimators}, max_depth={max_depth}: {e}")

# Convert the results to a DataFrame
results_df = pd.DataFrame(results)

# Find the best parameters
best_result = results_df.loc[results_df['accuracy'].idxmax()]
print(f"Best parameters: {best_result['parameters']}")
print(f"Best accuracy: {best_result['accuracy']:.4f}")
print(f"Best model file: {best_result['model_file']}")
```

## Complete Example

Here's a complete example that you can run:

```python
from ezbatch.workflow import EZBatchJob, EZBatchWorkflow
from ezbatch.s3 import S3Mounts

# Define the parameter grid
n_estimators_list = [10, 50, 100, 200]
max_depth_list = [None, 5, 10, 15, 20]

# Create jobs for each parameter combination
jobs = {}
for n_estimators in n_estimators_list:
    for max_depth in max_depth_list:
        # Create a unique job name
        job_name = f"train-n{n_estimators}-d{max_depth if max_depth is not None else 'None'}"
        
        # Create the job
        job = EZBatchJob(
            image="<your-account-id>.dkr.ecr.<your-region>.amazonaws.com/param-sweep:latest",
            command=f"/mnt/data /mnt/model {n_estimators} {max_depth if max_depth is not None else 'None'}",
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
                        "destination": f"s3://my-bucket/models/n{n_estimators}-d{max_depth if max_depth is not None else 'None'}",
                        "recursive": True,
                    }
                ],
            ),
            vcpus=2,
            memory=4096,
            platform="EC2",
            preloader=True,
        )
        
        # Add the job to the jobs dictionary
        jobs[job_name] = job

# Create a workflow with all the jobs
workflow = EZBatchWorkflow(
    name="parameter-sweep-workflow",
    jobs=jobs,
)

# Submit the workflow to a job queue
workflow.submit(queue="my-job-queue")
```

Save this code to a file (e.g., `parameter_sweep.py`) and run it:

```bash
python parameter_sweep.py
```

## Explanation

Let's break down what's happening in this example:

1. We create a Docker image that contains the tools we need to train the model with different parameters. The image includes a Python script that loads training data, trains a random forest classifier with the specified parameters, and saves the trained model and results.

2. We define a parameter grid with different values for `n_estimators` and `max_depth`.

3. We create a job for each parameter combination:
   - Each job uses the same Docker image but with different command-line arguments to specify the parameters.
   - Each job writes its results to a different S3 path based on the parameters.

4. We create a workflow with all the jobs and submit it to AWS Batch.

5. After all the jobs have completed, we analyze the results to find the best parameters.

## Next Steps

Now that you've performed a parameter sweep on AWS Batch, you can try more advanced features:

- [Creating a multi-stage pipeline using AWS Batch](multi-stage-pipeline.md)

You can also explore the [Advanced Usage](../user-guide/03-advanced-usage.md) guide to learn more about the advanced features of ezbatch.
