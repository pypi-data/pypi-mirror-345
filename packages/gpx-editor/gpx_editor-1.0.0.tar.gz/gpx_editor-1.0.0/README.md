# GPX Editor

A tool for editing GPX files, specifically designed for moving and copying attributes between waypoints.

## Features

- Copy attributes between waypoints
- Swap attributes
- Apply operations to all waypoints
- Process multiple GPX files with batch operations
- Preview attribute values before making changes
- Undo/redo functionality
- Automatic backups
- Prefix/suffix options for batch file saving
- File type preservation
- Directory-based file renaming with abbreviations
- Both GUI and CLI interfaces
- Safety features to prevent modifying critical attributes

## Installation

### Using Poetry (Recommended)

```bash
# Install dependencies with Poetry
poetry install

# Run the application
poetry run python -m gpx_editor
```

### Using pip

```bash
pip install -r requirements.txt
python -m gpx_editor
```

## Usage

### GUI Mode

The GPX Editor GUI follows a logical workflow:

1. **Select Files**: Choose one or more GPX files to work with
2. **View Attributes**: After file selection, attributes are loaded automatically
3. **Select Operation**: Choose to copy or swap attributes
4. **Execute Operation**: Perform the operation in memory
5. **Save Files**: Save changes only when you're ready

```bash
poetry run python -m gpx_editor
```

#### Multiple File Processing

The GPX Editor supports batch processing of multiple files:

1. Select multiple files using the file selection panel
2. Choose attributes and operations to perform
3. Execute operations on all files
4. Save all modified files with optional prefix/suffix

#### Attribute Preview

Before making changes, you can preview attribute values:

- View attribute values for the current file in the Preview tab
- Use "Show Batch Preview" to see the same attribute across all selected files

### CLI Mode

The command-line interface supports all core operations:

```bash
# Copy an attribute
poetry run python -m gpx_editor --input input.gpx --output output.gpx --copy description name

# Swap attributes
poetry run python -m gpx_editor --input input.gpx --output output.gpx --swap description name

# Apply to all waypoints
poetry run python -m gpx_editor --input input.gpx --output output.gpx --copy description name --all

# Rename file based on directory structure
poetry run python -m gpx_editor --input path/to/your/gpx/file.gpx --rename
```

## Directory-Based File Renaming

The GPX Editor can rename files based on their directory structure:

- Applies abbreviations to directory names (2-3 letters)
- Excludes the original filename
- Uses hyphens as separators (e.g., "D3-D2-D1.gpx")
- Reverses the order of directories (deepest directory first)

Example: For a file path `north/mountain/trail/hiking_route.gpx`, the new filename would be `TRL-MTN-N.gpx`

## Sample Files

The `samples` directory contains example GPX files for testing:

- `sample1.gpx` - Basic waypoints with standard attributes
- `sample2.gpx` - Different location with additional attributes
- `samples/north/mountain/trail/hiking_route.gpx` - For testing directory-based renaming

## Project Structure

```
.
├── gpx_editor/                # Main package directory
│   ├── __init__.py           # Package initialization
│   ├── __main__.py           # Entry point
│   ├── abbreviations.py      # Static abbreviation class (2-3 letters)
│   ├── cli.py                # Command-line interface using argparse
│   ├── editor.py             # Core GPX editing functionality
│   └── gui.py                # Tkinter-based GUI interface
├── samples/                  # Sample GPX files for testing
├── pyproject.toml           # Poetry configuration
├── requirements.txt         # Pip dependencies
├── README.md                # Project documentation
└── PROJECT_PLAN.md          # Development plan and checklist
```

## License

MIT License
