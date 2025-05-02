import logging
from typing import List

from pysubstitutor.handlers.format_handler import FormatHandler
from pysubstitutor.models.text_substitution import TextSubstitution

from .converter_interface import ConverterInterface


class FileConverter(ConverterInterface):
    """
    A file converter that uses a read handler for reading plist files
    and an export handler for exporting to Gboard dictionary files.
    """

    def __init__(
        self, read_handler: FormatHandler, export_handler: FormatHandler, logger=None
    ):
        """
        Initializes the converter with a read handler and an export handler.
        :param read_handler: Handler for reading input files (e.g., PlistHandler).
        :param export_handler: Handler for exporting output files (e.g., GboardHandler).
        :param logger: Optional logger instance.
        """
        self.read_handler = read_handler
        self.export_handler = export_handler
        self.entries: List[TextSubstitution] = []
        self.logger = logger or logging.getLogger(__name__)

    def read(self, input: str):
        """
        Reads data from the input file using the read handler.
        :param input: Path to the input file.
        :raises ValueError: If reading the file fails.
        """
        self.logger.info(f"Reading input file: {input}")
        try:
            with open(input, "rb") as input_stream:
                self.entries = self.read_handler.read(input_stream)
            self.logger.info(f"Loaded {len(self.entries)} entries from the input file.")
        except Exception as e:
            self.logger.error(f"Failed to read the input file: {e}")
            raise ValueError(f"Failed to read the input file: {e}")

    def export(self, output: str):
        """
        Exports data to the output file using the export handler.
        :param output: Path to the output file.
        :raises ValueError: If exporting the file fails.
        """
        self.logger.info(f"Exporting data to output file: {output}")
        try:
            with open(output, "w", encoding="utf-8") as output_stream:
                self.export_handler.export(output_stream, self.entries)
            self.logger.info(
                f"Exported {len(self.entries)} entries to the output file."
            )
        except Exception as e:
            self.logger.error(f"Failed to export the file: {e}")
            raise ValueError(f"Failed to export the file: {e}")
