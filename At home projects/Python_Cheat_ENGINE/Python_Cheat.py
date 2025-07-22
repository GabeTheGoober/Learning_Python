import sys
import time
import math
import os
import psutil
import pymem
import pymem.process
import ctypes
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QLabel, 
    QPushButton, QListWidget, QLineEdit, QComboBox, QHBoxLayout, QAbstractItemView,
    QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPalette, QFont, QIntValidator, QIcon


# ===========================[ Main Application Window ]===========================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Memory Editor')
        self.setMinimumSize(900, 650)
        
        # Store the currently selected process
        self.selected_process = None
        self.selected_process_name = None
        self.scan_results = []
        self.current_scan_value = None
        self.data_type = "int"
        
        # |||||||||[ Scene Management with Stacked Widget ]|||||||||
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # ||||[ Create Scene Instances with Backgrounds ]||||
        self.main_menu = MainMenu(self, QColor(0, 0, 0))                      # Black
        self.process_scanner = ProcessScanner(self, QColor(0, 20, 40))        # Dark blue
        self.memory_editor = MemoryEditor(self, QColor(20, 40, 20))           # Dark green

        # ||||[ Add Scenes to Stacked Widget ]||||
        self.stacked_widget.addWidget(self.main_menu)
        self.stacked_widget.addWidget(self.process_scanner)
        self.stacked_widget.addWidget(self.memory_editor)

        self.show()

    def switch_to_scene(self, scene_name):
        """Switch between different application scenes"""
        if scene_name == "main_menu":
            # Update main menu status when switching back
            self.main_menu.update_status()
            self.stacked_widget.setCurrentWidget(self.main_menu)
        elif scene_name == "process_scanner":
            # Refresh process list when switching to scanner
            self.process_scanner.refresh_process_list()
            self.stacked_widget.setCurrentWidget(self.process_scanner)
        elif scene_name == "memory_editor":
            self.stacked_widget.setCurrentWidget(self.memory_editor)


# ===========================[ Scene Widget Base Class ]===========================
class SceneWidget(QWidget):
    """Base class for scene widgets with solid color backgrounds"""
    def __init__(self, parent, bg_color):
        super().__init__(parent)
        self.parent = parent
        self.bg_color = bg_color

    def set_background(self):
        """Set solid color background"""
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, self.bg_color)
        self.setAutoFillBackground(True)
        self.setPalette(palette)


