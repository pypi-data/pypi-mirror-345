import argparse
import logging

from pysubstitutor.converters.file_converter import FileConverter
from pysubstitutor.utils.handler_selector import get_handler_by_extension


def main():
    # Initialize logger
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    logger.info("Welcome to Text Substitutions!")

    # Parse arguments
    parser = argparse.ArgumentParser(description="Convert text substitutions files.")
    parser.add_argument(
        "-i", "--input", type=str, required=True, help="Path to the input file."
    )
    parser.add_argument(
        "-o", "--output", type=str, required=True, help="Path to the output file."
    )
    parser.add_argument(
        "--zip", type=str, required=False, help="Path to the zip file to create."
    )
    args = parser.parse_args()

    # Dynamically select handlers
    read_handler = get_handler_by_extension(args.input, mode="read")
    export_handler = get_handler_by_extension(args.output, mode="export")

    # Initialize and run the converter
    converter = FileConverter(
        read_handler=read_handler, export_handler=export_handler, logger=logger
    )
    converter.read(args.input)
    converter.export(args.output)

    # Optionally zip the output
    if args.zip:
        from pysubstitutor.utils.zip_util import zip_file

        zip_file(args.output, args.zip, logger)


if __name__ == "__main__":
    main()
