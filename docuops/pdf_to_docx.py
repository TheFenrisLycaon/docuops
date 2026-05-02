import os
import tempfile
from pathlib import Path
from typing import List, Optional, Iterable
from PIL.Image import Image

from docuops import config, utils, errors


def merge_pdfs_to_docs(input_files_paths: Iterable[str]) -> None:
    """
    Convert each PDF in *input_dir* into its own ``.docx`` in *output_dir*.
    """
    for filename in sorted(input_files_paths):
        stem: str = Path(filename).stem

        with tempfile.TemporaryDirectory() as temp_dir:
            pages: List[Image] = utils._pdf_to_images(filename)
            utils._save_pages_to_dir(pages, temp_dir)
            out_path: str = os.path.join(config.OUTPUT_PATH, f"{stem}.docx")
            utils._build_docx_from_dir(temp_dir)
            print(f"  Saved: {out_path}")


def create_certificates(
    input_dir: str,
    output_path: str,
    poppler_path: Optional[str] = POPPLER_PATH,
) -> None:
    """Merge all PDFs in *input_dir* into a single ``.docx`` at *output_path*.

    All pages from all PDFs are collected in directory listing order and
    assembled into one Word document.

    Params:
        input_dir: Directory containing source PDF files.
        output_path: Full path (including filename) for the output ``.docx``.
        poppler_path: Optional path to Poppler binaries.
    """
    if not os.path.isdir(input_dir):
        raise ValueError(f"Input directory not found: {input_dir}")
    os.makedirs(Path(output_path).parent, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir: str:
        page_index = 0
        for filename: str in sorted(os.listdir(input_dir)):
            pdf_path: str = os.path.join(input_dir, filename)
            pages: List[Image] = _pdf_to_images(pdf_path, poppler_path)
            for page: Image in pages:
                page.save(os.path.join(temp_dir, f"{page_index + 1:03d}.jpg"), "JPEG")
                page_index += 1

        _build_docx_from_dir(temp_dir, output_path)

    print(f"  Saved: {output_path}")


def create_license(input_dir: str, output_path: str) -> None:
    """Embed all images in *input_dir* directly into a single ``.docx``.

    Unlike the PDF-based functions, this works with pre-existing image files
    (e.g. scanned licences) so no Poppler conversion is needed.

    Params:
        input_dir: Directory containing image files to embed.
        output_path: Full path (including filename) for the output ``.docx``.
    """
    if not os.path.isdir(input_dir):
        raise ValueError(f"Input directory not found: {input_dir}")
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

    Params:
        work_dir: Directory containing work-experience PDF files.
        comp_dir: Directory containing company/reference PDF files.
        output_path: Full path (including filename) for the output ``.docx``.
        poppler_path: Optional path to Poppler binaries.
    """
    os.makedirs(Path(output_path).parent, exist_ok=True)

    work_paths: list[str] = sorted([os.path.join(work_dir, x) for x: str in os.listdir(work_dir)])
    comp_paths: list[str] = sorted([os.path.join(comp_dir, x) for x: str in os.listdir(comp_dir)])

    with tempfile.TemporaryDirectory() as temp_dir: str:
        for i, (work_pdf, comp_pdf) in enumerate(zip(work_paths, comp_paths)):
            work_pages: List[Image] = _pdf_to_images(work_pdf, poppler_path)
            _save_pages_to_dir(work_pages, temp_dir, prefix=f"{i}_0_")

            comp_pages: List[Image] = _pdf_to_images(comp_pdf, poppler_path)
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

    Params:
        pdf_path: Path to the source PDF file.
        output_dir: Directory where JPEG files are written.  Created
            automatically if it does not exist.
        poppler_path: Optional path to Poppler binaries.
    """
    print(f"Converting: {pdf_path}")
    os.makedirs(output_dir, exist_ok=True)

    pages: List[Image] = convert_from_path(pdf_path, poppler_path=poppler_path)
    for count, page in enumerate(pages):
        page.save(os.path.join(output_dir, f"{count + 1:03d}.jpg"), "JPEG")

    print(f"Done → {output_dir}")
