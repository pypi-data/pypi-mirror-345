"""GPX Editor - A tool for editing GPX files."""

import xml.etree.ElementTree as ET
import xmltodict
import json
import os
import shutil
from datetime import datetime
import copy
import logging
import traceback

# Set up logging
logger = logging.getLogger(__name__)

class GPXEditor:
    def __init__(self):
        self.history = []
        self.future = []
        self.current_state = None
        self.current_waypoint = None
        self.original_file_path = None
        self.history_listeners = []  # Callbacks to notify when history changes
        
    def add_history_listener(self, callback):
        """Add a callback to be notified when history changes"""
        self.history_listeners.append(callback)
        
    def notify_history_changed(self):
        """Notify all listeners that history has changed"""
        for callback in self.history_listeners:
            callback()

    def get_all_waypoints(self):
        """Get all waypoints from the current state."""
        logger.debug("Getting all waypoints")
        if not self.current_state:
            logger.debug("No current state")
            return []
        
        waypoints = []
        try:
            logger.debug(f"Current state structure: {json.dumps(self.current_state, indent=2)}")
            if 'gpx' in self.current_state:
                # Check for waypoints
                if 'wpt' in self.current_state['gpx']:
                    wpts = self.current_state['gpx']['wpt']
                    if isinstance(wpts, dict):
                        wpts = [wpts]
                    waypoints.extend(wpts)
                    logger.debug(f"Found {len(waypoints)} waypoints")
            else:
                logger.debug("No 'gpx' key found in state")
        except KeyError as e:
            logger.error(f"KeyError while getting waypoints: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while getting waypoints: {e}")
        
        logger.debug(f"Returning {len(waypoints)} waypoints")
        return waypoints

    def get_all_attributes(self):
        """Get all unique attributes from all waypoints."""
        logger.debug("Getting all attributes")
        if not self.current_state:
            logger.debug("No current state")
            return []
        
        attributes = set()
        waypoints = self.get_all_waypoints()
        logger.debug(f"Got {len(waypoints)} waypoints")
        
        for waypoint in waypoints:
            if isinstance(waypoint, dict):
                logger.debug(f"Processing waypoint with keys: {list(waypoint.keys())}")
                # Get all keys including nested ones
                def get_all_keys(d, parent_key=''):
                    if isinstance(d, dict):
                        for k, v in d.items():
                            new_key = f"{parent_key}.{k}" if parent_key else k
                            attributes.add(new_key)
                            get_all_keys(v, new_key)
                    elif isinstance(d, list):
                        for i, v in enumerate(d):
                            get_all_keys(v, f"{parent_key}[{i}]")
                get_all_keys(waypoint)
        
        attributes_list = sorted(list(attributes))
        logger.debug(f"Found attributes: {attributes_list}")
        return attributes_list

    def get_attribute_value(self, attribute, waypoint_index=0):
        """Get the value of an attribute from a specific waypoint."""
        if not self.current_state:
            return ""
        
        waypoints = self.get_all_waypoints()
        if not waypoints:
            return ""
            
        if waypoint_index >= len(waypoints):
            waypoint_index = 0
        
        # Handle nested attributes with dot notation
        waypoint = waypoints[waypoint_index]
        
        return self.get_attribute_value_from_waypoint(waypoint, attribute)

    def copy_attribute_all(self, source_attr, target_attr):
        """Copy an attribute from source to target for all waypoints."""
        logger.debug(f"Copying attribute {source_attr} to {target_attr} for all waypoints")
        if not self.current_state:
            logger.debug("No current state")
            return False
        
        waypoints = self.get_all_waypoints()
        if not waypoints:
            logger.debug("No waypoints found")
            return False
        
        # Save current state for undo
        self.history.append(copy.deepcopy(self.current_state))
        self.future = []
        
        try:
            for waypoint in waypoints:
                source_value = self.get_attribute_value_from_waypoint(waypoint, source_attr)
                self.set_attribute_value_to_waypoint(waypoint, target_attr, source_value)
            
            self.notify_history_changed()
            return True
        except Exception as e:
            logger.error(f"Error copying attribute for all waypoints: {e}")
            return False

    def swap_attributes_all(self, attr1, attr2):
        """Swap two attributes for all waypoints."""
        logger.debug(f"Swapping attributes {attr1} and {attr2} for all waypoints")
        if not self.current_state:
            logger.debug("No current state")
            return False
        
        waypoints = self.get_all_waypoints()
        if not waypoints:
            logger.debug("No waypoints found")
            return False
        
        # Save current state for undo
        self.history.append(copy.deepcopy(self.current_state))
        self.future = []
        
        try:
            for waypoint in waypoints:
                value1 = self.get_attribute_value_from_waypoint(waypoint, attr1)
                value2 = self.get_attribute_value_from_waypoint(waypoint, attr2)
                self.set_attribute_value_to_waypoint(waypoint, attr1, value2)
                self.set_attribute_value_to_waypoint(waypoint, attr2, value1)
            
            self.notify_history_changed()
            return True
        except Exception as e:
            logger.error(f"Error swapping attributes for all waypoints: {e}")
            return False

    def load_gpx(self, file_path):
        """Load a GPX file and return its contents."""
        logger.debug(f"Loading GPX file: {file_path}")
        try:
            # Parse the XML file
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Convert XML to dict
            xml_dict = xmltodict.parse(ET.tostring(root))
            logger.debug(f"Parsed XML structure: {json.dumps(xml_dict, indent=2)}")
            
            # Store the current state
            self.current_state = xml_dict
            self.original_file_path = file_path
            
            # Clear history and future
            self.history = []
            self.future = []
            
            # Notify listeners
            self.notify_history_changed()
            
            return True
        except Exception as e:
            logger.error(f"Error loading GPX file: {e}")
            logger.error(traceback.format_exc())
            return False

    def save_gpx(self, file_path):
        """Save the current state to a GPX file."""
        logger.debug(f"Saving GPX file to: {file_path}")
        try:
            # Convert dict back to XML
            xml_str = xmltodict.unparse(self.current_state)
            with open(file_path, 'w') as f:
                f.write(xml_str)
            return True
        except Exception as e:
            logger.error(f"Error saving GPX file: {e}")
            return False

    def create_backup(self, file_path):
        """Create a backup of the original file."""
        backup_dir = os.path.join(os.path.dirname(file_path), "backup")
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, f"{os.path.basename(file_path)}.{datetime.now().strftime('%Y%m%d%H%M%S')}")
        shutil.copy2(file_path, backup_path)
        return backup_path

    def copy_attribute(self, source_attr, target_attr):
        """Copy an attribute from source to target."""
        logger.debug(f"Copying attribute {source_attr} to {target_attr}")
        if not self.current_state:
            logger.debug("No current state")
            return False
        
        waypoints = self.get_all_waypoints()
        if not waypoints:
            logger.debug("No waypoints found")
            return False
        
        # Save current state for undo
        self.history.append(copy.deepcopy(self.current_state))
        self.future = []
        
        try:
            # Get the first waypoint
            waypoint = waypoints[0]
            
            # Get source value
            source_value = self.get_attribute_value_from_waypoint(waypoint, source_attr)
            logger.debug(f"Source value: {source_value}")
            
            # Set target value
            self.set_attribute_value_to_waypoint(waypoint, target_attr, source_value)
            
            self.notify_history_changed()
            return True
        except Exception as e:
            logger.error(f"Error copying attribute: {e}")
            # Restore previous state
            if self.history:
                self.current_state = self.history.pop()
            return False

    def get_attribute_value_from_waypoint(self, waypoint, attribute):
        """Get the value of an attribute from a waypoint, handling nested attributes."""
        if not attribute:
            return ""
            
        parts = attribute.split('.')
        current = waypoint
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return ""
                
        return current

    def set_attribute_value_to_waypoint(self, waypoint, attribute, value):
        """Set the value of an attribute in a waypoint, handling nested attributes."""
        if not attribute:
            return
            
        parts = attribute.split('.')
        current = waypoint
        
        for i, part in enumerate(parts[:-1]):
            if part not in current:
                current[part] = {}
            current = current[part]
                
        current[parts[-1]] = value

    def swap_attributes(self, attr1, attr2):
        """Swap two attributes."""
        logger.debug(f"Swapping attributes {attr1} and {attr2}")
        if not self.current_state:
            logger.debug("No current state")
            return False
        
        waypoints = self.get_all_waypoints()
        if not waypoints:
            logger.debug("No waypoints found")
            return False
        
        # Save current state for undo
        self.history.append(copy.deepcopy(self.current_state))
        self.future = []
        
        try:
            # Get the first waypoint
            waypoint = waypoints[0]
            
            # Get values
            value1 = self.get_attribute_value_from_waypoint(waypoint, attr1)
            value2 = self.get_attribute_value_from_waypoint(waypoint, attr2)
            
            logger.debug(f"Value 1: {value1}, Value 2: {value2}")
            
            # Swap values
            self.set_attribute_value_to_waypoint(waypoint, attr1, value2)
            self.set_attribute_value_to_waypoint(waypoint, attr2, value1)
            
            self.notify_history_changed()
            return True
        except Exception as e:
            logger.error(f"Error swapping attributes: {e}")
            # Restore previous state
            if self.history:
                self.current_state = self.history.pop()
            return False

    def undo(self):
        """Undo the last action."""
        logger.debug("Undoing last action")
        if not self.history:
            logger.debug("No history to undo")
            return False
        
        try:
            # Save current state for redo
            self.future.append(copy.deepcopy(self.current_state))
            
            # Restore previous state
            self.current_state = self.history.pop()
            
            self.notify_history_changed()
            return True
        except Exception as e:
            logger.error(f"Error undoing action: {e}")
            return False

    def redo(self):
        """Redo the last undone action."""
        logger.debug("Redoing last undone action")
        if not self.future:
            logger.debug("No future to redo")
            return False
        
        try:
            # Save current state for undo
            self.history.append(copy.deepcopy(self.current_state))
            
            # Restore future state
            self.current_state = self.future.pop()
            
            self.notify_history_changed()
            return True
        except Exception as e:
            logger.error(f"Error redoing action: {e}")
            return False


def main():
    """Main entry point for the GPX Editor CLI."""
    parser = argparse.ArgumentParser(description='GPX File Editor')
    parser.add_argument('--input', help='Input GPX file')
    parser.add_argument('--output', help='Output GPX file')
    parser.add_argument('--copy', nargs=2, help='Copy attribute from source to target')
    parser.add_argument('--swap', nargs=2, help='Swap two attributes')
    parser.add_argument('--all', action='store_true', help='Apply operation to all waypoints')
    
    args = parser.parse_args()

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
        print("Error: Both input and output files must be specified.")
        parser.print_help()


if __name__ == "__main__":
    main()
