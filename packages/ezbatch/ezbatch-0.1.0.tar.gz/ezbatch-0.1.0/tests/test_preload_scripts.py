import os
from pathlib import Path

import pytest


class TestPreloadScripts:
    def test_preload_script_exists(self):
        """Test that the preload.sh script exists."""
        script_path = Path(__file__).parent.parent / "ezbatch" / "preload_scripts" / "preload.sh"
        assert script_path.exists(), f"Preload script not found at {script_path}"
        assert script_path.is_file(), f"Preload script at {script_path} is not a file"

    def test_preload_script_is_executable(self):
        """Test that the preload.sh script is executable."""
        script_path = Path(__file__).parent.parent / "ezbatch" / "preload_scripts" / "preload.sh"
        assert os.access(script_path, os.X_OK), f"Preload script at {script_path} is not executable"

    def test_preload_script_content(self):
        """Test that the preload.sh script has the expected content."""
        script_path = Path(__file__).parent.parent / "ezbatch" / "preload_scripts" / "preload.sh"
        with open(script_path) as f:
            content = f.read()

        # Check for key functions and commands
        assert "#!/bin/bash" in content, "Preload script does not have a shebang line"
        assert "setup_dependencies" in content, "Preload script does not have setup_dependencies function"
        assert "setup_aws_cli" in content, "Preload script does not have setup_aws_cli function"
        assert "EZBATCH_S3_MOUNTS" in content, "Preload script does not handle EZBATCH_S3_MOUNTS"
        assert "EZBATCH_COMMAND" in content, "Preload script does not handle EZBATCH_COMMAND"
        assert "aws s3 cp" in content, "Preload script does not use aws s3 cp command"

    def test_preload_script_package_init(self):
        """Test that the preload_scripts package has an __init__.py file."""
        init_path = Path(__file__).parent.parent / "ezbatch" / "preload_scripts" / "__init__.py"
        assert init_path.exists(), f"__init__.py not found at {init_path}"
        assert init_path.is_file(), f"__init__.py at {init_path} is not a file"
