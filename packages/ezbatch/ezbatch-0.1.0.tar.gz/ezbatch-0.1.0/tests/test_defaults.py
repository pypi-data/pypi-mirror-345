from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ezbatch.defaults import (
    CURRENT_AWS_ACCOUNT,
    DEFAULT_CONFIG_PATH,
    DEFAULT_MAX_VCPUS,
    DEFAULT_S3_BUCKET,
    DEFAULT_SSE,
    DEFAULT_SSE_KMS_KEY_ID,
)


class TestDefaults:
    def test_current_aws_account(self):
        """Test that CURRENT_AWS_ACCOUNT is set."""
        # Verify that CURRENT_AWS_ACCOUNT exists and is a string
        assert CURRENT_AWS_ACCOUNT is not None
        assert isinstance(CURRENT_AWS_ACCOUNT, str)

    def test_default_config_path(self):
        """Test that DEFAULT_CONFIG_PATH is set to the expected location."""
        expected_path = Path.home() / ".config" / "ezbatch.toml"
        assert DEFAULT_CONFIG_PATH == expected_path

    def test_default_max_vcpus(self):
        """Test that DEFAULT_MAX_VCPUS is set to the expected value."""
        assert DEFAULT_MAX_VCPUS == 256

    @patch("ezbatch.defaults.CURRENT_AWS_ACCOUNT", "123456789012")
    def test_default_s3_bucket(self):
        """Test that DEFAULT_S3_BUCKET is set to the expected value."""
        # Import the module to use the patched CURRENT_AWS_ACCOUNT
        from importlib import reload

        import ezbatch.defaults

        reload(ezbatch.defaults)

        # Verify
        assert ezbatch.defaults.DEFAULT_S3_BUCKET == "ezbatch-123456789012-bucket"

    def test_default_sse(self):
        """Test that DEFAULT_SSE is set to the expected value."""
        assert DEFAULT_SSE == "aws:kms"

    def test_default_sse_kms_key_id(self):
        """Test that DEFAULT_SSE_KMS_KEY_ID is set to the expected value."""
        assert DEFAULT_SSE_KMS_KEY_ID == ""
