import json
from unittest.mock import MagicMock, patch

import pytest

from ezbatch.s3 import S3Mount, S3Mounts, check_bucket_writable, check_s3_uri_valid


@pytest.fixture
def mock_s3_client():
    with patch("ezbatch.s3.S3_CLIENT") as mock:
        yield mock


@pytest.fixture
def mock_config():
    with patch("ezbatch.s3.CONFIG") as mock:
        mock.Settings.sse = "AES256"
        mock.Settings.sseKmsKeyId = "test-key-id"
        yield mock


class TestCheckS3UriValid:
    def test_check_s3_uri_valid_exists(self, mock_s3_client):
        """Test checking if an S3 URI is valid when it exists."""
        # Setup mock responses
        mock_s3_client.list_objects_v2.return_value = {"Contents": [{"Key": "test/file.txt"}]}

        # Test
        result = check_s3_uri_valid("s3://test-bucket/test/file.txt")

        # Verify
        assert result is True
        mock_s3_client.list_objects_v2.assert_called_once_with(Bucket="test-bucket", Prefix="test/file.txt", MaxKeys=10)

    def test_check_s3_uri_valid_not_exists(self, mock_s3_client):
        """Test checking if an S3 URI is valid when it doesn't exist."""
        # Setup mock responses
        mock_s3_client.list_objects_v2.return_value = {}  # No Contents key

        # Test
        result = check_s3_uri_valid("s3://test-bucket/test/file.txt")

        # Verify
        assert result is True  # Still returns True even if it doesn't exist
        mock_s3_client.list_objects_v2.assert_called_once_with(Bucket="test-bucket", Prefix="test/file.txt", MaxKeys=10)

    def test_check_s3_uri_valid_exception(self, mock_s3_client):
        """Test checking if an S3 URI is valid when an exception occurs."""
        # Setup mock responses
        mock_s3_client.list_objects_v2.side_effect = Exception("Test exception")

        # Test
        with pytest.warns(UserWarning, match="s3 uri does not currently exist"):
            result = check_s3_uri_valid("s3://test-bucket/test/file.txt")

        # Verify
        assert result is True  # Still returns True even if an exception occurs
        mock_s3_client.list_objects_v2.assert_called_once_with(Bucket="test-bucket", Prefix="test/file.txt", MaxKeys=10)

    def test_check_s3_uri_valid_invalid_uri(self):
        """Test checking if an S3 URI is valid with an invalid URI."""
        # Test
        with pytest.raises(ValueError, match="Invalid S3 URI"):
            check_s3_uri_valid("invalid-uri")


class TestCheckBucketWritable:
    def test_check_bucket_writable_success(self, mock_s3_client, mock_config):
        """Test checking if a bucket is writable when it is."""
        # Setup mock responses
        mock_s3_client.put_object.return_value = {}
        mock_s3_client.list_object_versions.return_value = {"Versions": [{"VersionId": "test-version-id"}]}

        # Test
        result = check_bucket_writable("test-bucket")

        # Verify
        assert result is True
        mock_s3_client.put_object.assert_called_once()
        mock_s3_client.list_object_versions.assert_called_once()
        mock_s3_client.delete_object.assert_called_once()

    def test_check_bucket_writable_failure(self, mock_s3_client, mock_config):
        """Test checking if a bucket is writable when it isn't."""
        # Setup mock responses
        mock_s3_client.put_object.side_effect = Exception("Test exception")

        # Test
        result = check_bucket_writable("test-bucket")

        # Verify
        assert result is False
        mock_s3_client.put_object.assert_called_once()
        mock_s3_client.list_object_versions.assert_called_once()
        # delete_object is called in a finally block, so it's still called even if put_object fails
        mock_s3_client.delete_object.assert_called_once()

    def test_check_bucket_writable_no_version_id(self, mock_s3_client, mock_config):
        """Test checking if a bucket is writable when there's no version ID."""
        # Setup mock responses
        mock_s3_client.put_object.return_value = {}
        mock_s3_client.list_object_versions.return_value = {"Versions": [{"Key": "test/file.txt"}]}  # No VersionId

        # Test
        result = check_bucket_writable("test-bucket")

        # Verify
        assert result is True
        mock_s3_client.put_object.assert_called_once()
        mock_s3_client.list_object_versions.assert_called_once()
        mock_s3_client.delete_object.assert_called_once()

    def test_check_bucket_writable_null_version_id(self, mock_s3_client, mock_config):
        """Test checking if a bucket is writable when the version ID is null."""
        # Setup mock responses
        mock_s3_client.put_object.return_value = {}
        mock_s3_client.list_object_versions.return_value = {"Versions": [{"VersionId": "null"}]}

        # Test
        result = check_bucket_writable("test-bucket")

        # Verify
        assert result is True
        mock_s3_client.put_object.assert_called_once()
        mock_s3_client.list_object_versions.assert_called_once()
        mock_s3_client.delete_object.assert_called_once()

    def test_check_bucket_writable_no_versions(self, mock_s3_client, mock_config):
        """Test checking if a bucket is writable when there are no versions."""
        # Setup mock responses
        mock_s3_client.put_object.return_value = {}
        mock_s3_client.list_object_versions.return_value = {}  # No Versions key

        # Test
        result = check_bucket_writable("test-bucket")

        # Verify
        assert result is True
        mock_s3_client.put_object.assert_called_once()
        mock_s3_client.list_object_versions.assert_called_once()
        mock_s3_client.delete_object.assert_called_once()


