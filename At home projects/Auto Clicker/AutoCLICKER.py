import sys
import time
import threading
import keyboard
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSystemTrayIcon, QMenu, QDialog,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSpinBox, QComboBox, QCheckBox, QGroupBox, QMessageBox, QStyle, QWidget
)
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PyQt6.QtCore import QTimer, Qt
import pyautogui

# Create a default application icon
def create_default_icon():
    """Create a default application icon programmatically"""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw circle
    painter.setBrush(QColor(70, 130, 180))  # Steel blue
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(4, 4, 56, 56)
    
    # Draw mouse icon
    painter.setBrush(Qt.GlobalColor.white)
    painter.drawEllipse(20, 15, 24, 35)  # Mouse body
    
    # Draw left/right buttons
    painter.setBrush(QColor(200, 200, 200))
    painter.drawRect(20, 15, 12, 15)  # Left button
    painter.drawRect(32, 15, 12, 15)  # Right button
    
    # Draw scroll wheel
    painter.setBrush(QColor(100, 100, 100))
    painter.drawRect(26, 30, 12, 5)
    
    painter.end()
    
    return QIcon(pixmap)

class AutoClickerSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Auto Clicker Settings")
        self.setWindowIcon(create_default_icon())
        self.setFixedSize(400, 350)
        
        # Create layout
        main_layout = QVBoxLayout()
        
        # Interval settings
        interval_group = QGroupBox("Click Settings")
        interval_layout = QVBoxLayout()
        
        # Click interval
        interval_layout.addWidget(QLabel("Click interval (milliseconds):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(10, 60000)  # 10ms to 60s
        self.interval_spin.setValue(100)
        interval_layout.addWidget(self.interval_spin)
        
        # Click type
        interval_layout.addWidget(QLabel("Click type:"))
        self.click_type_combo = QComboBox()
        self.click_type_combo.addItems(["Left Click", "Right Click", "Middle Click", "Double Click"])
        interval_layout.addWidget(self.click_type_combo)
        
        # Click location
        interval_layout.addWidget(QLabel("Click location:"))
        self.location_combo = QComboBox()
        self.location_combo.addItems(["Current Position", "Fixed Position"])
        interval_layout.addWidget(self.location_combo)
        
        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, pyautogui.size().width)
        self.x_spin.setValue(pyautogui.position().x)
        self.x_spin.setEnabled(False)
        
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, pyautogui.size().height)
        self.y_spin.setValue(pyautogui.position().y)
        self.y_spin.setEnabled(False)
        
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("X:"))
        pos_layout.addWidget(self.x_spin)
        pos_layout.addWidget(QLabel("Y:"))
        pos_layout.addWidget(self.y_spin)
        interval_layout.addLayout(pos_layout)
        
        # Set current position button
        self.set_pos_btn = QPushButton("Set to Current Position")
        self.set_pos_btn.setEnabled(False)
        interval_layout.addWidget(self.set_pos_btn)
        
        interval_group.setLayout(interval_layout)
        main_layout.addWidget(interval_group)
        
        # Shortcut settings
        shortcut_group = QGroupBox("Keyboard Shortcuts")
        shortcut_layout = QVBoxLayout()
        
        # Start/stop shortcut
        shortcut_layout.addWidget(QLabel("Start/Stop Shortcut:"))
        self.start_stop_edit = QLineEdit("F6")
        self.start_stop_edit.setReadOnly(True)
        shortcut_layout.addWidget(self.start_stop_edit)
        
        # Record shortcut button
        self.record_start_stop_btn = QPushButton("Record New Shortcut")
        shortcut_layout.addWidget(self.record_start_stop_btn)
        
        shortcut_group.setLayout(shortcut_layout)
        main_layout.addWidget(shortcut_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)
        
        # Connect signals
        self.location_combo.currentIndexChanged.connect(self.toggle_position_controls)
        self.set_pos_btn.clicked.connect(self.set_current_position)
        self.record_start_stop_btn.clicked.connect(self.record_shortcut)
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
    
    def toggle_position_controls(self, index):
        """Enable/disable position controls based on selection"""
        enabled = (index == 1)  # Fixed Position
        self.x_spin.setEnabled(enabled)
        self.y_spin.setEnabled(enabled)
        self.set_pos_btn.setEnabled(enabled)
    
    def set_current_position(self):
        """Set position to current mouse position"""
        x, y = pyautogui.position()
        self.x_spin.setValue(x)
        self.y_spin.setValue(y)
    
    def record_shortcut(self):
        """Record a new keyboard shortcut"""
        self.record_start_stop_btn.setText("Press any key combination...")
        self.record_start_stop_btn.setEnabled(False)
        QApplication.processEvents()  # Update UI immediately
        
        # Wait for key press in a separate thread
        def wait_for_key():
            # Use keyboard module to detect key press
            recorded = keyboard.read_hotkey(suppress=True)
            self.start_stop_edit.setText(recorded)
            self.record_start_stop_btn.setText("Record New Shortcut")
            self.record_start_stop_btn.setEnabled(True)
        
        threading.Thread(target=wait_for_key, daemon=True).start()
    
    def get_settings(self):
        """Return current settings as a dictionary"""
        return {
            "interval": self.interval_spin.value(),
            "click_type": self.click_type_combo.currentIndex(),
            "location": self.location_combo.currentIndex(),
            "x": self.x_spin.value(),
            "y": self.y_spin.value(),
            "shortcut": self.start_stop_edit.text()
        }


class AutoClickerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Auto Clicker")
        self.setWindowIcon(create_default_icon())
        self.setFixedSize(350, 250)
        
        # Default settings
        self.settings = {
            "interval": 100,  # ms
            "click_type": 0,  # Left click
            "location": 0,    # Current position
            "x": 0,           # Fixed X position
            "y": 0,           # Fixed Y position
            "shortcut": "F6"  # Default shortcut
        }
        
        # Auto clicker state
        self.clicking = False
        self.click_thread = None
        self.stop_event = threading.Event()
        
        # Create UI
        self.create_ui()
        
        # Setup system tray
        self.create_system_tray()
        
        # Register hotkey
        self.register_hotkey()
    
    def create_ui(self):
        """Create the main UI"""
        main_widget = QWidget()
        layout = QVBoxLayout()
        
        # Status display
        self.status_label = QLabel("Status: Stopped")
        self.status_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Current settings display
        settings_layout = QVBoxLayout()
        
        self.interval_label = QLabel(f"Interval: {self.settings['interval']}ms")
        settings_layout.addWidget(self.interval_label)
        
        self.click_type_label = QLabel("Click Type: Left Click")
        settings_layout.addWidget(self.click_type_label)
        
        self.location_label = QLabel("Location: Current Position")
        settings_layout.addWidget(self.location_label)
        
        self.shortcut_label = QLabel(f"Shortcut: {self.settings['shortcut']}")
        settings_layout.addWidget(self.shortcut_label)
        
        layout.addLayout(settings_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.toggle_btn = QPushButton("Start Clicking")
        self.toggle_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.toggle_btn.clicked.connect(self.toggle_clicking)
        
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self.open_settings)
        
        btn_layout.addWidget(self.toggle_btn)
        btn_layout.addWidget(self.settings_btn)
        layout.addLayout(btn_layout)
        
        # Quit button
        quit_btn = QPushButton("Quit to Tray")
        quit_btn.clicked.connect(self.hide)
        layout.addWidget(quit_btn)
        
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
    
    def create_system_tray(self):
        """Create system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(create_default_icon())
        
        # Create tray menu
        tray_menu = QMenu()
        
        self.tray_toggle_action = QAction("Start Clicking")
        self.tray_toggle_action.triggered.connect(self.toggle_clicking)
        
        settings_action = QAction("Settings")
        settings_action.triggered.connect(self.open_settings)
        
        show_action = QAction("Show Window")
        show_action.triggered.connect(self.show)
        
        quit_action = QAction("Quit")
        quit_action.triggered.connect(self.quit_app)
        
        tray_menu.addAction(self.tray_toggle_action)
        tray_menu.addAction(settings_action)
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """Handle tray icon click"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
    
    def register_hotkey(self):
        """Register keyboard shortcut"""
        try:
            keyboard.add_hotkey(
                self.settings["shortcut"], 
                self.toggle_clicking
            )
        except Exception as e:
            print(f"Error registering hotkey: {e}")
            QMessageBox.warning(
                self,
                "Hotkey Error",
                f"Could not register hotkey '{self.settings['shortcut']}':\n{e}",
                QMessageBox.StandardButton.Ok
            )
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = AutoClickerSettingsDialog(self)
        dialog.interval_spin.setValue(self.settings["interval"])
        dialog.click_type_combo.setCurrentIndex(self.settings["click_type"])
        dialog.location_combo.setCurrentIndex(self.settings["location"])
        dialog.x_spin.setValue(self.settings["x"])
        dialog.y_spin.setValue(self.settings["y"])
        dialog.start_stop_edit.setText(self.settings["shortcut"])
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Remove old hotkey
            try:
                keyboard.remove_hotkey(self.settings["shortcut"])
            except:
                pass
            
            # Save new settings
            self.settings = dialog.get_settings()
            
            # Register new hotkey
            self.register_hotkey()
            
            # Update UI
            self.update_ui()
    
    def update_ui(self):
        """Update UI with current settings"""
        click_types = ["Left Click", "Right Click", "Middle Click", "Double Click"]
        locations = ["Current Position", "Fixed Position"]
        
        self.interval_label.setText(f"Interval: {self.settings['interval']}ms")
        self.click_type_label.setText(f"Click Type: {click_types[self.settings['click_type']]}")
        self.location_label.setText(f"Location: {locations[self.settings['location']]}")
        self.shortcut_label.setText(f"Shortcut: {self.settings['shortcut']}")
        
        # Update tray action text
        self.tray_toggle_action.setText("Stop Clicking" if self.clicking else "Start Clicking")
    
    def toggle_clicking(self):
        """Start or stop auto clicking"""
        self.clicking = not self.clicking
        
        if self.clicking:
            self.start_clicking()
        else:
            self.stop_clicking()
    
    def start_clicking(self):
        """Start auto clicking"""
        self.status_label.setText("Status: Clicking...")
        self.status_label.setStyleSheet("color: green; font-weight: bold; font-size: 16px;")
        self.toggle_btn.setText("Stop Clicking")
        self.toggle_btn.setStyleSheet("background-color: #f44336; color: white;")
        self.tray_toggle_action.setText("Stop Clicking")
        
        # Start clicking in a separate thread
        self.stop_event.clear()
        self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
        self.click_thread.start()
    
    def stop_clicking(self):
        """Stop auto clicking"""
        self.status_label.setText("Status: Stopped")
        self.status_label.setStyleSheet("color: black; font-weight: bold; font-size: 16px;")
        self.toggle_btn.setText("Start Clicking")
        self.toggle_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        self.tray_toggle_action.setText("Start Clicking")
        
        # Signal to stop clicking
        self.stop_event.set()
        
        # Wait for thread to finish
        if self.click_thread and self.click_thread.is_alive():
            self.click_thread.join(timeout=1.0)
    
    def click_loop(self):
        """The main clicking loop"""
        interval = self.settings["interval"] / 1000.0  # Convert to seconds
        
        while not self.stop_event.is_set():
            # Get click position
            if self.settings["location"] == 0:  # Current position
                x, y = pyautogui.position()
            else:  # Fixed position
                x, y = self.settings["x"], self.settings["y"]
            
            # Perform click based on type
            if self.settings["click_type"] == 0:  # Left click
                pyautogui.click(x, y)
            elif self.settings["click_type"] == 1:  # Right click
                pyautogui.click(x, y, button="right")
            elif self.settings["click_type"] == 2:  # Middle click
                pyautogui.click(x, y, button="middle")
            elif self.settings["click_type"] == 3:  # Double click
                pyautogui.doubleClick(x, y)
            
            # Wait for the next click
            time.sleep(interval)
    
    def closeEvent(self, event):
        """Handle window close event"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Auto Clicker",
            "The application is still running in the system tray",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def quit_app(self):
        """Quit the application"""
        self.stop_clicking()
        self.tray_icon.hide()
        QApplication.quit()


if __name__ == "__main__":
    # Create application instance
    app = QApplication(sys.argv)
    
    # Set application name and style
    app.setApplicationName("Advanced Auto Clicker")
    app.setStyle("Fusion")
    
    # Create main window
    window = AutoClickerApp()
    
    # Show admin warning on Windows
    if sys.platform == "win32":
        QMessageBox.information(
            window,
            "Admin Rights Recommended",
            "For global shortcuts to work properly, you may need to run this application as administrator.",
            QMessageBox.StandardButton.Ok
        )
    
    # Show main window
    window.show()
    
    # Start application
    sys.exit(app.exec())