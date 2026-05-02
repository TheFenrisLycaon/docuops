"""
docuops — Document Operations Package
=====================================
A collection of utilities for working with PDF and DOCX files.

Submodules
----------
    pdf_compress        — Compress PDFs and convert them to JPEG images
    pdf_to_docx         — Convert PDF files to DOCX documents (4 modes)
    docx_image_replace  — Replace embedded images inside a .docx file
    image_compare       — Compare images via MSE, SSIM, and pixel equality
    docx_insert_images  — Insert images into a new DOCX document
    docx_table          — Populate a DOCX table from an Excel spreadsheet

Quick start
-----------
    # Programmatic use
    from docuops import replace_img, create_statement, run_pipeline

    # Command-line use
    python -m docuops --help

Note
----
Imports are lazy: submodule dependencies (Pillow, pdf2image, python-docx,
etc.) are only resolved when you first import or call a specific function,
not when ``import docuops`` is executed.  This means the package loads
instantly regardless of which dependencies are installed.
"""

from __future__ import annotations

__all__ = [
    # pdf_compress
    "compress",
    "to_img",
    "comp_img",
    "run_pipeline",
    # pdf_to_docx
    "create_statement",
    "create_certificates",
    "create_license",
    "create_work",
    "pdf_to_jpegs",
    # docx_image_replace
    "replace_img",
    "zip_dir",
    "find",
    # image_compare
    "mse",
    "ssim",
    "compare_images",
    "compare_directories",
    # docx_insert_images
    "insert_image",
    # docx_table
    "populate_table",
]


def __getattr__(name: str):
    """Lazy import implementation."""
    if name in __all__:
        # Map function names to their modules
        module_map = {
            # pdf_compress
            "compress": ".pdf_compress",
            "to_img": ".pdf_compress",
            "comp_img": ".pdf_compress",
            "run_pipeline": ".pdf_compress",
            # pdf_to_docx
            "create_statement": ".pdf_to_docx",
            "create_certificates": ".pdf_to_docx",
            "create_license": ".pdf_to_docx",
            "create_work": ".pdf_to_docx",
            "pdf_to_jpegs": ".pdf_to_docx",
            # docx_image_replace
            "replace_img": ".docx_image_replace",
            "zip_dir": ".docx_image_replace",
            "find": ".docx_image_replace",
            # image_compare
            "mse": ".image_compare",
            "ssim": ".image_compare",
            "compare_images": ".image_compare",
            "compare_directories": ".image_compare",
            # docx_insert_images
            "insert_image": ".docx_insert_images",
            # docx_table
            "populate_table": ".docx_table",
        }

        if name in module_map:
            from importlib import import_module

            module = import_module(module_map[name], __name__)
            return getattr(module, name)

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
