from pathlib import Path

from ezbatch.client import STS_CLIENT

CURRENT_AWS_ACCOUNT = STS_CLIENT.get_caller_identity()["Account"]
DEFAULT_CONFIG_PATH = Path.home() / ".config" / "ezbatch.toml"
DEFAULT_MAX_VCPUS = 256
DEFAULT_S3_BUCKET = f"ezbatch-{CURRENT_AWS_ACCOUNT}-bucket"
DEFAULT_SSE = "aws:kms"
DEFAULT_SSE_KMS_KEY_ID = ""
