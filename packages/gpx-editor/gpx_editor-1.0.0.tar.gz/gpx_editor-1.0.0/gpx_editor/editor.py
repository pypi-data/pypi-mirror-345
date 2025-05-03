"""GPX Editor - A tool for editing GPX files."""

import xml.etree.ElementTree as ET
import xmltodict
import json
import argparse
import os
import shutil
from datetime import datetime
import copy
import logging
import traceback

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class GPXEditor:
    # Define which attributes are editable
    EDITABLE_ATTRIBUTES = ['name', 'cmt', 'desc', 'sym', 'type']
    
    def __init__(self):
        self.history = []
        self.future = []
        self.current_state = None
        self.current_waypoint = None
        self.history_listeners = []
        
    def add_history_listener(self, listener):
        """Add a listener function to be called when history changes"""
        self.history_listeners.append(listener)
        
    def _notify_history_listeners(self):
        """Notify all history listeners of a change"""
        for listener in self.history_listeners:
            try:
                listener()
            except Exception as e:
                logger.error(f"Error in history listener: {e}")
                
    def create_backup(self, file_path):
        """Create a backup of the specified file"""
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
            
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(os.path.dirname(file_path), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = os.path.basename(file_path)
        backup_name = f"{os.path.splitext(file_name)[0]}_{timestamp}{os.path.splitext(file_name)[1]}"
        backup_path = os.path.join(backup_dir, backup_name)
        
        # Copy file to backup
        try:
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup at: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
            
    def load_gpx(self, file_path):
        """Load a GPX file and parse it"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                gpx_content = f.read()
                
            # Parse XML to dict
            gpx_dict = xmltodict.parse(gpx_content)
            
            # Save current state
            self.current_state = gpx_dict
            
            # Add to history
            self.history.append(copy.deepcopy(gpx_dict))
            self.future = []
            self._notify_history_listeners()
            
            logger.info(f"Loaded GPX file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading GPX file: {e}")
            logger.error(traceback.format_exc())
            return False
            
    def save_gpx(self, file_path):
        """Save the current state to a GPX file"""
        if not self.current_state:
            logger.error("No GPX data loaded")
            return False
            
        try:
            # Convert dict back to XML
            gpx_content = xmltodict.unparse(self.current_state, pretty=True)
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(gpx_content)
                
            logger.info(f"Saved GPX file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving GPX file: {e}")
            logger.error(traceback.format_exc())
            return False
            
    def undo(self):
        """Undo the last operation"""
        if len(self.history) <= 1:
            logger.warning("Nothing to undo")
            return False
            
        # Move current state to future
        self.future.append(copy.deepcopy(self.current_state))
        
        # Pop the current state from history
        self.history.pop()
        
        # Set current state to the last item in history
        self.current_state = copy.deepcopy(self.history[-1])
        
        self._notify_history_listeners()
        logger.info("Undo operation")
        return True
        
    def redo(self):
        """Redo the last undone operation"""
        if not self.future:
            logger.warning("Nothing to redo")
            return False
            
        # Get the last item from future
        state = self.future.pop()
        
        # Add to history
        self.history.append(copy.deepcopy(state))
        
        # Set current state
        self.current_state = copy.deepcopy(state)
        
        self._notify_history_listeners()
        logger.info("Redo operation")
        return True
        
    def get_all_attributes(self):
        """Get all available attributes from the current waypoint with editable status"""
        if not self.current_state:
            logger.error("No GPX data loaded")
            return []
            
        try:
            # Get the first waypoint to extract attributes
            if 'gpx' in self.current_state and 'wpt' in self.current_state['gpx']:
                wpt = self.current_state['gpx']['wpt']
                if isinstance(wpt, list) and wpt:
                    # Use the first waypoint
                    self.current_waypoint = wpt[0]
                elif isinstance(wpt, dict):
                    # Single waypoint
                    self.current_waypoint = wpt
                else:
                    logger.error("No waypoints found in GPX data")
                    return []
                    
                # Extract attributes and mark as editable or read-only
                attributes = []
                for attr in self.current_waypoint.keys():
                    # Check if attribute is in the editable list
                    is_editable = attr in self.EDITABLE_ATTRIBUTES
                    attributes.append({
                        'name': attr,
                        'editable': is_editable
                    })
                
                logger.info(f"Found attributes: {[a['name'] for a in attributes]}")
                return attributes
            else:
                logger.error("Invalid GPX structure")
                return []
        except Exception as e:
            logger.error(f"Error getting attributes: {e}")
            logger.error(traceback.format_exc())
            return []
            
    def copy_attribute(self, source_attr, target_attr):
        """Copy a source attribute to a target attribute in the first waypoint"""
        if not self.current_state:
            logger.error("No GPX data loaded")
            return False
            
        try:
            # Get the first waypoint
            if 'gpx' in self.current_state and 'wpt' in self.current_state['gpx']:
                wpt = self.current_state['gpx']['wpt']
                if isinstance(wpt, list) and wpt:
                    # Use the first waypoint
                    waypoint = wpt[0]
                elif isinstance(wpt, dict):
                    # Single waypoint
                    waypoint = wpt
                else:
                    logger.error("No waypoints found in GPX data")
                    return False
                    
                # Check if source attribute exists
                if source_attr not in waypoint:
                    logger.error(f"Source attribute '{source_attr}' not found in waypoint")
                    return False
                    
                # Copy source to target
                waypoint[target_attr] = waypoint[source_attr]
                
                # Add to history
                self.history.append(copy.deepcopy(self.current_state))
                self.future = []
                self._notify_history_listeners()
                
                logger.info(f"Copied attribute '{source_attr}' to '{target_attr}'")
                return True
            else:
                logger.error("Invalid GPX structure")
                return False
        except Exception as e:
            logger.error(f"Error copying attribute: {e}")
            logger.error(traceback.format_exc())
            return False
            
    def copy_attribute_all(self, source_attr, target_attr):
        """Copy a source attribute to a target attribute in all waypoints"""
        if not self.current_state:
            logger.error("No GPX data loaded")
            return False
            
        try:
            # Get all waypoints
            if 'gpx' in self.current_state and 'wpt' in self.current_state['gpx']:
                wpt = self.current_state['gpx']['wpt']
                if isinstance(wpt, list):
                    waypoints = wpt
                elif isinstance(wpt, dict):
                    # Single waypoint, convert to list
                    waypoints = [wpt]
                else:
                    logger.error("No waypoints found in GPX data")
                    return False
                    
                # Process each waypoint
                success = False
                for waypoint in waypoints:
                    # Check if source attribute exists
                    if source_attr in waypoint:
                        # Copy source to target
                        waypoint[target_attr] = waypoint[source_attr]
                        success = True
                        
                if success:
                    # Add to history
                    self.history.append(copy.deepcopy(self.current_state))
                    self.future = []
                    self._notify_history_listeners()
                    
                    logger.info(f"Copied attribute '{source_attr}' to '{target_attr}' in all waypoints")
                    return True
                else:
                    logger.error(f"Source attribute '{source_attr}' not found in any waypoint")
                    return False
            else:
                logger.error("Invalid GPX structure")
                return False
        except Exception as e:
            logger.error(f"Error copying attribute: {e}")
            logger.error(traceback.format_exc())
            return False
            
    def swap_attributes(self, attr1, attr2):
        """Swap two attributes in the first waypoint"""
        if not self.current_state:
            logger.error("No GPX data loaded")
            return False
            
        try:
            # Get the first waypoint
            if 'gpx' in self.current_state and 'wpt' in self.current_state['gpx']:
                wpt = self.current_state['gpx']['wpt']
                if isinstance(wpt, list) and wpt:
                    # Use the first waypoint
                    waypoint = wpt[0]
                elif isinstance(wpt, dict):
                    # Single waypoint
                    waypoint = wpt
                else:
                    logger.error("No waypoints found in GPX data")
                    return False
                    
                # Check if both attributes exist
                if attr1 not in waypoint:
                    logger.error(f"Attribute '{attr1}' not found in waypoint")
                    return False
                if attr2 not in waypoint:
                    logger.error(f"Attribute '{attr2}' not found in waypoint")
                    return False
                    
                # Swap attributes
                temp = waypoint[attr1]
                waypoint[attr1] = waypoint[attr2]
                waypoint[attr2] = temp
                
                # Add to history
                self.history.append(copy.deepcopy(self.current_state))
                self.future = []
                self._notify_history_listeners()
                
                logger.info(f"Swapped attributes '{attr1}' and '{attr2}'")
                return True
            else:
                logger.error("Invalid GPX structure")
                return False
        except Exception as e:
            logger.error(f"Error swapping attributes: {e}")
            logger.error(traceback.format_exc())
            return False
            
    def swap_attributes_all(self, attr1, attr2):
        """Swap two attributes in all waypoints"""
        if not self.current_state:
            logger.error("No GPX data loaded")
            return False
            
        try:
            # Get all waypoints
            if 'gpx' in self.current_state and 'wpt' in self.current_state['gpx']:
                wpt = self.current_state['gpx']['wpt']
                if isinstance(wpt, list):
                    waypoints = wpt
                elif isinstance(wpt, dict):
                    # Single waypoint, convert to list
                    waypoints = [wpt]
                else:
                    logger.error("No waypoints found in GPX data")
                    return False
                    
                # Process each waypoint
                success = False
                for waypoint in waypoints:
                    # Check if both attributes exist
                    if attr1 in waypoint and attr2 in waypoint:
                        # Swap attributes
                        temp = waypoint[attr1]
                        waypoint[attr1] = waypoint[attr2]
                        waypoint[attr2] = temp
                        success = True
                        
                if success:
                    # Add to history
                    self.history.append(copy.deepcopy(self.current_state))
                    self.future = []
                    self._notify_history_listeners()
                    
                    logger.info(f"Swapped attributes '{attr1}' and '{attr2}' in all waypoints")
                    return True
                else:
                    logger.error(f"Attributes '{attr1}' and '{attr2}' not found in any waypoint")
                    return False
            else:
                logger.error("Invalid GPX structure")
                return False
        except Exception as e:
            logger.error(f"Error swapping attributes: {e}")
            logger.error(traceback.format_exc())
            return False
