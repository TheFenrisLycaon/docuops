import subprocess
import sys
from pathlib import Path
from typing import List, NoReturn

from pdf2image import convert_from_path as convert
from PIL import Image
from tqdm import tqdm

from docuops import config


def compress(in_file: Path, out_path: Path, compression_level: int = 3) -> None:
    """Compress a single PDF using Ghostscript.

    Params:
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

    Params:
        file_path: Path to the input PDF.
        img_conversion_dir: Root directory where per-PDF image folders are created.
    """
    if not file_path.is_file() or file_path.suffix.lower() != ".pdf":
        raise ValueError(f"Invalid PDF file: {file_path}")
    out_dir: Path = img_conversion_dir / file_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    pages: List[Image] = convert(file_path)
    for count, page in enumerate(pages, start=1):
        page.save(out_dir / f"{count:03d}.jpg", "JPEG")


def comp_img(folder: str, img_conversion_dir: Path, img_compression_dir: Path) -> None:
    """Re-compress JPEG images from a converted PDF folder at quality=25.

    Params:
        folder: Name of the subdirectory inside *img_conversion_dir*.
        img_conversion_dir: Root directory containing per-PDF image folders.
        img_compression_dir: Root directory where compressed images are saved.
    """
    src_dir: Path = img_conversion_dir / folder
    if not src_dir.is_dir():
        raise ValueError(f"Source directory not found: {src_dir}")

    dst_dir: Path = img_compression_dir / folder
    dst_dir.mkdir(parents=True, exist_ok=True)

    for img_path in sorted(src_dir.iterdir()):
        Image.open(img_path).save(dst_dir / img_path.name, format="JPEG", quality=25)


def run_compression_pipeline(
    source_dir: Path,
    pdf_out_dir: Path,
    img_conversion_dir: Path,
    img_compression_dir: Path,
    quality: config.Quality_Preset = config.Quality_Preset.EBOOK,
) -> bool | NoReturn:
    """Run the full three-stage PDF compression pipeline.

    Params:
        source_dir: Directory containing the original PDF files.
        pdf_out_dir: Directory where compressed PDFs are saved.
        img_conversion_dir: Directory where per-PDF image folders are created.
        img_compression_dir: Directory where compressed images are saved.
        quality: Compression level preset (default: EBOOK).

    Raises:
        SystemExit: If *source_dir* does not exist.
    """
    if not source_dir.is_dir():
        print(f"Error::\tSource directory not found: {source_dir}")
        sys.exit(1)

    pdf_out_dir.mkdir(parents=True, exist_ok=True)
    img_conversion_dir.mkdir(parents=True, exist_ok=True)
    img_compression_dir.mkdir(parents=True, exist_ok=True)

    try:
        for pdf in tqdm(
            sorted(
                p
                for p in source_dir.iterdir()
                if p.is_file() and p.suffix.lower() == ".pdf"
            ),
            desc="Compressing PDFs",
            leave=False,
        ):
            compress(pdf, pdf_out_dir / pdf.name, compression_level=quality)

        for pdf in tqdm(
            sorted(
                p
                for p in pdf_out_dir.iterdir()
                if p.is_file() and p.suffix.lower() == ".pdf"
            ),
            desc="Converting to images",
            leave=False,
        ):
            to_img(pdf, img_conversion_dir)

        for folder in tqdm(
            sorted(f for f in img_conversion_dir.iterdir() if f.is_dir()),
            desc="Compressing images",
            leave=False,
        ):
            comp_img(folder.name, img_conversion_dir, img_compression_dir)

        return True

    except Exception as e:
        print(f"Error::\t{e}")
        sys.exit(1)
        return False
