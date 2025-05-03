"""GUI module for the GPX Editor."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import logging
import traceback
from .editor import GPXEditor

# Set up logging
logger = logging.getLogger(__name__)

class GPXEditorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GPX Editor")
        self.root.geometry("800x600")
        
        self.editor = GPXEditor()
        self.editor.add_history_listener(self.update_history_display)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Open Multiple", command=self.open_multiple_files)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.editor.undo)
        edit_menu.add_command(label="Redo", command=self.editor.redo)
        
        # Create tabs
        tab_control = ttk.Notebook(main_frame)
        
        # Attribute tab
        attr_tab = ttk.Frame(tab_control)
        tab_control.add(attr_tab, text="Attributes")
        
        # History tab
        history_tab = ttk.Frame(tab_control)
        tab_control.add(history_tab, text="History")
        
        tab_control.pack(expand=1, fill="both")
        
        # Attribute tab content
        attr_frame = ttk.LabelFrame(attr_tab, text="Attribute Operations", padding="10")
        attr_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Source attribute
        ttk.Label(attr_frame, text="Source Attribute:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_attr = ttk.Combobox(attr_frame, width=30)
        self.source_attr.grid(row=0, column=1, padx=5, pady=5)
        self.source_attr.bind("<<ComboboxSelected>>", self.update_previews)
        
        # Target attribute
        ttk.Label(attr_frame, text="Target Attribute:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.target_attr = ttk.Combobox(attr_frame, width=30)
        self.target_attr.grid(row=1, column=1, padx=5, pady=5)
        self.target_attr.bind("<<ComboboxSelected>>", self.update_previews)
        
        # Preview frame
        preview_frame = ttk.LabelFrame(attr_frame, text="Preview", padding="10")
        preview_frame.grid(row=2, column=0, columnspan=2, sticky=tk.EW, padx=5, pady=10)
        
        # Source preview
        ttk.Label(preview_frame, text="Source Value:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_preview = ttk.Label(preview_frame, text="")
        self.source_preview.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Target preview
        ttk.Label(preview_frame, text="Target Value:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.target_preview = ttk.Label(preview_frame, text="")
        self.target_preview.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(attr_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Copy button
        self.copy_btn = ttk.Button(button_frame, text="Copy", command=lambda: self.copy_attributes(False))
        self.copy_btn.grid(row=0, column=0, padx=5)
        
        # Copy All button
        self.copy_all_btn = ttk.Button(button_frame, text="Copy All", command=lambda: self.copy_attributes(True))
        self.copy_all_btn.grid(row=0, column=1, padx=5)
        
        # Swap button
        self.swap_btn = ttk.Button(button_frame, text="Swap", command=lambda: self.swap_attributes(False))
        self.swap_btn.grid(row=0, column=2, padx=5)
        
        # Swap All button
        self.swap_all_btn = ttk.Button(button_frame, text="Swap All", command=lambda: self.swap_attributes(True))
        self.swap_all_btn.grid(row=0, column=3, padx=5)
        
        # History tab content
        history_frame = ttk.Frame(history_tab, padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # History count
        ttk.Label(history_frame, text="Undo Steps:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.history_count = ttk.Label(history_frame, text="0")
        self.history_count.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Future count
        ttk.Label(history_frame, text="Redo Steps:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.future_count = ttk.Label(history_frame, text="0")
        self.future_count.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Status bar
        self.status_bar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def update_previews(self, event=None):
        """Update the preview labels with current attribute values."""
        source_attr = self.source_attr.get()
        target_attr = self.target_attr.get()
        
        if source_attr:
            source_value = self.editor.get_attribute_value(source_attr)
            self.source_preview.config(text=str(source_value))
        
        if target_attr:
            target_value = self.editor.get_attribute_value(target_attr)
            self.target_preview.config(text=str(target_value))
            
    def update_attributes(self):
        """Update the dropdown menus with available attributes."""
        attributes = self.editor.get_all_attributes()
        
        # Update source attribute dropdown
        current_source = self.source_attr.get()
        self.source_attr['values'] = attributes
        if current_source in attributes:
            self.source_attr.set(current_source)
        elif attributes:
            self.source_attr.set(attributes[0])
        
        # Update target attribute dropdown
        current_target = self.target_attr.get()
        self.target_attr['values'] = attributes
        if current_target in attributes:
            self.target_attr.set(current_target)
        elif attributes:
            self.target_attr.set(attributes[0])
            
        # Update previews
        self.update_previews()
        
    def update_history_display(self):
        """Update the history display with current counts"""
        self.history_count.config(text=str(len(self.editor.history)))
        self.future_count.config(text=str(len(self.editor.future)))
        
    def open_file(self):
        """Open a single GPX file."""
        file_path = filedialog.askopenfilename(
            title="Open GPX File",
            filetypes=[("GPX files", "*.gpx"), ("All files", "*.*")]
        )
        
        if file_path:
            self.load_single_file(file_path)
            
    def open_multiple_files(self):
        """Open multiple GPX files at once"""
        file_paths = filedialog.askopenfilenames(
            title="Open Multiple GPX Files",
            filetypes=[("GPX files", "*.gpx"), ("All files", "*.*")]
        )
        
        if file_paths:
            # Ask which operation to perform
            operation = messagebox.askquestion("Batch Operation", 
                                         "Do you want to perform an operation on all files?")
            
            if operation == 'yes':
                # Get operation details
                source_attr = self.source_attr.get()
                target_attr = self.target_attr.get()
                
                if not source_attr or not target_attr:
                    messagebox.showerror("Error", "Please select source and target attributes first.")
                    return
                
                # Ask for operation type
                op_type = messagebox.askquestion("Operation Type", 
                                           "Do you want to copy attributes? Select 'No' for swap.")
                
                operation = "copy" if op_type == 'yes' else "swap"
                
                # Ask for all waypoints
                all_waypoints = messagebox.askquestion("All Waypoints", 
                                                 "Apply to all waypoints?") == 'yes'
                
                # Process files
                self.process_multiple_files(operation, source_attr, target_attr, 
                                           all_waypoints, save_after=True)
            else:
                # Just load the first file
                if file_paths:
                    self.load_single_file(file_paths[0])
    
    def load_single_file(self, file_path):
        """Load a single GPX file"""
        try:
            # Create backup
            backup_path = self.editor.create_backup(file_path)
            self.status_bar.config(text=f"Backup created at: {backup_path}")
            
            # Load file
            if self.editor.load_gpx(file_path):
                self.status_bar.config(text=f"Loaded: {file_path}")
                
                # Update attributes
                self.update_attributes()
                
                # Update window title
                self.root.title(f"GPX Editor - {os.path.basename(file_path)}")
            else:
                messagebox.showerror("Error", f"Failed to load file: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading file: {str(e)}")
            logger.error(f"Error loading file: {e}")
            logger.error(traceback.format_exc())
    
    def save_file(self):
        """Save the current state to a file."""
        if not self.editor.current_state:
            messagebox.showerror("Error", "No file loaded")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save GPX File",
            filetypes=[("GPX files", "*.gpx"), ("All files", "*.*")],
            defaultextension=".gpx"
        )
        
        if file_path:
            try:
                if self.editor.save_gpx(file_path):
                    self.status_bar.config(text=f"Saved: {file_path}")
                    messagebox.showinfo("Success", f"File saved to: {file_path}")
                else:
                    messagebox.showerror("Error", "Failed to save file")
            except Exception as e:
                messagebox.showerror("Error", f"Error saving file: {str(e)}")
                logger.error(f"Error saving file: {e}")
                logger.error(traceback.format_exc())
                
    def copy_attributes(self, all_waypoints=False):
        """Copy attributes from source to target."""
        if not self.editor.current_state:
            messagebox.showerror("Error", "No file loaded")
            return
            
        source_attr = self.source_attr.get()
        target_attr = self.target_attr.get()
        
        if not source_attr or not target_attr:
            messagebox.showerror("Error", "Please select source and target attributes")
            return
            
        try:
            if all_waypoints:
                if self.editor.copy_attribute_all(source_attr, target_attr):
                    self.status_bar.config(text=f"Copied {source_attr} to {target_attr} for all waypoints")
                    self.update_previews()
                else:
                    messagebox.showerror("Error", "Failed to copy attributes for all waypoints")
            else:
                if self.editor.copy_attribute(source_attr, target_attr):
                    self.status_bar.config(text=f"Copied {source_attr} to {target_attr}")
                    self.update_previews()
                else:
                    messagebox.showerror("Error", "Failed to copy attributes")
        except Exception as e:
            messagebox.showerror("Error", f"Error copying attributes: {str(e)}")
            logger.error(f"Error copying attributes: {e}")
            logger.error(traceback.format_exc())
                
    def swap_attributes(self, all_waypoints=False):
        """Swap two attributes."""
        if not self.editor.current_state:
            messagebox.showerror("Error", "No file loaded")
            return
            
        attr1 = self.source_attr.get()
        attr2 = self.target_attr.get()
        
        if not attr1 or not attr2:
            messagebox.showerror("Error", "Please select source and target attributes")
            return
            
        try:
            if all_waypoints:
                if self.editor.swap_attributes_all(attr1, attr2):
                    self.status_bar.config(text=f"Swapped {attr1} and {attr2} for all waypoints")
                    self.update_previews()
                else:
                    messagebox.showerror("Error", "Failed to swap attributes for all waypoints")
            else:
                if self.editor.swap_attributes(attr1, attr2):
                    self.status_bar.config(text=f"Swapped {attr1} and {attr2}")
                    self.update_previews()
                else:
                    messagebox.showerror("Error", "Failed to swap attributes")
        except Exception as e:
            messagebox.showerror("Error", f"Error swapping attributes: {str(e)}")
            logger.error(f"Error swapping attributes: {e}")
            logger.error(traceback.format_exc())
            
    def process_multiple_files(self, operation, attr1, attr2, all_waypoints=False, save_after=False):
        """Process multiple files with the same operation"""
        file_paths = filedialog.askopenfilenames(
            title="Select GPX Files to Process",
            filetypes=[("GPX files", "*.gpx"), ("All files", "*.*")]
        )
        
        if not file_paths:
            return
            
        modified_states = []
        
        # Process each file
        for file_path in file_paths:
            try:
                # Create a new editor for each file
                editor = GPXEditor()
                
                # Create backup
                backup_path = editor.create_backup(file_path)
                logger.debug(f"Created backup at: {backup_path}")
                
                # Load file
                if not editor.load_gpx(file_path):
                    logger.error(f"Failed to load file: {file_path}")
                    continue
                    
                # Perform operation
                success = False
                if operation == "copy":
                    if all_waypoints:
                        success = editor.copy_attribute_all(attr1, attr2)
                    else:
                        success = editor.copy_attribute(attr1, attr2)
                elif operation == "swap":
                    if all_waypoints:
                        success = editor.swap_attributes_all(attr1, attr2)
                    else:
                        success = editor.swap_attributes(attr1, attr2)
                        
                if success:
                    if save_after:
                        # Save directly to original file
                        if editor.save_gpx(file_path):
                            logger.debug(f"Saved changes to: {file_path}")
                        else:
                            logger.error(f"Failed to save changes to: {file_path}")
                    else:
                        # Add to list of modified states
                        modified_states.append({
                            'path': file_path,
                            'state': editor.current_state
                        })
                else:
                    logger.error(f"Operation failed for file: {file_path}")
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                logger.error(traceback.format_exc())
                
        # If we have modified states and not saving directly, ask where to save them
        if modified_states and not save_after:
            self.save_modified_states(modified_states, operation)
            
    def save_modified_states(self, modified_states, operation):
        """Save a list of modified states to files"""
        # Ask for output directory
        output_dir = filedialog.askdirectory(
            title="Select Output Directory"
        )
        
        if not output_dir:
            return
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save each modified state
        success_count = 0
        error_count = 0
        
        for item in modified_states:
            try:
                file_path = item['path']
                state = item['state']
                
                # Create output path
                basename = os.path.basename(file_path)
                output_path = os.path.join(output_dir, basename)
                
                # Convert dict back to XML
                xml_str = xmltodict.unparse(state)
                with open(output_path, 'w') as f:
                    f.write(xml_str)
                    
                success_count += 1
                logger.debug(f"Saved modified state to: {output_path}")
            except Exception as e:
                logger.error(f"Error saving modified state: {e}")
                logger.error(traceback.format_exc())
                error_count += 1
        
        # Show results
        if success_count > 0:
            messagebox.showinfo("Batch Save Complete", 
                             f"Successfully saved {success_count} files.\n"
                             f"Failed to save {error_count} files.")
            logger.debug(f"Batch save completed: {success_count} successful, {error_count} failed")
            return True
        else:
            messagebox.showerror("Batch Save Failed", 
                              f"Failed to save any files. Errors occurred in {error_count} files.")
            logger.debug(f"Batch save failed: {error_count} errors")
            return False


def main():
    """Launch the GPX Editor GUI."""
    app = GPXEditorGUI()
    app.root.mainloop()


if __name__ == "__main__":
    main()
