# -*- coding: utf-8 -*-
from pathlib import Path

from docling.datamodel.base_models import ConversionStatus
from docling.datamodel.document import ConversionResult
from docling.document_converter import DocumentConverter
from docling_core.types.doc import ImageRefMode
from pydantic import Field
from sinapsis_core.data_containers.data_packet import DataContainer
from sinapsis_core.template_base import Template
from sinapsis_core.template_base.base_models import (TemplateAttributes,
    TemplateAttributeType, UIPropertiesMetadata, OutputTypes
)
from sinapsis_core.utils.env_var_keys import SINAPSIS_CACHE_DIR

from sinapsis_docling.helpers.docling_config import (
    ConvertConfig,
    DoclingKeys,
    ExporFormat,
    SaveFormat,
)
from sinapsis_docling.helpers.docling_utils import (
    export_doc,
    initialize_output_dir,
    save_doc_locally,
)


class DoclingSimpleConversion(Template):
    """
    Template for simple document conversions using the Docling framework.

    This template handles the document conversion process by initializing the conversion settings, processing
    the source document, and exporting the result in the desired format. It includes methods to configure the
    conversion, initialize the output directory, and save the converted document to a specified location.

    Usage example:

    agent:
      name: my_test_agent
    templates:
    - template_name: InputTemplate
      class_name: InputTemplate
      attributes: {}
    - template_name: DoclingSimpleConversion
      class_name: DoclingSimpleConversion
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
        path_to_doc: 'input template'

        """

    class AttributesBaseModel(TemplateAttributes):
        """
        Attributes for configuring document conversion and export options.

        Args:
            convert_options (ConvertConfig): Configuration for document conversion, such as error handling,
                page range, and file size limits. Default: An empty dictionary.
            export_format (ExportFormat | None): Format for document export. Options: 'export_to_dict',
                'export_to_doctags', 'export_to_element_tree', 'export_to_html', 'export_to_markdown',
                'export_to_text'. Default: 'export_to_markdown'.
            image_mode (ImageRefMode | None): Image handling mode. Options: 'placeholder', 'embedded', 'referenced'.
                Default: 'placeholder'.
            output_dir (str | Path): Directory for saving the converted document. Default:
                `SINAPSIS_CACHE_DIR/docling/documents`.
            save_in_container (bool): Whether to store the converted document in the container. Default: True.
            save_locally (bool): Whether to save the converted document locally. Default: False.
            save_format (SaveFormat | None): Format for saving the document. Options: 'save_as_doctags', 'save_as_html',
                'save_as_json', 'save_as_markdown', 'save_as_yaml'. Default: 'save_as_markdown'.
            path_to_doc (str | list[str]): The source document(s) to convert. This can be a file path, a URL, or a list of
                file paths or URLs.
        """

        convert_options: ConvertConfig = Field(default_factory=dict)  # type: ignore[arg-type]
        export_format: ExporFormat | None = ExporFormat.EXPORT_TO_MARKDOWN
        image_mode: ImageRefMode | None = ImageRefMode.PLACEHOLDER
        output_dir: str | Path = Path(f"{SINAPSIS_CACHE_DIR}/{DoclingKeys.docling}/{DoclingKeys.documents}")
        save_in_container: bool = True
        save_locally: bool = False
        save_format: SaveFormat | None = SaveFormat.SAVE_AS_MARKDOWN
        path_to_doc: str | list[str]
    UIProperties = UIPropertiesMetadata(category="Docling", output_type=OutputTypes.MULTIMODAL)

    def __init__(self, attributes: TemplateAttributeType) -> None:
        """Initializes the DoclingSimpleConversion template with the provided attributes."""
        super().__init__(attributes)
        self.converter = self.initialize_converter()
        if self.attributes.save_locally:
            self.attributes.output_dir = initialize_output_dir(self.attributes.output_dir)

    @staticmethod
    def initialize_converter() -> DocumentConverter:
        """
        Initialize the document converter based on the provided configuration.

        Returns:
            DocumentConverter: An instance of the document converter used for processing the source document.
        """
        return DocumentConverter()

    def process_conversion_results(
        self,
        conversion_results: list[ConversionResult],
        container: DataContainer,
    ) -> None:
        """
        Process the conversion results, saving them either locally or to the container.

        This method handles saving the converted documents based on the configured settings, and exports them
        to the container if necessary. It also logs the success or failure of the conversions.

        Args:
            conversion_results (list[ConversionResult]): A list of conversion results to process.
            container (DataContainer): The container to store the converted documents if configured.
        """
        exported_docs = []
        success_count = 0

        for conv_result in conversion_results:
            if conv_result.status == ConversionStatus.SUCCESS:
                success_count += 1

                if self.attributes.save_locally:
                    save_doc_locally(
                        conv_result, self.attributes.output_dir, self.attributes.save_format, self.attributes.image_mode
                    )

                if self.attributes.save_in_container:
                    exported_doc = export_doc(conv_result.document, self.attributes.export_format)
                    exported_docs.append(exported_doc)

        if success_count > 0:
            self.logger.debug(f"Successfully converted {success_count} documents.")
        else:
            self.logger.error("No documents were successfully converted.")

        if exported_docs:
            self.logger.debug("Saved converted documents in the container's generic data")
            self._set_generic_data(container, exported_docs)

    def convert_docs(self, container: DataContainer) -> None:
        """
        Convert the source documents and store the results either in the container or save them locally.

        This method initiates the document conversion for each source, processes the results, and handles
        saving and exporting as required.

        Args:
            container (DataContainer): The container where converted document data will be stored if configured.
        """
        if isinstance(self.attributes.path_to_doc, str):
            self.attributes.path_to_doc = [self.attributes.path_to_doc]

        results = self.converter.convert_all(self.attributes.path_to_doc, **self.attributes.convert_options)
        self.process_conversion_results(results, container)

    def execute(self, container: DataContainer) -> DataContainer:
        """
        Execute the document conversion and return the updated container.

        Args:
            container (DataContainer): The container where the converted document data will be stored.

        Returns:
            DataContainer: The updated container with the converted data.
        """
        self.convert_docs(container)
        return container
