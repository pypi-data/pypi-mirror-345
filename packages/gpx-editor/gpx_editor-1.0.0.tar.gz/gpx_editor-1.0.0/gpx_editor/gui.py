"""GUI module for the GPX Editor."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import logging
import traceback
import json
from .editor import GPXEditor

# Set up logging
logger = logging.getLogger(__name__)

class GPXEditorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GPX Editor")
        self.root.geometry("900x700")
        
        # Initialize variables
        self.editor = GPXEditor()
        self.editor.add_history_listener(self.update_history_display)
        self.selected_files = []  # List to store selected files
        self.current_file_index = -1  # Index of currently loaded file
        self.operations_performed = []  # Track operations for batch saving
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface following the correct operation order."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Select File(s)", command=self.select_files)
        file_menu.add_command(label="Save Current File", command=self.save_current_file)
        file_menu.add_command(label="Save All Modified Files", command=self.save_all_files)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self.editor.undo)
        edit_menu.add_command(label="Redo", command=self.editor.redo)
        
        # Create a paned window for the main interface
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - File selection and navigation
        left_panel = ttk.Frame(paned_window, padding="5")
        paned_window.add(left_panel, weight=1)
        
        # Right panel - Operations and attribute viewing
        right_panel = ttk.Frame(paned_window, padding="5")
        paned_window.add(right_panel, weight=3)
        
        # Set up left panel (file selection)
        self.setup_file_panel(left_panel)
        
        # Set up right panel (operations)
        self.setup_operations_panel(right_panel)
        
        # Status bar
        self.status_bar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_file_panel(self, parent):
        """Set up the file selection and navigation panel"""
        # File selection frame
        file_frame = ttk.LabelFrame(parent, text="Selected Files", padding="5")
        file_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Button to select files
        select_btn = ttk.Button(file_frame, text="Select File(s)", command=self.select_files)
        select_btn.pack(fill=tk.X, pady=5)
        
        # Create a frame for the listbox and scrollbar
        list_frame = ttk.Frame(file_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add listbox for selected files
        self.file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        # Configure scrollbar
        scrollbar.config(command=self.file_listbox.yview)
        
        # File action buttons
        btn_frame = ttk.Frame(file_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Remove Selected", 
                  command=self.remove_selected_file).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Clear All", 
                  command=self.clear_files).pack(side=tk.LEFT, padx=2)
        
        # File info frame
        info_frame = ttk.LabelFrame(parent, text="File Information", padding="5")
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Current file info
        ttk.Label(info_frame, text="Current File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.current_file_var = tk.StringVar(value="None")
        ttk.Label(info_frame, textvariable=self.current_file_var, wraplength=200).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # File count
        ttk.Label(info_frame, text="Total Files:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.file_count_var = tk.StringVar(value="0")
        ttk.Label(info_frame, textvariable=self.file_count_var).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Modified status
        ttk.Label(info_frame, text="Modified:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.modified_var = tk.StringVar(value="No")
        ttk.Label(info_frame, textvariable=self.modified_var).grid(row=2, column=1, sticky=tk.W, pady=2)
        
    def setup_operations_panel(self, parent):
        """Set up the operations and attribute viewing panel"""
        # Create notebook for operations
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Attributes tab
        attr_tab = ttk.Frame(notebook, padding="5")
        notebook.add(attr_tab, text="Attributes")
        
        # Preview tab
        preview_tab = ttk.Frame(notebook, padding="5")
        notebook.add(preview_tab, text="Preview")
        
        # History tab
        history_tab = ttk.Frame(notebook, padding="5")
        notebook.add(history_tab, text="History")
        
        # Set up each tab
        self.setup_attribute_tab(attr_tab)
        self.setup_preview_tab(preview_tab)
        self.setup_history_tab(history_tab)
        
    def setup_attribute_tab(self, parent):
        """Set up the attribute tab with operations"""
        # Create frame for attribute selection
        attr_select_frame = ttk.LabelFrame(parent, text="Attribute Selection", padding="10")
        attr_select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Source attribute
        ttk.Label(attr_select_frame, text="Source Attribute:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_attr = ttk.Combobox(attr_select_frame, width=30)
        self.source_attr.grid(row=0, column=1, sticky=tk.W, pady=5)
        self.source_attr.bind("<<ComboboxSelected>>", self.on_attribute_select)
        
        # Target attribute
        ttk.Label(attr_select_frame, text="Target Attribute:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.target_attr = ttk.Combobox(attr_select_frame, width=30)
        self.target_attr.grid(row=1, column=1, sticky=tk.W, pady=5)
        self.target_attr.bind("<<ComboboxSelected>>", self.on_attribute_select)
        
        # Create frame for operation selection
        op_frame = ttk.LabelFrame(parent, text="Operation Selection", padding="10")
        op_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Operation type
        self.operation_var = tk.StringVar(value="copy")
        ttk.Radiobutton(op_frame, text="Copy Attribute", 
                       variable=self.operation_var, value="copy").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(op_frame, text="Swap Attributes", 
                       variable=self.operation_var, value="swap").grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # All waypoints option
        self.all_waypoints_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(op_frame, text="Apply to all waypoints", 
                       variable=self.all_waypoints_var).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Operation execution
        exec_frame = ttk.Frame(op_frame)
        exec_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(exec_frame, text="Execute Operation", 
                  command=self.execute_operation).pack(pady=10)
        
        # Save options
        save_frame = ttk.LabelFrame(parent, text="Save Options", padding="10")
        save_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(save_frame, text="Save Current File", 
                  command=self.save_current_file).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(save_frame, text="Save All Modified Files", 
                  command=self.save_all_files).grid(row=0, column=1, padx=5, pady=5)
                  
    def setup_preview_tab(self, parent):
        """Set up the attribute preview tab"""
        # Create frame for attribute preview
        preview_frame = ttk.Frame(parent, padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Preview controls
        control_frame = ttk.Frame(preview_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(control_frame, text="Attribute to Preview:").pack(side=tk.LEFT, padx=5)
        self.preview_attr = ttk.Combobox(control_frame, width=30)
        self.preview_attr.pack(side=tk.LEFT, padx=5)
        self.preview_attr.bind("<<ComboboxSelected>>", self.update_preview)
        
        ttk.Button(control_frame, text="Refresh Preview", 
                  command=self.update_preview).pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the preview content
        content_frame = ttk.LabelFrame(preview_frame, text="Attribute Value", padding="10")
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(content_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add text widget for preview
        self.preview_text = tk.Text(content_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        self.preview_text.config(state=tk.DISABLED)  # Read-only
        
        # Configure scrollbar
        scrollbar.config(command=self.preview_text.yview)
        
        # Batch preview button
        ttk.Button(preview_frame, text="Show Batch Preview", 
                  command=self.show_batch_preview).pack(pady=10)
        
    def setup_history_tab(self, parent):
        """Set up the history tab"""
        # Create frame for history
        history_frame = ttk.Frame(parent, padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # History list
        ttk.Label(history_frame, text="Operation History:").pack(anchor=tk.W, pady=5)
        
        # Create a frame for the listbox and scrollbar
        list_frame = ttk.Frame(history_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add listbox
        self.history_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbar
        scrollbar.config(command=self.history_listbox.yview)
        
        # Buttons
        button_frame = ttk.Frame(history_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Undo", 
                  command=self.editor.undo).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Redo", 
                  command=self.editor.redo).pack(side=tk.LEFT, padx=5)
        
    # File handling methods
    def select_files(self):
        """Select one or more GPX files"""
        file_paths = filedialog.askopenfilenames(
            title="Select GPX File(s)",
            filetypes=[("GPX files", "*.gpx"), ("All files", "*.*")]
        )
        
        if not file_paths:
            return
            
        # Add files to the list
        for path in file_paths:
            if path not in self.selected_files:
                self.selected_files.append(path)
                self.file_listbox.insert(tk.END, os.path.basename(path))
                
        # Update file count
        self.file_count_var.set(str(len(self.selected_files)))
        
        # Load the first file if no file is currently loaded
        if self.current_file_index == -1 and self.selected_files:
            self.load_file(0)
            
        self.status_bar.config(text=f"Selected {len(file_paths)} file(s)")
        
    def on_file_select(self, event):
        """Handle file selection from the listbox"""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            self.load_file(index)
            
    def load_file(self, index):
        """Load a file by index from the selected files list"""
        if 0 <= index < len(self.selected_files):
            file_path = self.selected_files[index]
            
            try:
                # Create backup
                backup_path = self.editor.create_backup(file_path)
                self.status_bar.config(text=f"Backup created at: {backup_path}")
                
                # Load file
                if self.editor.load_gpx(file_path):
                    self.current_file_index = index
                    self.current_file_var.set(os.path.basename(file_path))
                    self.status_bar.config(text=f"Loaded: {file_path}")
                    self.modified_var.set("No")
                    
                    # Update attributes
                    self.update_attributes()
                    
                    # Update window title
                    self.root.title(f"GPX Editor - {os.path.basename(file_path)}")
                    
                    # Highlight the selected file in the listbox
                    self.file_listbox.selection_clear(0, tk.END)
                    self.file_listbox.selection_set(index)
                    self.file_listbox.see(index)
                else:
                    messagebox.showerror("Error", f"Failed to load file: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading file: {e}")
                logger.error(f"Error loading file: {e}")
                logger.error(traceback.format_exc())
                
    def remove_selected_file(self):
        """Remove the selected file from the list"""
        selection = self.file_listbox.curselection()
        if not selection:
            return
            
        index = selection[0]
        file_path = self.selected_files[index]
        
        # Remove from list and listbox
        self.selected_files.pop(index)
        self.file_listbox.delete(index)
        
        # Update file count
        self.file_count_var.set(str(len(self.selected_files)))
        
        # Update current file if needed
        if self.current_file_index == index:
            # We removed the current file
            if self.selected_files:
                # Load another file
                new_index = min(index, len(self.selected_files) - 1)
                self.load_file(new_index)
            else:
                # No files left
                self.current_file_index = -1
                self.current_file_var.set("None")
                self.modified_var.set("No")
                self.root.title("GPX Editor")
        elif self.current_file_index > index:
            # Adjust current file index
            self.current_file_index -= 1
            
        self.status_bar.config(text=f"Removed file: {os.path.basename(file_path)}")
        
    def clear_files(self):
        """Clear all files from the list"""
        if not self.selected_files:
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all files?"):
            self.selected_files = []
            self.file_listbox.delete(0, tk.END)
            self.file_count_var.set("0")
            self.current_file_index = -1
            self.current_file_var.set("None")
            self.modified_var.set("No")
            self.root.title("GPX Editor")
            self.status_bar.config(text="All files cleared")
            
    def get_current_file_path(self):
        """Get the path of the currently loaded file"""
        if 0 <= self.current_file_index < len(self.selected_files):
            return self.selected_files[self.current_file_index]
        return None
        
    def update_attributes(self):
        """Update the attribute comboboxes with available attributes"""
        all_attributes = self.editor.get_all_attributes()
        
        # Extract attribute names for display
        attribute_names = [attr['name'] for attr in all_attributes]
        self.preview_attr['values'] = attribute_names
        
        # Filter editable attributes for source and target
        editable_attributes = [attr['name'] for attr in all_attributes if attr['editable']]
        self.source_attr['values'] = editable_attributes
        self.target_attr['values'] = editable_attributes
        
        # Store attribute info for reference
        self.attribute_info = {attr['name']: attr for attr in all_attributes}
        
        # Set default values if available
        if editable_attributes:
            if not self.source_attr.get() or self.source_attr.get() not in editable_attributes:
                self.source_attr.set(editable_attributes[0])
            if not self.target_attr.get() or self.target_attr.get() not in editable_attributes:
                if len(editable_attributes) > 1:
                    self.target_attr.set(editable_attributes[1])
                else:
                    self.target_attr.set(editable_attributes[0])
        
        if attribute_names:
            if not self.preview_attr.get() or self.preview_attr.get() not in attribute_names:
                self.preview_attr.set(attribute_names[0])
                
            # Update preview
            self.update_preview()
                    
    def update_history_display(self):
        """Update the history display"""
        self.history_listbox.delete(0, tk.END)
        
        # Add history items
        for i, _ in enumerate(self.editor.history):
            self.history_listbox.insert(tk.END, f"Operation {i+1}")
            
        # Highlight current state
        current_index = len(self.editor.history) - 1
        if current_index >= 0:
            self.history_listbox.selection_set(current_index)
            self.history_listbox.see(current_index)
            
        # Update modified status
        if len(self.editor.history) > 1:
            self.modified_var.set("Yes")
        else:
            self.modified_var.set("No")
            
    # Attribute handling methods
    def on_attribute_select(self, event=None):
        """Handle attribute selection"""
        # Update preview when attributes are selected
        self.update_preview()
        
    def update_preview(self, event=None):
        """Update the attribute preview"""
        if self.current_file_index == -1:
            return
            
        attr = self.preview_attr.get()
        if not attr:
            return
            
        try:
            # Get the current waypoint
            if not self.editor.current_state or not self.editor.current_waypoint:
                return
                
            # Enable text widget for editing
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete(1.0, tk.END)
            
            # Display attribute value
            if attr in self.editor.current_waypoint:
                value = self.editor.current_waypoint[attr]
                self.preview_text.insert(tk.END, str(value))
            else:
                self.preview_text.insert(tk.END, "(Attribute not found in current waypoint)")
                
            # Disable text widget again
            self.preview_text.config(state=tk.DISABLED)
        except Exception as e:
            logger.error(f"Error updating preview: {e}")
            logger.error(traceback.format_exc())
            
    def show_batch_preview(self):
        """Show a preview of the selected attribute across all files"""
        if not self.selected_files:
            messagebox.showinfo("Info", "No files selected")
            return
            
        attr = self.preview_attr.get()
        if not attr:
            messagebox.showinfo("Info", "No attribute selected for preview")
            return
            
        # Create a new window for batch preview
        preview_window = tk.Toplevel(self.root)
        preview_window.title(f"Batch Preview: {attr}")
        preview_window.geometry("600x400")
        preview_window.transient(self.root)  # Set as transient to main window
        
        # Create a frame for the preview
        frame = ttk.Frame(preview_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a scrolled text widget
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text = tk.Text(frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=text.yview)
        
        # Populate with attribute values from all files
        current_editor = self.editor  # Save current editor
        current_file_index = self.current_file_index  # Save current file index
        
        for i, file_path in enumerate(self.selected_files):
            try:
                # Create a temporary editor for each file
                temp_editor = GPXEditor()
                if temp_editor.load_gpx(file_path):
                    # Get the first waypoint
                    if 'gpx' in temp_editor.current_state and 'wpt' in temp_editor.current_state['gpx']:
                        wpt = temp_editor.current_state['gpx']['wpt']
                        if isinstance(wpt, list) and wpt:
                            waypoint = wpt[0]
                        elif isinstance(wpt, dict):
                            waypoint = wpt
                        else:
                            waypoint = None
                            
                        if waypoint and attr in waypoint:
                            value = waypoint[attr]
                            text.insert(tk.END, f"File: {os.path.basename(file_path)}\n")
                            text.insert(tk.END, f"Value: {value}\n\n")
                        else:
                            text.insert(tk.END, f"File: {os.path.basename(file_path)}\n")
                            text.insert(tk.END, f"Value: (Attribute not found)\n\n")
                    else:
                        text.insert(tk.END, f"File: {os.path.basename(file_path)}\n")
                        text.insert(tk.END, f"Value: (No waypoints found)\n\n")
                else:
                    text.insert(tk.END, f"File: {os.path.basename(file_path)}\n")
                    text.insert(tk.END, f"Value: (Failed to load file)\n\n")
            except Exception as e:
                text.insert(tk.END, f"File: {os.path.basename(file_path)}\n")
                text.insert(tk.END, f"Error: {str(e)}\n\n")
                logger.error(f"Error previewing file {file_path}: {e}")
                
        # Make text read-only
        text.config(state=tk.DISABLED)
        
        # Add close button
        ttk.Button(frame, text="Close", command=preview_window.destroy).pack(pady=10)
        
    # Operation execution methods
    def execute_operation(self):
        """Execute the selected operation on the current file"""
        if self.current_file_index == -1:
            messagebox.showinfo("Info", "No file loaded")
            return
            
        source_attr = self.source_attr.get()
        target_attr = self.target_attr.get()
        
        if not source_attr or not target_attr:
            messagebox.showerror("Error", "Please select source and target attributes")
            return
            
        # Check if attributes are editable
        if source_attr not in self.editor.EDITABLE_ATTRIBUTES:
            messagebox.showerror("Error", f"The attribute '{source_attr}' is read-only and cannot be modified")
            return
            
        if target_attr not in self.editor.EDITABLE_ATTRIBUTES:
            messagebox.showerror("Error", f"The attribute '{target_attr}' is read-only and cannot be modified")
            return
            
        operation = self.operation_var.get()
        all_waypoints = self.all_waypoints_var.get()
        
        try:
            success = False
            if operation == "copy":
                if all_waypoints:
                    success = self.editor.copy_attribute_all(source_attr, target_attr)
                else:
                    success = self.editor.copy_attribute(source_attr, target_attr)
                    
                if success:
                    op_desc = f"Copied {source_attr} to {target_attr}"
            else:  # swap
                if all_waypoints:
                    success = self.editor.swap_attributes_all(source_attr, target_attr)
                else:
                    success = self.editor.swap_attributes(source_attr, target_attr)
                    
                if success:
                    op_desc = f"Swapped {source_attr} and {target_attr}"
                    
            if success:
                # Record the operation for batch processing
                self.operations_performed.append({
                    'operation': operation,
                    'source_attr': source_attr,
                    'target_attr': target_attr,
                    'all_waypoints': all_waypoints
                })
                
                self.status_bar.config(text=op_desc)
                self.modified_var.set("Yes")
                
                # Update preview
                self.update_preview()
                
                messagebox.showinfo("Success", op_desc)
            else:
                messagebox.showerror("Error", "Operation failed")
        except Exception as e:
            messagebox.showerror("Error", f"Error executing operation: {e}")
            logger.error(f"Error executing operation: {e}")
            logger.error(traceback.format_exc())
            
    # Save methods
    def save_current_file(self):
        """Save the current file"""
        if self.current_file_index == -1:
            messagebox.showinfo("Info", "No file loaded")
            return
            
        current_path = self.selected_files[self.current_file_index]
        
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            title="Save GPX File",
            initialfile=os.path.basename(current_path),
            defaultextension=".gpx",
            filetypes=[("GPX files", "*.gpx")]
        )
        
        if not file_path:
            return
            
        try:
            if self.editor.save_gpx(file_path):
                self.status_bar.config(text=f"Saved: {file_path}")
                self.modified_var.set("No")
                messagebox.showinfo("Success", f"File saved to: {file_path}")
                
                # Update the file list if saving to a new location
                if file_path != current_path:
                    self.selected_files[self.current_file_index] = file_path
                    self.file_listbox.delete(self.current_file_index)
                    self.file_listbox.insert(self.current_file_index, os.path.basename(file_path))
                    self.file_listbox.selection_set(self.current_file_index)
                    self.current_file_var.set(os.path.basename(file_path))
            else:
                messagebox.showerror("Error", "Failed to save file")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving file: {e}")
            logger.error(f"Error saving file: {e}")
            logger.error(traceback.format_exc())
            
    def save_all_files(self):
        """Save all modified files"""
        if not self.selected_files:
            messagebox.showinfo("Info", "No files selected")
            return
            
        if not self.operations_performed:
            messagebox.showinfo("Info", "No operations performed")
            return
            
        # Ask for output directory
        output_dir = filedialog.askdirectory(
            title="Select Output Directory for Modified Files"
        )
        
        if not output_dir:
            return
            
        # Ask for filename prefix/suffix
        prefix_suffix_window = tk.Toplevel(self.root)
        prefix_suffix_window.title("Filename Options")
        prefix_suffix_window.geometry("400x200")
        prefix_suffix_window.transient(self.root)  # Set as transient to main window
        prefix_suffix_window.grab_set()  # Make window modal
        
        frame = ttk.Frame(prefix_suffix_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Prefix
        ttk.Label(frame, text="Filename Prefix:").grid(row=0, column=0, sticky=tk.W, pady=5)
        prefix_var = tk.StringVar()
        ttk.Entry(frame, textvariable=prefix_var).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Suffix
        ttk.Label(frame, text="Filename Suffix:").grid(row=1, column=0, sticky=tk.W, pady=5)
        suffix_var = tk.StringVar()
        ttk.Entry(frame, textvariable=suffix_var).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Result
        result = {'prefix': '', 'suffix': '', 'confirmed': False}
        
        def on_confirm():
            result['prefix'] = prefix_var.get()
            result['suffix'] = suffix_var.get()
            result['confirmed'] = True
            prefix_suffix_window.destroy()
            
        def on_cancel():
            prefix_suffix_window.destroy()
            
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Confirm", command=on_confirm).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).grid(row=0, column=1, padx=5)
        
        # Wait for the window to close
        self.root.wait_window(prefix_suffix_window)
        
        if not result['confirmed']:
            return
            
        # Process each file
        success_count = 0
        error_count = 0
        
        # Save current editor and file index
        current_editor = self.editor
        current_file_index = self.current_file_index
        
        for i, file_path in enumerate(self.selected_files):
            try:
                # Create a new editor for each file
                editor = GPXEditor()
                
                # Load file
                if not editor.load_gpx(file_path):
                    logger.error(f"Failed to load file: {file_path}")
                    error_count += 1
                    continue
                    
                # Apply all operations
                file_modified = False
                for op in self.operations_performed:
                    # Check if attributes are editable
                    source_attr = op['source_attr']
                    target_attr = op['target_attr']
                    
                    if source_attr not in self.editor.EDITABLE_ATTRIBUTES or target_attr not in self.editor.EDITABLE_ATTRIBUTES:
                        logger.warning(f"Skipping operation with read-only attributes: {source_attr}, {target_attr}")
                        continue
                    
                    success = False
                    if op['operation'] == "copy":
                        if op['all_waypoints']:
                            success = editor.copy_attribute_all(source_attr, target_attr)
                        else:
                            success = editor.copy_attribute(source_attr, target_attr)
                    else:  # swap
                        if op['all_waypoints']:
                            success = editor.swap_attributes_all(source_attr, target_attr)
                        else:
                            success = editor.swap_attributes(source_attr, target_attr)
                            
                    if success:
                        file_modified = True
                        
                if file_modified:
                    # Create output filename with prefix/suffix
                    basename = os.path.basename(file_path)
                    name, ext = os.path.splitext(basename)
                    new_name = f"{result['prefix']}{name}{result['suffix']}{ext}"
                    output_path = os.path.join(output_dir, new_name)
                    
                    # Save file
                    if editor.save_gpx(output_path):
                        success_count += 1
                        logger.info(f"Saved modified file to: {output_path}")
                    else:
                        error_count += 1
                        logger.error(f"Failed to save file: {output_path}")
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing file {file_path}: {e}")
                logger.error(traceback.format_exc())
                
        # Restore current editor and file index
        self.editor = current_editor
        self.current_file_index = current_file_index
        
        # Show results
        if success_count > 0:
            messagebox.showinfo("Success", f"Saved {success_count} modified files to {output_dir}\n\nErrors: {error_count}")
        else:
            messagebox.showerror("Error", f"Failed to save any modified files\n\nErrors: {error_count}")
            
        # Update status
        self.status_bar.config(text=f"Batch save completed: {success_count} successful, {error_count} failed")
            
    # Main function to run the application
    def main(self):
        """Main function to run the GUI application"""
        self.root.mainloop()
        
    # Helper method to mark a file as modified
    def mark_as_modified(self):
        """Mark the current file as modified"""
        if 0 <= self.current_file_index < len(self.selected_files):
            self.modified_var.set("Yes")
            
            # Update window title to indicate modification
            file_name = os.path.basename(self.selected_files[self.current_file_index])
            self.root.title(f"GPX Editor - {file_name} *")

# Main function to run the application
def main():
    """Main function to run the GUI application"""
    app = GPXEditorGUI()
    app.root.mainloop()
    
if __name__ == "__main__":
    main()
