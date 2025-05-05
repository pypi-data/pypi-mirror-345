# API Reference

This section provides detailed documentation for the ezbatch API. Each module and class is documented with its parameters, methods, and examples.

```{toctree}
:maxdepth: 2

workflow
job
s3
compute_environment
job_queue
job_definition
client
conf
logs
```

## Module Overview

- **workflow**: Contains the `EZBatchWorkflow` and `EZBatchJob` classes for creating and submitting workflows
- **job**: Functions for submitting and listing jobs
- **s3**: Contains the `S3Mounts` and `S3Mount` classes for specifying S3 paths to read from or write to
- **compute_environment**: Functions for creating, listing, toggling, and deleting compute environments
- **job_queue**: Functions for creating, listing, toggling, and deleting job queues
- **job_definition**: Functions for creating and deregistering job definitions
- **client**: AWS clients used by ezbatch
- **conf**: Configuration management
- **logs**: Functions for retrieving job logs
