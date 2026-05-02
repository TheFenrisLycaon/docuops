"""
pdf_compress.py — PDF Compression and Image Conversion Pipeline
===============================================================
Three-stage batch processing pipeline for PDF files:

  Stage 1 — PDF Compression
    Compress each PDF via Ghostscript (``gs`` must be on PATH).
    Quality is controlled by a PDFSETTINGS preset (default: /ebook).

  Stage 2 — PDF → Image Conversion
    Rasterise each compressed PDF into per-page JPEG images
    using pdf2image (wraps Poppler's ``pdftoppm``).

  Stage 3 — Image Compression
    Re-save the converted JPEGs at a reduced quality (25/100) via Pillow.

Public API
----------
    compress(in_file, out_path, compression_level=3)
    to_img(file_path, img_conversion_dir)
    comp_img(folder, img_conversion_dir, img_compression_dir)
    run_pipeline(source_dir, pdf_out_dir, img_conversion_dir,
                 img_compression_dir, quality=3)

Dependencies
------------
    Ghostscript  (system binary ``gs``)
    Poppler      (system binary ``pdftoppm``, used by pdf2image)
    pdf2image    (pip)
    Pillow       (pip)
    tqdm         (pip)
"""

import subprocess
import sys
from pathlib import Path

from pdf2image import convert_from_path as convert
from PIL import Image
from tqdm import tqdm

# Ghostscript PDFSETTINGS presets, ordered roughly from highest to lowest quality.
# See: https://ghostscript.com/docs/9.54.0/VectorDevices.htm#PSPDF_IN
QUALITY_PRESETS: dict[int, str] = {
    0: "/default",
    1: "/prepress",
    2: "/printer",
    3: "/ebook",
    4: "/screen",
}


def compress(in_file: Path, out_path: Path, compression_level: int = 3) -> None:
    """Compress a single PDF using Ghostscript.

    Args:
        in_file: Path to the input PDF file.
        out_path: Destination path for the compressed output PDF.
        compression_level: Quality preset key (0–4). Defaults to 3 (/ebook).

    Raises:
        SystemExit: If the input file does not exist or is not a PDF.
    """
    if not in_file.is_file():
        print("Error::\tInvalid path for input PDF file")
        sys.exit(1)

    if in_file.suffix.lower() != ".pdf":
        print("Error::\tInput file is not a PDF")
        sys.exit(1)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    subprocess.call(
        [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={QUALITY_PRESETS[compression_level]}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={out_path}",
            str(in_file),
        ]
    )


def to_img(file_path: Path, img_conversion_dir: Path) -> None:
    """Convert a PDF into per-page JPEG images.

    Images are saved into a subdirectory named after the PDF stem so that
    files from different PDFs do not overwrite each other.  Page numbers are
    zero-padded to three digits (e.g. ``001.jpg``) to preserve sort order.

    Args:
        file_path: Path to the input PDF.
        img_conversion_dir: Root directory where per-PDF image folders are created.
    """
    out_dir = img_conversion_dir / file_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    pages = convert(file_path)
    for count, page in enumerate(pages, start=1):
        page.save(out_dir / f"{count:03d}.jpg", "JPEG")


def comp_img(folder: str, img_conversion_dir: Path, img_compression_dir: Path) -> None:
    """Re-compress JPEG images from a converted PDF folder at quality=25.

    Args:
        folder: Name of the subdirectory inside *img_conversion_dir*.
        img_conversion_dir: Root directory containing per-PDF image folders.
        img_compression_dir: Root directory where compressed images are saved.
    """
    src_dir = img_conversion_dir / folder
    dst_dir = img_compression_dir / folder
    dst_dir.mkdir(parents=True, exist_ok=True)

    for img_path in sorted(src_dir.iterdir()):
        Image.open(img_path).save(dst_dir / img_path.name, format="JPEG", quality=25)


def run_pipeline(
    source_dir: Path,
    pdf_out_dir: Path,
    img_conversion_dir: Path,
    img_compression_dir: Path,
    quality: int = 3,
) -> None:
    """Run the full three-stage PDF compression pipeline.

    Args:
        source_dir: Directory containing the source PDF files.
        pdf_out_dir: Directory for Ghostscript-compressed PDFs.
        img_conversion_dir: Directory for PDF-to-image output.
        img_compression_dir: Directory for final compressed images.
        quality: Ghostscript quality preset (0–4, default 3 = /ebook).

    Raises:
        SystemExit: If *source_dir* does not exist.
    """
    if not source_dir.is_dir():
        print(f"Error::\tSource directory not found: {source_dir}")
        sys.exit(1)

    pdf_out_dir.mkdir(parents=True, exist_ok=True)
    img_conversion_dir.mkdir(parents=True, exist_ok=True)
    img_compression_dir.mkdir(parents=True, exist_ok=True)

    for pdf in tqdm(sorted(source_dir.iterdir()), desc="Compressing PDFs", leave=False):
        compress(pdf, pdf_out_dir / pdf.name, compression_level=quality)

    for pdf in tqdm(
        sorted(pdf_out_dir.iterdir()), desc="Converting to images", leave=False
    ):
        to_img(pdf, img_conversion_dir)

    for folder in tqdm(
        sorted(img_conversion_dir.iterdir()), desc="Compressing images", leave=False
    ):
        comp_img(folder.name, img_conversion_dir, img_compression_dir)
