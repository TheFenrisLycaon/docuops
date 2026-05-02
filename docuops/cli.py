from pathlib import Path
from typing import Iterable

import docx as _docx
import fire
from docx.document import Document

from docuops import config
from docuops.docx_image_replace import replace_img
from docuops.docx_insert_images import insert_image
from docuops.image_compare import compare_directories


class docuopsCLI:
    """Command-line interface for document operations."""

    def compress(self) -> bool:
        """
        3-stage PDF compression pipeline.
        """
        from docuops.pdf_compress import run_compression_pipeline

        return run_compression_pipeline(
            source_dir=Path(config.SOURCE_PATH),
            pdf_out_dir=Path(config.OUTPUT_PATH),
            img_conversion_dir=Path(config.CONVERSION_PATH),
            img_compression_dir=Path(config.COMPRESSION_DIR),
            quality=config.QUALITY,
        )

    def pdf2docx(
        self,
        subcommand: str,
        input_dir: str,
        output_dir: str,
        output: str,
        work_dir: str,
        comp_dir: str,
        pdf: str,
        poppler_path: str,
    ) -> bool:
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
            merge_pdfs_to_docs,
            create_work,
            pdf_to_jpegs,
        )

        if subcommand == "statement":
            merge_pdfs_to_docs(input_dir, output_dir, poppler_path)
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

    def replace(
        self, doc, img_num, new_img, cache_dir=".cache", output_dir="data"
    ) -> None:
        """
        Replace an embedded image in a .docx file.

        Args:
            doc: Path to source .docx file
            img_num: 1-based index of the image to replace
            new_img: Path to the replacement JPEG
            cache_dir: Temp extraction directory (default: .cache)
            output_dir: Output directory (default: data)
        """
        output: str = replace_img(
            doc_path=doc,
            img_num=int(img_num),
            new_image_path=new_img,
            cache_dir=cache_dir,
            output_dir=output_dir,
        )
        print(f"Done — modified document saved to: {output}")

    def compare(self, dir_a, dir_b) -> None:
        """
        Compare two image directories.

        Args:
            dir_a: First image directory
            dir_b: Second image directory
        """

        results = compare_directories(dir_a, dir_b)
        print(f"{'File A':<40} {'File B':<40} {'MSE':>10} {'SSIM':>8} {'Equal':>6}")
        print("-" * 110)
        for r in results:
            print(
                f"{Path(r['file_a']).name:<40} {Path(r['file_b']).name:<40}"
                f" {r['mse']:>10.2f} {r['ssim']:>8.4f} {str(r['equal']):>6}"
            )

    def insert(
        self,
        images: Iterable[str],
        output: str,
        width: int = config.IMAGE_SIZE_X,
        height: int = config.IMAGE_SIZE_Y,
        auto_title: bool = False,
    ) -> None:
        """
        Insert images into a new DOCX document.

        Args:
            images: List of image file paths
            output: Output .docx path
            width: Image width in inches (default: 5.0)
            height: Image height in inches (default: 7.0)
            auto_title: Use the image filename stem as a heading
        """
        doc: Document = _docx.Document()
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


def main() -> None:
    """Entry point for the CLI."""
    fire.Fire(docuopsCLI)


if __name__ == "__main__":
    main()
