from boto3 import client

BATCH_CLIENT = client("batch")
STS_CLIENT = client("sts")
IAM_CLIENT = client("iam")
LOGS_CLIENT = client("logs")
S3_CLIENT = client("s3")
