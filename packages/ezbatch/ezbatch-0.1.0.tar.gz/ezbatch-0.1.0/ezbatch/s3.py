import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from random import getrandbits
from typing import Literal, TypedDict, cast
from warnings import warn

from dataclasses_json import DataClassJsonMixin

from .client import S3_CLIENT
from .conf import CONFIG


def check_s3_uri_valid(s3_uri: str) -> bool:
    """Check if an S3 URI is valid.

    Parameters
    ----------
    s3_uri : str
        The S3 URI to check.

    Returns
    -------
    bool
        Whether the S3 URI is valid.
    """
    # check is valid s3 uri
    if not s3_uri.startswith("s3://"):
        raise ValueError("Invalid S3 URI")
    # check if object exists
    try:
        response = S3_CLIENT.list_objects_v2(
            Bucket=s3_uri.split("/")[2], Prefix="/".join(s3_uri.split("/")[3:]), MaxKeys=10
        )
        if "Contents" in response:
            return True
    except Exception:
        # warn that path does not exists
        warn(f"s3 uri does not currently exist: {s3_uri}")
    # return True for now
    return True


def check_bucket_writable(
    bucket: str,
    sse: Literal["AES256", "aws:kms", "aws:kms:dsse"] = CONFIG.Settings.sse,
    sse_kms_key_id: str = CONFIG.Settings.sseKmsKeyId,
) -> bool:
    """Check if a bucket is writable.

    Parameters
    ----------
    bucket : str
        The bucket to check.
    sse : Literal["AES256", "aws:kms", "aws:kms:dsse"]
        The server-side encryption to use.
    sse_kms_key_id : str
        The KMS key ID to use.

    Returns
    -------
    bool
        Whether the bucket is writable.
    """
    random_key = str(getrandbits(512))
    try:
        S3_CLIENT.put_object(
            Bucket=bucket, Key=f"test/{random_key}", Body=b"test", ServerSideEncryption=sse, SSEKMSKeyId=sse_kms_key_id
        )
        result = True
    except Exception as e:
        print(e)
        result = False
    finally:
        response = S3_CLIENT.list_object_versions(Bucket=bucket, Prefix=f"test/{random_key}")
        if (
            "Versions" in response
            and "VersionId" in response["Versions"][0]
            and response["Versions"][0]["VersionId"] != "null"
        ):
            S3_CLIENT.delete_object(
                Bucket=bucket, Key=f"test/{random_key}", VersionId=response["Versions"][0]["VersionId"]
            )
        else:
            S3_CLIENT.delete_object(Bucket=bucket, Key=f"test/{random_key}")
    return result


@dataclass
class S3Mount(DataClassJsonMixin):
    """An S3 mount for a job."""

    source: str
    destination: str
    recursive: bool | None = None
    sse: str | None = None
    sse_kms_key_id: str | None = None
    options: str = "--quiet"

    def __post_init__(self):
        """Post-initialization."""
        if self.recursive is not None:
            self.options += f" --recursive"
        if self.sse is not None:
            self.options += f" --sse {self.sse}"
        if self.sse_kms_key_id is not None:
            self.options += f" --sse-kms-key-id {self.sse_kms_key_id}"

    def validate(self):
        """Validate the S3 mount."""
        # check if source is valid, if s3_uri
        if self.source.startswith("s3://") and not check_s3_uri_valid(self.source):
            raise ValueError(f"Invalid Source S3 URI: {self.source}")
        # check if destination is writable, if s3_uri
        # get sse and sse_kms_key_id from options
        sse = cast(
            Literal["AES256", "aws:kms", "aws:kms:dsse"],
            self.options.split("--sse ")[1].split(" ")[0] if "--sse" in self.options else CONFIG.Settings.sse,
        )
        sse_kms_key_id = (
            self.options.split("--sse-kms-key-id ")[1].split(" ")[0] if "--sse-kms-key-id" in self.options else ""
        )
        if self.destination.startswith("s3://") and not check_bucket_writable(
            self.destination.split("/")[2], sse=sse, sse_kms_key_id=sse_kms_key_id
        ):
            raise ValueError(f"Destination S3 URI: {self.destination} is not writable")


@dataclass
class S3Mounts(DataClassJsonMixin):
    """S3 mounts for a job."""

    read: Sequence[S3Mount | dict] = field(default_factory=list)
    write: Sequence[S3Mount | dict] = field(default_factory=list)

    def __post_init__(self):
        """Post-initialization."""
        self.read = [S3Mount(**mount) if isinstance(mount, dict) else mount for mount in self.read]
        self.write = [S3Mount(**mount) if isinstance(mount, dict) else mount for mount in self.write]

    def validate(self):
        """Validate the S3 mounts."""
        for mount in self.read:
            mount.validate()  # type: ignore
        for mount in self.write:
            mount.validate()  # type: ignore

    def to_json(self, *args, **kwargs):
        """Convert to JSON."""
        json_string = super().to_json(*args, **kwargs)
        data_dict = json.loads(json_string)
        # loop through entries and delete anything except source, destination, and options
        nonnull_read = [
            {key: value for key, value in entry.items() if key == "source" or key == "destination" or key == "options"}
            for entry in data_dict["read"]
        ]
        nonnull_write = [
            {key: value for key, value in entry.items() if key == "source" or key == "destination" or key == "options"}
            for entry in data_dict["write"]
        ]
        data_dict["read"] = nonnull_read
        data_dict["write"] = nonnull_write
        return json.dumps(data_dict)
