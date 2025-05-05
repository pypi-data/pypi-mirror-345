# Command-Line Interface

ezbatch provides a command-line interface (CLI) for managing compute environments, job queues, and jobs. This section documents the available commands and their options.

```{toctree}
:maxdepth: 2

compute-environment
job-queue
job-definition
jobs
interactive
```

## Overview

The ezbatch CLI is installed as `ezbatch-cli` when you install the ezbatch package. You can run `ezbatch-cli -h` to see the available commands:

```bash
ezbatch-cli -h
```

## Main Commands

- **compute-environment**: Manage compute environments
- **job-queue**: Manage job queues
- **job-definition**: Manage job definitions
- **jobs**: Submit and list jobs
- **interactive**: Launch the interactive TUI

## Configuration

Upon first launch, the CLI will create a configuration file at `~/.config/ezbatch.toml`. You can edit this file to set default values for various parameters.

## Examples

Here are some common examples of using the ezbatch CLI:

### Creating a Compute Environment

```bash
ezbatch-cli compute-environment create --name my-compute-environment --type EC2 --max-vcpus 256
```

### Creating a Job Queue

```bash
ezbatch-cli job-queue create --name my-job-queue --compute-environment my-compute-environment
```

### Listing Jobs

```bash
ezbatch-cli jobs list --queue my-job-queue
```

### Launching Interactive Mode

```bash
ezbatch-cli interactive
```
