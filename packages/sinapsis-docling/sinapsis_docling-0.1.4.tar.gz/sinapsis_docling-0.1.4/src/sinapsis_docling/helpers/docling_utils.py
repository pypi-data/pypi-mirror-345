# -*- coding: utf-8 -*-
from pathlib import Path

from docling.datamodel.document import ConversionResult
from docling_core.types.doc import ImageRefMode
from docling_core.types.doc.document import DoclingDocument
from sinapsis_core.utils.logging_utils import sinapsis_logger

from sinapsis_docling.helpers.docling_config import (
    DoclingKeys,
    ExporFormat,
    SaveFormat,
    format_mapping,
)


def initialize_output_dir(output_dir: str | Path) -> Path:
    """
    Initialize and return the output directory path.
    If the directory does not exist, it is created.

    Args:
        output_dir (str | Path): Path to the output directory.

    Returns:
        Path: The initialized Path object pointing to the output directory.
    """
    if isinstance(output_dir, str):
        output_dir = Path(output_dir)

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def save_doc_locally(
    conversion_result: ConversionResult, output_dir: Path, save_format: SaveFormat, image_mode: ImageRefMode
) -> None:
    """
    Save the converted document to the specified output directory.

    This method constructs the appropriate file path using the output directory and the conversion result's
    input file name, and then calls the appropriate method to save the document in the desired format.

    Args:
        conversion_result (ConversionResult): The result of the document conversion, which contains the converted
            document and metadata such as the input file and its status.
        output_dir (Path): The directory where the converted document should be saved.
        save_format (SaveFormat): The format in which the document should be saved.
        image_mode (ImageRefMode): Specifies how images in the document should be handled.
        conversion_result (ConversionResult): The result of the document conversion.
    """
    file_path = output_dir / f"{conversion_result.input.file.stem}{format_mapping[save_format]}"
    method = getattr(conversion_result.document, save_format)
    method_args = {
        DoclingKeys.filename: file_path,
        **({DoclingKeys.image_mode: image_mode} if save_format != SaveFormat.SAVE_AS_DOCTAGS else {}),
    }
    method(**method_args)
    sinapsis_logger.debug(f"Saved converted document as {file_path}")


def export_doc(conv_document: DoclingDocument, export_format: ExporFormat) -> str | dict:
    """
    Export the converted document's data in the specified format.

    This method selects the appropriate export method dynamically based on the `export_format` parameter
    and returns the converted document's data in the corresponding format.

    Args:
        conv_document (DoclingDocument): The document object that has been converted and is ready for export.
        export_format (ExporFormat): The export format to use.

    Returns:
        str | dict: The exported data in the chosen format. This could be a string or a dictionary.
    """
    try:
        method = getattr(conv_document, export_format)
        return method()
    except AttributeError:
        sinapsis_logger.error(f"Invalid export format: {export_format}")
        raise
