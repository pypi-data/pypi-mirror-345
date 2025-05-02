### Pysubstitutor

# Description

`pysubstitutor` is a Python package designed to convert text substitution files between different formats. It supports reading and exporting text substitutions in formats such as Apple `.plist`, Gboard `.gboard`, and Markdown `.md`. The package is modular, extensible, and includes utilities for handling file conversions and zipping output files.

This tool is particularly useful for managing and migrating text substitution dictionaries across platforms or exporting them for documentation purposes.

### Features

- **Plist to Gboard Conversion**: Convert Apple `.plist` files to Gboard `.gboard` format.
- **Markdown Export**: Export text substitutions to a Markdown table for easy documentation.
- **Extensible Handlers**: Easily add support for new file formats by implementing custom handlers.
- **Command-Line Interface**: Run the tool via the command line with customizable input and output paths.
- **Dockerized Environment**: Run the application and tests in a Docker container for consistency.

### Installation

#### Using Conda

1. Create the conda environment:
   ```bash
   conda env create -f environment.yml
   ```

2. Activate the environment:
   ```bash
   conda activate pysubstitutor
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

#### Using Docker

1. Build the Docker image:
   ```bash
   make build
   ```

2. Verify the Docker image is built:
   ```bash
   docker images
   ```

### Testing

Run the tests inside the Conda environment:
```bash
pytest tests
```

Or, run the tests inside the Docker container:
```bash
make test
```

### Execution

Run the application inside the Docker container:
```bash
make run
```

Replace the `--input` and `--output` arguments in the `Makefile` if you need to customize the input and output file paths.