class TestS3Mount:
    def test_s3_mount_init(self):
        """Test initializing an S3Mount."""
        # Test
        mount = S3Mount(
            source="s3://source-bucket/path",
            destination="/destination/path",
            recursive=True,
            sse="AES256",
            sse_kms_key_id="test-key-id",
        )

        # Verify
        assert mount.source == "s3://source-bucket/path"
        assert mount.destination == "/destination/path"
        assert mount.recursive is True
        assert mount.sse == "AES256"
        assert mount.sse_kms_key_id == "test-key-id"
        assert "--quiet" in mount.options
        assert "--recursive" in mount.options
        assert "--sse AES256" in mount.options
        assert "--sse-kms-key-id test-key-id" in mount.options

    def test_s3_mount_init_defaults(self):
        """Test initializing an S3Mount with default values."""
        # Test
        mount = S3Mount(
            source="s3://source-bucket/path",
            destination="/destination/path",
        )

        # Verify
        assert mount.source == "s3://source-bucket/path"
        assert mount.destination == "/destination/path"
        assert mount.recursive is None
        assert mount.sse is None
        assert mount.sse_kms_key_id is None
        assert mount.options == "--quiet"

    @patch("ezbatch.s3.check_s3_uri_valid")
    @patch("ezbatch.s3.check_bucket_writable")
    def test_s3_mount_validate_success(self, mock_check_bucket_writable, mock_check_s3_uri_valid):
        """Test validating an S3Mount successfully."""
        # Setup mock responses
        mock_check_s3_uri_valid.return_value = True
        mock_check_bucket_writable.return_value = True

        # Test
        mount = S3Mount(
            source="s3://source-bucket/path",
            destination="s3://destination-bucket/path",
            sse="AES256",
            sse_kms_key_id="test-key-id",
        )
        mount.validate()

        # Verify
        mock_check_s3_uri_valid.assert_called_once_with("s3://source-bucket/path")
        mock_check_bucket_writable.assert_called_once_with(
            "destination-bucket", sse="AES256", sse_kms_key_id="test-key-id"
        )

    @patch("ezbatch.s3.check_s3_uri_valid")
    def test_s3_mount_validate_invalid_source(self, mock_check_s3_uri_valid):
        """Test validating an S3Mount with an invalid source."""
        # Setup mock responses
        mock_check_s3_uri_valid.return_value = False

        # Test
        mount = S3Mount(
            source="s3://source-bucket/path",
            destination="/destination/path",
        )
        with pytest.raises(ValueError, match="Invalid Source S3 URI"):
            mount.validate()

        # Verify
        mock_check_s3_uri_valid.assert_called_once_with("s3://source-bucket/path")

    @patch("ezbatch.s3.check_s3_uri_valid")
    @patch("ezbatch.s3.check_bucket_writable")
    def test_s3_mount_validate_unwritable_destination(self, mock_check_bucket_writable, mock_check_s3_uri_valid):
        """Test validating an S3Mount with an unwritable destination."""
        # Setup mock responses
        mock_check_s3_uri_valid.return_value = True
        mock_check_bucket_writable.return_value = False

        # Test
        mount = S3Mount(
            source="s3://source-bucket/path",
            destination="s3://destination-bucket/path",
        )
        with pytest.raises(ValueError, match="Destination S3 URI.*is not writable"):
            mount.validate()

        # Verify
        mock_check_s3_uri_valid.assert_called_once_with("s3://source-bucket/path")
        mock_check_bucket_writable.assert_called_once()


