"""
cli.py — Unified Command-Line Interface for docuops
====================================================
Run as ``python -m docuops <command> [options]``.

This CLI uses Google's Fire library for automatic argument parsing.

Commands
--------
    compress   — 3-stage PDF compression pipeline
    pdf2docx   — Convert PDFs to DOCX (statement / certificates / license / work)
    replace    — Replace an embedded image inside a .docx file
    compare    — Compare two image directories (MSE, SSIM, equality)
    insert     — Insert images into a new DOCX document
    table      — Populate a DOCX table from an Excel file
    test       — Run the test suite
"""

import fire
from pathlib import Path


class DocOpsCLI:
    """Command-line interface for document operations using Google's Fire."""

    def compress(
        self,
        source="./Source",
        pdf_out="./PDFCompression",
        img_conversion="./ImageConversion",
        img_compression="./ImageCompression",
        quality=3,
    ):
        """
        3-stage PDF compression pipeline.

        Args:
            source: Source PDF directory (default: ./Source)
            pdf_out: Compressed PDF output dir (default: ./PDFCompression)
            img_conversion: PDF→image output dir (default: ./ImageConversion)
            img_compression: Image compression output dir (default: ./ImageCompression)
            quality: Ghostscript quality preset 0=default … 4=screen (default: 3)
        """
        from docuops.pdf_compress import run_pipeline

        run_pipeline(
            source_dir=Path(source),
            pdf_out_dir=Path(pdf_out),
            img_conversion_dir=Path(img_conversion),
            img_compression_dir=Path(img_compression),
            quality=int(quality),
        )

    def pdf2docx(
        self,
        subcommand,
        input_dir=None,
        output_dir=".",
        output=None,
        work_dir=None,
        comp_dir=None,
        pdf=None,
        poppler_path=None,
    ):
        """
        Convert PDFs to DOCX documents.

        Args:
            subcommand: Mode - statement, certificates, license, work, or conv
            input_dir: Input directory for PDFs
            output_dir: Output directory (for statement mode)
            output: Output file path (for certificates, license, work modes)
            work_dir: Work directory (for work mode)
            comp_dir: Company directory (for work mode)
            pdf: PDF file path (for conv mode)
            poppler_path: Path to Poppler bin directory if not on PATH
        """
        from docuops.pdf_to_docx import (
            create_certificates,
            create_license,
            create_statement,
            create_work,
            pdf_to_jpegs,
        )

        if subcommand == "statement":
            create_statement(input_dir, output_dir, poppler_path)
        elif subcommand == "certificates":
            create_certificates(input_dir, output, poppler_path)
        elif subcommand == "license":
            create_license(input_dir, output)
        elif subcommand == "work":
            create_work(work_dir, comp_dir, output, poppler_path)
        elif subcommand == "conv":
            pdf_to_jpegs(pdf, output_dir, poppler_path)
        else:
            raise ValueError(f"Unknown subcommand: {subcommand}")

    def replace(self, doc, img_num, new_img, cache_dir=".cache", output_dir="data"):
        """
        Replace an embedded image in a .docx file.

        Args:
            doc: Path to source .docx file
            img_num: 1-based index of the image to replace
            new_img: Path to the replacement JPEG
            cache_dir: Temp extraction directory (default: .cache)
            output_dir: Output directory (default: data)
        """
        from docuops.docx_image_replace import replace_img

        output = replace_img(
            doc_path=doc,
            img_num=int(img_num),
            new_image_path=new_img,
            cache_dir=cache_dir,
            output_dir=output_dir,
        )
        print(f"Done — modified document saved to: {output}")

    def compare(self, dir_a, dir_b):
        """
        Compare two image directories.

        Args:
            dir_a: First image directory
            dir_b: Second image directory
        """
        from docuops.image_compare import compare_directories

        results = compare_directories(dir_a, dir_b)
        print(f"{'File A':<40} {'File B':<40} {'MSE':>10} {'SSIM':>8} {'Equal':>6}")
        print("-" * 110)
        for r in results:
            print(
                f"{Path(r['file_a']).name:<40} {Path(r['file_b']).name:<40}"
                f" {r['mse']:>10.2f} {r['ssim']:>8.4f} {str(r['equal']):>6}"
            )

    def insert(self, images, output, width=5.0, height=7.0, auto_title=False):
        """
        Insert images into a new DOCX document.

        Args:
            images: List of image file paths
            output: Output .docx path
            width: Image width in inches (default: 5.0)
            height: Image height in inches (default: 7.0)
            auto_title: Use the image filename stem as a heading
        """
        import docx as _docx

        from docuops.docx_insert_images import insert_image

        doc = _docx.Document()
        for img_path in images:
            insert_image(
                doc,
                img_path=img_path,
                size_x=float(width),
                size_y=float(height),
                title=Path(img_path).stem if auto_title else None,
            )
        doc.save(output)
        print(f"Done — saved to: {output}")

    def table(self, excel, template, output):
        """
        Populate a DOCX table from an Excel file.

        Args:
            excel: Path to source .xlsx file
            template: Path to .docx template file
            output: Output .docx path
        """
        from docuops.docx_table import populate_table

        populate_table(
            excel_path=excel,
            template_path=template,
            output_path=output,
        )

    def test(self):
        """Run the test suite."""
        import subprocess
        import sys

        try:
            # Run pytest on the tests directory
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "-v"],
                capture_output=True,
                text=True,
            )
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
            sys.exit(result.returncode)
        except FileNotFoundError:
            print("Error: pytest not found. Install with: pip install pytest")
            sys.exit(1)


def main():
    """Entry point for the CLI."""
    fire.Fire(DocOpsCLI)


if __name__ == "__main__":
    main()