# ===========================[ Main Menu Scene ]===========================
class MainMenu(SceneWidget):
    def __init__(self, parent, bg_color):
        super().__init__(parent, bg_color)
        self.editor_btn = None
        self.status_label = None
        self.init_ui()

    def init_ui(self):
        # ||||[ Set background color ]||||
        self.set_background()

        # |||||[ Container outline for menu content ]|||||
        content_widget = QWidget(self)
        content_widget.setStyleSheet("""
            background-color: rgba(40, 40, 40, 220); 
            border-radius: 15px;
            border: 2px solid #00fb09; /* Bright green */
        """) # Green
        content_widget.setGeometry(100, 100, 700, 450)

        # ||||[ Title ]||||
        title = QLabel("G's Python Cheat Engine", content_widget)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet('''
            font-size: 36px; 
            font-weight: bold; 
            color: #00fb09;  /* Bright green */
            background-color: transparent;
        ''')
        title.setFont(QFont("Courier New", 24, QFont.Weight.Bold))

        # ||||[ Description ]||||
        description = QLabel('This is a Python-based memory scanner and editor,\nI am not responsible for any misuse. Have fun ;)', content_widget)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet('''
            font-size: 16px; 
            color: #FFFFFF; /* White */
            background-color: transparent;
            margin: 15px;
        ''') # White
        description.setFont(QFont("Georgia", 14, QFont.Weight.Normal))

        # ||||[ Process Scanner Button ]||||
        scanner_btn = QPushButton('Process Scanner', content_widget)
        scanner_btn.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50; /* Green */
                color: white;
                font-weight: bold;
                font-size: 18px;
                border-radius: 10px;
                padding: 15px;
                border: 2px solid #2E7D32; /* Very Dark Green */
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #45a045; /* Lighter Green */
            }
            QPushButton:disabled {
                background-color: #2E7D32; /* Dark Green */
                color: #AAAAAA;
            }
        ''')
        scanner_btn.clicked.connect(lambda: self.parent.switch_to_scene("process_scanner"))

        # ||||[ Memory Editor Button ]||||
        editor_btn = QPushButton('Memory Editor', content_widget)
        editor_btn.setStyleSheet('''
            QPushButton {
                background-color: #2196F3; /* Blue */
                color: white;
                font-weight: bold;
                font-size: 18px;
                border-radius: 10px;
                padding: 15px;
                border: 2px solid #0D47A1; /* Darker Blue */
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #0b7dda; /* Lighter Blue */
            }
            QPushButton:disabled {
                background-color: #1565C0; /* Dark Blue */
                color: #AAAAAA;
            }
        ''')
        editor_btn.clicked.connect(lambda: self.parent.switch_to_scene("memory_editor"))
        self.editor_btn = editor_btn  # Save reference to update later

        # ||||[ Status Bar ]||||
        status = QLabel("", content_widget)
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status.setStyleSheet('''
            font-size: 14px; 
            color: #FFA500; /* Orange */
            background-color: transparent;
            margin-top: 20px;
        ''')
        self.status_label = status  # Save reference to update later

        # |||||[ Layout ]|||||
        layout = QVBoxLayout(content_widget)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addSpacing(30)
        layout.addWidget(scanner_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(15)
        layout.addWidget(editor_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(30)
        layout.addWidget(status)
        layout.addStretch()
        
        # Initial status update
        self.update_status()

    def update_status(self):
        """Update the status based on selected process"""
        if self.parent.selected_process is None:
            self.status_label.setText("No process selected")
            self.editor_btn.setEnabled(False)
        else:
            name = self.parent.selected_process_name or "Unknown Process"
            self.status_label.setText(f"Selected: {name} (PID: {self.parent.selected_process})")
            self.editor_btn.setEnabled(True)


# ===========================[ Process Scanner Scene ]===========================
class ProcessScanner(SceneWidget):
    def __init__(self, parent, bg_color):
        super().__init__(parent, bg_color)
        self.init_ui()

    def init_ui(self):
        self.set_background()

        # |||||[ Container for UI ]|||||
        content_widget = QWidget(self)
        content_widget.setStyleSheet("""
            background-color: rgba(10, 30, 50, 220); 
            border-radius: 15px;
            border: 2px solid #2196F3; /* Blue */
        """)
        content_widget.setGeometry(50, 30, 800, 590)

        # ||||[ Back Button ]||||
        back_btn = QPushButton("← Back to Menu", content_widget)
        back_btn.setStyleSheet('''
            QPushButton {
                background-color: #9C27B0; /* Purple */
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px;
                border: 1px solid #7B1FA2; /* Darker Purple */ 
            }
            QPushButton:hover {
                background-color: #7B1FA2; /* Lighter Purple */
            }
        ''')
        back_btn.clicked.connect(lambda: self.parent.switch_to_scene("main_menu"))

        # ||||[ Title ]||||
        title = QLabel('Process Scanner', content_widget)
        title.setStyleSheet('''
            font-size: 28px; 
            font-weight: bold; 
            color: #FF9800; /* Orange */
            background-color: transparent;
        ''')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))

        # ||||[ Process List ]||||
        self.process_list = QListWidget(content_widget)
        self.process_list.setStyleSheet('''
            QListWidget {
                background-color: rgba(20, 40, 60, 200);
                color: #E0E0E0; /* Light gray */
                border: 1px solid #0D47A1; /* Darker blue */
                border-radius: 5px;
                font-size: 14px;
            }
            QListWidget::item:selected {
                background-color: #1976D2; /* Blue */
                color: white;
            }
        ''')
        self.process_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        # ||||[ Refresh Button ]||||
        refresh_btn = QPushButton('⟳ Refresh List', content_widget)
        refresh_btn.setStyleSheet('''
            QPushButton {
                background-color: #FF9800; /* Orange */
                color: black;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px;
                border: 1px solid #F57C00; /* Darker Orange */
            }
            QPushButton:hover {
                background-color: #F57C00; /* Lighter Orange */
            }
        ''')
        refresh_btn.clicked.connect(self.refresh_process_list)
        
        # ||||[ Select Button ]||||
        select_btn = QPushButton('Select Process', content_widget)
        select_btn.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50; /* Green */
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px 20px;
                border: 1px solid #388E3C; /* Darker Green */
            }
            QPushButton:hover {
                background-color: #45a049; /* Lighter Green */
            }
        ''')
        select_btn.clicked.connect(self.select_process)

        # ||||[ Button Layout ]||||
        button_layout = QHBoxLayout()
        button_layout.addWidget(refresh_btn)
        button_layout.addWidget(select_btn)
        
        # ||||[ Status Message ]||||
        self.status_msg = QLabel("", content_widget)
        self.status_msg.setStyleSheet('''
            font-size: 14px; 
            color: #FFEB3B; /* Yellow */
            background-color: transparent;
            padding: 5px;
        ''')
        self.status_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # |||||[ Layout ]|||||
        layout = QVBoxLayout(content_widget)
        layout.addWidget(back_btn)
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(self.process_list)
        layout.addSpacing(10)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_msg)
        layout.addStretch()
        
        # Populate process list
        self.refresh_process_list()

    def refresh_process_list(self):
        """Refresh the list of running processes with icons"""
        self.process_list.clear()
        self.status_msg.setText("Refreshing process list...")
        QApplication.processEvents()  # Update UI immediately

        # Get list of processes
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                name = proc.info['name']
                pid = proc.info['pid']
                exe_path = proc.info['exe']
                processes.append((name, pid, exe_path))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort by process name
        processes.sort(key=lambda x: x[0].lower())
        
        # Add to list widget with icons
        for name, pid, exe_path in processes:
            item = QListWidgetItem()
            
            # Try to get the icon from the executable
            icon = self.get_process_icon(exe_path)
            if icon:
                item.setIcon(icon)
                
            item.setText(f"{name} (PID: {pid})")
            item.setData(Qt.ItemDataRole.UserRole, (pid, name))  # Store both PID and name
            self.process_list.addItem(item)
        
        self.status_msg.setText(f"Found {len(processes)} processes")

    def get_process_icon(self, exe_path):
        """Get the application icon for a process"""
        if not exe_path or not os.path.exists(exe_path):
            return None
            
        try:
            # Windows icon extraction
            if sys.platform == "win32":
                # Use ExtractIconEx API for better icon handling
                from PyQt6.QtWinExtras import QtWin
                large_icon = QtWin.extractIcon(exe_path, 0, True)
                if large_icon:
                    return large_icon
                
            # Fallback method for all platforms
            return QIcon(exe_path)
        except:
            return None

    def select_process(self):
        """Select the highlighted process"""
        selected_items = self.process_list.selectedItems()
        if not selected_items:
            self.status_msg.setText("Please select a process first")
            self.status_msg.setStyleSheet('color: #F44336;')  # Red
            return
            
        selected_item = selected_items[0]
        pid, name = selected_item.data(Qt.ItemDataRole.UserRole)
        
        # Try to open the process to verify access
        try:
            pm = pymem.Pymem()
            pm.open_process_from_id(pid)
            pm.close_process()
            
            # Store selected process and name
            self.parent.selected_process = pid
            self.parent.selected_process_name = name
            
            self.status_msg.setText(f"Selected: {name} (PID: {pid})")
            self.status_msg.setStyleSheet('color: #4CAF50;') # Green
            
            # Switch back to main menu after a delay
            QTimer.singleShot(1500, lambda: self.parent.switch_to_scene("main_menu"))
            
        except pymem.exception.ProcessNotFound:
            self.status_msg.setText(f"Process not found: {name}")
            self.status_msg.setStyleSheet('color: #F44336;')  # Red
        except pymem.exception.CouldNotOpenProcess:
            self.status_msg.setText(f"Access denied: {name}")
            self.status_msg.setStyleSheet('color: #F44336;')  # Red
        except Exception as e:
            self.status_msg.setText(f"Error: {str(e)}")
            self.status_msg.setStyleSheet('color: #F44336;')  # Red 


