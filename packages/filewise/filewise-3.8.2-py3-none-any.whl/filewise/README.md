# filewise

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/filewise.svg)](https://pypi.org/project/filewise/)

**filewise** is a Python toolkit designed to simplify file operations and management. It provides a comprehensive set of tools for file handling, directory management, and file system operations, making it easier to work with files in Python applications.

## Features

- **File Operations**:
  - Advanced file reading and writing
  - File type detection and handling
  - File compression and decompression
- **Directory Management**:
  - Directory creation and cleanup
  - File system navigation
  - Path manipulation utilities
- **File System Tools**:
  - File system monitoring
  - File pattern matching
  - File metadata handling
- **Data Processing**:
  - File-based data processing
  - Batch file operations
  - File format conversion

## Installation

### Prerequisites

Before installing, please ensure the following dependencies are available on your system:

- **Required Third-Party Libraries**:

  ```bash
  pip install PyYAML pandas numpy
  ```

  Or via Anaconda (recommended channel: `conda-forge`):

  ```bash
  conda install -c conda-forge pyyaml pandas numpy
  ```

### Installation (from PyPI)

Install the package using pip:

```bash
pip install filewise
```

### Development Installation

For development purposes, you can install the package in editable mode:

```bash
git clone https://github.com/yourusername/filewise.git
cd filewise
pip install -e .
```

## Usage

### Basic Example

```python
from filewise.operations import FileHandler
from filewise.directory import DirectoryManager

# Create a file handler
handler = FileHandler('data.txt')
handler.write('Hello, World!')

# Manage directories
manager = DirectoryManager('my_project')
manager.create_structure(['data', 'output', 'logs'])
```

### Advanced Example

```python
from filewise.filesystem import FileSystem
from filewise.processing import BatchProcessor

# Monitor file system changes
fs = FileSystem('watch_directory')
fs.watch_for_changes(callback=process_changes)

# Process files in batch
processor = BatchProcessor('input_directory')
processor.process_files(
    pattern='*.csv',
    processor=convert_to_parquet
)
```

## Project Structure

The package is organised into several sub-packages:

```text
filewise/
├── operations/
│   ├── file_handler.py
│   └── file_utils.py
├── directory/
│   ├── manager.py
│   └── path_utils.py
├── filesystem/
│   ├── monitor.py
│   └── matcher.py
└── processing/
    ├── batch.py
    └── converter.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Python file system community
- Open-source contributors
- Python ecosystem maintainers

## Contact

For any questions or suggestions, please open an issue on GitHub or contact the maintainers.
