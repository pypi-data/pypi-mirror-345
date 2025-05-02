from pysubstitutor.handlers.format_handler import FormatHandler
from pysubstitutor.handlers.gboard_handler import GboardHandler
from pysubstitutor.handlers.markdown_handler import MarkdownHandler
from pysubstitutor.handlers.plist_handler import PlistHandler


def get_handler_by_extension(file_path: str, mode: str = "read") -> FormatHandler:
    """
    Returns the appropriate handler based on the file extension.
    :param file_path: Path to the file.
    :param mode: Mode of operation, either "read" or "export".
    :return: An instance of the appropriate FormatHandler.
    :raises ValueError: If the file extension is unsupported.
    """
    extension_to_handler = {
        ".gboard": GboardHandler,
        ".md": MarkdownHandler,
        ".plist": PlistHandler,
        ".txt": GboardHandler,
    }

    # Extract the file extension
    file_extension = file_path.split(".")[-1].lower()
    file_extension = f".{file_extension}"

    if file_extension not in extension_to_handler:
        raise ValueError(f"Unsupported file extension: {file_extension}")

    handler_class = extension_to_handler[file_extension]

    if mode == "read":
        return handler_class()
    elif mode == "export":
        return handler_class()
    else:
        raise ValueError(f"Unsupported mode: {mode}")
