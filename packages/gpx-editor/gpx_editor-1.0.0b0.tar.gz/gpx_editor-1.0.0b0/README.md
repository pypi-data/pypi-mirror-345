# GPX Editor

A tool for editing GPX files, specifically designed for moving and copying attributes between waypoints.

## Features

- Copy attributes between waypoints
- Swap attributes
- Process multiple GPX files
- Undo/redo functionality
- Automatic backups
- Both GUI and CLI interfaces
- Rename files based on directory structure with abbreviations

## Installation

```bash
# Install from PyPI
pip install gpx-editor

# Or using Poetry
poetry add gpx-editor
```

## Usage

### GUI Mode

```bash
# Run the GUI application
gpx-editor-gui
```

### CLI Mode

```bash
# Basic usage
gpx-editor --input input.gpx --output output.gpx --copy description name
gpx-editor --input input.gpx --output output.gpx --swap description name

# Apply to all waypoints
gpx-editor --input input.gpx --output output.gpx --copy description name --all

# Rename file based on directory structure
gpx-editor --input path/to/your/gpx/file.gpx --rename
```

## Development

This project uses Poetry for dependency management.

```bash
# Clone the repository
git clone https://github.com/ironscripter/gpx-editor.git
cd gpx-editor

# Install dependencies with Poetry
poetry install

# Run the application in development mode
poetry run gpx-editor
poetry run gpx-editor-gui
```

## License

MIT

## File Structure

```
.
├── gpx_editor.py
├── requirements.txt
└── README.md
```

## License

MIT License
