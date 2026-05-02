# docuops

A small Python toolkit for PDF and DOCX operations.

Features:

- Compress PDFs and convert them into JPEGs
- Convert PDFs and images into DOCX documents
- Replace embedded images in a DOCX file
- Compare image directories using MSE, SSIM, and exact equality
- Insert images into a new DOCX document
- Populate a DOCX table from an Excel spreadsheet

## Installation

This repository does not include a packaged requirements file, but the main dependencies are:

```bash
pip install pillow python-docx pandas openpyxl docxtpl pdf2image opencv-python scikit-image matplotlib numpy tqdm
```

Additional system dependencies:

- Ghostscript (`gs`) for PDF compression
- Poppler (`pdftoppm`) for PDF-to-image conversion

## Usage

Run the CLI via:

```bash
python -m docuops <command> [options]
```

### Commands

`compress`

- Compress PDFs with Ghostscript, convert them to images, and recompress the images.
- Example:

  ```bash
  python -m docops compress --source ./Source --pdf-out ./PDFCompression --img-conversion ./ImageConversion --img-compression ./ImageCompression --quality 3
  ```

`pdf2docx`

- Convert PDFs and images into DOCX documents.
- Modes:
  - `statement`: Convert each PDF in a directory into its own DOCX.
  - `certificates`: Merge all PDFs in a directory into one DOCX.
  - `license`: Embed all images in a directory into a single DOCX.
  - `work`: Interleave work and company PDFs into one DOCX.
  - `conv`: Convert a single PDF into numbered JPEGs.

Example:

```bash
python -m docops pdf2docx statement --input-dir ./pdfs --output-dir ./docx
```

`replace`

- Replace an embedded image inside a DOCX file.

Example:

```bash
python -m docops replace --doc path/to/file.docx --img-num 1 --new-img path/to/new.jpg --cache-dir .cache --output-dir data
```

`compare`

- Compare two image directories.

Example:

```bash
python -m docops compare ./dir_a ./dir_b
```

`insert`

- Insert images into a new DOCX document.

Example:

```bash
python -m docops insert --images a.jpg b.jpg --output output.docx --width 5.0 --height 7.0 --auto-title
```

`table`

- Render Excel rows into a DOCX template table using `docxtpl`.

Example:

```bash
python -m docops table --excel data.xlsx --template template.docx --output output.docx
```

## Notes

- The package lazily imports submodules, so only the dependencies required for a specific command need to be installed.
- For `pdf2docx` commands that use PDFs, make sure Poppler is installed and available on PATH, or pass `--poppler-path`.
- `pdf_compress` requires Ghostscript available on PATH.
