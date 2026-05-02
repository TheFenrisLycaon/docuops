"""
Tests for docx_table module.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from pathlib import Path

from docuops.docx_table import populate_table


class TestDocxTable:
    """Test cases for DOCX table population functions."""

    @patch('docuops.docx_table.DocxTemplate')
    def test_populate_table(self, mock_docx_template, temp_dir):
        """Test populate_table function with mock data."""
        # Create mock Excel data
        excel_data = pd.DataFrame({
            'Name': ['Alice', 'Bob'],
            'Age': [25, 30],
            'City': ['NYC', 'LA']
        })

        # Mock files
        excel_file = temp_dir / "test.xlsx"
        template_file = temp_dir / "template.docx"
        output_file = temp_dir / "output.docx"

        # Create empty files
        excel_file.write_text("")
        template_file.write_text("")
        output_file.write_text("")

        # Mock pandas read_excel
        with patch('pandas.read_excel', return_value=excel_data) as mock_read_excel:
            # Mock DocxTemplate
            mock_template_instance = MagicMock()
            mock_docx_template.return_value = mock_template_instance

            populate_table(str(excel_file), str(template_file), str(output_file))

            # Check that pandas.read_excel was called
            mock_read_excel.assert_called_once_with(str(excel_file))

            # Check that DocxTemplate was instantiated
            mock_docx_template.assert_called_once_with(str(template_file))

            # Check that render was called with correct context
            expected_context = {
                "tbl_contents": [
                    {"cols": ["Alice", 25, "NYC"]},
                    {"cols": ["Bob", 30, "LA"]}
                ]
            }
            mock_template_instance.render.assert_called_once_with(expected_context)

            # Check that save was called
            mock_template_instance.save.assert_called_once_with(output_file)