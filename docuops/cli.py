"""
cli.py — Unified Command-Line Interface for docuops
====================================================
Run as ``python -m docuops <command> [options]``.

Commands
--------
    compress   — 3-stage PDF compression pipeline
    pdf2docx   — Convert PDFs to DOCX (statement / certificates / license / work)
    replace    — Replace an embedded image inside a .docx file
    compare    — Compare two image directories (MSE, SSIM, equality)
    insert     — Insert images into a new DOCX document
    table      — Populate a DOCX table from an Excel file
"""

import argparse
from pathlib import Path

# ---------------------------------------------------------------------------
# Sub-command handlers
# ---------------------------------------------------------------------------


def _cmd_compress(args: argparse.Namespace) -> None:
    from docuops.pdf_compress import run_pipeline

    run_pipeline(
        source_dir=args.source,
        pdf_out_dir=args.pdf_out,
        img_conversion_dir=args.img_conversion,
        img_compression_dir=args.img_compression,
        quality=args.quality,
    )


def _cmd_pdf2docx(args: argparse.Namespace) -> None:
    from docuops.pdf_to_docx import (
        create_certificates,
        create_license,
        create_statement,
        create_work,
        pdf_to_jpegs,
    )

    poppler = args.poppler_path

    if args.subcommand == "statement":
        create_statement(args.input_dir, args.output_dir, poppler)
    elif args.subcommand == "certificates":
        create_certificates(args.input_dir, args.output_path, poppler)
    elif args.subcommand == "license":
        create_license(args.input_dir, args.output_path)
    elif args.subcommand == "work":
        create_work(args.work_dir, args.comp_dir, args.output_path, poppler)
    elif args.subcommand == "conv":
        pdf_to_jpegs(args.pdf_path, args.output_dir, poppler)


def _cmd_replace(args: argparse.Namespace) -> None:
    from docuops.docx_image_replace import replace_img

    output = replace_img(
        doc_path=args.doc,
        img_num=args.img_num,
        new_image_path=args.new_img,
        cache_dir=args.cache_dir,
        output_dir=args.output_dir,
    )
    print(f"Done — modified document saved to: {output}")


def _cmd_compare(args: argparse.Namespace) -> None:
    from docuops.image_compare import compare_directories

    results = compare_directories(args.dir_a, args.dir_b)
    print(f"{'File A':<40} {'File B':<40} {'MSE':>10} {'SSIM':>8} {'Equal':>6}")
    print("-" * 110)
    for r in results:
        print(
            f"{Path(r['file_a']).name:<40} {Path(r['file_b']).name:<40}"
            f" {r['mse']:>10.2f} {r['ssim']:>8.4f} {str(r['equal']):>6}"
        )


def _cmd_insert(args: argparse.Namespace) -> None:
    import docx as _docx

    from docuops.docx_insert_images import insert_image

    doc = _docx.Document()
    for img_path in args.images:
        insert_image(
            doc,
            img_path=img_path,
            size_x=args.width,
            size_y=args.height,
            title=Path(img_path).stem if args.auto_title else None,
        )
    doc.save(args.output)
    print(f"Done — saved to: {args.output}")


def _cmd_table(args: argparse.Namespace) -> None:
    from docuops.docx_table import populate_table

    populate_table(
        excel_path=args.excel,
        template_path=args.template,
        output_path=args.output,
    )


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

