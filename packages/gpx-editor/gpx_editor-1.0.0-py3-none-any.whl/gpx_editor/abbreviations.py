"""Abbreviations module for the GPX Editor.

This module provides a static class for handling directory name abbreviations.
As per requirements:
- Abbreviations should be 2-3 letters in length
- Abbreviation class remains static (no need for dynamic saving)
"""

import logging

# Set up logging
logger = logging.getLogger(__name__)

class Abbreviations:
    """Static class for handling directory name abbreviations.
    
    Abbreviations are 2-3 letters in length and are used to shorten directory names
    when creating new filenames based on directory structure.
    """
    
    # Static abbreviation dictionary
    _abbreviations = {
        # Common location abbreviations (2-3 letters)
        "north": "N",
        "south": "S",
        "east": "E",
        "west": "W",
        "northeast": "NE",
        "northwest": "NW",
        "southeast": "SE",
        "southwest": "SW",
        
        # Common trail abbreviations
        "trail": "TRL",
        "path": "PTH",
        "road": "RD",
        "street": "ST",
        "avenue": "AVE",
        "highway": "HWY",
        "route": "RT",
        
        # Common geographic abbreviations
        "mountain": "MTN",
        "hill": "HL",
        "valley": "VAL",
        "lake": "LK",
        "river": "RVR",
        "creek": "CRK",
        "forest": "FOR",
        "park": "PK",
        "national": "NAT",
        "state": "ST",
        
        # Common activity abbreviations
        "hike": "HK",
        "bike": "BK",
        "walk": "WK",
        "run": "RN",
        "camp": "CMP",
        
        # Common direction abbreviations
        "upper": "UP",
        "lower": "LWR",
        "middle": "MID",
        "central": "CTR",
    }
    
    @classmethod
    def get_abbreviation(cls, name):
        """Get the abbreviation for a directory name.
        
        If the name exists in the abbreviation dictionary, return the abbreviation.
        Otherwise, return the first 2-3 letters of the name.
        
        Args:
            name (str): The directory name to abbreviate
            
        Returns:
            str: The abbreviated name (2-3 letters)
        """
        # Convert to lowercase for case-insensitive matching
        name_lower = name.lower()
        
        # Check if name exists in abbreviation dictionary
        if name_lower in cls._abbreviations:
            return cls._abbreviations[name_lower]
            
        # Otherwise, return first 2-3 letters
        if len(name) <= 3:
            return name.upper()
        else:
            return name[:3].upper()
            
    @classmethod
    def get_all_abbreviations(cls):
        """Get all abbreviations as a dictionary.
        
        Returns:
            dict: Dictionary of all abbreviations
        """
        return cls._abbreviations.copy()
        
    @classmethod
    def abbreviate_path(cls, path):
        """Convert a file path to an abbreviated filename.
        
        Takes a file path and converts it to a filename with abbreviated directory names.
        Format: "D3-D2-D1.gpx" (deepest directory first)
        
        Args:
            path (str): The file path to abbreviate
            
        Returns:
            str: The abbreviated filename
        """
        import os
        
        # Split path into components
        path_parts = os.path.normpath(path).split(os.sep)
        
        # Get directory names (exclude the filename)
        dir_names = path_parts[:-1]
        
        # Skip empty directory names
        dir_names = [d for d in dir_names if d]
        
        if not dir_names:
            logger.warning(f"No directory names found in path: {path}")
            return os.path.basename(path)
            
        # Abbreviate directory names
        abbr_names = [cls.get_abbreviation(d) for d in dir_names]
        
        # Reverse the order (deepest directory first)
        abbr_names.reverse()
        
        # Join with hyphens
        abbr_path = "-".join(abbr_names)
        
        # Get the extension from the original file
        _, ext = os.path.splitext(path)
        
        # Create the new filename
        new_filename = f"{abbr_path}{ext}"
        
        logger.info(f"Abbreviated path '{path}' to '{new_filename}'")
        return new_filename