class TestS3Mounts:
    def test_s3_mounts_init(self):
        """Test initializing S3Mounts."""
        # Test
        mounts = S3Mounts(
            read=[
                S3Mount(source="s3://read-bucket/path", destination="/read/path"),
                {"source": "s3://read-bucket2/path", "destination": "/read/path2"},
            ],
            write=[
                S3Mount(source="/write/path", destination="s3://write-bucket/path"),
                {"source": "/write/path2", "destination": "s3://write-bucket2/path"},
            ],
        )

        # Verify
        assert len(mounts.read) == 2
        assert isinstance(mounts.read[0], S3Mount)
        assert isinstance(mounts.read[1], S3Mount)
        assert mounts.read[0].source == "s3://read-bucket/path"
        assert mounts.read[1].source == "s3://read-bucket2/path"

        assert len(mounts.write) == 2
        assert isinstance(mounts.write[0], S3Mount)
        assert isinstance(mounts.write[1], S3Mount)
        assert mounts.write[0].source == "/write/path"
        assert mounts.write[1].source == "/write/path2"

    def test_s3_mounts_init_defaults(self):
        """Test initializing S3Mounts with default values."""
        # Test
        mounts = S3Mounts()

        # Verify
        assert len(mounts.read) == 0
        assert len(mounts.write) == 0

    @patch("ezbatch.s3.S3Mount.validate")
    def test_s3_mounts_validate(self, mock_validate):
        """Test validating S3Mounts."""
        # Test
        mounts = S3Mounts(
            read=[
                S3Mount(source="s3://read-bucket/path", destination="/read/path"),
            ],
            write=[
                S3Mount(source="/write/path", destination="s3://write-bucket/path"),
            ],
        )
        mounts.validate()

        # Verify
        assert mock_validate.call_count == 2

    def test_s3_mounts_to_json(self):
        """Test converting S3Mounts to JSON."""
        # Test
        mounts = S3Mounts(
            read=[
                S3Mount(
                    source="s3://read-bucket/path",
                    destination="/read/path",
                    recursive=True,
                    sse="AES256",
                    sse_kms_key_id="test-key-id",
                ),
            ],
            write=[
                S3Mount(
                    source="/write/path",
                    destination="s3://write-bucket/path",
                    recursive=True,
                    sse="AES256",
                    sse_kms_key_id="test-key-id",
                ),
            ],
        )
        json_str = mounts.to_json()
        json_data = json.loads(json_str)

        # Verify
        assert "read" in json_data
        assert "write" in json_data
        assert len(json_data["read"]) == 1
        assert len(json_data["write"]) == 1

        # Check that only source, destination, and options are included
        read_mount = json_data["read"][0]
        assert "source" in read_mount
        assert "destination" in read_mount
        assert "options" in read_mount
        assert "recursive" not in read_mount
        assert "sse" not in read_mount
        assert "sse_kms_key_id" not in read_mount

        write_mount = json_data["write"][0]
        assert "source" in write_mount
        assert "destination" in write_mount
        assert "options" in write_mount
        assert "recursive" not in write_mount
        assert "sse" not in write_mount
        assert "sse_kms_key_id" not in write_mount
