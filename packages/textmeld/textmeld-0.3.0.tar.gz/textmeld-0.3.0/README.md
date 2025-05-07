# TextMeld
A CLI tool to combine text files into one. Perfect for preparing LLM training data and prompt engineering.

## Features
- Combine multiple text files into a single file
- Automatic recognition of .gitignore patterns
- Automatic skipping of binary files and hidden files
- Option to limit output character count
- Flexible file exclusion patterns

## Installation
```bash
pip install textmeld
```

Using Poetry:
```bash
poetry add textmeld
```

## Usage
### Basic Usage
```bash
# Basic usage (outputs to stdout)
textmeld /path/to/your/directory
# Specify output file
textmeld /path/to/your/directory -o output.txt
# Limit maximum character count
textmeld /path/to/your/directory --max-chars 100000
```

### Available Options
```
usage: textmeld [-h] [-o OUTPUT] [-e EXCLUDE] [-m MAX_CHARS] directory
A tool to merge multiple text files into one file
positional arguments:
  directory             Target directory path
options:
  -h, --help            Show help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file path (if not specified, outputs to stdout)
  -e EXCLUDE, --exclude EXCLUDE
                        File patterns to exclude (can specify multiple)
  -m MAX_CHARS, --max-chars MAX_CHARS
                        Maximum character count for output
```

### Using Exclusion Patterns
To exclude specific files or directories:
```bash
# Exclude specific extensions
textmeld /path/to/your/directory -e "*.log" -e "*.tmp"
# Exclude specific directories
textmeld /path/to/your/directory -e "node_modules/" -e "venv/"
```

## Output Format
TextMeld's output consists of two parts:
1. **Directory Structure**: A tree view of the target directory
2. **Merged Content**: Combined contents of all text files (each file has a header)
```
Directory Structure:
====================
└── project/
    ├── README.md
    ├── main.py
    └── utils/
        └── helper.py
Merged Content:
====================
==========
File: project/README.md
==========
# Project Documentation
...
==========
File: project/main.py
==========
def main():
    print("Hello World")
...
==========
File: project/utils/helper.py
==========
def helper_function():
    return True
...
```

## Supported File Formats
TextMeld automatically detects text files. Generally supported file formats include:
- Markdown (.md)
- Text (.txt)
- YAML (.yaml, .yml)
- JSON (.json)
- Python (.py)
- JavaScript (.js)
- TypeScript (.ts)
- JSX/TSX (.jsx, .tsx)
- HTML (.html)
- CSS (.css)
- Other text-based file formats

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.