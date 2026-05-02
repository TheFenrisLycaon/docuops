"""
Tests for CLI module.
"""

import pytest
from unittest.mock import patch

from docuops.cli import docuopsCLI, main


class TestCLI:
    """Test cases for CLI functions."""

    def test_cli_class_exists(self):
        """Test that the docuopsCLI class can be instantiated."""
        cli = docuopsCLI()
        assert cli is not None

    @patch("sys.argv", ["docuops", "test"])
    @patch("subprocess.run")
    @patch("sys.exit")
    def test_main_test_command(self, mock_exit, mock_subprocess):
        """Test that main function can handle test command."""
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "Tests passed"
        mock_subprocess.return_value.stderr = ""

        # This should not raise an exception
        main()

        # Check that sys.exit was called with 0
        mock_exit.assert_called_once_with(0)

    @patch("docuops.pdf_compress.run_pipeline")
    def test_compress_command(self, mock_run_pipeline):
        """Test the compress command."""
        cli = docuopsCLI()
        cli.compress(source="./test_source", quality=2)
        mock_run_pipeline.assert_called_once()
        Params, kwParams = mock_run_pipeline.call_Params
        assert str(kwParams["source_dir"]) == "test_source"
        assert kwParams["quality"] == 2

    @patch("docuops.image_compare.compare_directories")
    def test_compare_command(self, mock_compare):
        """Test the compare command."""
        mock_compare.return_value = [
            {
                "file_a": "a.jpg",
                "file_b": "b.jpg",
                "mse": 1.0,
                "ssim": 0.9,
                "equal": True,
            }
        ]
        cli = docuopsCLI()
        cli.compare("dir_a", "dir_b")
        mock_compare.assert_called_once_with("dir_a", "dir_b")
