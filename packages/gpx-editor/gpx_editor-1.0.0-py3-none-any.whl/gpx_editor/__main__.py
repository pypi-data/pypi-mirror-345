"""Main entry point for the GPX Editor package."""

import sys
import os

if __name__ == "__main__":
    # Check if any arguments are provided
    if len(sys.argv) > 1:
        # If arguments are provided, run CLI
        from .cli import main as cli_main
        cli_main()
    else:
        # If no arguments, run GUI
        from .gui import main as gui_main
        gui_main()
