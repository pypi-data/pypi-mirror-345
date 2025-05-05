# Troubleshooting

This section provides solutions to common issues you might encounter when using ezbatch.

## AWS Permissions Issues

### Insufficient Permissions

**Symptom**: You receive an error message like `An error occurred (AccessDeniedException) when calling the CreateComputeEnvironment operation: User: arn:aws:iam::123456789012:user/username is not authorized to perform: batch:CreateComputeEnvironment`.

**Solution**: Make sure your AWS user or role has the necessary permissions. For ezbatch, you typically need the following policies:

- `AWSBatchFullAccess`
- `AmazonEC2FullAccess`

You can attach these policies to your user or role by following the instructions in the [AWS documentation](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_manage-attach-detach.html).

### Missing IAM Roles

**Symptom**: You receive an error message like `Service role arn:aws:iam::123456789012:role/aws-service-role/batch.amazonaws.com/AWSServiceRoleForBatch does not exist.`

**Solution**: Create the required IAM roles. ezbatch requires several IAM roles:

1. **Service Role**: Used by AWS Batch to create and manage resources on your behalf.
2. **Instance Role**: Used by the EC2 instances that run your jobs.
3. **Task Role**: Used by the ECS tasks that run your jobs.
4. **Execution Role**: Used by AWS Batch to execute your jobs.

You can create these roles by following the instructions in the [AWS documentation](https://docs.aws.amazon.com/batch/latest/userguide/service_IAM_role.html).

## Job Failures

### Job Stuck in RUNNABLE State

**Symptom**: Your job is stuck in the RUNNABLE state and doesn't start running.

**Solution**: This usually means that AWS Batch can't find suitable resources to run your job. Check the following:

1. Make sure your compute environment has enough resources (vCPUs, memory) to run your job.
2. Check if your compute environment is in the ENABLED state.
3. Check if your job queue is in the ENABLED state.
4. Check if your job's resource requirements (vCPUs, memory) are compatible with the compute environment.

You can check the status of your compute environments and job queues using the ezbatch CLI:

```bash
ezbatch-cli compute-environment list
ezbatch-cli job-queue list
```

### Job Fails with Error

**Symptom**: Your job fails with an error message.

**Solution**: Check the job logs to see what went wrong. You can view the logs using the AWS Management Console or the AWS CLI:

```bash
aws logs get-log-events --log-group-name /aws/batch/job --log-stream-name job-name/default/job-id
```

Common issues include:

1. **Docker Image Not Found**: Make sure the Docker image exists and is accessible.
2. **Command Fails**: Check if the command you're running is valid and has the correct syntax.
3. **Resource Limits**: Make sure your job has enough resources (vCPUs, memory) to run.

### Job Fails with No Error

**Symptom**: Your job fails without any error message.

**Solution**: This could be due to various reasons. Check the following:

1. Make sure your Docker image is compatible with AWS Batch.
2. Check if your command is valid and has the correct syntax.
3. Make sure your job has enough resources (vCPUs, memory) to run.
4. Check if your job is trying to access resources that are not available.

## S3 Mount Issues

### S3 Path Not Found

**Symptom**: Your job fails with an error message like `The specified key does not exist.`

**Solution**: Make sure the S3 path exists and is accessible. You can check if the S3 path exists using the AWS CLI:

```bash
aws s3 ls s3://bucket-name/path/
```

### S3 Permission Denied

**Symptom**: Your job fails with an error message like `Access Denied`.

**Solution**: Make sure your task role has the necessary permissions to access the S3 bucket. You need to attach a policy that allows the following actions:

- `s3:GetObject` for reading from S3
- `s3:PutObject` for writing to S3
- `s3:ListBucket` for listing objects in the bucket

Here's an example policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::bucket-name",
                "arn:aws:s3:::bucket-name/*"
            ]
        }
    ]
}
```

### S3 KMS Key Issues

**Symptom**: Your job fails with an error message like `KMS key not found` or `Access Denied to KMS key`.

**Solution**: Make sure your task role has the necessary permissions to use the KMS key. You need to attach a policy that allows the following actions:

- `kms:Decrypt` for reading from S3
- `kms:GenerateDataKey` for writing to S3

Here's an example policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "kms:Decrypt",
                "kms:GenerateDataKey"
            ],
            "Resource": "arn:aws:kms:region:account-id:key/key-id"
        }
    ]
}
```

