# <img src="assets/luxport-logo.png" alt="LuxPort Logo" width="400"/>

[![PyPI version](https://img.shields.io/pypi/v/luxport.svg)](https://pypi.org/project/luxport/)
[![PyPI downloads](https://img.shields.io/pypi/dm/luxport.svg)](https://pypi.org/project/luxport/)
[![GitHub stars](https://img.shields.io/github/stars/project-lux/luxport.svg)](https://github.com/project-lux/luxport/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/project-lux/luxport.svg)](https://github.com/project-lux/luxport/network)
[![GitHub issues](https://img.shields.io/github/issues/project-lux/luxport.svg)](https://github.com/project-lux/luxport/issues)
[![License](https://img.shields.io/github/license/project-lux/luxport.svg)](https://github.com/project-lux/luxport/blob/main/LICENSE)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/)

A utility for exporting IIIF manifest data to ZIP files. LuxPort is specifically designed to work with Yale Library's digital collections and other IIIF-compliant repositories.

## Features

- 📦 Downloads and exports IIIF manifest data to a ZIP file
- 🖼️ Downloads all images in both full size and thumbnail formats
- 🧩 Saves the original JSON manifest and a simplified version
- 📁 Organizes content in a structured, accessible format
- 💻 Provides both a command-line interface and a Python API
- ⚡ Supports parallel batch processing for multiple manifests

## Installation

### From PyPI

```bash
pip install luxport
```

### From Source

```bash
git clone https://github.com/project-lux/luxport.git
cd luxport
pip install -e .
```

## Quick Start

```python
from luxport import ManifestExporter

# Export a manifest from URL to ZIP file
exporter = ManifestExporter("https://collections.library.yale.edu/manifests/16867950")
exporter.export("yale_collection.zip")
```

## Usage

### Command Line Interface

```bash
# Export a manifest by URL
luxport export https://collections.library.yale.edu/manifests/16867950 --output-dir ./exported

# Specify a custom output filename
luxport export https://collections.library.yale.edu/manifests/16867950 --output-file yale_collection.zip

# Show help
luxport --help
luxport export --help
```

### Python API

```python
from luxport import ManifestExporter

# Export a manifest from URL to ZIP file
exporter = ManifestExporter("https://collections.library.yale.edu/manifests/16867950")
exporter.export("yale_collection.zip")

# Or export to a directory
exporter.export_to_directory("./exported")
```

## Output Structure

```
manifest_16867950.zip
├── manifest.json            # Original JSON manifest
├── manifest_simplified.json # Simplified JSON manifest 
├── images/
│   ├── full/                # Full-size images
│   │   ├── 16868023.jpg
│   │   ├── 16868024.jpg
│   │   └── ...
│   └── thumbnails/          # Thumbnail images
│       ├── 16868023.jpg
│       ├── 16868024.jpg
│       └── ...
├── metadata.txt             # Extracted metadata in readable format
└── info.txt                 # Summary information about the export
```

## Advanced Usage

### Batch Export

```python
from luxport import ManifestExporter
from concurrent.futures import ThreadPoolExecutor

# List of manifest URLs to export
manifests = [
    "https://collections.library.yale.edu/manifests/16867950",
    "https://collections.library.yale.edu/manifests/12345678"
]

def export_manifest(url, output_dir="./output"):
    exporter = ManifestExporter(url)
    manifest_id = exporter.downloader.get_manifest_id()
    output_file = f"{output_dir}/manifest_{manifest_id}.zip"
    exporter.export(output_file)
    return output_file

# Export manifests in parallel using a thread pool
with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(export_manifest, manifests))
```

### Simplified Manifest Format

LuxPort includes utilities to simplify complex IIIF manifests into a more accessible format:

```python
from luxport import ManifestDownloader
from luxport.utils import simplify_manifest

# Download a manifest
downloader = ManifestDownloader("https://collections.library.yale.edu/manifests/16867950")
manifest = downloader.download_manifest()

# Simplify it
simplified = simplify_manifest(manifest)

# Work with the simplified data
print(f"Title: {simplified['title']}")
print(f"Number of images: {len(simplified['images'])}")
```

## Examples

Several example scripts are included in the `examples/` directory:

### Basic Export (example.py)

```python
from luxport import ManifestExporter

# Create the exporter with a manifest URL
exporter = ManifestExporter("https://collections.library.yale.edu/manifests/16867950")

# Export to a ZIP file
exporter.export("output/manifest.zip")
```

### Batch Export (examples/batch_export.py)

```bash
# Run the example
python examples/batch_export.py

# Export specific manifests
python examples/batch_export.py -m "https://collections.library.yale.edu/manifests/16867950" "https://collections.library.yale.edu/manifests/12345678"

# Specify output directory and parallel workers
python examples/batch_export.py -o ./batch_output -w 8
```

### Manifest Analysis (examples/analyze_manifest.py)

```bash
# Analyze a manifest from a URL
python examples/analyze_manifest.py https://collections.library.yale.edu/manifests/16867950

# Analyze a previously exported ZIP file
python examples/analyze_manifest.py output/manifest_16867950.zip

# Save analysis results to a JSON file
python examples/analyze_manifest.py output/manifest_16867950.zip -o analysis.json
```

## Development

### Running Tests

```bash
python tests.py
```

### Creating a Distribution

```bash
python -m build
```

### Uploading to PyPI

```bash
python -m twine upload dist/*
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Yale University Library for their IIIF implementation
- International Image Interoperability Framework (IIIF) community
- Project Lux at Yale University Library