# ===========================[ Memory Editor Scene ]===========================
class MemoryEditor(SceneWidget):
    def __init__(self, parent, bg_color):
        super().__init__(parent, bg_color)
        self.pm = None
        self.init_ui()

    def init_ui(self):
        self.set_background()

        # |||||[ Container for UI ]|||||
        content_widget = QWidget(self)
        content_widget.setStyleSheet("""
            background-color: rgba(20, 50, 30, 220); 
            border-radius: 15px;
            border: 2px solid #4CAF50; /* Green */
        """)
        content_widget.setGeometry(50, 30, 800, 590)

        # ||||[ Back Button ]||||
        back_btn = QPushButton("← Back to Menu", content_widget)
        back_btn.setStyleSheet('''
            QPushButton {
                background-color: #9C27B0; /* Purple */
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px;
                border: 1px solid #7B1FA2; /* Darker Purple */
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        ''')
        back_btn.clicked.connect(lambda: self.parent.switch_to_scene("main_menu"))

        # ||||[ Title ]||||
        title = QLabel('Memory Editor', content_widget)
        title.setStyleSheet('''
            font-size: 28px; 
            font-weight: bold; 
            color: #4CAF50; /* Green */
            background-color: transparent;
        ''')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))

        # ||||[ Process Info ]||||
        process_info = f"Editing: {self.parent.selected_process_name or 'Unknown'} (PID: {self.parent.selected_process})"
        self.process_info = QLabel(process_info, content_widget)
        self.process_info.setStyleSheet('''
            font-size: 16px; 
            color: #FF9800; /* Amber */
            background-color: transparent;
        ''')
        self.process_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ||||[ Value Input ]||||
        value_layout = QHBoxLayout()
        
        value_label = QLabel("Value:")
        value_label.setStyleSheet('color: #E0E0E0; font-size: 16px;') # Light gray
        
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter value to scan for...")
        self.value_input.setStyleSheet('''
            QLineEdit {
                background-color: rgba(30, 60, 40, 200);
                color: white;
                border: 1px solid #2E7D32; /* Dark green */
                border-radius: 4px;
                padding: 6px;
                font-size: 14px;
            }
        ''')
        self.value_input.setValidator(QIntValidator())
        
        # Data type selector
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["int", "float"])
        self.data_type_combo.setStyleSheet('''
            QComboBox {
                background-color: rgba(30, 60, 40, 200);
                color: white;
                border: 1px solid #2E7D32; /* Dark green */
                border-radius: 4px;
                padding: 6px;
                font-size: 14px;
            }
        ''')
        
        value_layout.addWidget(value_label)
        value_layout.addWidget(self.value_input)
        value_layout.addWidget(self.data_type_combo)

        # ||||[ Buttons ]||||
        button_layout = QHBoxLayout()
        
        self.scan_btn = QPushButton('First Scan')
        self.scan_btn.setStyleSheet('''
            QPushButton {
                background-color: #2196F3; /* Blue */
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px 15px;
                border: 1px solid #0D47A1; /* Darker Blue */
            }
            QPushButton:hover {
                background-color: #0b7dda;  /* Lighter Blue */
            }
            QPushButton:disabled {
                background-color: #1565C0; /* Dark Blue */
                color: #AAAAAA;
            }
        ''')
        self.scan_btn.clicked.connect(self.first_scan)
        
        self.next_scan_btn = QPushButton('Next Scan')
        self.next_scan_btn.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50; /* Green */
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px 15px;
                border: 1px solid #388E3C; /* Darker Green */
            }
            QPushButton:hover {
                background-color: #45a049; /* Lighter Green */
            }
            QPushButton:disabled {
                background-color: #2E7D32; /* Dark Green */
                color: #AAAAAA;
            }
        ''')
        self.next_scan_btn.setEnabled(False)
        self.next_scan_btn.clicked.connect(self.next_scan)
        
        self.modify_btn = QPushButton('Modify Selected')
        self.modify_btn.setStyleSheet('''
            QPushButton {
                background-color: #FF9800; /* Orange */
                color: black;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px 15px;
                border: 1px solid #F57C00; /* Darker Orange */
            }
            QPushButton:hover {
                background-color: #F57C00; /* Darker Orange */
            }
            QPushButton:disabled {
                background-color: #FF8F00; /* Lighter Orange */
                color: #666666;
            }
        ''')
        self.modify_btn.setEnabled(False)
        self.modify_btn.clicked.connect(self.modify_value)
        
        button_layout.addWidget(self.scan_btn)
        button_layout.addWidget(self.next_scan_btn)
        button_layout.addWidget(self.modify_btn)

        # ||||[ Results List ]||||
        self.results_list = QListWidget()
        self.results_list.setStyleSheet('''
            QListWidget {
                background-color: rgba(30, 60, 40, 200);
                color: #E0E0E0;
                border: 1px solid #2E7D32; /* Dark Green */
                border-radius: 5px;
                font-size: 14px;
            }
            QListWidget::item:selected {
                background-color: #388E3C; /* Selected Green */
                color: white;
            }
        ''')
        self.results_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.results_list.itemSelectionChanged.connect(self.enable_modify_button)

        # ||||[ New Value Input ]||||
        new_value_layout = QHBoxLayout()
        
        new_value_label = QLabel("New Value:")
        new_value_label.setStyleSheet('color: #E0E0E0; font-size: 16px;') # Light gray
        
        self.new_value_input = QLineEdit()
        self.new_value_input.setPlaceholderText("Enter new value...")
        self.new_value_input.setStyleSheet('''
            QLineEdit {
                background-color: rgba(30, 60, 40, 200);
                color: white;
                border: 1px solid #2E7D32; /* Dark Green */
                border-radius: 4px;
                padding: 6px;
                font-size: 14px;
            }
        ''')
        self.new_value_input.setValidator(QIntValidator())
        
        new_value_layout.addWidget(new_value_label)
        new_value_layout.addWidget(self.new_value_input)

        # ||||[ Status Message ]||||
        self.status_msg = QLabel("Ready to scan")
        self.status_msg.setStyleSheet('''
            font-size: 14px; 
            color: #FFEB3B; /* Yellow */
            background-color: transparent;
            padding: 5px;
        ''')
        self.status_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # |||||[ Layout ]|||||
        layout = QVBoxLayout(content_widget)
        layout.addWidget(back_btn)
        layout.addWidget(title)
        layout.addWidget(self.process_info)
        layout.addSpacing(15)
        layout.addLayout(value_layout)
        layout.addSpacing(10)
        layout.addLayout(button_layout)
        layout.addSpacing(10)
        layout.addWidget(self.results_list)
        layout.addSpacing(10)
        layout.addLayout(new_value_layout)
        layout.addSpacing(10)
        layout.addWidget(self.status_msg)
        layout.addStretch()
        
        # Try to open the process
        try:
            self.pm = pymem.Pymem()
            self.pm.open_process_from_id(self.parent.selected_process)
            self.status_msg.setText("Process opened successfully")
            self.status_msg.setStyleSheet('color: #4CAF50;') # Light Green
        except Exception as e:
            self.status_msg.setText(f"Error: {str(e)}")
            self.status_msg.setStyleSheet('color: #F44336;') # Red
            self.scan_btn.setEnabled(False)
            self.next_scan_btn.setEnabled(False)

    def first_scan(self):
        """Perform initial scan for the specified value"""
        if not self.value_input.text():
            self.status_msg.setText("Please enter a value to scan for")
            self.status_msg.setStyleSheet('color: #F44336;') # Red
            return
            
        try:
            value = int(self.value_input.text())
            data_type = self.data_type_combo.currentText()
            self.parent.data_type = data_type
            
            self.status_msg.setText("Scanning memory...")
            QApplication.processEvents()  # Update UI
            
            # Store the current scan value
            self.parent.current_scan_value = value
            
            # Clear previous results
            self.results_list.clear()
            self.parent.scan_results = []
            
            # Scan process memory
            for module in self.pm.list_modules():
                base_address = module.lpBaseOfDll
                size = module.SizeOfImage
                
                try:
                    # Read memory chunk by chunk
                    memory_bytes = self.pm.read_bytes(base_address, size)
                    
                    # Search for value
                    offset = 0
                    while offset < size:
                        try:
                            # Convert bytes to value based on data type
                            if data_type == "int":
                                val = int.from_bytes(memory_bytes[offset:offset+4], 'little')
                                if val == value:
                                    addr = base_address + offset
                                    self.parent.scan_results.append(addr)
                                    self.results_list.addItem(f"0x{addr:08X} - {val}")
                            elif data_type == "float":
                                # For floats, we need to use struct or ctypes
                                val_bytes = memory_bytes[offset:offset+4]
                                val = ctypes.c_float.from_buffer(bytearray(val_bytes)).value
                                if math.isclose(val, value, abs_tol=0.1):
                                    addr = base_address + offset
                                    self.parent.scan_results.append(addr)
                                    self.results_list.addItem(f"0x{addr:08X} - {val:.2f}")
                        except:
                            pass
                        offset += 4
                except:
                    # Skip modules we can't read
                    pass
            
            self.status_msg.setText(f"Found {len(self.parent.scan_results)} addresses")
            self.next_scan_btn.setEnabled(True)
            self.modify_btn.setEnabled(False)
            
        except Exception as e:
            self.status_msg.setText(f"Scan error: {str(e)}")
            self.status_msg.setStyleSheet('color: #F44336;') # Red

    def next_scan(self):
        """Narrow down results with a new value"""
        if not self.value_input.text():
            self.status_msg.setText("Please enter a new value to scan for")
            self.status_msg.setStyleSheet('color: #F44336;') # Red
            return
            
        try:
            new_value = int(self.value_input.text())
            data_type = self.parent.data_type
            
            self.status_msg.setText("Scanning memory again...")
            QApplication.processEvents()  # Update UI
            
            # Store the current scan value
            self.parent.current_scan_value = new_value
            
            # Create a copy of results to iterate over
            current_results = self.parent.scan_results.copy()
            self.parent.scan_results = []
            self.results_list.clear()
            
            # Scan only the previously found addresses
            for addr in current_results:
                try:
                    if data_type == "int":
                        val = self.pm.read_int(addr)
                        if val == new_value:
                            self.parent.scan_results.append(addr)
                            self.results_list.addItem(f"0x{addr:08X} - {val}")
                    elif data_type == "float":
                        val = self.pm.read_float(addr)
                        if math.isclose(val, new_value, abs_tol=0.1):
                            self.parent.scan_results.append(addr)
                            self.results_list.addItem(f"0x{addr:08X} - {val:.2f}")
                except:
                    # Address might not be readable anymore
                    pass
            
            self.status_msg.setText(f"Narrowed down to {len(self.parent.scan_results)} addresses")
            self.modify_btn.setEnabled(False)
            
        except Exception as e:
            self.status_msg.setText(f"Scan error: {str(e)}")
            self.status_msg.setStyleSheet('color: #F44336;') # Red

    def enable_modify_button(self):
        """Enable modify button when an item is selected"""
        self.modify_btn.setEnabled(len(self.results_list.selectedItems()) > 0)

    def modify_value(self):
        """Modify the selected memory address with a new value"""
        selected_items = self.results_list.selectedItems()
        if not selected_items:
            return
            
        if not self.new_value_input.text():
            self.status_msg.setText("Please enter a new value")
            self.status_msg.setStyleSheet('color: #F44336;') # Red
            return
            
        try:
            selected_text = selected_items[0].text()
            addr_start = selected_text.find("0x") + 2
            addr_end = selected_text.find(" - ")
            addr = int(selected_text[addr_start:addr_end], 16)
            
            new_value = int(self.new_value_input.text())
            data_type = self.parent.data_type
            
            # Write the new value
            if data_type == "int":
                self.pm.write_int(addr, new_value)
            elif data_type == "float":
                self.pm.write_float(addr, new_value)
            
            # Verify the write
            if data_type == "int":
                current_value = self.pm.read_int(addr)
            else:
                current_value = self.pm.read_float(addr)
            
            self.status_msg.setText(f"Changed value at 0x{addr:08X} to {current_value}")
            self.status_msg.setStyleSheet('color: #4CAF50;') # Light Green

            # Update the list item
            if data_type == "int":
                selected_items[0].setText(f"0x{addr:08X} - {current_value}")
            else:
                selected_items[0].setText(f"0x{addr:08X} - {current_value:.2f}")
                
        except Exception as e:
            self.status_msg.setText(f"Modify error: {str(e)}")
            self.status_msg.setStyleSheet('color: #F44336;') # Red


# ===========================[ App Entry Point ]===========================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())