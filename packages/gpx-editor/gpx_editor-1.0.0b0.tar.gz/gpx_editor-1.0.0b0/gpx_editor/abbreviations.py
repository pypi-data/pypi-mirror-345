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
        "central": "CTR",
        "center": "CTR",
        "middle": "MID",
        "upper": "UPR",
        "lower": "LWR",
        "mountain": "MTN",
        "mountains": "MTS",
        "hill": "HL",
        "hills": "HLS",
        "valley": "VAL",
        "forest": "FOR",
        "woods": "WDS",
        "lake": "LK",
        "river": "RVR",
        "stream": "STR",
        "creek": "CRK",
        "trail": "TRL",
        "path": "PTH",
        "road": "RD",
        "highway": "HWY",
        "route": "RT",
        "park": "PRK",
        "national": "NAT",
        "state": "ST",
        "county": "CTY",
        "city": "CTY",
        "town": "TWN",
        "village": "VLG",
        "point": "PT",
        "peak": "PK",
        "summit": "SMT",
        "ridge": "RDG",
        "canyon": "CYN",
        "gorge": "GRG",
        "pass": "PS",
        "junction": "JCT",
        "crossing": "XNG",
        "bridge": "BRG",
        "campground": "CG",
        "campsite": "CS",
        "trailhead": "TH",
        "parking": "PKG",
        "overlook": "OVR",
        "viewpoint": "VP",
        "vista": "VST",
        "spring": "SPG",
        "falls": "FLS",
        "waterfall": "WF",
        
        # Months
        "january": "JAN",
        "february": "FEB",
        "march": "MAR",
        "april": "APR",
        "may": "MAY",
        "june": "JUN",
        "july": "JUL",
        "august": "AUG",
        "september": "SEP",
        "october": "OCT",
        "november": "NOV",
        "december": "DEC",
        
        # Seasons
        "winter": "WIN",
        "spring": "SPR",
        "summer": "SUM",
        "fall": "FAL",
        "autumn": "AUT",
        
        # Common words
        "the": "T",
        "and": "AND",
        "of": "OF",
        "in": "IN",
        "on": "ON",
        "at": "AT",
        "to": "TO",
        "from": "FRM",
        "with": "W",
        "without": "WO",
        "between": "BTW",
        "through": "THR",
        "around": "ARD",
        "over": "OVR",
        "under": "UND",
        "above": "ABV",
        "below": "BLW",
        "near": "NR",
        "far": "FR",
        "by": "BY",
        "for": "FOR",
    }
    
    @classmethod
    def get_abbreviation(cls, name):
        """Get the abbreviation for a directory name.
        
        If the name is not in the abbreviation dictionary, return the name as is.
        
        Args:
            name: The directory name to abbreviate
            
        Returns:
            The abbreviation for the directory name, or the name itself if no abbreviation exists
        """
        # Convert to lowercase for case-insensitive matching
        name_lower = name.lower()
        
        # Check if the name is in the abbreviation dictionary
        if name_lower in cls._abbreviations:
            return cls._abbreviations[name_lower]
        
        # If not found, return the original name
        return name
    
    @classmethod
    def get_all_abbreviations(cls):
        """Get all abbreviations as a dictionary.
        
        Returns:
            A dictionary of all abbreviations
        """
        return cls._abbreviations.copy()
