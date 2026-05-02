"""
Tests for docx_insert_images module.
"""

import pytest
from unittest.mock import MagicMock, patch

from docuops.docx_insert_images import insert_image


class TestDocxInsertImages:
    """Test cases for DOCX image insertion functions."""

    @patch("docx.shared.Inches")
    def test_insert_image_with_title(self, mock_inches):
        """Test insert_image function with a title."""
        mock_doc = MagicMock()
        mock_inches.side_effect = lambda x: int(
            x * 914400
        )  # Mock Inches conversion (approx)

        insert_image(mock_doc, "test.jpg", 5.0, 7.0, title="Test Title")

        # Check that add_heading was called
        mock_doc.add_heading.assert_called_once_with("Test Title", level=0)

        # Check that add_picture was called
        mock_doc.add_picture.assert_called_once_with(
            "test.jpg",
            width=5 * 914400,  # 5 inches in EMUs
            height=7 * 914400,  # 7 inches in EMUs
        )

        # Check that add_page_break was called
        mock_doc.add_page_break.assert_called_once()

    @patch("docx.shared.Inches")
    def test_insert_image_without_title(self, mock_inches):
        """Test insert_image function without a title."""
        mock_doc = MagicMock()
        mock_inches.side_effect = lambda x: int(
            x * 914400
        )  # Mock Inches conversion (approx)

        insert_image(mock_doc, "test.jpg", 5.0, 7.0)

        # Check that add_heading was not called
        mock_doc.add_heading.assert_not_called()

        # Check that add_picture was called
        mock_doc.add_picture.assert_called_once_with(
            "test.jpg",
            width=5 * 914400,  # 5 inches in EMUs
            height=7 * 914400,  # 7 inches in EMUs
        )

        # Check that add_page_break was called
        mock_doc.add_page_break.assert_called_once()
