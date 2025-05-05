# Multi-Stage Pipeline with ezbatch

This tutorial demonstrates how to use ezbatch to create a multi-stage pipeline on AWS Batch. A multi-stage pipeline consists of multiple jobs that depend on each other, with the output of one job serving as the input for the next job.

## Prerequisites

Before you begin, make sure you have:

1. Installed ezbatch (`pip install ezbatch`)
2. Set up your AWS credentials
3. Created a compute environment and job queue (see the [Getting Started](../user-guide/01-getting-started.md) guide)
4. An S3 bucket with raw data
5. Permissions to read from and write to the S3 bucket

## Pipeline Overview

In this tutorial, we'll create a three-stage pipeline for a machine learning workflow:

1. **Data Preprocessing**: Clean and prepare the raw data
2. **Model Training**: Train a machine learning model on the preprocessed data
3. **Model Evaluation**: Evaluate the trained model on a test dataset

Each stage will be implemented as a separate job, and the jobs will be connected through dependencies.

## Step 1: Prepare Your Data

For this tutorial, we'll assume you have raw data in an S3 bucket. Let's say the data is located at `s3://my-bucket/raw-data/`.

## Step 2: Create Docker Images for Each Stage

We need to create Docker images for each stage of the pipeline. Let's start with the data preprocessing stage.

### Data Preprocessing Image

Create a Dockerfile:

```dockerfile
FROM python:3.9-slim

# Install dependencies
RUN pip install pandas scikit-learn

# Set the working directory
WORKDIR /app

# Copy the preprocessing script
COPY preprocess.py .

# Set the entrypoint
ENTRYPOINT ["python", "preprocess.py"]
```

Create a preprocessing script (`preprocess.py`):

```python
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import sys

def preprocess_data(input_dir, output_dir):
    """Preprocess the raw data and save the preprocessed data."""
    print(f"Loading data from {input_dir}...")
    
    # Load the data
    data_file = os.path.join(input_dir, "raw_data.csv")
    df = pd.read_csv(data_file)
    
    # Preprocess the data
    print("Preprocessing the data...")
    
    # Handle missing values
    df = df.fillna(df.mean())
    
    # Remove outliers
    for column in df.select_dtypes(include=[np.number]).columns:
        if column != "target":
            mean = df[column].mean()
            std = df[column].std()
            df = df[(df[column] >= mean - 3 * std) & (df[column] <= mean + 3 * std)]
    
    # Split the data into training and testing sets
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    # Save the preprocessed data
    train_file = os.path.join(output_dir, "train.csv")
    test_file = os.path.join(output_dir, "test.csv")
    train_df.to_csv(train_file, index=False)
    test_df.to_csv(test_file, index=False)
    
    print(f"Preprocessed training data saved to {train_file}")
    print(f"Preprocessed testing data saved to {test_file}")

if __name__ == "__main__":
    # Get the input and output directories from the command line
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Preprocess the data
    preprocess_data(input_dir, output_dir)
```

Build and push the preprocessing image:

```bash
# Build the image
docker build -t data-preprocessor .

# Tag the image
docker tag data-preprocessor:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/data-preprocessor:latest

# Push the image
docker push <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/data-preprocessor:latest
```

### Model Training Image

Create a Dockerfile:

```dockerfile
FROM python:3.9-slim

# Install dependencies
RUN pip install pandas scikit-learn joblib

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
import joblib
import sys

def train_model(input_dir, output_dir):
    """Train a machine learning model and save it."""
    print(f"Loading data from {input_dir}...")
    
    # Load the training data
    train_file = os.path.join(input_dir, "train.csv")
    train_df = pd.read_csv(train_file)
    
    # Prepare the data
    X_train = train_df.drop("target", axis=1)
    y_train = train_df["target"]
    
    # Train the model
    print("Training the model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Save the model
    model_file = os.path.join(output_dir, "model.joblib")
    joblib.dump(model, model_file)
    print(f"Model saved to {model_file}")

if __name__ == "__main__":
    # Get the input and output directories from the command line
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Train the model
    train_model(input_dir, output_dir)
```

Build and push the training image:

```bash
# Build the image
docker build -t model-trainer .

# Tag the image
docker tag model-trainer:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/model-trainer:latest

# Push the image
docker push <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/model-trainer:latest
```

### Model Evaluation Image

Create a Dockerfile:

```dockerfile
FROM python:3.9-slim

# Install dependencies
RUN pip install pandas scikit-learn joblib

# Set the working directory
WORKDIR /app

# Copy the evaluation script
COPY evaluate.py .

# Set the entrypoint
ENTRYPOINT ["python", "evaluate.py"]
```

Create an evaluation script (`evaluate.py`):

