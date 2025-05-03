# -*- coding: utf-8 -*-
import sys
from enum import Enum

from docling.datamodel.pipeline_options import (
    EasyOcrOptions,
    OcrMacOptions,
    RapidOcrOptions,
    TesseractCliOcrOptions,
    TesseractOcrOptions,
)
from docling.datamodel.settings import (
    DEFAULT_PAGE_RANGE,
    PageRange,
)
from pydantic import BaseModel
from pydantic.dataclasses import dataclass

format_mapping: dict = {
    """A mapping dictionary that associates save formats with file extensions"""
    "save_as_doctags": ".doctags",
    "save_as_html": ".html",
    "save_as_json": ".json",
    "save_as_markdown": ".md",
    "save_as_yaml": ".yaml",
}

ocr_classes = {
    "easyocr": EasyOcrOptions,
    "ocrmac": OcrMacOptions,
    "rapidocr": RapidOcrOptions,
    "tesserocr": TesseractOcrOptions,
    "tesseract": TesseractCliOcrOptions,
}


class ConvertConfig(BaseModel):
    """
    Configuration model for controlling the document conversion process.

    This class holds settings related to headers, error handling, page ranges, file sizes, and other options
    that control the conversion process for documents. It is used to define the conversion parameters when
    invoking the document converter.

    Args:
        headers (dict[str, str] | None): Optional dictionary of headers to include in the conversion request.
        raises_on_error (bool): Flag to determine whether errors during conversion should raise exceptions.
            Default is True.
        max_num_pages (int): The maximum number of pages to convert. Default is sys.maxsize (no limit).
        max_file_size (int): The maximum file size for documents to be processed. Default is sys.maxsize (no limit).
        page_range (PageRange): The range of pages to convert. Default is the predefined `DEFAULT_PAGE_RANGE`.
    """

    headers: dict[str, str] | None = None
    raises_on_error: bool = True
    max_num_pages: int = sys.maxsize
    max_file_size: int = sys.maxsize
    page_range: PageRange = DEFAULT_PAGE_RANGE


@dataclass(frozen=True)
class DoclingKeys:
    """A dataclass that holds constant keys related to the 'docling' configuration."""

    docling: str = "docling"
    documents: str = "documents"
    filename: str = "filename"
    image_mode: str = "image_mode"


class ExporFormat(str, Enum):
    """Enum representing the different export formats available for exporting data."""

    EXPORT_TO_DICT = "export_to_dict"
    EXPORT_TO_DOCTAGS = "export_to_doctags"
    EXPORT_TO_ELEMENT_TREE = "export_to_element_tree"
    EXPORT_TO_HTML = "export_to_html"
    EXPORT_TO_MARKDOWN = "export_to_markdown"
    EXPORT_TO_TEXT = "export_to_text"


class SaveFormat(str, Enum):
    """Enum representing the different save formats available for saving data."""

    SAVE_AS_DOCTAGS = "save_as_doctags"
    SAVE_AS_HTML = "save_as_html"
    SAVE_AS_JSON = "save_as_json"
    SAVE_AS_MARKDOWN = "save_as_markdown"
    SAVE_AS_YAML = "save_as_yaml"
