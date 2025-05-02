from abc import ABC, abstractmethod


class ConverterInterface(ABC):
    """
    An interface for file conversion operations.
    """

    @abstractmethod
    def read(self, input_stream):
        """
        Reads data from a file-like input stream.
        :param input_stream: File-like object for the input data.
        """
        pass

    @abstractmethod
    def export(self, output_stream):
        """
        Exports data to a file-like output stream.
        :param output_stream: File-like object for the output data.
        """
        pass
