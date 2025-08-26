import sys
import platform
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QSlider, QMessageBox, QProgressBar, QToolButton, QMenu, QStyleFactory, QListWidget, QFileDialog, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from config_manager import ConfigManager
from audio_processor import AudioWorker
from overlay import OverlayWindow
from settings_dialogs import AppearanceSettings, AdvancedSettings
from utils import find_or_create_mv_pr
from collections import deque
import subprocess
import os

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import PyQt5
        import pyaudio
        import numpy
        import scipy.signal
    except ImportError as e:
        QMessageBox.critical(None, "Missing Dependency", f"Required module not found: {e}\nPlease install dependencies from requirements.txt")
        sys.exit(1)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MicVis")
        self.setGeometry(100, 100, 500, 650)
        
        self.audio_worker = None
        self.audio_devices = []
        self.volume_history = deque(maxlen=100)
        
        # Initialize configuration
        self.mv_pr_path, self.accessories_dir, self.characters_dir = find_or_create_mv_pr()
        self.config_manager = ConfigManager(self.mv_pr_path)
        self.config = self.config_manager.load_config()
        
        self.setup_ui()
        self.apply_theme(self.config.get('theme', 'default'))
        self.populate_accessories()
        self.update_accessories_list()
        self.refresh_audio_devices()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("MicVis Controller")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.theme_button = QToolButton()
        self.theme_button.setText("🎨")
        self.theme_button.setToolTip("Theme")
        self.theme_button.setPopupMode(QToolButton.InstantPopup)
        theme_menu = QMenu(self)
        themes = ['Default', 'Red', 'Blue', 'Dark', 'Light', 'Purple', 'Green']
        for theme in themes:
            theme_menu.addAction(theme, lambda t=theme: self.apply_theme(t.lower()))
        self.theme_button.setMenu(theme_menu)
        header_layout.addWidget(self.theme_button)
        layout.addLayout(header_layout)
        
        # Audio Settings
        device_group = QGroupBox("Audio Settings")
        device_layout = QVBoxLayout(device_group)
        device_select_layout = QHBoxLayout()
        device_select_layout.addWidget(QLabel("Microphone:"))
        self.device_combo = QComboBox()
        self.device_combo.setMaximumWidth(250)
        device_select_layout.addWidget(self.device_combo)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_audio_devices)
        device_select_layout.addWidget(refresh_btn)
        device_layout.addLayout(device_select_layout)
        self.calibrate_btn = QPushButton("Calibrate Sensitivity")
        self.calibrate_btn.clicked.connect(self.calibrate_sensitivity)
        device_layout.addWidget(self.calibrate_btn)
        layout.addWidget(device_group)
        
        # Visualization Settings
        viz_group = QGroupBox("Visualization Settings")
        viz_layout = QVBoxLayout(viz_group)
        
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Sensitivity:"))
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(50)
        self.threshold_slider.setMaximum(1000)
        self.threshold_slider.setValue(self.config['threshold'])
        self.threshold_slider.setTickPosition(QSlider.TicksBelow)
        self.threshold_slider.setTickInterval(100)
        self.threshold_slider.setPageStep(50)
        self.threshold_slider.valueChanged.connect(self.update_threshold)
        threshold_layout.addWidget(self.threshold_slider)
        self.threshold_label = QLabel(str(self.config['threshold']))
        self.threshold_label.setMinimumWidth(40)
        threshold_layout.addWidget(self.threshold_label)
        viz_layout.addLayout(threshold_layout)
        
        appearance_btn = QPushButton("Appearance Settings")
        appearance_btn.clicked.connect(self.open_appearance_settings)
        viz_layout.addWidget(appearance_btn)
        
        advanced_btn = QPushButton("Advanced Settings")
        advanced_btn.clicked.connect(self.open_advanced_settings)
        viz_layout.addWidget(advanced_btn)
        
        accessory_group = QGroupBox("Accessories")
        acc_layout = QVBoxLayout(accessory_group)
        add_layout = QHBoxLayout()
        add_layout.addWidget(QLabel("Add Accessory:"))
        self.add_accessory_combo = QComboBox()
        self.add_accessory_combo.setMaximumWidth(250)
        add_layout.addWidget(self.add_accessory_combo)
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_accessory)
        add_layout.addWidget(add_btn)
        acc_layout.addLayout(add_layout)
        self.accessories_list = QListWidget()
        self.accessories_list.currentRowChanged.connect(self.update_selected_accessory)
        acc_layout.addWidget(self.accessories_list)
        acc_btn_layout = QHBoxLayout()
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_accessory)
        acc_btn_layout.addWidget(remove_btn)
        self.move_btn = QPushButton("Enable Accessory Move")
        self.move_btn.clicked.connect(self.toggle_accessory_drag_mode)
        acc_btn_layout.addWidget(self.move_btn)
        self.resize_btn = QPushButton("Enable Accessory Resize")
        self.resize_btn.clicked.connect(self.toggle_accessory_resize_mode)
        acc_btn_layout.addWidget(self.resize_btn)
        self.character_resize_btn = QPushButton("Resize Character")
        self.character_resize_btn.clicked.connect(self.toggle_character_resize_mode)
        acc_btn_layout.addWidget(self.character_resize_btn)
        acc_layout.addLayout(acc_btn_layout)
        viz_layout.addWidget(accessory_group)
        
        layout.addWidget(viz_group)
        
        # Volume Meter
        meter_group = QGroupBox("Volume Meter")
        meter_layout = QVBoxLayout(meter_group)
        self.volume_bar = QProgressBar()
        self.volume_bar.setMaximum(1000)
        self.volume_bar.setTextVisible(False)
        meter_layout.addWidget(self.volume_bar)
        self.volume_label = QLabel("Volume: 0")
        meter_layout.addWidget(self.volume_label)
        layout.addWidget(meter_group)
        
        # Control Buttons
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Overlay")
        self.start_btn.clicked.connect(self.start_overlay)
        btn_layout.addWidget(self.start_btn)
        self.stop_btn = QPushButton("Stop Overlay")
        self.stop_btn.clicked.connect(self.stop_overlay)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)
        
        # Settings Buttons
        settings_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self.save_config)
        settings_layout.addWidget(self.save_btn)
        self.load_btn = QPushButton("Load Settings")
        self.load_btn.clicked.connect(self.load_settings)
        settings_layout.addWidget(self.load_btn)
        layout.addLayout(settings_layout)
        
        # Bottom Bar
        bottom_layout = QHBoxLayout()
        self.manual_button = QToolButton()
        self.manual_button.setText("🕮")
        self.manual_button.setToolTip("Manual")
        self.manual_button.clicked.connect(self.open_manual)
        bottom_layout.addWidget(self.manual_button)
        self.status_bar = QLabel("Ready")
        self.status_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        bottom_layout.addWidget(self.status_bar)
        bottom_layout.addStretch()
        layout.addLayout(bottom_layout)

    def apply_theme(self, theme_name):
        self.config['theme'] = theme_name
        volume_bar_styles = {
            'default': """
                QProgressBar {
                    border: 2px solid #888888;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #f0f0f0;
                }
                QProgressBar::chunk {
                    background-color: #05B8CC;
                    width: 10px;
                }
            """,
            # ... other theme styles (unchanged from original)
            'green': """
                QProgressBar {
                    border: 2px solid #88cc88;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #e5ffe5;
                }
                QProgressBar::chunk {
                    background-color: #55aa55;
                    width: 10px;
                }
            """
        }

        stylesheets = {
            'default': """
                QMainWindow, QWidget {
                    background-color: #f0f0f0;
                    color: #333333;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    border: 1px solid #bbbbbb;
                    padding: 6px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #bbbbbb;
                    border-radius: 6px;
                    margin-top: 1.5ex;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                QComboBox {
                    background-color: white;
                    border: 1px solid #bbbbbb;
                    padding: 4px;
                    border-radius: 4px;
                }
                QComboBox::drop-down {
                    border-left: 1px solid #bbbbbb;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #bbbbbb;
                    height: 8px;
                    background: #e0e0e0;
                    margin: 2px 0;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #05B8CC;
                    border: 1px solid #999999;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 4px;
                }
                QLabel {
                    color: #333333;
                }
                QStatusBar, QLabel#status_bar {
                    background-color: #e0e0e0;
                    padding: 4px;
                    border-radius: 4px;
                }
            """,
            # ... other theme styles (unchanged from original)
            'green': """
                QMainWindow, QWidget {
                    background-color: #e5ffe5;
                    color: #003300;
                }
                QPushButton {
                    background-color: #ccffcc;
                    border: 1px solid #88cc88;
                    padding: 6px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #aaffaa;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #88cc88;
                    border-radius: 6px;
                    margin-top: 1.5ex;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                QComboBox {
                    background-color: #f0fff0;
                    border: 1px solid #88cc88;
                    padding: 4px;
                    border-radius: 4px;
                }
                QComboBox::drop-down {
                    border-left: 1px solid #88cc88;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #88cc88;
                    height: 8px;
                    background: #ccffcc;
                    margin: 2px 0;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #55aa55;
                    border: 1px solid #88cc88;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 4px;
                }
                QLabel {
                    color: #003300;
                }
                QStatusBar, QLabel#status_bar {
                    background-color: #ccffcc;
                    padding: 4px;
                    border-radius: 4px;
                }
            """
        }

        self.setStyleSheet(stylesheets.get(theme_name, stylesheets['default']))
        self.volume_bar.setStyleSheet(volume_bar_styles.get(theme_name, volume_bar_styles['default']))
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 6px;
                border-radius: 4px;
                border: 1px solid #388E3C;
            }
            QPushButton:hover {
                background-color: #45A049;
            }
        """)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                font-weight: bold;
                padding: 6px;
                border-radius: 4px;
                border: 1px solid #D32F2F;
            }
            QPushButton:hover {
                background-color: #E53935;
            }
        """)
        
    def preview_theme(self, theme_name):
        self.current_theme = self.config['theme']
        self.apply_theme(theme_name)
        
    def populate_accessories(self):
        self.add_accessory_combo.clear()
        accessories = []
        if os.path.exists(self.accessories_dir):
            for root, _, files in os.walk(self.accessories_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.gif')):
                        rel_path = os.path.relpath(os.path.join(root, file), self.accessories_dir)[:-4]
                        accessories.append(rel_path)
        accessories.sort()
        for name in accessories:
            self.add_accessory_combo.addItem(name)
    
    def update_accessories_list(self):
        self.accessories_list.clear()
        for acc in self.config.get('accessories', []):
            self.accessories_list.addItem(acc['name'])
    
    def add_accessory(self):
        name = self.add_accessory_combo.currentText()
        if name:
            self.config['accessories'].append({'name': name, 'x_offset': 0, 'y_offset': 0, 'scale': 1.0, 'animation': 'none'})
            self.update_accessories_list()
            if hasattr(self, 'overlay'):
                self.overlay.update()
    
    def remove_accessory(self):
        row = self.accessories_list.currentRow()
        if row >= 0:
            del self.config['accessories'][row]
            self.update_accessories_list()
            if hasattr(self, 'overlay'):
                self.overlay.selected_accessory_index = -1
                self.overlay.update()
    
    def update_selected_accessory(self, row):
        if hasattr(self, 'overlay'):
            self.overlay.selected_accessory_index = row
            self.overlay.update()
    
    def toggle_accessory_drag_mode(self):
        if hasattr(self, 'overlay'):
            self.overlay.set_accessory_drag_mode(not self.overlay.accessory_drag_mode)
            self.move_btn.setText("Disable Accessory Move" if self.overlay.accessory_drag_mode else "Enable Accessory Move")
            self.overlay.update()
    
    def toggle_accessory_resize_mode(self):
        if hasattr(self, 'overlay'):
            self.overlay.set_accessory_resize_mode(not self.overlay.accessory_resize_mode)
            self.resize_btn.setText("Disable Accessory Resize" if self.overlay.accessory_resize_mode else "Enable Accessory Resize")
            self.overlay.update()
    
    def toggle_character_resize_mode(self):
        if hasattr(self, 'overlay'):
            self.overlay.set_character_resize_mode(not self.overlay.character_resize_mode)
            self.character_resize_btn.setText("Stop Resize" if self.overlay.character_resize_mode else "Resize Character")
            self.overlay.update()
    
    def refresh_audio_devices(self):
        self.device_combo.clear()
        self.audio_devices = []
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    self.audio_devices.append((i, device_info['name']))
                    self.device_combo.addItem(device_info['name'], i)
            p.terminate()
            if self.config['last_device'] is not None:
                index = self.device_combo.findData(self.config['last_device'])
                if index >= 0:
                    self.device_combo.setCurrentIndex(index)
            if not self.audio_devices:
                self.start_btn.setEnabled(False)
                self.status_bar.setText("No audio input devices found.")
                QMessageBox.warning(self, "No Devices", "No audio input devices found.")
            else:
                self.start_btn.setEnabled(True)
                self.status_bar.setText(f"Found {len(self.audio_devices)} audio devices.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to enumerate audio devices: {e}")
            self.status_bar.setText("Error enumerating audio devices.")
        
    def calibrate_sensitivity(self):
        if self.device_combo.count() == 0:
            QMessageBox.warning(self, "No Device", "Please select a microphone first.")
            return
        device_index = self.device_combo.currentData()
        worker = AudioWorker(device_index)
        measurements = []
        def collect_volume(volume):
            measurements.append(volume)
        worker.volume_signal.connect(collect_volume)
        worker.start()
        msg = QMessageBox(self)
        msg.setWindowTitle("Calibrating")
        msg.setText("Please be silent for 3 seconds while we measure background noise...")
        msg.setStandardButtons(QMessageBox.Cancel)
        msg.show()
        import time
        start_time = time.time()
        while time.time() - start_time < 3 and worker.isRunning():
            QApplication.processEvents()
            time.sleep(0.1)
        worker.stop()
        msg.close()
        if measurements:
            avg_noise = sum(measurements) / len(measurements)
            recommended_threshold = avg_noise * 2
            self.threshold_slider.setValue(int(recommended_threshold))
            QMessageBox.information(self, "Calibration Complete", 
                                  f"Background noise: {avg_noise:.0f}\nRecommended sensitivity: {recommended_threshold:.0f}")
        
    def start_overlay(self):
        if self.device_combo.count() == 0:
            QMessageBox.warning(self, "No Device", "No audio devices available.")
            return
        device_index = self.device_combo.currentData()
        self.config['last_device'] = device_index
        self.overlay = OverlayWindow(self.config, self.accessories_dir, self.characters_dir)
        self.overlay.show()
        self.audio_worker = AudioWorker(device_index)
        self.audio_worker.volume_signal.connect(self.update_volume)
        self.audio_worker.frequency_signal.connect(self.update_frequency)
        self.audio_worker.error_signal.connect(self.handle_audio_error)
        self.audio_worker.set_frequency_analysis(self.config.get('frequency_analysis', False))
        self.audio_worker.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.device_combo.setEnabled(False)
        self.calibrate_btn.setEnabled(False)
        self.status_bar.setText("Overlay active. Speak to see the character respond.")
        
    def stop_overlay(self):
        if self.audio_worker:
            self.audio_worker.stop()
            self.audio_worker = None
        if hasattr(self, 'overlay'):
            self.config['window_x'] = self.overlay.x()
            self.config['window_y'] = self.overlay.y()
            self.config['window_width'] = self.overlay.width()
            self.config['window_height'] = self.overlay.height()
            self.overlay.close()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.device_combo.setEnabled(True)
        self.calibrate_btn.setEnabled(True)
        self.status_bar.setText("Overlay stopped.")
        
    def update_volume(self, volume):
        self.volume_label.setText(f"Volume: {volume}")
        self.volume_bar.setValue(volume)
        self.volume_history.append(volume)
        if hasattr(self, 'overlay'):
            self.overlay.set_volume(volume)
            
    def update_frequency(self, data):
        if hasattr(self, 'overlay'):
            self.overlay.set_frequency_data(data)
            
    def handle_audio_error(self, error_msg):
        QMessageBox.critical(self, "Audio Error", error_msg)
        self.status_bar.setText(f"Audio error: {error_msg}")
        self.stop_overlay()
            
    def update_threshold(self, value):
        self.threshold_label.setText(str(value))
        self.config['threshold'] = value
        if self.audio_worker:
            self.audio_worker.set_threshold(value)
        if hasattr(self, 'overlay'):
            self.overlay.set_threshold(value)
            
    def update_wave_count(self, value):
        self.config['wave_count'] = value
        if hasattr(self, 'overlay'):
            self.overlay.config['wave_count'] = value
            self.overlay.update()
            
    def change_color(self, color_type):
        from PyQt5.QtWidgets import QColorDialog
        color = QColorDialog.getColor(QColor(*self.config[color_type]), self)
        if color.isValid():
            self.config[color_type] = [color.red(), color.green(), color.blue()]
            if hasattr(self, 'overlay'):
                self.overlay.config[color_type] = [color.red(), color.green(), color.blue()]
                self.overlay.static_cache = None
                self.overlay.update()
                
    def open_appearance_settings(self):
        dialog = AppearanceSettings(self)
        dialog.exec_()
        
    def open_manual(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        manual_path = os.path.join(script_dir, "MV_manual.py")
        if os.path.exists(manual_path):
            subprocess.Popen([sys.executable, manual_path])
        else:
            QMessageBox.critical(self, "Error", "MV_manual.py not found.")
                
    def load_settings(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Settings", "", "JSON Files (*.json)")
        if file_path:
            try:
                self.config = self.config_manager.load_config(file_path)
                self.threshold_slider.setValue(self.config['threshold'])
                self.update_accessories_list()
                self.apply_theme(self.config.get('theme', 'default'))
                self.status_bar.setText("Settings loaded successfully.")
                QMessageBox.information(self, "Success", "Settings loaded successfully.")
            except Exception as e:
                self.status_bar.setText(f"Error loading settings: {e}")
                QMessageBox.critical(self, "Error", f"Failed to load settings: {e}")
                
    def save_config(self):
        self.config_manager.save_config(self.config)
        self.status_bar.setText("Settings saved successfully.")
        
    def closeEvent(self, event):
        self.stop_overlay()
        self.save_config()
        event.accept()

if __name__ == "__main__":
    check_dependencies()
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())