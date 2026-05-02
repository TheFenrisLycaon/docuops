"""
docx_image_replace.py — DOCX Embedded Image Replacement
=========================================================
Replaces a specific embedded image inside a ``.docx`` file by treating the
document as a ZIP archive, swapping the target JPEG in the extracted
``word/media/`` directory, and re-packaging the result as a new ``.docx``.

Public API
----------
    replace_img(doc_path, img_num, new_image_path, cache_dir, output_dir) -> str
    zip_dir(folder_path, zip_path)
    find(pattern, path) -> list[str]

Dependencies
------------
    Standard library only (``fnmatch``, ``os``, ``shutil``, ``zipfile``)
"""

import fnmatch
import os
import shutil
import zipfile
from pathlib import Path


def zip_dir(folder_path: str, zip_path: str) -> None:
    """Recursively compress *folder_path* into a ZIP archive at *zip_path*.

    Stored paths inside the archive are relative to *folder_path* so the
    directory itself is not included as a root entry.

    Args:
        folder_path: Path to the directory that should be compressed.
        zip_path: Destination path for the resulting ``.zip`` / ``.docx`` file.
    """
    with zipfile.ZipFile(zip_path, mode="w") as zipf:
        prefix_len = len(folder_path)
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, file_path[prefix_len:])


def find(pattern: str, path: str) -> list[str]:
    """Return all files under *path* whose names match *pattern*.

    Uses :func:`fnmatch.fnmatch` so standard shell wildcards (``*``, ``?``,
    ``[seq]``) are supported.

    Args:
        pattern: Shell-style filename pattern (e.g. ``"*.pdf"``).
        path: Root directory to search recursively.

    Returns:
        A list of file paths that matched.
    """
    result: list[str] = []
    for root, _, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result


def replace_img(
    doc_path: str,
    img_num: int,
    new_image_path: str,
    cache_dir: str = ".cache",
    output_dir: str = "data",
) -> str:
    """Replace an embedded image inside a ``.docx`` file.

    ``.docx`` files are ZIP archives.  This function:

    1. Extracts the document into a temporary sub-directory under *cache_dir*.
    2. Removes the existing ``image<img_num>.jpeg`` from ``word/media/``.
    3. Copies *new_image_path* into ``word/media/`` and renames it to match
       the original image filename (``image<img_num>.jpeg``).
    4. Re-zips the modified tree and writes the result to *output_dir*.

    Args:
        doc_path: Path to the source ``.docx`` file.
        img_num: 1-based index of the image to replace (e.g. ``1`` targets
            ``image1.jpeg`` inside ``word/media/``).
        new_image_path: Path to the JPEG that will replace the existing image.
        cache_dir: Root directory used for temporary extraction.  A unique
            sub-directory is created per document to avoid collisions.
        output_dir: Directory where the modified ``.docx`` is written.

    Returns:
        The path of the newly created ``.docx`` file.
    """
    doc_name = Path(doc_path).stem

    extract_dir = os.path.join(cache_dir, doc_name, "run1")
    dest_file = os.path.join(output_dir, f"{doc_name}_changed.docx")

    os.makedirs(extract_dir, mode=0o777, exist_ok=True)
    os.makedirs(output_dir, mode=0o777, exist_ok=True)

    # Step 1: Extract the .docx (ZIP) to the cache directory
    with zipfile.ZipFile(doc_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    # Step 2: Locate target image and replacement file
    media_dir = os.path.join(extract_dir, "word", "media")
    target_img = os.path.join(media_dir, f"image{img_num}.jpeg")
    replacement_name = Path(new_image_path).name

    # Step 3: Remove the old image and copy in the new one
    os.remove(target_img)
    shutil.copy(new_image_path, media_dir)

    # Step 4: Rename the copied file to match the expected image filename
    os.rename(
        os.path.join(media_dir, replacement_name),
        os.path.join(media_dir, f"image{img_num}.jpeg"),
    )

    # Step 5: Re-package the modified directory tree back into a .docx
    zip_dir(extract_dir, dest_file)

    return dest_file
