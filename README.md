# All Compressor

A CLI tool for compressing and decompressing files in directories using Brotli compression.

## Installation

### Using Virtual Environment (Recommended)

Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows
```

Install dependencies:
```bash
pip install brotli pytest
```

### Global Installation

```bash
pip install brotli pytest
```

### Using Install Script

Run the install script to install globally and use `compress-all` from anywhere:

```bash
./install.sh
```

Add to PATH if needed:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

To update after pulling new changes:
```bash
./install.sh
```

The script automatically detects previous installations and updates them.

## Usage

```bash
python src/main.py <directory> [options]
```

### Options

- `-c, --compress`          Compress files (default)
- `-d, --decompress`        Decompress .br files
- `-v, --verbose`           Enable verbose output
- `-r, --remove-original`  Remove original files after operation
- `-e, --exclude`           List of directories to exclude (space-separated)
- `-h, --help`             Show help message

### Examples

Compress all files in a directory:
```bash
python src/main.py ./myfiles -c
```

Decompress .br files:
```bash
python src/main.py ./myfiles -d
```

With verbose output:
```bash
python src/main.py ./myfiles -v
```

Compress and remove original files:
```bash
python src/main.py ./myfiles -c -r
```

Decompress and remove .br files:
```bash
python src/main.py ./myfiles -d -r
```

Exclude directories from compression/decompression:
```bash
python src/main.py ./myfiles -c -e temp cache
```

Exclude a subdirectory (relative path):
```bash
python src/main.py ./myfiles -c -e assets/images
```

## How it works

- Files in the specified directory and its subdirectories are processed recursively
- Compressed files get a `.br` extension added
- Already compressed files (.br) are skipped during compression
- Only `.br` files are processed during decompression
- Original files are preserved after compression
- Directories specified in `--exclude` are skipped entirely

## For Developers

### Running Tests

Run all tests:
```bash
pytest tests/ -v
```

Run a specific test file:
```bash
pytest tests/test_integration.py -v
```

---

## Created with AI

This project was developed using artificial intelligence.

### Tools and LLMs Used

| Tool/LLM | Purpose |
|----------|---------|
| OpenCode | AI coding assistant |
| Claude (Anthropic) | Code generation and review |
