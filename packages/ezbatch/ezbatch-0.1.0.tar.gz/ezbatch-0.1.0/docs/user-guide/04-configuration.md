# Configuration

ezbatch uses a configuration file to store default values for various parameters. This section explains how to configure ezbatch.

## Configuration File

The configuration file is located at `~/.config/ezbatch.toml` by default. You can override this location by setting the `EZBATCH_CONFIG_PATH` environment variable.

The configuration file is created automatically when you first run the ezbatch CLI. You can edit this file to set default values for various parameters.

## Configuration Format

The configuration file uses the TOML format. Here's an example configuration file:

```toml
[Settings]
executionRoleArn = "arn:aws:iam::123456789012:role/ecsTaskExecutionRole"
maxvCpus = 256
serviceRole = "arn:aws:iam::123456789012:role/aws-service-role/batch.amazonaws.com/AWSServiceRoleForBatch"
instanceRole = "arn:aws:iam::123456789012:role/ecsInstanceRole"
securityGroupIds = ["sg-0123456789abcdef0"]
sse = "aws:kms"
sseKmsKeyId = "mrk-0123456789abcdef0"
subnets = ["subnet-0123456789abcdef0", "subnet-0123456789abcdef1"]
taskRoleArn = "arn:aws:iam::123456789012:role/ecsTaskExecutionRole"
```

## Configuration Options

### executionRoleArn

The ARN of the IAM role that AWS Batch can assume to execute your job. This role is used by the Amazon ECS container agent to make AWS API calls on your behalf.

Example:
```toml
executionRoleArn = "arn:aws:iam::123456789012:role/ecsTaskExecutionRole"
```

### maxvCpus

The maximum number of vCPUs for compute environments. This is the maximum number of vCPUs that can be allocated to jobs running in the compute environment.

Example:
```toml
maxvCpus = 256
```

### serviceRole

The ARN of the IAM role that AWS Batch can assume to create and manage resources on your behalf. This role is used by AWS Batch to create and manage AWS resources.

Example:
```toml
serviceRole = "arn:aws:iam::123456789012:role/aws-service-role/batch.amazonaws.com/AWSServiceRoleForBatch"
```

### instanceRole

The ARN of the IAM role that the EC2 instances that run your jobs can assume. This role is used by the EC2 instances to make AWS API calls on your behalf.

Example:
```toml
instanceRole = "arn:aws:iam::123456789012:role/ecsInstanceRole"
```

### securityGroupIds

A list of security group IDs that the EC2 instances that run your jobs will be associated with. These security groups control the network access to and from the EC2 instances.

Example:
```toml
securityGroupIds = ["sg-0123456789abcdef0"]
```

### sse

The server-side encryption algorithm to use for the job's output. The default is `aws:kms`. This can be overwritten during job definition.

Example:
```toml
sse = "aws:kms"
```

### sseKmsKeyId

The ARN of the KMS key to use for server-side encryption. This is required if `sse` is set to `aws:kms`. Note this the default and can be overwritten during job definition.

Example:
```toml
sseKmsKeyId = "mrk-0123456789abcdef0"
```

### subnets

A list of subnet IDs that the EC2 instances that run your jobs will be launched in. These subnets determine the VPC and availability zones where your jobs will run.

Example:
```toml
subnets = ["subnet-0123456789abcdef0", "subnet-0123456789abcdef1"]
```

### taskRoleArn

The ARN of the IAM role that the ECS tasks that run your jobs can assume. This role is used by the ECS tasks to make AWS API calls on your behalf.

Example:
```toml
taskRoleArn = "arn:aws:iam::123456789012:role/ecsTaskExecutionRole"
```

## Environment Variables

You can override the configuration file location by setting the `EZBATCH_CONFIG_PATH` environment variable:

```bash
export EZBATCH_CONFIG_PATH=/path/to/config.toml
```

## AWS Credentials

ezbatch uses the AWS SDK for Python (Boto3) to interact with AWS services. Boto3 uses the standard AWS credential resolution chain to find AWS credentials. This means you can use any of the standard methods to provide AWS credentials:

- Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`)
- Shared credential file (`~/.aws/credentials`)
- AWS config file (`~/.aws/config`)
- Assume Role provider
- Instance metadata service on an Amazon EC2 instance that has an IAM role configured

For more information, see the [AWS SDK for Python (Boto3) documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html).

## AWS Region

ezbatch uses the AWS SDK for Python (Boto3) to interact with AWS services. Boto3 uses the standard AWS region resolution chain to find the AWS region. This means you can use any of the standard methods to provide the AWS region:

- Environment variables (`AWS_REGION`, `AWS_DEFAULT_REGION`)
- Shared config file (`~/.aws/config`)
- Instance metadata service on an Amazon EC2 instance

For more information, see the [AWS SDK for Python (Boto3) documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#environment-variables).

## AWS Profiles

If you have multiple AWS profiles, you can use the `AWS_PROFILE` environment variable to specify which profile to use:

```bash
export AWS_PROFILE=my-profile
```

Alternatively, you can use the `aws configure export-credentials` command to export your AWS credentials to environment variables:

```bash
eval "$(aws configure export-credentials --profile my-profile --format env)"
```

This will set the `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN` environment variables based on the specified profile.
