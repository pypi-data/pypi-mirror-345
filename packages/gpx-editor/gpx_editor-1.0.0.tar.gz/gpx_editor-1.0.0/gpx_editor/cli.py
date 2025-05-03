"""Command-line interface for the GPX Editor."""

import argparse
import sys
import os
import logging
from .editor import GPXEditor
from .abbreviations import Abbreviations

# Set up logging
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="GPX Editor - A tool for editing GPX files")
    
    # Input file(s)
    parser.add_argument("--input", "-i", required=True, nargs='+',
                      help="Input GPX file(s). Can specify multiple files for batch processing.")
                      
    # Output directory or file
    parser.add_argument("--output", "-o",
                      help="Output file or directory. For batch processing, this should be a directory.")
                      
    # Operations (mutually exclusive)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--copy", "-c", nargs=2, metavar=("SOURCE", "TARGET"),
                     help="Copy source attribute to target attribute")
    group.add_argument("--swap", "-s", nargs=2, metavar=("ATTR1", "ATTR2"),
                     help="Swap two attributes")
    group.add_argument("--rename", "-r", action="store_true",
                     help="Rename file based on directory structure")
    group.add_argument("--list-attributes", "-l", action="store_true",
                     help="List all available attributes in the GPX file(s)")
                     
    # Apply to all waypoints
    parser.add_argument("--all", "-a", action="store_true",
                      help="Apply operation to all waypoints (default: first waypoint only)")
                      
    # Batch processing options
    parser.add_argument("--prefix", "-p", 
                      help="Add prefix to output filenames (batch processing only)")
    parser.add_argument("--suffix", "-sf", 
                      help="Add suffix to output filenames (batch processing only)")
                      
    # Verbose output
    parser.add_argument("--verbose", "-v", action="store_true",
                      help="Enable verbose output")
                      
    return parser.parse_args()
    
def main():
    """Main function for the CLI application"""
    # Parse arguments
    args = parse_args()
    
    # Set up logging level
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        
    # Check input files
    for input_file in args.input:
        if not os.path.exists(input_file):
            logger.error(f"Input file not found: {input_file}")
            sys.exit(1)
    
    # Check if we're processing multiple files
    is_batch = len(args.input) > 1
    
    # Check output path for operations that require it
    if not args.rename and not args.list_attributes and not args.output:
        logger.error("Output file/directory is required for copy and swap operations")
        sys.exit(1)
        
    # For batch processing, output should be a directory
    if is_batch and args.output and not args.rename and not args.list_attributes:
        if not os.path.isdir(args.output):
            try:
                os.makedirs(args.output, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create output directory: {args.output}")
                logger.error(f"Error: {e}")
                sys.exit(1)
    
    # List attributes mode
    if args.list_attributes:
        for input_file in args.input:
            editor = GPXEditor()
            if editor.load_gpx(input_file):
                print(f"\nAttributes in {input_file}:")
                attributes = editor.get_all_attributes()
                print("Editable attributes:")
                for attr in attributes:
                    if attr['editable']:
                        print(f"  - {attr['name']}")
                print("Read-only attributes:")
                for attr in attributes:
                    if not attr['editable']:
                        print(f"  - {attr['name']}")
            else:
                logger.error(f"Failed to load file: {input_file}")
        return
    
    # Check if attributes are editable for copy/swap operations
    if args.copy or args.swap:
        attrs = args.copy if args.copy else args.swap
        for attr in attrs:
            if attr not in GPXEditor.EDITABLE_ATTRIBUTES:
                logger.error(f"The attribute '{attr}' is read-only and cannot be modified.")
                logger.error(f"Editable attributes are: {', '.join(GPXEditor.EDITABLE_ATTRIBUTES)}")
                sys.exit(1)
    
    # Process each input file
    success_count = 0
    error_count = 0
    
    for input_file in args.input:
        try:
            # Create editor for this file
            editor = GPXEditor()
            
            # Create backup
            backup_path = editor.create_backup(input_file)
            logger.info(f"Created backup at: {backup_path}")
            
            # Load input file
            if not editor.load_gpx(input_file):
                logger.error(f"Failed to load input file: {input_file}")
                error_count += 1
                continue
            
            # Determine output path
            if args.rename:
                # Generate new filename based on directory structure
                new_filename = Abbreviations.abbreviate_path(input_file)
                
                # Create output path
                output_dir = os.path.dirname(input_file)
                if args.output:
                    # If output is specified, use it as the directory
                    output_dir = args.output
                    
                output_path = os.path.join(output_dir, new_filename)
            else:
                # For copy/swap operations
                if is_batch:
                    # Batch mode - use input filename with prefix/suffix in output directory
                    basename = os.path.basename(input_file)
                    name, ext = os.path.splitext(basename)
                    prefix = args.prefix or ""
                    suffix = args.suffix or ""
                    new_name = f"{prefix}{name}{suffix}{ext}"
                    output_path = os.path.join(args.output, new_name)
                else:
                    # Single file mode - use specified output path
                    output_path = args.output
            
            # Perform operation
            success = True  # Default for rename operation
            
            if args.copy:
                source_attr, target_attr = args.copy
                logger.info(f"Copying attribute '{source_attr}' to '{target_attr}' in {input_file}")
                
                if args.all:
                    success = editor.copy_attribute_all(source_attr, target_attr)
                else:
                    success = editor.copy_attribute(source_attr, target_attr)
                    
            elif args.swap:
                attr1, attr2 = args.swap
                logger.info(f"Swapping attributes '{attr1}' and '{attr2}' in {input_file}")
                
                if args.all:
                    success = editor.swap_attributes_all(attr1, attr2)
                else:
                    success = editor.swap_attributes(attr1, attr2)
            
            # Save the file if operation was successful
            if success:
                if editor.save_gpx(output_path):
                    if args.rename:
                        logger.info(f"Renamed file to: {output_path}")
                    else:
                        logger.info(f"Saved changes to: {output_path}")
                    success_count += 1
                else:
                    logger.error(f"Failed to save output file: {output_path}")
                    error_count += 1
            else:
                logger.error(f"Operation failed for file: {input_file}")
                error_count += 1
                
        except Exception as e:
            logger.error(f"Error processing file {input_file}: {e}")
            logger.error(traceback.format_exc())
            error_count += 1
    
    # Summary
    if is_batch:
        logger.info(f"Batch processing completed: {success_count} successful, {error_count} failed")
    else:
        if success_count > 0:
            logger.info("Operation completed successfully")
        else:
            logger.error("Operation failed")
    
if __name__ == "__main__":
    main()
