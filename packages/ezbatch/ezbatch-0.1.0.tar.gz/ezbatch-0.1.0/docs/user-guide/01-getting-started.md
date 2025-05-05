# Getting Started

## Installation

To install `ezbatch` from PyPI, run:

```bash
pip install ezbatch
```

## AWS credentials and Configuration

First, you need to set up your AWS credentials. There are many ways to do this, so we recommend following the
[official AWS documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html).

Once your credentials are setup, you need to make sure the you have the correct permissions to run AWS Batch jobs.
The following sections describe how to set up the necessary permissions.

## Setting up AWS Batch

It is recommended to have the following IAM policies attached to the user or role that will be running `ezbatch`:

```
AWSBatchFullAccess
AmazonEC2FullAccess
```

You can attach these policies to your user or role by following the instructions in the
[AWS documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html).

You may also want to set up several new roles:

2. **Service Role**: This role is used by AWS Batch to create and manage resources on your behalf. You can create this
    role by following the instructions in the
    [AWS documentation](https://docs.aws.amazon.com/batch/latest/userguide/service_IAM_role.html).

3. **Instance Role**: This role is used by the EC2 instances that run your jobs. You can create this role by following
    the instructions in the
    [AWS documentation](https://docs.aws.amazon.com/batch/latest/userguide/instance_IAM_role.html).

4. **Task Role**: This role is used by the ECS tasks that run your jobs. You can create this role by following the
    instructions in the
    [AWS documentation](https://docs.aws.amazon.com/batch/latest/userguide/execution-IAM-role.html).

## Setting up `ezbatch` profile

First, activate the AWS profile you intend to use. I typically use this
[script](https://gist.github.com/vanandrew/c1952546961a47b8f51c461daba980cb) to switch between profiles.
But you can also use:

```bash
eval "$(aws configure export-credentials --profile your-profile-name --format env)"
```

to export your aws credentials to the environment. 

Upon launching the `ezbatch` CLI for the first time, it will create a new toml configuration file in 
`~/.config/ezbatch.toml`.

For example, running:

```bash
ezbatch-cli -h
```

will create the following configuration file:

```toml
[Settings]
executionRoleArn = ""
maxvCpus = 256
serviceRole = ""
instanceRole = ""
securityGroupIds = []
sse = "aws:kms"
sseKmsKeyId = "mrk-xxx"
subnets = []
taskRoleArn = ""
```

You can then fill in the values for the `executionRoleArn`, `serviceRole`, `instanceRole`, `taskRoleArn`,
`securityGroupIds`, `subnets`, `sse`, and `sseKmsKeyId` fields:

1. `executionRoleArn`: The ARN of the IAM role that AWS Batch can assume to execute your job.
2. `serviceRole`: The ARN of the IAM role that AWS Batch can assume to create and manage resources on your behalf.
3. `instanceRole`: The ARN of the IAM role that the EC2 instances that run your jobs can assume.
4. `taskRoleArn`: The ARN of the IAM role that the ECS tasks that run your jobs can assume.
5. `securityGroupIds`: A list of security group IDs that the EC2 instances that run your jobs will be associated with.
6. `subnets`: A list of subnet IDs that the EC2 instances that run your jobs will be launched in.
7. `sse`: The server-side encryption algorithm to use for the job's output. The default is `aws:kms`. This can be
overwritten during job definition.
8. `sseKmsKeyId`: The ARN of the KMS key to use for server-side encryption.
This is required if `sse` is set to `aws:kms`. Note this the default and can be overwritten during job definition.

## Setting up Compute Environments and Queues

In order to use, AWS Batch, you need to set up a compute environment and corresponding job queue. `ezbatch` provides
a simple interface for setting up these resources (which you can then modify as needed).

To create a compute environment, run the following command:

```bash
# Create a compute environment
ezbatch-cli create-compute-environment create --name [name_of_compute_environment] --type [EC2/Fargate] --maxvCpus [num_cpus]
# Example
ezbatch-cli create-compute-environment create --name my-compute-environment --type EC2 --maxvCpus 256
```

this will create a new compute environment with the specified name, type, and maximum number of vCPUs.

You can check the status of all your compute environments by running:

```bash
# Check the status of all compute environments
ezbatch-cli compute-environment list
```

Now you can create a job queue, that will use the compute environment you just created:

```bash
# Create a job queue
ezbatch-cli job-queue create --name [name_of_job_queue] --compute-environment [name_of_compute_environment]
# Example
ezbatch-cli job-queue create --name my-job-queue --compute-environment my-compute-environment
```

Jobs will now be submittable to the job queue you just created.

You can check the status of all your job queues by running:

```bash
# Check the status all job queues
ezbatch-cli job-queue list
```
