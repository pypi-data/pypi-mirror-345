# DataReader

A Python package for extracting and formatting content from various sources including PDFs, URLs, videos, and audio files.

## Features

- PDF processing with multiple backends (PyMuPDF, pypdf, markitdown)
- Web page content extraction
- Video content processing
- Audio transcription
- Markdown formatting

## Installation

```bash
pip install keytake-datareader
```

All dependencies are included with the package by default, so you can immediately use all features without installing additional packages.

## Quick Start

```python
from datareader import DataReader

# Process a PDF file
text = DataReader.read_pdf("document.pdf")

# Process a URL
web_content = DataReader.read_url("https://example.com")

# Process a video file
transcript = DataReader.read_video("video.mp4")

# Process an audio file
audio_text = DataReader.read_audio("audio.mp3")

# Save as markdown
DataReader.save_markdown(text, "output.md")
```

## Command Line Usage

The package provides command-line scripts for batch processing:

```bash
# Process PDFs
./run_pdf.sh

# Process URLs
./run_url.sh
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.