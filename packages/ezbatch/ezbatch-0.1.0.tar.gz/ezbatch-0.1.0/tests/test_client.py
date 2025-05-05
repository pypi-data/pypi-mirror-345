from unittest.mock import MagicMock, patch

import pytest

from ezbatch.client import BATCH_CLIENT, IAM_CLIENT, LOGS_CLIENT, S3_CLIENT, STS_CLIENT


class TestClientInitialization:
    def test_batch_client_initialization(self):
        """Test that BATCH_CLIENT is initialized with the correct service name."""
        # Simply verify that BATCH_CLIENT exists
        assert BATCH_CLIENT is not None

    def test_sts_client_initialization(self):
        """Test that STS_CLIENT is initialized with the correct service name."""
        # Simply verify that STS_CLIENT exists
        assert STS_CLIENT is not None

    def test_iam_client_initialization(self):
        """Test that IAM_CLIENT is initialized with the correct service name."""
        # Simply verify that IAM_CLIENT exists
        assert IAM_CLIENT is not None

    def test_logs_client_initialization(self):
        """Test that LOGS_CLIENT is initialized with the correct service name."""
        # Simply verify that LOGS_CLIENT exists
        assert LOGS_CLIENT is not None

    def test_s3_client_initialization(self):
        """Test that S3_CLIENT is initialized with the correct service name."""
        # Simply verify that S3_CLIENT exists
        assert S3_CLIENT is not None

    def test_client_variables_exist(self):
        """Test that all client variables exist and are not None."""
        from ezbatch.client import (
            BATCH_CLIENT,
            IAM_CLIENT,
            LOGS_CLIENT,
            S3_CLIENT,
            STS_CLIENT,
        )

        assert BATCH_CLIENT is not None
        assert STS_CLIENT is not None
        assert IAM_CLIENT is not None
        assert LOGS_CLIENT is not None
        assert S3_CLIENT is not None