```python
import os
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import sys
import json

def evaluate_model(data_dir, model_dir, output_dir):
    """Evaluate the trained model and save the results."""
    print(f"Loading model from {model_dir}...")
    
    # Load the model
    model_file = os.path.join(model_dir, "model.joblib")
    model = joblib.load(model_file)
    
    # Load the test data
    test_file = os.path.join(data_dir, "test.csv")
    test_df = pd.read_csv(test_file)
    
    # Prepare the data
    X_test = test_df.drop("target", axis=1)
    y_test = test_df["target"]
    
    # Evaluate the model
    print("Evaluating the model...")
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    
    # Save the results
    results = {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
    }
    
    results_file = os.path.join(output_dir, "evaluation_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=4)
    
    print(f"Evaluation results saved to {results_file}")

if __name__ == "__main__":
    # Get the directories from the command line
    data_dir = sys.argv[1]
    model_dir = sys.argv[2]
    output_dir = sys.argv[3]
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Evaluate the model
    evaluate_model(data_dir, model_dir, output_dir)
```

Build and push the evaluation image:

```bash
# Build the image
docker build -t model-evaluator .

# Tag the image
docker tag model-evaluator:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/model-evaluator:latest

# Push the image
docker push <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/model-evaluator:latest
```

## Step 3: Create the Pipeline

Now we'll create a workflow with three jobs, one for each stage of the pipeline:

```python
from ezbatch.workflow import EZBatchJob, EZBatchWorkflow
from ezbatch.s3 import S3Mounts

# Create the preprocessing job
preprocess_job = EZBatchJob(
    image="<your-account-id>.dkr.ecr.<your-region>.amazonaws.com/data-preprocessor:latest",
    command="/mnt/raw-data /mnt/preprocessed-data",
    mounts=S3Mounts(
        read=[
            {
                "source": "s3://my-bucket/raw-data",
                "destination": "/mnt/raw-data",
                "recursive": True,
            }
        ],
        write=[
            {
                "source": "/mnt/preprocessed-data",
                "destination": "s3://my-bucket/preprocessed-data",
                "recursive": True,
            }
        ],
    ),
    vcpus=2,
    memory=4096,
    platform="EC2",
    preloader=True,
)

# Create the training job
train_job = EZBatchJob(
    image="<your-account-id>.dkr.ecr.<your-region>.amazonaws.com/model-trainer:latest",
    command="/mnt/preprocessed-data /mnt/model",
    mounts=S3Mounts(
        read=[
            {
                "source": "s3://my-bucket/preprocessed-data",
                "destination": "/mnt/preprocessed-data",
                "recursive": True,
            }
        ],
        write=[
            {
                "source": "/mnt/model",
                "destination": "s3://my-bucket/model",
                "recursive": True,
            }
        ],
    ),
    vcpus=4,
    memory=8192,
    platform="EC2",
    preloader=True,
)

# Create the evaluation job
evaluate_job = EZBatchJob(
    image="<your-account-id>.dkr.ecr.<your-region>.amazonaws.com/model-evaluator:latest",
    command="/mnt/preprocessed-data /mnt/model /mnt/evaluation",
    mounts=S3Mounts(
        read=[
            {
                "source": "s3://my-bucket/preprocessed-data",
                "destination": "/mnt/preprocessed-data",
                "recursive": True,
            },
            {
                "source": "s3://my-bucket/model",
                "destination": "/mnt/model",
                "recursive": True,
            }
        ],
        write=[
            {
                "source": "/mnt/evaluation",
                "destination": "s3://my-bucket/evaluation",
                "recursive": True,
            }
        ],
    ),
    vcpus=2,
    memory=4096,
    platform="EC2",
    preloader=True,
)

# Create a workflow with the jobs and dependencies
workflow = EZBatchWorkflow(
    name="ml-pipeline-workflow",
    jobs={
        "preprocess": preprocess_job,
        "train": train_job,
        "evaluate": evaluate_job,
    },
    dependencies={
        "train": ["preprocess"],  # train depends on preprocess
        "evaluate": ["train"],    # evaluate depends on train
    },
)
```

## Step 4: Submit the Workflow

Now that we have created a workflow with our pipeline, we can submit it to AWS Batch:

```python
# Submit the workflow to a job queue
workflow.submit(queue="my-job-queue")
```

Replace `"my-job-queue"` with the name of your job queue.

## Step 5: Monitor the Pipeline

You can monitor the pipeline using the AWS Management Console or the ezbatch CLI:

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

