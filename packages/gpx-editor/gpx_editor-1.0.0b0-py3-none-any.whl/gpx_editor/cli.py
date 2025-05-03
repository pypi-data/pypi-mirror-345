"""Command-line interface for the GPX Editor."""

import argparse
import os
import logging
from .editor import GPXEditor
from .abbreviations import Abbreviations

# Set up logging
logger = logging.getLogger(__name__)

def create_parser():
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(description='GPX File Editor')
    
    # File arguments
    parser.add_argument('--input', '-i', help='Input GPX file')
    parser.add_argument('--output', '-o', help='Output GPX file')
    
    # Operation arguments
    operations = parser.add_mutually_exclusive_group()
    operations.add_argument('--copy', '-c', nargs=2, metavar=('SOURCE', 'TARGET'),
                           help='Copy attribute from source to target')
    operations.add_argument('--swap', '-s', nargs=2, metavar=('ATTR1', 'ATTR2'),
                           help='Swap two attributes')
    operations.add_argument('--rename', '-r', action='store_true',
                           help='Rename file based on directory structure')
    
    # Additional options
    parser.add_argument('--all', '-a', action='store_true',
                       help='Apply operation to all waypoints')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    
    return parser

def rename_file(input_path, abbreviations=None):
    """Rename a file based on directory structure.
    
    Following the rules:
    - Apply abbreviations to directory names
    - Exclude the original filename
    - Use hyphens without spaces as separators
    - Reverse the order of directories (deepest directory first)
    """
    if not os.path.exists(input_path):
        logger.error(f"Input file does not exist: {input_path}")
        return None
    
    # Get the directory path and filename
    dir_path = os.path.dirname(input_path)
    filename = os.path.basename(input_path)
    extension = os.path.splitext(filename)[1]
    
    # Split the directory path into components
    dir_components = dir_path.split(os.sep)
    # Filter out empty components and reverse the order
    dir_components = [c for c in dir_components if c]
    dir_components.reverse()
    
    # Apply abbreviations if available
    if abbreviations:
        dir_components = [abbreviations.get_abbreviation(c) for c in dir_components]
    
    # Join with hyphens
    new_name = "-".join(dir_components) + extension
    
    # Create the new path with the same directory
    new_path = os.path.join(dir_path, new_name)
    
    return new_path

def main():
    """Main entry point for the GPX Editor CLI."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # Initialize abbreviations
    abbreviations = Abbreviations()
    
    # Handle rename operation
    if args.rename and args.input:
        new_path = rename_file(args.input, abbreviations)
        if new_path:
            print(f"Renamed file would be: {new_path}")
            if args.output:
                # If output is specified, save to that path
                import shutil
                shutil.copy2(args.input, args.output)
                print(f"File copied to: {args.output}")
            return
        else:
            print("Error renaming file")
            return
    
    # Handle other operations
    if args.input and args.output:
        editor = GPXEditor()
        
        # Create backup
        backup_path = editor.create_backup(args.input)
        print(f"Backup created at: {backup_path}")
        
        # Load file
        if not editor.load_gpx(args.input):
            print("Error loading file")
            return
            
        # Perform operations
        if args.copy:
            if args.all:
                if editor.copy_attribute_all(args.copy[0], args.copy[1]):
                    print(f"Copied attribute {args.copy[0]} to {args.copy[1]} for all waypoints")
                else:
                    print("Error copying attributes for all waypoints")
                    return
            else:
                if editor.copy_attribute(args.copy[0], args.copy[1]):
                    print(f"Copied attribute {args.copy[0]} to {args.copy[1]}")
                else:
                    print("Error copying attributes")
                    return
        elif args.swap:
            if args.all:
                if editor.swap_attributes_all(args.swap[0], args.swap[1]):
                    print(f"Swapped attributes {args.swap[0]} and {args.swap[1]} for all waypoints")
                else:
                    print("Error swapping attributes for all waypoints")
                    return
            else:
                if editor.swap_attributes(args.swap[0], args.swap[1]):
                    print(f"Swapped attributes {args.swap[0]} and {args.swap[1]}")
                else:
                    print("Error swapping attributes")
                    return
                
        # Save file
        if editor.save_gpx(args.output):
            print(f"File saved to: {args.output}")
        else:
            print("Error saving file")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
