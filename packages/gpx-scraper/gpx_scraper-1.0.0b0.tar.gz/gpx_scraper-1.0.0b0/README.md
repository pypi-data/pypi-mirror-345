# GPX Scraper

A command-line tool for downloading GPX files from websites. This tool can download individual GPX files or batch process multiple files from a list of links.

## Features

- Download individual GPX files from a webpage
- Batch download multiple GPX files from a list of links
- Organize downloads into hierarchical folder structures based on page titles
- Command-line interface for easy integration into scripts
- Interactive mode for manual operation

## Installation

Using pip:
```bash
pip install gpx-scraper
```

Using Poetry:
```bash
poetry add gpx-scraper
```

Or install directly from the repository:
```bash
pip install git+https://github.com/ironscripter/gpx-scraper.git
```

## Usage

### Command Line

Download a single GPX file:
```bash
gpx-scraper download https://example.com/hike-page
```

Download multiple GPX files from a list page:
```bash
gpx-scraper batch https://example.com/hikes-list --organize
```

Run in interactive mode:
```bash
gpx-scraper interactive
```

### Options

- `download` - Download a single GPX file
  - `--output-dir, -o` - Directory to save downloaded files (default: downloads)

- `batch` - Download multiple GPX files from a list
  - `--organize, -g` - Organize downloads into subfolders based on page titles
  - `--output-dir, -o` - Directory to save downloaded files (default: downloads)

- `interactive` - Run in interactive mode

## Development

### Setup with Poetry

```bash
# Clone the repository
git clone https://github.com/ironscripter/gpx-scraper.git
cd gpx-scraper

# Install dependencies
poetry install

# Run the tool
poetry run gpx-scraper
```

## License

MIT
