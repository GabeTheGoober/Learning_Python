import sys
import time
import math
import os
import psutil
import pymem
import pymem.process
import ctypes
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QLineEdit, QComboBox, QAbstractItemView,
    QListWidgetItem, QGroupBox, QSplitter, QStatusBar, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPalette, QFont, QIntValidator, QIcon, QFontDatabase


class MemoryEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        # ===========================[ Window Setup ]===========================
        self.setWindowTitle("G's Python Cheat Engine")
        self.setMinimumSize(1000, 800)
        
        # ===========================[ Application State ]===========================
        # Store the currently selected process and its name
        self.selected_process = None
        self.selected_process_name = None
        
        # Store scan results and current scan parameters
        self.scan_results = []        # List of memory addresses from scan
        self.current_scan_value = None # The value we're currently scanning for
        self.data_type = "int"         # Default data type for scanning
        
        # Pymem instance for memory access
        self.pm = None
        
        # ===========================[ UI Initialization ]===========================
        # Apply dark theme with green accents
        self.set_dark_theme()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Add application title
        self.create_title(main_layout)
        
        # Create main content area with splitter
        self.create_main_content(main_layout)
        
        # Create status bar
        self.create_status_bar()
        
        # Initial process list refresh
        self.refresh_process_list()
        
        # Update status message
        self.update_status("Ready. Select a process to begin.")
    
    # ===========================[ UI Creation Methods ]===========================
    def set_dark_theme(self):
        """Apply a dark theme with hacker-style green accents to the application"""
        # Create a dark palette
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(40, 40, 40))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(50, 50, 50))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 128, 0))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        self.setPalette(dark_palette)
        
        # Apply custom styles for a hacker/cheat engine look
        self.setStyleSheet("""
            /* Group box styling */
            QGroupBox {
                border: 2px solid #00fb09; /* Bright green border */
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
                color: #00fb09; /* Bright green text */
                background-color: rgba(40, 40, 40, 200); /* Semi-transparent dark background */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: transparent;
            }
            
            /* List widget styling */
            QListWidget {
                background-color: rgba(30, 30, 30, 200);
                color: #e0e0e0; /* Light gray text */
                border: 1px solid #333;
                border-radius: 3px;
                font-family: 'Courier New'; /* Monospace for addresses */
            }
            QListWidget::item:selected {
                background-color: #008000; /* Dark green selection */
                color: white;
            }
            
            /* Input field styling */
            QLineEdit, QComboBox {
                background-color: rgba(30, 30, 30, 200);
                color: white;
                border: 1px solid #333;
                border-radius: 3px;
                padding: 3px;
                font-family: 'Courier New'; /* Monospace font */
            }
            
            /* Button styling */
            QPushButton {
                background-color: #4CAF50; /* Green */
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-family: 'Courier New';
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049; /* Slightly darker green on hover */
            }
            QPushButton:disabled {
                background-color: #2E7D32; /* Dark green when disabled */
                color: #aaa; /* Gray text when disabled */
            }
            
            /* Special button types */
            QPushButton#scanButton {
                background-color: #2196F3; /* Blue for scan buttons */
            }
            QPushButton#scanButton:hover {
                background-color: #0b7dda; /* Darker blue on hover */
            }
            QPushButton#modifyButton {
                background-color: #FF9800; /* Orange for modify button */
                color: black;
            }
            QPushButton#modifyButton:hover {
                background-color: #F57C00; /* Darker orange on hover */
            }
        """)
    
    def create_title(self, layout):
        """Create and add the application title to the layout"""
        title = QLabel("G's Python Cheat Engine")
        title.setFont(QFont("Courier New", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #00fb09;")  # Bright green
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Add a separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #00fb09; height: 2px;")
        layout.addWidget(separator)
    
    def create_main_content(self, layout):
        """Create the main content area with split panels"""
        # Create a horizontal splitter for left and right panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter, 1)  # Takes most of the space
        
        # Create left panel (process selection)
        left_panel = self.create_process_panel()
        splitter.addWidget(left_panel)
        
        # Create right panel (memory editor)
        right_panel = self.create_memory_panel()
        splitter.addWidget(right_panel)
        
        # Set initial sizes for the splitter
        splitter.setSizes([300, 700])  # Left: 30%, Right: 70%
    
    def create_process_panel(self):
        """Create the process selection panel"""
        # Create group box container
        panel = QGroupBox("Process Selection")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(10, 20, 10, 10)
        panel_layout.setSpacing(10)
        
        # =====[ Process List ]=====
        self.process_list = QListWidget()
        self.process_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        panel_layout.addWidget(self.process_list)
        
        # =====[ Button Row ]=====
        button_layout = QHBoxLayout()
        
        # Refresh button
        refresh_btn = QPushButton("⟳ Refresh List")
        refresh_btn.clicked.connect(self.refresh_process_list)
        button_layout.addWidget(refresh_btn)
        
        # Select button
        self.select_btn = QPushButton("Select Process")
        self.select_btn.setEnabled(False)  # Disabled until process is selected
        self.select_btn.clicked.connect(self.select_process)
        button_layout.addWidget(self.select_btn)
        
        panel_layout.addLayout(button_layout)
        
        return panel
    
    def create_memory_panel(self):
        """Create the memory editor panel"""
        # Create group box container
        panel = QGroupBox("Memory Editor")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(10, 20, 10, 10)
        panel_layout.setSpacing(10)
        
        # =====[ Process Info Display ]=====
        self.process_info = QLabel("No process selected")
        self.process_info.setStyleSheet("font-size: 14px; color: #FF9800;")  # Amber color
        self.process_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        panel_layout.addWidget(self.process_info)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #00fb09; height: 1px;")
        panel_layout.addWidget(separator)
        
        # =====[ Scan Controls ]=====
        scan_layout = QHBoxLayout()
        
        # --- Value Input ---
        value_layout = QVBoxLayout()
        value_layout.addWidget(QLabel("Value to Scan:"))
        self.value_input = QLineEdit()
        self.value_input.setValidator(QIntValidator())  # Only numbers allowed
        self.value_input.setPlaceholderText("Enter value...")
        value_layout.addWidget(self.value_input)
        scan_layout.addLayout(value_layout)
        
        # --- Data Type Selector ---
        type_layout = QVBoxLayout()
        type_layout.addWidget(QLabel("Data Type:"))
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["int", "float", "string", "byte"])
        type_layout.addWidget(self.data_type_combo)
        scan_layout.addLayout(type_layout)
        
        # --- Scan Buttons ---
        # First Scan button
        self.first_scan_btn = QPushButton("First Scan")
        self.first_scan_btn.setObjectName("scanButton")  # For custom styling
        self.first_scan_btn.setEnabled(False)  # Disabled until process is selected
        self.first_scan_btn.clicked.connect(self.first_scan)
        scan_layout.addWidget(self.first_scan_btn)
        
        # Next Scan button
        self.next_scan_btn = QPushButton("Next Scan")
        self.next_scan_btn.setObjectName("scanButton")  # For custom styling
        self.next_scan_btn.setEnabled(False)  # Disabled until first scan is done
        self.next_scan_btn.clicked.connect(self.next_scan)
        scan_layout.addWidget(self.next_scan_btn)
        
        panel_layout.addLayout(scan_layout)
        
        # =====[ Scan Results ]=====
        results_layout = QVBoxLayout()
        results_layout.addWidget(QLabel("Scan Results:"))
        self.results_list = QListWidget()
        self.results_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.results_list.itemSelectionChanged.connect(self.enable_modify_button)
        results_layout.addWidget(self.results_list)
        panel_layout.addLayout(results_layout)
        
        # =====[ Modification Controls ]=====
        modify_layout = QHBoxLayout()
        
        # --- Address Display ---
        address_layout = QVBoxLayout()
        address_layout.addWidget(QLabel("Selected Address:"))
        self.address_display = QLineEdit()
        self.address_display.setReadOnly(True)  # Display only, not editable
        address_layout.addWidget(self.address_display)
        modify_layout.addLayout(address_layout)
        
        # --- New Value Input ---
        new_value_layout = QVBoxLayout()
        new_value_layout.addWidget(QLabel("New Value:"))
        self.new_value_input = QLineEdit()
        self.new_value_input.setPlaceholderText("Enter new value...")
        new_value_layout.addWidget(self.new_value_input)
        modify_layout.addLayout(new_value_layout)
        
        # --- Modify Button ---
        self.modify_btn = QPushButton("Modify")
        self.modify_btn.setObjectName("modifyButton")  # For custom styling
        self.modify_btn.setEnabled(False)  # Disabled until address is selected
        self.modify_btn.clicked.connect(self.modify_value)
        modify_layout.addWidget(self.modify_btn)
        
        panel_layout.addLayout(modify_layout)
        
        return panel
    
    def create_status_bar(self):
        """Create and configure the status bar"""
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #1e1e1e;
                color: #00fb09; /* Bright green text */
                font-size: 12px;
                border-top: 1px solid #333;
                font-family: 'Courier New';
            }
        """)
        self.setStatusBar(self.status_bar)
    
    # ===========================[ Core Functionality Methods ]===========================
    def refresh_process_list(self):
        """Refresh the list of running processes"""
        # Clear existing items
        self.process_list.clear()
        
        # Show status message
        self.update_status("Refreshing process list...")
        QApplication.processEvents()  # Update UI immediately
        
        # Get list of all running processes
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                # Extract process information
                name = proc.info['name']
                pid = proc.info['pid']
                exe_path = proc.info['exe']
                processes.append((name, pid, exe_path))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Skip processes we can't access
                pass
        
        # Sort processes by name
        processes.sort(key=lambda x: x[0].lower())
        
        # Add processes to the list widget
        for name, pid, exe_path in processes:
            item = QListWidgetItem(f"{name} (PID: {pid})")
            item.setData(Qt.ItemDataRole.UserRole, (pid, name))
            
            # Add application icon if available
            if exe_path and os.path.exists(exe_path):
                try:
                    icon = QIcon(exe_path)
                    item.setIcon(icon)
                except:
                    # Skip if we can't load the icon
                    pass
            
            self.process_list.addItem(item)
        
        # Update status and UI
        self.update_status(f"Found {len(processes)} processes")
        self.select_btn.setEnabled(False)  # Disable until new selection
    
    def select_process(self):
        """Select the highlighted process for memory editing"""
        # Get selected item
        selected_items = self.process_list.selectedItems()
        if not selected_items:
            self.update_status("Please select a process first", error=True)
            return
            
        # Extract process info from selected item
        selected_item = selected_items[0]
        pid, name = selected_item.data(Qt.ItemDataRole.UserRole)
        
        try:
            # Close any previously opened process
            if self.pm:
                try:
                    self.pm.close_process()
                except:
                    pass
                self.pm = None
            
            # Open the selected process
            self.pm = pymem.Pymem()
            self.pm.open_process_from_id(pid)
            
            # Update application state
            self.selected_process = pid
            self.selected_process_name = name
            self.process_info.setText(f"Editing: {name} (PID: {pid})")
            
            # Clear previous scan results
            self.scan_results = []
            self.results_list.clear()
            self.address_display.clear()
            
            # Update UI state
            self.first_scan_btn.setEnabled(True)    # Enable scanning
            self.next_scan_btn.setEnabled(False)     # Not ready for next scan
            self.modify_btn.setEnabled(False)        # Nothing to modify yet
            
            # Update status
            self.update_status(f"Selected process: {name} (PID: {pid})")
        except pymem.exception.ProcessNotFound:
            self.update_status(f"Process not found: {name}", error=True)
        except pymem.exception.CouldNotOpenProcess:
            self.update_status(f"Access denied: {name}", error=True)
        except Exception as e:
            self.update_status(f"Error: {str(e)}", error=True)
    
    def first_scan(self):
        """Perform the initial memory scan for the specified value"""
        # Validate input
        if not self.value_input.text():
            self.update_status("Please enter a value to scan for", error=True)
            return
            
        try:
            # Get scan parameters
            value = int(self.value_input.text())
            data_type = self.data_type_combo.currentText()
            self.data_type = data_type
            
            # Show scanning status
            self.update_status("Scanning memory...")
            QApplication.processEvents()  # Update UI immediately
            
            # Clear previous results
            self.scan_results = []
            self.results_list.clear()
            self.address_display.clear()
            
            # Scan each module in the process
            for module in self.pm.list_modules():
                base_address = module.lpBaseOfDll
                size = module.SizeOfImage
                
                try:
                    # Read memory in chunks
                    memory_bytes = self.pm.read_bytes(base_address, size)
                    
                    # Search for the value
                    offset = 0
                    while offset < size:
                        try:
                            if data_type == "int":
                                # Convert 4 bytes to integer
                                val = int.from_bytes(memory_bytes[offset:offset+4], 'little')
                                if val == value:
                                    addr = base_address + offset
                                    self.scan_results.append(addr)
                                    self.results_list.addItem(f"0x{addr:08X} - {val}")
                            elif data_type == "float":
                                # Convert 4 bytes to float
                                val_bytes = memory_bytes[offset:offset+4]
                                val = ctypes.c_float.from_buffer(bytearray(val_bytes)).value
                                if math.isclose(val, value, abs_tol=0.1):
                                    addr = base_address + offset
                                    self.scan_results.append(addr)
                                    self.results_list.addItem(f"0x{addr:08X} - {val:.2f}")
                        except:
                            # Skip invalid memory locations
                            pass
                        offset += 4
                except:
                    # Skip modules we can't read
                    pass
            
            # Update UI and status
            self.update_status(f"Found {len(self.scan_results)} addresses")
            self.next_scan_btn.setEnabled(len(self.scan_results) > 0)
            self.modify_btn.setEnabled(False)
            
        except Exception as e:
            self.update_status(f"Scan error: {str(e)}", error=True)
    
    def next_scan(self):
        """Narrow down results by scanning for a new value"""
        # Validate input
        if not self.value_input.text():
            self.update_status("Please enter a new value to scan for", error=True)
            return
            
        try:
            # Get new scan value
            new_value = int(self.value_input.text())
            data_type = self.data_type
            
            # Show scanning status
            self.update_status("Scanning memory again...")
            QApplication.processEvents()  # Update UI immediately
            
            # Create a copy of current results to scan
            current_results = self.scan_results.copy()
            self.scan_results = []
            self.results_list.clear()
            self.address_display.clear()
            
            # Scan only the previously found addresses
            for addr in current_results:
                try:
                    if data_type == "int":
                        # Read current value at address
                        val = self.pm.read_int(addr)
                        if val == new_value:
                            self.scan_results.append(addr)
                            self.results_list.addItem(f"0x{addr:08X} - {val}")
                    elif data_type == "float":
                        # Read current float value
                        val = self.pm.read_float(addr)
                        if math.isclose(val, new_value, abs_tol=0.1):
                            self.scan_results.append(addr)
                            self.results_list.addItem(f"0x{addr:08X} - {val:.2f}")
                except:
                    # Skip addresses that are no longer accessible
                    pass
            
            # Update UI and status
            self.update_status(f"Narrowed down to {len(self.scan_results)} addresses")
            self.modify_btn.setEnabled(False)
            
        except Exception as e:
            self.update_status(f"Scan error: {str(e)}", error=True)
    
    def enable_modify_button(self):
        """Enable the modify button when an address is selected"""
        # Get selected item
        selected_items = self.results_list.selectedItems()
        if selected_items:
            # Extract address from the selected item
            selected_text = selected_items[0].text()
            addr_start = selected_text.find("0x") + 2
            addr_end = selected_text.find(" - ")
            addr = selected_text[addr_start:addr_end]
            
            # Update address display and enable modify button
            self.address_display.setText(f"0x{addr}")
            self.modify_btn.setEnabled(True)
        else:
            # Clear and disable if nothing is selected
            self.address_display.clear()
            self.modify_btn.setEnabled(False)
    
    def modify_value(self):
        """Modify the value at the selected memory address"""
        # Validate selection and input
        selected_items = self.results_list.selectedItems()
        if not selected_items:
            return
            
        if not self.new_value_input.text():
            self.update_status("Please enter a new value", error=True)
            return
            
        try:
            # Extract address from selected item
            selected_text = selected_items[0].text()
            addr_start = selected_text.find("0x") + 2
            addr_end = selected_text.find(" - ")
            addr = int(selected_text[addr_start:addr_end], 16)
            
            # Get new value and data type
            new_value = self.new_value_input.text()
            data_type = self.data_type
            
            # Write the new value to memory
            if data_type == "int":
                self.pm.write_int(addr, int(new_value))
                current_value = self.pm.read_int(addr)
            elif data_type == "float":
                self.pm.write_float(addr, float(new_value))
                current_value = self.pm.read_float(addr)
            
            # Update the list item with the new value
            if data_type == "int":
                selected_items[0].setText(f"0x{addr:08X} - {current_value}")
            else:
                selected_items[0].setText(f"0x{addr:08X} - {current_value:.2f}")
            
            # Show success message
            self.update_status(f"Changed value at 0x{addr:08X} to {current_value}")
            
        except Exception as e:
            self.update_status(f"Modify error: {str(e)}", error=True)
    
    # ===========================[ Utility Methods ]===========================
    def update_status(self, message, error=False):
        """Update the status bar with a message"""
        if error:
            # Red text for errors
            self.status_bar.setStyleSheet("color: #ff5555;")
        else:
            # Green text for normal messages
            self.status_bar.setStyleSheet("color: #00fb09;")
        
        # Show the message
        self.status_bar.showMessage(message)
    
    def closeEvent(self, event):
        """Clean up resources when the application is closed"""
        if self.pm:
            try:
                self.pm.close_process()
            except:
                pass
        event.accept()


# ===========================[ Application Entry Point ]===========================
if __name__ == '__main__':
    # Create application instance
    app = QApplication(sys.argv)
    
    # Configure monospace font for better hex display
    fixed_font = QFont("Courier New")
    fixed_font.setPointSize(10)
    app.setFont(fixed_font)
    
    # Create and show main window
    window = MemoryEditor()
    window.show()
    
    # Start application event loop
    sys.exit(app.exec())