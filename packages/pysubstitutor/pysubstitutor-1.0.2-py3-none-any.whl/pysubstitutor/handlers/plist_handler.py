import html
import plistlib
import re
from typing import List

from pysubstitutor.models.text_substitution import TextSubstitution

from .format_handler import FormatHandler


class PlistHandler(FormatHandler):
    def read(self, input_stream) -> List[TextSubstitution]:
        """
        Reads data from a plist input stream.
        :param input_stream: File-like object for the input plist data.
        :return: A list of TextSubstitution objects parsed from the plist.
        """
        plist_data = plistlib.load(input_stream)

        if isinstance(plist_data, list):
            raw_entries = plist_data
        elif isinstance(plist_data, dict):
            raw_entries = plist_data.get("NSUserDictionaryReplacementItems", [])
        else:
            raise ValueError("Unsupported plist format: Expected a dict or list.")

        return [
            TextSubstitution(
                shortcut=html.unescape(entry.get("shortcut", "").strip()),
                phrase=html.unescape(
                    re.sub(
                        r"\s+",
                        " ",
                        entry.get("phrase", "").replace("\n", "").strip(),
                    )
                ),
            )
            for entry in raw_entries
            if isinstance(entry, dict) and entry.get("shortcut") and entry.get("phrase")
        ]

    def export(self, output_stream, entries: List[TextSubstitution]):
        """
        Exports data to a plist output stream.
        :param output_stream: File-like object for the output plist data.
        :param entries: List of TextSubstitution objects to export.
        """
        raise NotImplementedError("Plist export is not implemented.")
