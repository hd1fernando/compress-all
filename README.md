# All Compressor

A CLI tool for compressing and decompressing files in directories using Brotli compression.

## Installation

```bash
pip install brotli
```

Or use the included virtual environment:

```bash
source venv/bin/activate
```

## Usage

```bash
python src/main.py <directory> [options]
```

### Options

- `-c, --compress`     Compress files (default)
- `-d, --decompress`   Decompress .br files
- `-v, --verbose`      Enable verbose output
- `-h, --help`         Show help message

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

## How it works

- Only files in the specified directory are processed (subdirectories are ignored)
- Compressed files get a `.br` extension added
- Already compressed files (.br) are skipped during compression
- Only `.br` files are processed during decompression
- Original files are preserved after compression

---

## Created with AI

This project was developed using artificial intelligence.

### Tools and LLMs Used

| Tool/LLM | Purpose |
|----------|---------|
| OpenCode | AI coding assistant |
| Claude (Anthropic) | Code generation and review |
