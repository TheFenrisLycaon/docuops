import os
from PIL.Image import Image

from typing import Iterable, List

import docx
from docx.document import Document
from docx.shared import Inches
from pdf2image import convert_from_path

from docuops import config
from docuops.errors import InstallationError


def _pdf_to_images(pdf_path: str) -> List[Image]:
    """
    Render all pages of a PDF as PIL ``Image`` objects.

    Tries without a custom Poppler path first; falls back to *poppler_path*
    if that raises (e.g. Poppler not on PATH).

    Param:
        pdf_path: Path to the PDF file to convert.

    Returns:
        A list of ``PIL.Image.Image`` objects, one per page.
    """
    if not os.path.isfile(pdf_path):
        raise ValueError(f"PDF file not found: {pdf_path}")

    if not isinstance(config.POPPLER_PATH, str):
        try:
            return convert_from_path(pdf_path)
        except Exception:
            raise InstallationError(
                "Poppler not found on PATH. Please install Poppler and/or set POPPLER_PATH in config.py"
            )

    return convert_from_path(pdf_path, poppler_path=config.POPPLER_PATH)


def _save_pages_to_dir(pages: Iterable[Image], filename_prefix: str = "") -> bool:
    """
    Save a list of PIL images as numbered JPEGs inside *temp_dir*.

    Params:
        pages: Iterable of ``PIL.Image.Image`` objects.
        filename_prefix: Optional filename prefix (e.g. ``"0_0_"`` for interleaved work docs).
    """
    for i, page in enumerate(pages):
        filename: str = f"{filename_prefix}{i + 1:03d}.jpg"
        page.save(os.path.join(config.TEMP_PATH, filename), "JPEG")
    return True


def _build_docx_from_dir(image_dir: str) -> None:
    """
    Insert every image in *image_dir* into a new ``.docx`` and save it.

    Images are added in sorted order; a page break is inserted after each one.

    Params:
        image_dir: Directory containing JPEG images to embed.
        output_path: Destination path for the resulting ``.docx`` file.
    """
    document: Document = docx.Document()
    for img_name in sorted(os.listdir(image_dir)):
        document.add_picture(
            os.path.join(image_dir, img_name), width=Inches(config.IMAGE_WIDTH_INCHES)
        )
        document.add_page_break()
    document.save(config.OUTPUT_PATH)
