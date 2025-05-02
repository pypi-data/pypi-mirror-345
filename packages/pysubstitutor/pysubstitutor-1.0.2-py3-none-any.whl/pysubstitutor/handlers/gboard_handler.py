import csv
from typing import List

from pysubstitutor.models.text_substitution import TextSubstitution

from .format_handler import FormatHandler


class GboardHandler(FormatHandler):
    def read(self, input_stream) -> List[TextSubstitution]:
        """
        Reads data from a Gboard input stream.
        :param input_stream: File-like object for the input Gboard data.
        :return: A list of TextSubstitution objects parsed from the Gboard file.
        """
        entries = []
        for line in input_stream:
            line = line.strip()
            if line.startswith("#") or not line:  # Skip comments and empty lines
                continue
            parts = line.split("\t")
            if len(parts) >= 2:  # Ensure there are at least shortcut and phrase
                shortcut, phrase = parts[:2]
                entries.append(
                    TextSubstitution(shortcut=shortcut.strip(), phrase=phrase.strip())
                )
        return entries

    def export(self, output_stream, entries: List[TextSubstitution]):
        """
        Exports data to a Gboard output stream.
        :param output_stream: File-like object for the output Gboard data.
        :param entries: List of TextSubstitution objects to export.
        """
        output_stream.write("# Gboard Dictionary version:1\n\n")
        writer = csv.writer(output_stream, delimiter="\t")
        for entry in entries:
            writer.writerow([entry.shortcut.strip(), entry.phrase.strip(), "en-US"])
