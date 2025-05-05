# Architecture

This page provides an overview of the ezbatch architecture and how the different components interact with each other and with AWS services.

## High-Level Architecture

ezbatch is designed to provide a simple, Pythonic interface to AWS Batch, abstracting away the complexity of the AWS Batch API. The library is structured around several key components:

```
                                 ┌───────────────┐
                                 │   EZBatch     │
                                 │   Workflow    │
                                 └───────┬───────┘
                                         │
                                         │ contains
                                         ▼
┌───────────────┐  depends on  ┌───────────────┐  uses   ┌───────────────┐
│   EZBatch     │◄────────────►│   EZBatch     │────────►│     S3        │
│     Job       │              │     Job       │         │    Mounts     │
└───────┬───────┘              └───────┬───────┘         └───────────────┘
        │                              │
        │                              │
        │                              │
        │                              │
        ▼                              ▼
┌───────────────┐              ┌───────────────┐
│  AWS Batch    │              │  AWS Batch    │
│Job Definition │              │Job Definition │
└───────┬───────┘              └───────┬───────┘
        │                              │
        │                              │
        │                              │
        │                              │
        ▼                              ▼
┌───────────────┐              ┌───────────────┐
│  AWS Batch    │              │  AWS Batch    │
│     Job       │              │     Job       │
└───────────────┘              └───────────────┘
```

## Core Components

### EZBatchWorkflow

The `EZBatchWorkflow` class is the main entry point for creating and submitting workflows. A workflow consists of one or more jobs with optional dependencies between them. The workflow handles the registration of job definitions, submission of jobs, and management of job dependencies.

### EZBatchJob

The `EZBatchJob` class represents a single job in a workflow. It encapsulates the Docker image, command, environment variables, resource requirements, and S3 mounts for the job. When a workflow is submitted, each job is converted to an AWS Batch job definition and submitted to the specified job queue.

### S3Mounts

The `S3Mounts` class provides a way to specify S3 paths to read from or write to during job execution. This is particularly useful for data-intensive workflows where input data needs to be downloaded from S3 and output data needs to be uploaded to S3.

## AWS Integration

ezbatch integrates with several AWS services:

### AWS Batch

ezbatch uses AWS Batch to run containerized jobs. It provides abstractions for:

- **Compute Environments**: Where jobs run (EC2 or Fargate)
- **Job Queues**: Where jobs are submitted
- **Job Definitions**: Templates for jobs
- **Jobs**: The actual units of work

### Amazon S3

ezbatch integrates with Amazon S3 for data storage and transfer. The S3Mounts class provides a way to specify S3 paths to read from or write to during job execution.

### AWS IAM

ezbatch requires several IAM roles to function properly:

- **Service Role**: Used by AWS Batch to create and manage resources
- **Instance Role**: Used by EC2 instances that run jobs
- **Task Role**: Used by ECS tasks that run jobs
- **Execution Role**: Used by AWS Batch to execute jobs

## Preloader Functionality

ezbatch includes a preloader script that can be used to download data from S3 before job execution and upload data to S3 after job execution. This is particularly useful for jobs that need to process large amounts of data.

## Command-Line Interface

ezbatch provides a command-line interface (CLI) for managing compute environments, job queues, and jobs. The CLI is implemented using the Python `argparse` module and provides commands for creating, listing, toggling, and deleting compute environments and job queues, as well as submitting and listing jobs.

## Interactive Mode

ezbatch includes an interactive mode that provides a terminal user interface (TUI) for monitoring jobs. The TUI is implemented using the Textual library and provides a way to view job status and logs.
