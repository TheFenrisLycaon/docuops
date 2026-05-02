"""
Tests for pdf_compress module.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from docuops.pdf_compress import QUALITY_PRESETS, compress


class TestPdfCompress:
    """Test cases for PDF compression functions."""

    def test_quality_presets(self):
        """Test that quality presets are correctly defined."""
        expected = {
            0: "/default",
            1: "/prepress",
            2: "/printer",
            3: "/ebook",
            4: "/screen",
        }
        assert QUALITY_PRESETS == expected

    @patch("subprocess.call")
    def test_compress_valid_pdf(self, mock_subprocess, temp_dir):
        """Test compress function with valid PDF file."""
        # Create a mock PDF file
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_text("mock pdf content")

        output_file = temp_dir / "output.pdf"

        # Mock subprocess.call to return 0 (success)
        mock_subprocess.return_value = 0

        compress(pdf_file, output_file, compression_level=3)

        # Check that subprocess.call was called with correct arguments
        mock_subprocess.assert_called_once()
        args = mock_subprocess.call_args[0][0]
        assert "gs" in args
        assert f"-sOutputFile={output_file}" in args
        assert "-dPDFSETTINGS=/ebook" in args

    @patch("subprocess.call")
    def test_compress_invalid_file_extension(self, mock_subprocess, temp_dir):
        """Test compress function with non-PDF file."""
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("not a pdf")

        output_file = temp_dir / "output.pdf"

        with pytest.raises(SystemExit):
            compress(txt_file, output_file)

    @patch("subprocess.call")
    def test_compress_nonexistent_file(self, mock_subprocess, temp_dir):
        """Test compress function with nonexistent file."""
        nonexistent = temp_dir / "nonexistent.pdf"
        output_file = temp_dir / "output.pdf"

        with pytest.raises(SystemExit):
            compress(nonexistent, output_file)
