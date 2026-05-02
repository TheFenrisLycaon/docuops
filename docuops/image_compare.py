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
from typing import Any
from typing import Any

from PIL.ImageFile import ImageFile
from PIL.ImageFile import ImageFile
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

    Params:
        img_a: First image as a grayscale NumPy array.
        img_b: Second image as a grayscale NumPy array.
        title: Figure title.
    """
    m: float = mse(img_a, img_b)
    s: float = ssim_score(img_a, img_b)
    fig: plt.Figure = plt.figure(title)
    plt.suptitle(f"MSE: {m:.2f}, SSIM: {s:.2f}")
    ax: plt.Axes = fig.add_subplot(1, 2, 1)
    plt.imshow(img_a, cmap=plt.cm.gray)
    plt.axis("off")
    ax.set_title("Image A")
    ax: plt.Axes = fig.add_subplot(1, 2, 2)
    plt.imshow(img_b, cmap=plt.cm.gray)
    plt.axis("off")
    ax.set_title("Image B")
    plt.tight_layout()
    plt.show()


def compare_directories(dir_a: str, dir_b: str) -> list[dict]:
    """Batch-compare identically sorted images from two directories.

    The i-th file in each sorted directory listing is treated as a pair.

    Params:
        dir_a: Path to the first directory of images.
        dir_b: Path to the second directory of images.

    Returns:
        List of dicts with keys: ``file_a``, ``file_b``, ``mse``, ``ssim``, ``equal``.
    """
    if not os.path.isdir(dir_a):
        raise ValueError(f"Directory not found: {dir_a}")
    if not os.path.isdir(dir_b):
        raise ValueError(f"Directory not found: {dir_b}")
    files_a: list[str] = sorted(os.listdir(dir_a))
    files_b: list[str] = sorted(os.listdir(dir_b))
    results: list[dict] = []

    for name_a, name_b in zip(files_a, files_b):
        path_a: str = os.path.join(dir_a, name_a)
        path_b: str = os.path.join(dir_b, name_b)
        cv_a: (
            cv2.Mat
            | np.ndarray[Any, np.dtype[np.integer[Any] | np.floating[Any]]]
            | None
        ) = cv2.imread(path_a, cv2.IMREAD_GRAYSCALE)
        cv_b: (
            cv2.Mat
            | np.ndarray[Any, np.dtype[np.integer[Any] | np.floating[Any]]]
            | None
        ) = cv2.imread(path_b, cv2.IMREAD_GRAYSCALE)
        if cv_a is None:
            raise ValueError(f"Could not read image: {path_a}")
        if cv_b is None:
            raise ValueError(f"Could not read image: {path_b}")
        pil_a: ImageFile = Image.open(path_a)
        pil_b: ImageFile = Image.open(path_b)
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
