"""
Tests for image_compare module.
"""

import numpy as np
import pytest
from PIL import Image

from docuops.image_compare import mse, ssim_score, images_equal


class TestImageCompare:
    """Test cases for image comparison functions."""

    def test_mse_identical_images(self):
        """Test MSE returns 0 for identical images."""
        img = np.array([[1, 2], [3, 4]], dtype=np.uint8)
        assert mse(img, img) == 0.0

    def test_mse_different_images(self):
        """Test MSE returns positive value for different images."""
        img1 = np.array([[1, 2], [3, 4]], dtype=np.uint8)
        img2 = np.array([[2, 3], [4, 5]], dtype=np.uint8)
        result = mse(img1, img2)
        assert result > 0.0
        assert isinstance(result, float)

    def test_ssim_identical_images(self):
        """Test SSIM returns 1.0 for identical images."""
        img = np.random.randint(0, 256, (10, 10), dtype=np.uint8)
        assert ssim_score(img, img) == 1.0

    def test_ssim_different_images(self):
        """Test SSIM returns less than 1.0 for different images."""
        img1 = np.random.randint(0, 256, (10, 10), dtype=np.uint8)
        img2 = np.random.randint(0, 256, (10, 10), dtype=np.uint8)
        result = ssim_score(img1, img2)
        assert result < 1.0
        assert isinstance(result, float)

    def test_images_equal_identical(self):
        """Test images_equal returns True for identical PIL images."""
        img = Image.new("RGB", (10, 10), color="red")
        assert images_equal(img, img) is True

    def test_images_equal_different(self):
        """Test images_equal returns False for different PIL images."""
        img1 = Image.new("RGB", (10, 10), color="red")
        img2 = Image.new("RGB", (10, 10), color="blue")
        assert images_equal(img1, img2) is False

    def test_images_equal_different_sizes(self):
        """Test images_equal returns False for images of different sizes."""
        img1 = Image.new("RGB", (10, 10), color="red")
        img2 = Image.new("RGB", (20, 20), color="red")
        assert images_equal(img1, img2) is False
