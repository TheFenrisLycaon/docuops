"""
Tests for CLI module.
"""

import pytest
from unittest.mock import patch

from docuops.cli import _build_parser, main


class TestCLI:
    """Test cases for CLI functions."""

    def test_build_parser(self):
        """Test that the argument parser can be built."""
        parser = _build_parser()
        assert parser is not None
        assert parser.description is not None

    def test_parser_has_commands(self):
        """Test that all expected commands are available."""
        parser = _build_parser()
        # Check that we can parse help
        with pytest.raises(SystemExit):
            parser.parse_args(['--help'])

    @patch('sys.argv', ['docops', 'test'])
    @patch('subprocess.run')
    @patch('sys.exit')
    def test_main_test_command(self, mock_exit, mock_subprocess):
        """Test that main function can handle test command."""
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "Tests passed"
        mock_subprocess.return_value.stderr = ""

        # This should not raise an exception
        main()

        # Check that sys.exit was called with 0
        mock_exit.assert_called_once_with(0)