# Create the preprocessing job
preprocess_job = EZBatchJob(
    image="<your-account-id>.dkr.ecr.<your-region>.amazonaws.com/data-preprocessor:latest",
    command="/mnt/raw-data /mnt/preprocessed-data",
    mounts=S3Mounts(
        read=[
            {
                "source": "s3://my-bucket/raw-data",
                "destination": "/mnt/raw-data",
                "recursive": True,
            }
        ],
        write=[
            {
                "source": "/mnt/preprocessed-data",
                "destination": "s3://my-bucket/preprocessed-data",
                "recursive": True,
            }
        ],
    ),
    vcpus=2,
    memory=4096,
    platform="EC2",
    preloader=True,
)

# Create the training job
train_job = EZBatchJob(
    image="<your-account-id>.dkr.ecr.<your-region>.amazonaws.com/model-trainer:latest",
    command="/mnt/preprocessed-data /mnt/model",
    mounts=S3Mounts(
        read=[
            {
                "source": "s3://my-bucket/preprocessed-data",
                "destination": "/mnt/preprocessed-data",
                "recursive": True,
            }
        ],
        write=[
            {
                "source": "/mnt/model",
                "destination": "s3://my-bucket/model",
                "recursive": True,
            }
        ],
    ),
    vcpus=4,
    memory=8192,
    platform="EC2",
    preloader=True,
)

# Create the evaluation job
evaluate_job = EZBatchJob(
    image="<your-account-id>.dkr.ecr.<your-region>.amazonaws.com/model-evaluator:latest",
    command="/mnt/preprocessed-data /mnt/model /mnt/evaluation",
    mounts=S3Mounts(
        read=[
            {
                "source": "s3://my-bucket/preprocessed-data",
                "destination": "/mnt/preprocessed-data",
                "recursive": True,
            },
            {
                "source": "s3://my-bucket/model",
                "destination": "/mnt/model",
                "recursive": True,
            }
        ],
        write=[
            {
                "source": "/mnt/evaluation",
                "destination": "s3://my-bucket/evaluation",
                "recursive": True,
            }
        ],
    ),
    vcpus=2,
    memory=4096,
    platform="EC2",
    preloader=True,
)

# Create a workflow with the jobs and dependencies
workflow = EZBatchWorkflow(
    name="ml-pipeline-workflow",
    jobs={
        "preprocess": preprocess_job,
        "train": train_job,
        "evaluate": evaluate_job,
    },
    dependencies={
        "train": ["preprocess"],  # train depends on preprocess
        "evaluate": ["train"],    # evaluate depends on train
    },
)

# Submit the workflow to a job queue
workflow.submit(queue="my-job-queue")
```

Save this code to a file (e.g., `ml_pipeline.py`) and run it:

```bash
python ml_pipeline.py
```

## Explanation

Let's break down what's happening in this example:

1. We create Docker images for each stage of the pipeline:
   - **Data Preprocessing**: This image contains a script that loads raw data, handles missing values, removes outliers, splits the data into training and testing sets, and saves the preprocessed data.
   - **Model Training**: This image contains a script that loads the preprocessed training data, trains a random forest classifier, and saves the trained model.
   - **Model Evaluation**: This image contains a script that loads the trained model and test data, evaluates the model, and saves the evaluation results.

2. We create an `EZBatchJob` for each stage of the pipeline:
   - Each job uses a different Docker image and command.
   - Each job has different S3 mounts for reading and writing data.
   - The jobs have different resource requirements based on their computational needs.

3. We create an `EZBatchWorkflow` with all the jobs and dependencies:
   - The workflow contains all three jobs.
   - The dependencies specify that the training job depends on the preprocessing job, and the evaluation job depends on the training job.

4. We submit the workflow to AWS Batch, which will execute the jobs in the correct order based on the dependencies.

## Benefits of Using ezbatch for Pipelines

Using ezbatch for multi-stage pipelines offers several benefits:

1. **Simplified Orchestration**: ezbatch handles the orchestration of jobs, ensuring they run in the correct order based on dependencies.
2. **Resource Optimization**: Each stage can have different resource requirements, allowing you to optimize resource usage.
3. **Isolation**: Each stage runs in its own container, providing isolation and reproducibility.
4. **Scalability**: AWS Batch automatically scales resources based on the workload, allowing you to process large datasets efficiently.
5. **Cost Efficiency**: You only pay for the resources you use, and you can use spot instances for cost savings.

## Next Steps

Now that you've created a multi-stage pipeline on AWS Batch, you can explore more advanced features:

- Add more stages to your pipeline
- Implement error handling and retry logic
- Use spot instances for cost savings
- Integrate with other AWS services like Amazon SageMaker for model deployment

You can also explore the [Advanced Usage](../user-guide/03-advanced-usage.md) guide to learn more about the advanced features of ezbatch.
