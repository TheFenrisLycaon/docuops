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

#### `compress`

Compress PDFs using Ghostscript and convert them to images, then recompress the images for optimal file size reduction.

**Parameters:**

- `--source`: Directory containing source PDFs
- `--pdf-out`: Output directory for compressed PDFs
- `--img-conversion`: Output directory for converted images
- `--img-compression`: Output directory for recompressed images
- `--quality`: Quality level for compression (1-5, lower = smaller file size)

**Basic example:**

```bash
python -m docuops compress --source ./Source --pdf-out ./PDFCompression --img-conversion ./ImageConversion --img-compression ./ImageCompression --quality 3
```

**High-quality compression (for archival):**

```bash
python -m docuops compress --source ./pdfs --pdf-out ./compressed --img-conversion ./temp_images --img-compression ./final_images --quality 5
```

**Aggressive compression (for web distribution):**

```bash
python -m docuops compress --source ./pdfs --pdf-out ./web_pdfs --img-conversion ./temp --img-compression ./web_images --quality 1
```

---

#### `pdf2docx`

Convert PDFs and images into DOCX documents using multiple modes for different use cases.

**Modes:**

- `statement`: Convert each PDF in a directory into its own separate DOCX file
- `certificates`: Merge all PDFs in a directory into one combined DOCX
- `license`: Embed all images from a directory into a single DOCX
- `work`: Interleave work and company PDFs into one DOCX document
- `conv`: Convert a single PDF into numbered JPEGs

**Convert individual PDFs to separate DOCX files:**

```bash
python -m docuops pdf2docx statement --input-dir ./pdfs --output-dir ./docx
```

**Merge multiple PDFs into one DOCX:**

```bash
python -m docuops pdf2docx certificates --input-dir ./certificates_pdf --output-dir ./output
```

**Embed image gallery into DOCX:**

```bash
python -m docuops pdf2docx license --input-dir ./images --output-dir ./output
```

**Interleave work and company documents:**

```bash
python -m docuops pdf2docx work --input-dir ./mixed_documents --output-dir ./organized
```

**Convert single PDF to numbered JPEG sequence:**

```bash
python -m docuops pdf2docx conv --input path/to/document.pdf --output-dir ./pages
```

**With Poppler path specified (if not on PATH):**

```bash
python -m docuops pdf2docx statement --input-dir ./pdfs --output-dir ./docx --poppler-path "C:\Program Files\poppler\Library\bin"
```

---

#### `replace`

Replace an embedded image within an existing DOCX file. Useful for updating diagrams, logos, or photos in documents.

**Parameters:**

- `--doc`: Path to the DOCX file
- `--img-num`: Index of the image to replace (1-based)
- `--new-img`: Path to the new image file
- `--cache-dir`: Temporary directory for processing
- `--output-dir`: Directory for the modified DOCX

**Basic replacement:**

```bash
python -m docuops replace --doc path/to/file.docx --img-num 1 --new-img path/to/new.jpg --cache-dir .cache --output-dir data
```

**Replace second image with a PNG:**

```bash
python -m docuops replace --doc report.docx --img-num 2 --new-img updated_chart.png --cache-dir ./temp --output-dir ./output
```

**Replace logo (first image) across multiple documents:**

```bash
python -m docuops replace --doc document1.docx --img-num 1 --new-img new_logo.png --cache-dir .cache --output-dir ./updated
```

---

#### `compare`

Compare two image directories using multiple similarity metrics: MSE (Mean Squared Error), SSIM (Structural Similarity), and exact equality.

**Parameters:**

- `dir_a`: First directory containing images
- `dir_b`: Second directory containing images

**Basic comparison:**

```bash
python -m docuops compare ./dir_a ./dir_b
```

**Compare before/after image optimization:**

```bash
python -m docuops compare ./original_images ./compressed_images
```

**Compare template versions:**

```bash
python -m docuops compare ./design_v1 ./design_v2
```

---

#### `insert`

Insert images into a new DOCX document with automatic layout and formatting.

**Parameters:**

- `--images`: List of image files to insert
- `--output`: Output DOCX filename
- `--width`: Page width in inches
- `--height`: Page height in inches
- `--auto-title`: Automatically add filenames as titles (optional)

**Insert multiple images with auto-titling:**

```bash
python -m docuops insert --images a.jpg b.jpg c.png --output output.docx --width 5.0 --height 7.0 --auto-title
```

**Create photo gallery (standard letter size):**

```bash
python -m docuops insert --images photo1.jpg photo2.jpg photo3.jpg --output gallery.docx --width 8.5 --height 11.0
```

**Create image book (custom dimensions):**

```bash
python -m docuops insert --images page1.png page2.png page3.png --output book.docx --width 6.0 --height 9.0 --auto-title
```

**Insert single image:**

```bash
python -m docuops insert --images diagram.png --output diagram_doc.docx --width 8.5 --height 11.0
```

---

#### `table`

Render data from Excel spreadsheets into DOCX template tables using `docxtpl`. Perfect for mail merge and bulk document generation.

**Parameters:**

- `--excel`: Path to Excel file containing data
- `--template`: Path to DOCX template file
- `--output`: Output DOCX filename

**Basic table population:**

```bash
python -m docuops table --excel data.xlsx --template template.docx --output output.docx
```

**Generate reports from data:**

```bash
python -m docuops table --excel quarterly_data.xlsx --template report_template.docx --output Q1_Report.docx
```

**Create batch invoices:**

```bash
python -m docuops table --excel invoice_data.xlsx --template invoice_template.docx --output invoices.docx
```

**Mail merge letters:**

```bash
python -m docuops table --excel recipients.xlsx --template letter_template.docx --output merged_letters.docx
```

## Testing

Install test dependencies:

```bash
pip install pytest
```

Run the test suite:

```bash
python -m docuops test
```

Or run pytest directly:

```bash
pytest tests/
```

## Notes

- The package lazily imports submodules, so only the dependencies required for a specific command need to be installed.
- For `pdf2docx` commands that use PDFs, make sure Poppler is installed and available on PATH, or pass `--poppler-path`.
- `pdf_compress` requires Ghostscript available on PATH.
