# ezbatch

*For the computational scientist who doesn't want to spend all day reading AWS documentation...*

`ezbatch` is a Python package that provides a simple interface for running batch jobs on AWS. It is designed to
quickly take your Docker container code and run it on AWS Batch.

## Overview

ezbatch simplifies the process of:

- Setting up AWS Batch compute environments and job queues
- Defining and submitting batch jobs
- Creating workflows with job dependencies
- Managing S3 data transfers for your jobs
- Monitoring job status and logs

Whether you're running simple one-off jobs or complex workflows with dependencies, ezbatch provides a clean, 
Pythonic interface that abstracts away the complexity of AWS Batch.

```{toctree}
:maxdepth: 2
:caption: Contents

user-guide/index
api-reference/index
cli/index
tutorials/index
architecture
```