QUALITY_CHOICES = [0, 1, 2, 3, 4]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="docops",
        description="Document operations: PDF compression, DOCX generation, image tools.",
    )
    sub = parser.add_subparsers(dest="command", required=True, metavar="<command>")

    # ------------------------------------------------------------------ compress
    p_comp = sub.add_parser("compress", help="3-stage PDF compression pipeline.")
    p_comp.add_argument(
        "--source",
        type=Path,
        default=Path("./Source"),
        help="Source PDF directory (default: ./Source)",
    )
    p_comp.add_argument(
        "--pdf-out",
        type=Path,
        default=Path("./PDFCompression"),
        dest="pdf_out",
        help="Compressed PDF output dir (default: ./PDFCompression)",
    )
    p_comp.add_argument(
        "--img-conversion",
        type=Path,
        default=Path("./ImageConversion"),
        dest="img_conversion",
        help="PDF→image output dir (default: ./ImageConversion)",
    )
    p_comp.add_argument(
        "--img-compression",
        type=Path,
        default=Path("./ImageCompression"),
        dest="img_compression",
        help="Image compression output dir (default: ./ImageCompression)",
    )
    p_comp.add_argument(
        "--quality",
        type=int,
        default=3,
        choices=QUALITY_CHOICES,
        help="Ghostscript quality preset 0=default … 4=screen (default: 3)",
    )
    p_comp.set_defaults(func=_cmd_compress)

    # ------------------------------------------------------------------ pdf2docx
    p_p2d = sub.add_parser("pdf2docx", help="Convert PDFs to DOCX documents.")
    p_p2d.add_argument(
        "--poppler-path",
        default=None,
        dest="poppler_path",
        help="Path to Poppler bin directory if not on PATH.",
    )
    p2d_sub = p_p2d.add_subparsers(dest="subcommand", required=True, metavar="<mode>")

    ps = p2d_sub.add_parser("statement", help="Each PDF → its own .docx.")
    ps.add_argument("--input-dir", required=True, dest="input_dir")
    ps.add_argument("--output-dir", default=".", dest="output_dir")

    pc = p2d_sub.add_parser("certificates", help="All PDFs → one .docx.")
    pc.add_argument("--input-dir", required=True, dest="input_dir")
    pc.add_argument("--output", required=True, dest="output_path")

    pl = p2d_sub.add_parser("license", help="All images → one .docx.")
    pl.add_argument("--input-dir", required=True, dest="input_dir")
    pl.add_argument("--output", required=True, dest="output_path")

    pw = p2d_sub.add_parser("work", help="Interleave work + company PDFs → one .docx.")
    pw.add_argument("--work-dir", required=True, dest="work_dir")
    pw.add_argument("--comp-dir", required=True, dest="comp_dir")
    pw.add_argument("--output", required=True, dest="output_path")

    pv = p2d_sub.add_parser("conv", help="Convert a single PDF to numbered JPEGs.")
    pv.add_argument("--pdf", required=True, dest="pdf_path")
    pv.add_argument("--output-dir", required=True, dest="output_dir")

    p_p2d.set_defaults(func=_cmd_pdf2docx)

    # ------------------------------------------------------------------ replace
    p_rep = sub.add_parser("replace", help="Replace an embedded image in a .docx file.")
    p_rep.add_argument("--doc", required=True, help="Path to source .docx file.")
    p_rep.add_argument(
        "--img-num",
        type=int,
        required=True,
        dest="img_num",
        help="1-based index of the image to replace.",
    )
    p_rep.add_argument(
        "--new-img", required=True, dest="new_img", help="Path to the replacement JPEG."
    )
    p_rep.add_argument(
        "--cache-dir",
        default=".cache",
        dest="cache_dir",
        help="Temp extraction directory (default: .cache)",
    )
    p_rep.add_argument(
        "--output-dir",
        default="data",
        dest="output_dir",
        help="Output directory (default: data)",
    )
    p_rep.set_defaults(func=_cmd_replace)

    # ------------------------------------------------------------------ compare
    p_cmp = sub.add_parser("compare", help="Compare two image directories.")
    p_cmp.add_argument("dir_a", help="First image directory.")
    p_cmp.add_argument("dir_b", help="Second image directory.")
    p_cmp.set_defaults(func=_cmd_compare)

    # ------------------------------------------------------------------ insert
    p_ins = sub.add_parser("insert", help="Insert images into a new DOCX document.")
    p_ins.add_argument("--images", nargs="+", required=True, help="Image file paths.")
    p_ins.add_argument("--output", required=True, help="Output .docx path.")
    p_ins.add_argument(
        "--width", type=float, default=5.0, help="Image width in inches (default: 5.0)"
    )
    p_ins.add_argument(
        "--height",
        type=float,
        default=7.0,
        help="Image height in inches (default: 7.0)",
    )
    p_ins.add_argument(
        "--auto-title",
        action="store_true",
        dest="auto_title",
        help="Use the image filename stem as a heading.",
    )
    p_ins.set_defaults(func=_cmd_insert)

    # ------------------------------------------------------------------ table
    p_tbl = sub.add_parser("table", help="Populate a DOCX table from an Excel file.")
    p_tbl.add_argument("--excel", required=True, help="Path to source .xlsx file.")
    p_tbl.add_argument("--template", required=True, help="Path to .docx template file.")
    p_tbl.add_argument("--output", required=True, help="Output .docx path.")
    p_tbl.set_defaults(func=_cmd_table)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
