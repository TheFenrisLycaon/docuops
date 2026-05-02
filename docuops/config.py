from enum import StrEnum
from typing import List, Optional


# Default configuration values for docuops.
# These can be overridden by CLI arguments or environment variables.
class Quality_Preset(StrEnum):
    DEFAULT = "/default"
    PREPRESS = "/prepress"
    PRINTER = "/printer"
    EBOOK = "/ebook"
    SCREEN = "/screen"


# Default paths and settings for the CLI.
# Users can override these by passing arguments to the CLI commands or by setting environment variables.
SOURCE_PATH = "~/source_pdfs"
OUTPUT_PATH = "~/Downloads/docuops"
TEMP_PATH = "~/docuops_tmp"

# Subdirectories within TEMP_PATH for intermediate files during PDF compression.
CONVERSION_PATH = f"~/{TEMP_PATH}/conversion"
COMPRESSION_PATH = f"~/{TEMP_PATH}/compression"

# Default size of images used in the DOCX output, in inches.
# This is a good size for A4 pages at 150 DPI.
IMAGE_SIZE_X = 5
IMAGE_SIZE_Y = 7


# Set to the directory containing Poppler binaries if they are not on PATH.
# Example (Windows): POPPLER_PATH = r"C:\tools\poppler\bin"
POPPLER_PATH: Optional[str] = None

# Width (in inches) used when inserting images into Word documents.
IMAGE_WIDTH_INCHES: float = 5.0
