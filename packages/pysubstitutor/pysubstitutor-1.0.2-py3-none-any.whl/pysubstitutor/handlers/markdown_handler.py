import re
from typing import List

from pysubstitutor.models.text_substitution import TextSubstitution

from .format_handler import FormatHandler


class MarkdownHandler(FormatHandler):
    def read(self, input_stream) -> List[TextSubstitution]:
        """
        Reads data from a markdown input stream.
        :param input_stream: File-like object for the input markdown data.
        :return: A list of TextSubstitution objects parsed from the markdown.
        """
        entries = []
        lines = input_stream.readlines()
        table_started = False

        for line in lines:
            line = line.strip()
            if not table_started:
                if re.match(r"^\|.*\|$", line):  # Detect table start
                    table_started = True
                continue

            if table_started:
                if re.match(r"^\|:.*\|$", line):  # Skip the header separator row
                    continue
                if re.match(r"^\|.*\|$", line):  # Table row
                    columns = [col.strip() for col in line.split("|")[1:-1]]
                    if len(columns) == 2:
                        shortcut, phrase = columns
                        entries.append(
                            TextSubstitution(shortcut=shortcut, phrase=phrase)
                        )

        return entries

    def export(self, output_stream, entries: List[TextSubstitution]):
        """
        Exports data to a markdown output stream.
        :param output_stream: File-like object for the output markdown data.
        :param entries: List of TextSubstitution objects to export.
        """
        output_stream.write("| Shortcut | Phrase |\n")
        output_stream.write("|:--|:--|\n")
        for entry in entries:
            output_stream.write(f"| {entry.shortcut} | {entry.phrase} |\n")
