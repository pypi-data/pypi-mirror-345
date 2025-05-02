from abc import ABC, abstractmethod
from typing import List

from pysubstitutor.models.text_substitution import TextSubstitution


class FormatHandler(ABC):
    """
    Base class for handling specific file formats.
    """

    @abstractmethod
    def read(self, input_stream) -> List[TextSubstitution]:
        """
        Reads data from a file-like input stream and returns a list of TextSubstitution objects.
        :param input_stream: File-like object for the input data.
        :return: A list of TextSubstitution objects.
        """
        pass

    @abstractmethod
    def export(self, output_stream, entries: List[TextSubstitution]):
        """
        Exports a list of TextSubstitution objects to a file-like output stream.
        :param output_stream: File-like object for the output data.
        :param entries: List of TextSubstitution objects to export.
        """
        pass
