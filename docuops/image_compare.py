"""
image_compare.py — Image Similarity Comparison
===============================================
Utilities for measuring and visualising the similarity between two images
using MSE (Mean Squared Error), SSIM (Structural Similarity Index), and
pixel-exact equality.

Public API
----------
    mse(img_a, img_b) -> float
    ssim_score(img_a, img_b) -> float
    images_equal(pil_a, pil_b) -> bool
    compare_images(img_a, img_b, title) -> None
    compare_directories(dir_a, dir_b) -> list[dict]

Dependencies
------------
    opencv-python (pip, ``cv2``)
    Pillow        (pip, ``PIL``)
    scikit-image  (pip, ``skimage``)
    matplotlib    (pip)
    numpy         (pip)
"""

import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageChops
from skimage.metrics import structural_similarity as _ssim


def mse(img_a: np.ndarray, img_b: np.ndarray) -> float:
    """Mean Squared Error between two grayscale images (lower = more similar)."""
    err = np.sum((img_a.astype("float") - img_b.astype("float")) ** 2)
    err /= float(img_a.shape[0] * img_a.shape[1])
    return float(err)


def ssim_score(img_a: np.ndarray, img_b: np.ndarray) -> float:
    """Structural Similarity Index between two grayscale images (1.0 = identical)."""
    return float(_ssim(img_a, img_b))


def images_equal(pil_a: Image.Image, pil_b: Image.Image) -> bool:
    """Pixel-exact equality check using PIL ImageChops."""
    if pil_a.size != pil_b.size:
        return False
    return ImageChops.difference(pil_a, pil_b).getbbox() is None


def compare_images(
    img_a: np.ndarray, img_b: np.ndarray, title: str = "Comparison"
) -> None:
    """Display two grayscale images side-by-side with MSE and SSIM in the title.

    Args:
        img_a: First image as a grayscale NumPy array.
        img_b: Second image as a grayscale NumPy array.
        title: Figure title.
    """
    m = mse(img_a, img_b)
    s = ssim_score(img_a, img_b)
    fig = plt.figure(title)
    plt.suptitle(f"MSE: {m:.2f}, SSIM: {s:.2f}")
    ax = fig.add_subplot(1, 2, 1)
    plt.imshow(img_a, cmap=plt.cm.gray)
    plt.axis("off")
    ax.set_title("Image A")
    ax = fig.add_subplot(1, 2, 2)
    plt.imshow(img_b, cmap=plt.cm.gray)
    plt.axis("off")
    ax.set_title("Image B")
    plt.tight_layout()
    plt.show()


def compare_directories(dir_a: str, dir_b: str) -> list[dict]:
    """Batch-compare identically sorted images from two directories.

    The i-th file in each sorted directory listing is treated as a pair.

    Args:
        dir_a: Path to the first directory of images.
        dir_b: Path to the second directory of images.

    Returns:
        List of dicts with keys: ``file_a``, ``file_b``, ``mse``, ``ssim``, ``equal``.
    """
    files_a = sorted(os.listdir(dir_a))
    files_b = sorted(os.listdir(dir_b))
    results: list[dict] = []

    for name_a, name_b in zip(files_a, files_b):
        path_a = os.path.join(dir_a, name_a)
        path_b = os.path.join(dir_b, name_b)
        cv_a = cv2.imread(path_a, cv2.IMREAD_GRAYSCALE)
        cv_b = cv2.imread(path_b, cv2.IMREAD_GRAYSCALE)
        pil_a = Image.open(path_a)
        pil_b = Image.open(path_b)
        results.append(
            {
                "file_a": path_a,
                "file_b": path_b,
                "mse": mse(cv_a, cv_b),
                "ssim": ssim_score(cv_a, cv_b),
                "equal": images_equal(pil_a, pil_b),
            }
        )

    return results
