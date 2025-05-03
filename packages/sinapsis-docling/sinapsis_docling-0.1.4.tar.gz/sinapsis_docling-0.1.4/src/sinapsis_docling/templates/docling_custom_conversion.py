# -*- coding: utf-8 -*-
from typing import Any, Literal

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    AcceleratorOptions,
    EasyOcrOptions,
    OcrOptions,
    PdfPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from pydantic import Field

from sinapsis_docling.helpers.docling_config import (
    ocr_classes,
)
from sinapsis_docling.templates.docling_simple_conversion import DoclingSimpleConversion


class DoclingCustomConversion(DoclingSimpleConversion):
    """
    Template for advanced document conversions using the Docling framework.

    This template extends the basic document conversion process by adding advanced configuration options, such as
    OCR settings and pipeline processing. It manages the entire document conversion lifecycle: initializing conversion
    settings, processing the source document, and exporting the result in the desired format. The class includes
    methods to configure OCR options, update processing pipeline settings, and initialize the document converter.

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: DoclingCustomConversion
      class_name: DoclingCustomConversion
      template_input: InputTemplate
      attributes:
        convert_options:
          headers: null
          raises_on_error: true
          max_num_pages: 90
          max_file_size: 1000
          page_range:
          - 1
          - 90
        export_format:
        - export_to_markdown
        image_mode:
        - placeholder
        output_dir: /path/to/sinapsis/cache/dir
        save_in_container: true
        save_locally: false
        save_format:
        - save_as_markdown
        path_to_doc: document.pdf
        accelerator_options:
          num_threads: 4
          device: auto
          cuda_use_flash_attention2: false
        ocr_engine: easyocr
        ocr_options:
        pipeline_options:
          create_legacy_output: true
          document_timeout: null
          accelerator_options:
            num_threads: 4
            device: auto
            cuda_use_flash_attention2: false
          enable_remote_services: false
          allow_external_plugins: false
          artifacts_path: null
          images_scale: 1.0
          generate_page_images: false
          generate_picture_images: false
          do_table_structure: true
          do_ocr: true
          do_code_enrichment: false
          do_formula_enrichment: false
          do_picture_classification: false
          do_picture_description: false
          force_backend_text: false
          table_structure_options:
            do_cell_matching: true
            mode:
            - accurate
          ocr_options:
            lang: '`replace_me:typing.List[str]`'
            force_full_page_ocr: false
            bitmap_area_threshold: 0.05
          picture_description_options:
            batch_size: 8
            scale: 2
            picture_area_threshold: 0.05
          generate_table_images: false
          generate_parsed_pages: false
    """

    class AttributesBaseModel(DoclingSimpleConversion.AttributesBaseModel):
        """
        Attributes for configuring document conversion and export options.

        Args:
            accelerator_options (AcceleratorOptions): Options for the accelerator, including `num_threads`, `device`,
                `cuda_use_flash_attention2`. Default: an empty dictionary.
            ocr_engine (Literal["easyocr", "ocrmac", "rapidocr", "tesserocr", "tesseract"]): OCR engine to use.
                Default: "easyocr".
            ocr_options (dict[str, Any]): OCR engine configuration options. Default: an empty dictionary. Check the
            pipeline_options (PdfPipelineOptions): Conversion pipeline options. Default: an empty dictionary.

            For detailed documentation on setting accelerator, OCR, and pipeline options, refer to the Docling
            reference: https://docling-project.github.io/docling/reference/pipeline_options/
        """

        accelerator_options: AcceleratorOptions = Field(default_factory=dict)  # type: ignore[arg-type]
        ocr_engine: Literal["easyocr", "ocrmac", "rapidocr", "tesserocr", "tesseract"] = "easyocr"
        ocr_options: dict[str, Any] = Field(default_factory=dict)
        pipeline_options: PdfPipelineOptions = Field(default_factory=dict)  # type: ignore[arg-type]

    def init_ocr_options(self) -> OcrOptions:
        """
        Initialize the OCR options based on the selected OCR engine and provided configuration.

        This method retrieves the OCR engine specified in `ocr_engine` and uses the options in `ocr_options`
        to configure it. If no options are provided, the default settings for the OCR engine are applied.

        Returns:
            OcrOptions: The configured OCR options based on the selected engine.
        """
        if self.attributes.ocr_engine:
            ocr_engine = ocr_classes.get(self.attributes.ocr_engine)
            if ocr_engine is not None:
                return ocr_engine(**self.attributes.ocr_options)
            else:
                self.logger.error(f"Unknown OCR engine: {self.attributes.ocr_engine}. Defaulting to EasyOCR")
        return EasyOcrOptions()

    def update_pipeline_options(self) -> None:
        """
        Update the pipeline options for document conversion, including OCR and accelerator settings.

        This method ensures that the pipeline options are properly configured, including OCR options,
        accelerator settings, and any other conversion-related settings.
        """
        ocr_options = self.init_ocr_options()
        if not self.attributes.pipeline_options:
            self.attributes.pipeline_options = PdfPipelineOptions()
        if ocr_options:
            self.attributes.pipeline_options.ocr_options = ocr_options
        if self.attributes.accelerator_options:
            self.attributes.pipeline_options.accelerator_options = self.attributes.accelerator_options

    def initialize_converter(self) -> DocumentConverter:
        """
        Initialize and configure the document converter based on the pipeline options.

        This method ensures that the document converter is properly initialized with the required pipeline
        options, including OCR settings and accelerator configurations.

        Returns:
            DocumentConverter: An instance of the configured document converter.
        """
        self.update_pipeline_options()
        return DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=self.attributes.pipeline_options)}
        )
