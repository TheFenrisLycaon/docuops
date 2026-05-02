"""
pdf_to_docx.py — PDF-to-DOCX Document Generation
==================================================
Converts collections of PDF files (and plain images) into Microsoft Word
``.docx`` documents.  Four document types are supported:

* **statement**    – Each PDF in a directory becomes its own ``.docx`` file.
* **certificates** – All PDFs in a directory are merged into one ``.docx``.
* **license**      – All images in a directory are merged into one ``.docx``.
* **work**         – Work-experience and company PDFs are interleaved into one ``.docx``.

A ``pdf_to_jpegs()`` helper converts a single PDF to numbered JPEG files.

PDFs are rendered to intermediate JPEG images via ``pdf2image`` (which wraps
Poppler).  If Poppler is not on the system PATH, pass its bin directory via
the ``poppler_path`` argument or set ``POPPLER_PATH`` below.

Public API
----------
    create_statement(input_dir, output_dir, poppler_path)
    create_certificates(input_dir, output_path, poppler_path)
    create_license(input_dir, output_path)
    create_work(work_dir, comp_dir, output_path, poppler_path)
    pdf_to_jpegs(pdf_path, output_dir, poppler_path)

Dependencies
------------
    Poppler   (system binary ``pdftoppm``, used by pdf2image)
    pdf2image (pip)
    python-docx (pip, imported as ``docx``)
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

import docx
from docx.shared import Inches
from pdf2image import convert_from_path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Set to the directory containing Poppler binaries if they are not on PATH.
# Example (Windows): POPPLER_PATH = r"C:\tools\poppler\bin"
POPPLER_PATH: Optional[str] = None

# Width (in inches) used when inserting images into Word documents.
IMAGE_WIDTH_INCHES: float = 5.0


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _pdf_to_images(pdf_path: str, poppler_path: Optional[str] = POPPLER_PATH):
    """Render all pages of a PDF as PIL ``Image`` objects.

    Tries without a custom Poppler path first; falls back to *poppler_path*
    if that raises (e.g. Poppler not on PATH).

    Args:
        pdf_path: Path to the PDF file to convert.
        poppler_path: Optional path to the Poppler ``bin`` directory.

    Returns:
        A list of ``PIL.Image.Image`` objects, one per page.
    """
    try:
        return convert_from_path(pdf_path)
    except Exception:
        return convert_from_path(pdf_path, poppler_path=poppler_path)


def _save_pages_to_dir(pages, temp_dir: str, prefix: str = "") -> None:
    """Save a list of PIL images as numbered JPEGs inside *temp_dir*.

    Args:
        pages: Iterable of ``PIL.Image.Image`` objects.
        temp_dir: Directory where JPEG files are written.
        prefix: Optional filename prefix (e.g. ``"0_0_"`` for interleaved work docs).
    """
    for i, page in enumerate(pages):
        filename = f"{prefix}{i + 1:03d}.jpg"
        page.save(os.path.join(temp_dir, filename), "JPEG")


def _build_docx_from_dir(image_dir: str, output_path: str) -> None:
    """Insert every image in *image_dir* into a new ``.docx`` and save it.

    Images are added in sorted order; a page break is inserted after each one.

    Args:
        image_dir: Directory containing JPEG images to embed.
        output_path: Destination path for the resulting ``.docx`` file.
    """
    document = docx.Document()
    for img_name in sorted(os.listdir(image_dir)):
        document.add_picture(
            os.path.join(image_dir, img_name), width=Inches(IMAGE_WIDTH_INCHES)
        )
        document.add_page_break()
    document.save(output_path)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_statement(
    input_dir: str,
    output_dir: str = ".",
    poppler_path: Optional[str] = POPPLER_PATH,
) -> None:
    """Convert each PDF in *input_dir* into its own ``.docx`` in *output_dir*.

    Args:
        input_dir: Directory containing source PDF files.
        output_dir: Directory where the output ``.docx`` files are written.
            Created automatically if it does not exist.
        poppler_path: Optional path to Poppler binaries.
    """
    os.makedirs(output_dir, exist_ok=True)

    for filename in sorted(os.listdir(input_dir)):
        pdf_path = os.path.join(input_dir, filename)
        stem = Path(filename).stem

        with tempfile.TemporaryDirectory() as temp_dir:
            pages = _pdf_to_images(pdf_path, poppler_path)
            _save_pages_to_dir(pages, temp_dir)
            out_path = os.path.join(output_dir, f"{stem}.docx")
            _build_docx_from_dir(temp_dir, out_path)
            print(f"  Saved: {out_path}")


def create_certificates(
    input_dir: str,
    output_path: str,
    poppler_path: Optional[str] = POPPLER_PATH,
) -> None:
    """Merge all PDFs in *input_dir* into a single ``.docx`` at *output_path*.

    All pages from all PDFs are collected in directory listing order and
    assembled into one Word document.

    Args:
        input_dir: Directory containing source PDF files.
        output_path: Full path (including filename) for the output ``.docx``.
        poppler_path: Optional path to Poppler binaries.
    """
    os.makedirs(Path(output_path).parent, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        page_index = 0
        for filename in sorted(os.listdir(input_dir)):
            pdf_path = os.path.join(input_dir, filename)
            pages = _pdf_to_images(pdf_path, poppler_path)
            for page in pages:
                page.save(os.path.join(temp_dir, f"{page_index + 1:03d}.jpg"), "JPEG")
                page_index += 1

        _build_docx_from_dir(temp_dir, output_path)

    print(f"  Saved: {output_path}")


def create_license(input_dir: str, output_path: str) -> None:
    """Embed all images in *input_dir* directly into a single ``.docx``.

    Unlike the PDF-based functions, this works with pre-existing image files
    (e.g. scanned licences) so no Poppler conversion is needed.

    Args:
        input_dir: Directory containing image files to embed.
        output_path: Full path (including filename) for the output ``.docx``.
    """
    os.makedirs(Path(output_path).parent, exist_ok=True)
    _build_docx_from_dir(input_dir, output_path)
    print(f"  Saved: {output_path}")


def create_work(
    work_dir: str,
    comp_dir: str,
    output_path: str,
    poppler_path: Optional[str] = POPPLER_PATH,
) -> None:
    """Pair work-experience PDFs with company PDFs and merge into one ``.docx``.

    Files from *work_dir* and *comp_dir* are matched by sorted order.  For
    each pair the work PDF pages come first, followed by the company PDF pages.

    Args:
        work_dir: Directory containing work-experience PDF files.
        comp_dir: Directory containing company/reference PDF files.
        output_path: Full path (including filename) for the output ``.docx``.
        poppler_path: Optional path to Poppler binaries.
    """
    os.makedirs(Path(output_path).parent, exist_ok=True)

    work_paths = sorted([os.path.join(work_dir, x) for x in os.listdir(work_dir)])
    comp_paths = sorted([os.path.join(comp_dir, x) for x in os.listdir(comp_dir)])

    with tempfile.TemporaryDirectory() as temp_dir:
        for i, (work_pdf, comp_pdf) in enumerate(zip(work_paths, comp_paths)):
            work_pages = _pdf_to_images(work_pdf, poppler_path)
            _save_pages_to_dir(work_pages, temp_dir, prefix=f"{i}_0_")

            comp_pages = _pdf_to_images(comp_pdf, poppler_path)
            _save_pages_to_dir(comp_pages, temp_dir, prefix=f"{i}_1_")

        _build_docx_from_dir(temp_dir, output_path)

    print(f"  Saved: {output_path}")


def pdf_to_jpegs(
    pdf_path: str,
    output_dir: str,
    poppler_path: Optional[str] = POPPLER_PATH,
) -> None:
    """Convert a single PDF into numbered JPEG images saved to *output_dir*.

    Useful for inspecting individual pages or preparing images for further
    processing outside of this module.

    Args:
        pdf_path: Path to the source PDF file.
        output_dir: Directory where JPEG files are written.  Created
            automatically if it does not exist.
        poppler_path: Optional path to Poppler binaries.
    """
    print(f"Converting: {pdf_path}")
    os.makedirs(output_dir, exist_ok=True)

    pages = convert_from_path(pdf_path, poppler_path=poppler_path)
    for count, page in enumerate(pages):
        page.save(os.path.join(output_dir, f"{count + 1:03d}.jpg"), "JPEG")

    print(f"Done → {output_dir}")
