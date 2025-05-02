import logging
import zipfile


def zip_file(output_file: str, zip_path: str, logger: logging.Logger):
    """
    Zips the specified output file to the given zip path.

    :param output_file: Path to the file to be zipped.
    :param zip_path: Path to the zip file to create.
    :param logger: Logger instance for logging messages.
    """
    try:
        with zipfile.ZipFile(zip_path, "w") as zipf:
            zipf.write(output_file, arcname=output_file.split("/")[-1])
        logger.info(f"Output file zipped successfully to {zip_path}")
    except Exception as e:
        logger.error(f"Failed to zip the output file: {e}")
        raise ValueError(f"Failed to zip the output file: {e}")