## Configuration Issues

### Configuration File Not Found

**Symptom**: You receive an error message like `Configuration file not found at: ~/.config/ezbatch.toml`.

**Solution**: Create the configuration file by running any ezbatch CLI command, such as:

```bash
ezbatch-cli -h
```

This will create a new configuration file with default values.

### Invalid Configuration

**Symptom**: You receive an error message like `Invalid configuration: ...`.

**Solution**: Check your configuration file and make sure it has the correct format and values. See the [Configuration](04-configuration.md) section for details.

## Network Issues

### VPC Connectivity Issues

**Symptom**: Your job can't connect to the internet or other AWS services.

**Solution**: Make sure your VPC is configured correctly. You need to:

1. Make sure your subnets have a route to the internet (via an Internet Gateway or NAT Gateway).
2. Make sure your security groups allow the necessary outbound traffic.
3. If you're using a private subnet, make sure you have a NAT Gateway or VPC Endpoints for the AWS services you need to access.

### Security Group Issues

**Symptom**: Your job can't connect to specific services or ports.

**Solution**: Make sure your security groups allow the necessary traffic. You need to:

1. Make sure your security groups allow outbound traffic to the services you need to access.
2. If you're connecting to other AWS resources, make sure their security groups allow inbound traffic from your job's security group.

## Resource Limits

### Service Quotas

**Symptom**: You receive an error message like `Service Quota Exceeded`.

**Solution**: Check your AWS service quotas and request an increase if necessary. You can view your service quotas in the AWS Management Console or using the AWS CLI:

```bash
aws service-quotas list-service-quotas --service-code batch
```

Common quotas that might need to be increased include:

- Maximum number of compute environments
- Maximum number of job queues
- Maximum number of job definitions
- Maximum number of jobs in a job queue

### Resource Constraints

**Symptom**: Your jobs are queued but not running, or you can't create new compute environments.

**Solution**: Check if you have enough resources in your AWS account. You might need to:

1. Request an increase in your EC2 instance limits.
2. Use a different instance type that has more availability.
3. Spread your workload across multiple regions.

## CLI Issues

### Command Not Found

**Symptom**: You receive an error message like `command not found: ezbatch-cli`.

**Solution**: Make sure ezbatch is installed correctly. You can install it using pip:

```bash
pip install ezbatch
```

Make sure the installation directory is in your PATH.

### Invalid Command

**Symptom**: You receive an error message like `invalid choice: ...`.

**Solution**: Check the command syntax and make sure you're using the correct command and options. You can see the available commands and options by running:

```bash
ezbatch-cli -h
```

## Interactive Mode Issues

### TUI Not Displaying Correctly

**Symptom**: The interactive TUI is not displaying correctly or is showing errors.

**Solution**: Make sure you have a compatible terminal emulator and that your terminal supports the necessary features. You can try:

1. Using a different terminal emulator.
2. Updating your terminal emulator to the latest version.
3. Setting the `TERM` environment variable to a compatible value, such as `xterm-256color`.

### Job Status Not Updating

**Symptom**: The job status in the interactive TUI is not updating.

**Solution**: This could be due to various reasons. Try:

1. Refreshing the display by pressing a key.
2. Restarting the interactive mode.
3. Checking if your AWS credentials are still valid.

## Getting Help

If you're still having issues, you can:

1. Check the [AWS Batch documentation](https://docs.aws.amazon.com/batch/latest/userguide/what-is-batch.html) for more information.
2. Check the [ezbatch GitHub repository](https://github.com/vanandrew/ezbatch) for known issues and solutions.
3. Open an issue on the [ezbatch GitHub repository](https://github.com/vanandrew/ezbatch/issues) if you think you've found a bug or have a feature request.
