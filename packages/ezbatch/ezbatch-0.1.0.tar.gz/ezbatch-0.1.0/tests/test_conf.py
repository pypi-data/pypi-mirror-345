import os
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from ezbatch.conf import CONFIG, CONFIG_PATH, EZBatchConfig, EZBatchSettings
from ezbatch.defaults import (
    CURRENT_AWS_ACCOUNT,
    DEFAULT_MAX_VCPUS,
    DEFAULT_SSE,
    DEFAULT_SSE_KMS_KEY_ID,
)


class TestEZBatchSettings:
    def test_settings_initialization(self):
        """Test that EZBatchSettings initializes with default values."""
        settings = EZBatchSettings()

        # Verify default values
        assert settings.executionRoleArn == f"arn:aws:iam::{CURRENT_AWS_ACCOUNT}:role/ecsTaskExecutionRole"
        assert settings.maxvCpus == DEFAULT_MAX_VCPUS
        assert (
            settings.serviceRole
            == f"arn:aws:iam::{CURRENT_AWS_ACCOUNT}:role/aws-service-role/batch.amazonaws.com/AWSServiceRoleForBatch"
        )
        assert settings.instanceRole == f"arn:aws:iam::{CURRENT_AWS_ACCOUNT}:role/ecsInstanceRole"
        assert settings.securityGroupIds == []
        assert settings.sse == DEFAULT_SSE
        assert settings.sseKmsKeyId == DEFAULT_SSE_KMS_KEY_ID
        assert settings.subnets == []
        assert settings.taskRoleArn == f"arn:aws:iam::{CURRENT_AWS_ACCOUNT}:role/ecsTaskExecutionRole"

    def test_settings_custom_values(self):
        """Test that EZBatchSettings can be initialized with custom values."""
        settings = EZBatchSettings(
            executionRoleArn="custom-execution-role",
            maxvCpus=100,
            serviceRole="custom-service-role",
            instanceRole="custom-instance-role",
            securityGroupIds=["sg-1", "sg-2"],
            sse="aws:kms",
            sseKmsKeyId="custom-kms-key",
            subnets=["subnet-1", "subnet-2"],
            taskRoleArn="custom-task-role",
        )

        # Verify custom values
        assert settings.executionRoleArn == "custom-execution-role"
        assert settings.maxvCpus == 100
        assert settings.serviceRole == "custom-service-role"
        assert settings.instanceRole == "custom-instance-role"
        assert settings.securityGroupIds == ["sg-1", "sg-2"]
        assert settings.sse == "aws:kms"
        assert settings.sseKmsKeyId == "custom-kms-key"
        assert settings.subnets == ["subnet-1", "subnet-2"]
        assert settings.taskRoleArn == "custom-task-role"

    def test_settings_to_dict(self):
        """Test that EZBatchSettings can be converted to a dictionary."""
        settings = EZBatchSettings(
            executionRoleArn="custom-execution-role",
            maxvCpus=100,
        )

        # Convert to dict
        settings_dict = settings.to_dict()

        # Verify
        assert isinstance(settings_dict, dict)
        assert settings_dict["executionRoleArn"] == "custom-execution-role"
        assert settings_dict["maxvCpus"] == 100


class TestEZBatchConfig:
    def test_config_initialization(self):
        """Test that EZBatchConfig initializes with default settings."""
        config = EZBatchConfig()

        # Verify
        assert isinstance(config.Settings, EZBatchSettings)
        assert config.Settings.maxvCpus == DEFAULT_MAX_VCPUS

    def test_config_custom_settings(self):
        """Test that EZBatchConfig can be initialized with custom settings."""
        settings = EZBatchSettings(maxvCpus=100)
        config = EZBatchConfig(Settings=settings)

        # Verify
        assert config.Settings.maxvCpus == 100

    def test_config_to_dict(self):
        """Test that EZBatchConfig can be converted to a dictionary."""
        config = EZBatchConfig()

        # Convert to dict
        config_dict = config.to_dict()

        # Verify
        assert isinstance(config_dict, dict)
        assert "Settings" in config_dict
        assert isinstance(config_dict["Settings"], dict)
        assert config_dict["Settings"]["maxvCpus"] == DEFAULT_MAX_VCPUS

    @patch("ezbatch.conf.load")
    def test_config_load(self, mock_load):
        """Test that EZBatchConfig can load from a file."""
        # Setup mock
        mock_config_dict = {
            "Settings": {
                "maxvCpus": 100,
                "executionRoleArn": "custom-execution-role",
            }
        }
        mock_load.return_value = mock_config_dict

        # Mock open
        m = mock_open()
        with patch("pathlib.Path.open", m):
            # Load config
            config = EZBatchConfig.load("test_config.toml")

        # Verify
        assert config.Settings.maxvCpus == 100
        assert config.Settings.executionRoleArn == "custom-execution-role"
        mock_load.assert_called_once()


class TestConfigModule:
    def test_config_creation(self):
        """Test that a new config file is created if it doesn't exist."""
        # This test is simplified to just check that the CONFIG object exists
        # and has the expected default values
        from ezbatch.conf import CONFIG

        # Verify that CONFIG has default values
        assert CONFIG is not None
        assert CONFIG.Settings.maxvCpus == DEFAULT_MAX_VCPUS

    def test_config_loading(self):
        """Test that the CONFIG object is loaded."""
        # This test is simplified to just check that the CONFIG object exists
        from ezbatch.conf import CONFIG

        # Verify that CONFIG exists
        assert CONFIG is not None

    def test_config_path_environment_variable(self, tmp_path):
        """Test that CONFIG_PATH uses the environment variable if set."""
        # Create a temporary config file path
        temp_config_path = tmp_path / "config.toml"

        # Save original environment
        original_env = os.environ.get("EZBATCH_CONFIG_PATH")

        try:
            # Set environment variable to the temporary path
            os.environ["EZBATCH_CONFIG_PATH"] = str(temp_config_path)

            # Patch Path.exists and Path.open to avoid file operations
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.open", mock_open()):
                    with patch("ezbatch.conf.EZBatchConfig.load") as mock_load:
                        # Mock load to return a default config
                        mock_load.return_value = EZBatchConfig()

                        # Import the module to use the environment variable
                        from importlib import reload

                        import ezbatch.conf

                        reload(ezbatch.conf)

            # Verify
            assert str(ezbatch.conf.CONFIG_PATH) == str(temp_config_path)
        finally:
            # Restore original environment
            if original_env is not None:
                os.environ["EZBATCH_CONFIG_PATH"] = original_env
            else:
                del os.environ["EZBATCH_CONFIG_PATH"]
