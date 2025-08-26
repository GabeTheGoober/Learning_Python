import sys
import numpy as np
import audioop
import pyaudio
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QComboBox, QLabel, 
                             QSlider, QMessageBox, QProgressBar, QCheckBox,
                             QColorDialog, QSpinBox, QGroupBox, QFileDialog,
                             QMenu, QToolButton, QStyleFactory, QListWidget,
                             QDialog, QSizePolicy, QTextBrowser)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSettings, QPoint, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap, QImage, QMouseEvent, QFont
import threading
import time
from collections import deque
import subprocess

if sys.platform == 'win32':
    import ctypes

# Function to find or create the MV_pr.json file and MV_accessories folder
def find_or_create_mv_pr():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_filename = "MV_pr.json"
    
    # Create MV_accessories folder if it doesn't exist
    accessories_dir = os.path.join(script_dir, "MV_accessories")
    try:
        os.makedirs(accessories_dir, exist_ok=True)
    except Exception as e:
        print(f"Error creating MV_accessories: {e}")
    
    # Check for MV_pr.json
    file_path = os.path.join(script_dir, target_filename)
    
    # Create default config if not found
    if not os.path.exists(file_path):
        default_config = {
            'threshold': 300,
            'head_color': [100, 150, 255],
            'mouth_color': [255, 0, 0],
            'wave_color': [255, 255, 255],
            'wave_count': 5,
            'window_x': 100,
            'window_y': 100,
            'window_width': 800,
            'window_height': 800,
            'last_device': None,
            'theme': 'default',
            'accessories': [],
            'character_scale': 1.0
        }
        try:
            with open(file_path, 'w') as f:
                json.dump(default_config, f, indent=4)
        except Exception as e:
            print(f"Error creating default config: {e}")
    
    return file_path, accessories_dir

class AudioWorker(QThread):
    volume_signal = pyqtSignal(int)
    error_signal = pyqtSignal(str)
    
    def __init__(self, device_index, parent=None):
        super().__init__(parent)
        self.device_index = device_index
        self.running = False
        self.threshold = 300
        self.audio_interface = None
        self.stream = None
        
    def run(self):
        self.running = True
        self.audio_interface = pyaudio.PyAudio()
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024
        
        try:
            self.stream = self.audio_interface.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=CHUNK
            )
            while self.running:
                try:
                    data = self.stream.read(CHUNK, exception_on_overflow=False)
                    rms = audioop.rms(data, 2)
                    self.volume_signal.emit(rms)
                except OSError as e:
                    self.error_signal.emit(f"Audio device error: {e}")
                    break
                except Exception as e:
                    self.error_signal.emit(f"Audio processing error: {e}")
        except Exception as e:
            self.error_signal.emit(f"Failed to initialize audio: {e}")
        finally:
            self.cleanup()
                
    def cleanup(self):
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
        if self.audio_interface:
            try:
                self.audio_interface.terminate()
            except:
                pass
        
    def stop(self):
        self.running = False
        self.cleanup()
        self.wait()
        
    def set_threshold(self, value):
        self.threshold = value

class OverlayWindow(QWidget):
    def __init__(self, config, accessories_dir):
        super().__init__()
        self.config = config
        self.accessories_dir = accessories_dir
        self.setWindowTitle("MicVis Overlay")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        
        self.setGeometry(config.get('window_x', 100), config.get('window_y', 100), 
                         config.get('window_width', 800), config.get('window_height', 800))
        
        self.volume_level = 0
        self.threshold = config.get('threshold', 300)
        self.is_speaking = False
        self.mouth_openness = 0
        self.eye_state = 0
        self.blink_timer = 0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)
        
        self.static_cache = None
        self.last_mouth_openness = -1
        self.last_is_speaking = False
        self.last_eye_state = -1
        self.last_character_scale = None
        self.accessory_images = {}
        
        self.dragging_window = False
        self.dragging_accessory = False
        self.accessory_drag_mode = False
        self.resizing_accessory = False
        self.accessory_resize_mode = False
        self.resizing_character = False
        self.character_resize_mode = False
        self.selected_accessory_index = -1
        self.resize_corner = None
        self.drag_position = QPoint()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            head_center = self.rect().center()
            head_radius = min(self.width(), self.height()) * 0.4 * self.config.get('character_scale', 1.0)
            
            # Check for character resize
            if self.character_resize_mode:
                handle_size = 10
                head_width = int(head_radius * 2.0)
                head_x = head_center.x() - head_width // 2
                head_y = head_center.y() - head_width // 2
                corners = [
                    ('top-left', QRect(head_x, head_y, handle_size, handle_size)),
                    ('top-right', QRect(head_x + head_width - handle_size, head_y, handle_size, handle_size)),
                    ('bottom-left', QRect(head_x, head_y + head_width - handle_size, handle_size, handle_size)),
                    ('bottom-right', QRect(head_x + head_width - handle_size, head_y + head_width - handle_size, handle_size, handle_size))
                ]
                for corner, rect in corners:
                    if rect.contains(event.pos()):
                        self.resizing_character = True
                        self.resize_corner = corner
                        self.drag_position = event.pos()
                        event.accept()
                        return
            
            # Check for accessory resize or drag
            if self.accessory_drag_mode and self.selected_accessory_index >= 0:
                acc = self.config.get('accessories', [])[self.selected_accessory_index]
                accessory_image = self.load_accessory_image(acc['name'])
                if accessory_image:
                    scale = acc.get('scale', 1.0)
                    hat_width = int(head_radius * 2.0 * scale)
                    hat_height = int(accessory_image.height() * (hat_width / accessory_image.width()))
                    hat_x = head_center.x() + acc.get('x_offset', 0) - hat_width // 2
                    hat_y = head_center.y() + acc.get('y_offset', 0) - hat_height // 2
                    
                    if self.accessory_resize_mode:
                        handle_size = 10
                        corners = [
                            ('top-left', QRect(hat_x, hat_y, handle_size, handle_size)),
                            ('top-right', QRect(hat_x + hat_width - handle_size, hat_y, handle_size, handle_size)),
                            ('bottom-left', QRect(hat_x, hat_y + hat_height - handle_size, handle_size, handle_size)),
                            ('bottom-right', QRect(hat_x + hat_width - handle_size, hat_y + hat_height - handle_size, handle_size, handle_size))
                        ]
                        for corner, rect in corners:
                            if rect.contains(event.pos()):
                                self.resizing_accessory = True
                                self.resize_corner = corner
                                self.drag_position = event.pos()
                                event.accept()
                                return
                    
                    if QRect(hat_x, hat_y, hat_width, hat_height).contains(event.pos()):
                        self.dragging_accessory = True
                        self.drag_position = event.pos()
                        event.accept()
                        return
            
            self.dragging_window = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        head_center = self.rect().center()
        head_radius = min(self.width(), self.height()) * 0.4 * self.config.get('character_scale', 1.0)
        
        if self.resizing_character and self.character_resize_mode and event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.drag_position
            current_scale = self.config.get('character_scale', 1.0)
            scale_change = delta.x() / (head_radius * 2.0)
            if 'left' in self.resize_corner:
                scale_change = -scale_change
            new_scale = max(0.1, current_scale + scale_change * 0.1)
            self.config['character_scale'] = new_scale
            self.drag_position = event.pos()
            self.static_cache = None
            self.update()
            event.accept()
        elif self.resizing_accessory and self.accessory_resize_mode and self.selected_accessory_index >= 0 and event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.drag_position
            acc = self.config.get('accessories', [])[self.selected_accessory_index]
            current_scale = acc.get('scale', 1.0)
            scale_change = delta.x() / (head_radius * 2.0)
            if 'left' in self.resize_corner:
                scale_change = -scale_change
            new_scale = max(0.1, current_scale + scale_change * 0.1)
            acc['scale'] = new_scale
            self.drag_position = event.pos()
            self.update()
            event.accept()
        elif self.dragging_accessory and self.accessory_drag_mode and self.selected_accessory_index >= 0 and event.buttons() & Qt.LeftButton:
            delta = event.pos() - self.drag_position
            acc = self.config.get('accessories', [])[self.selected_accessory_index]
            acc['x_offset'] = acc.get('x_offset', 0) + delta.x()
            acc['y_offset'] = acc.get('y_offset', 0) + delta.y()
            self.drag_position = event.pos()
            self.update()
            event.accept()
        elif self.dragging_window and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        self.dragging_accessory = False
        self.resizing_accessory = False
        self.resizing_character = False
        self.resize_corner = None
        self.dragging_window = False
        event.accept()
        
    def update_animation(self):
        target_openness = min(self.volume_level / 1000, 1.0) if self.is_speaking else 0
        self.mouth_openness = 0.7 * self.mouth_openness + 0.3 * target_openness
        self.blink_timer += 1
        if self.blink_timer > 100:
            self.eye_state = 2
            if self.blink_timer > 103:
                self.blink_timer = 0
                self.eye_state = 0
        elif self.blink_timer > 97:
            self.eye_state = 1
        self.update()
        
    def set_volume(self, volume):
        self.volume_level = volume
        self.is_speaking = volume > self.threshold
        
    def set_threshold(self, threshold):
        self.threshold = threshold
        
    def set_accessory_drag_mode(self, enabled):
        self.accessory_drag_mode = enabled
        self.update()
        
    def set_accessory_resize_mode(self, enabled):
        self.accessory_resize_mode = enabled
        self.update()
        
    def set_character_resize_mode(self, enabled):
        self.character_resize_mode = enabled
        self.static_cache = None
        self.update()
        
    def load_accessory_image(self, accessory_name):
        if not accessory_name:
            return None
        if accessory_name not in self.accessory_images:
            accessory_path = os.path.join(self.accessories_dir, f"{accessory_name}.png")
            if os.path.exists(accessory_path):
                image = QImage(accessory_path)
                if not image.isNull():
                    self.accessory_images[accessory_name] = image
                    return image
                else:
                    print(f"Failed to load accessory image: {accessory_path}")
            else:
                print(f"Accessory image not found: {accessory_path}")
        return self.accessory_images.get(accessory_name)
    
    def paintEvent(self, event):
        if (abs(self.mouth_openness - self.last_mouth_openness) < 0.01 and 
            self.is_speaking == self.last_is_speaking and
            self.eye_state == self.last_eye_state and
            self.config.get('character_scale') == self.last_character_scale and
            self.static_cache):
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.static_cache)
            self.draw_dynamic_elements(painter)
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.static_cache or self.static_cache.size() != self.size():
            self.static_cache = QPixmap(self.size())
            self.static_cache.fill(Qt.transparent)
            cache_painter = QPainter(self.static_cache)
            cache_painter.setRenderHint(QPainter.Antialiasing)
            self.draw_static_elements(cache_painter)
            cache_painter.end()
        
        painter.drawPixmap(0, 0, self.static_cache)
        self.draw_dynamic_elements(painter)
        
        self.last_mouth_openness = self.mouth_openness
        self.last_is_speaking = self.is_speaking
        self.last_eye_state = self.eye_state
        self.last_character_scale = self.config.get('character_scale')
        
    def draw_static_elements(self, painter):
        head_center = self.rect().center()
        head_radius = min(self.width(), self.height()) * 0.4 * self.config.get('character_scale', 1.0)
        
        head_color = QColor(*self.config.get('head_color', [100, 150, 255]))
        painter.setBrush(head_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(head_center, int(head_radius), int(head_radius))
        
        eye_offset_x = int(head_radius * 0.3)
        eye_offset_y = int(-head_radius * 0.2)
        eye_radius = int(head_radius * 0.15)
        
        painter.setBrush(Qt.white)
        painter.drawEllipse(head_center.x() - eye_offset_x, head_center.y() + eye_offset_y, 
                           eye_radius, eye_radius)
        painter.drawEllipse(head_center.x() + eye_offset_x, head_center.y() + eye_offset_y, 
                           eye_radius, eye_radius)
        
        if self.character_resize_mode:
            head_width = int(head_radius * 2.0)
            head_x = head_center.x() - head_width // 2
            head_y = head_center.y() - head_width // 2
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(255, 255, 255, 200))
            handle_size = 10
            corners = [
                (head_x, head_y),
                (head_x + head_width - handle_size, head_y),
                (head_x, head_y + head_width - handle_size),
                (head_x + head_width - handle_size, head_y + head_width - handle_size)
            ]
            for x, y in corners:
                painter.drawEllipse(x, y, handle_size, handle_size)
        
    def draw_dynamic_elements(self, painter):
        head_center = self.rect().center()
        head_radius = min(self.width(), self.height()) * 0.4 * self.config.get('character_scale', 1.0)
        
        eye_offset_x = int(head_radius * 0.3)
        eye_offset_y = int(-head_radius * 0.2)
        eye_radius = int(head_radius * 0.15)
        pupil_radius = int(eye_radius * 0.5)
        
        painter.setBrush(Qt.black)
        if self.eye_state == 0:
            painter.drawEllipse(head_center.x() - eye_offset_x, head_center.y() + eye_offset_y, 
                               pupil_radius, pupil_radius)
            painter.drawEllipse(head_center.x() + eye_offset_x, head_center.y() + eye_offset_y, 
                               pupil_radius, pupil_radius)
        elif self.eye_state == 1:
            half_pupil_height = int(pupil_radius * 0.5)
            painter.drawEllipse(head_center.x() - eye_offset_x, head_center.y() + eye_offset_y + int(half_pupil_height/2), 
                               pupil_radius, half_pupil_height)
            painter.drawEllipse(head_center.x() + eye_offset_x, head_center.y() + eye_offset_y + int(half_pupil_height/2), 
                               pupil_radius, half_pupil_height)
        
        mouth_width = int(head_radius * 0.7)
        mouth_height = int(head_radius * 0.4 * self.mouth_openness)
        mouth_y_offset = int(head_radius * 0.3)
        
        mouth_color = QColor(*self.config.get('mouth_color', [255, 0, 0]))
        painter.setBrush(mouth_color)
        painter.drawEllipse(head_center.x() - int(mouth_width/2), 
                           head_center.y() + mouth_y_offset, 
                           mouth_width, mouth_height)
        
        if self.is_speaking:
            wave_count = self.config.get('wave_count', 5)
            max_wave_radius = int(head_radius * 1.5)
            wave_spread = int((max_wave_radius - head_radius) / wave_count)
            wave_color = QColor(*self.config.get('wave_color', [255, 255, 255]))
            for i in range(wave_count):
                wave_radius = int(head_radius + wave_spread * (i + 1))
                alpha = 150 - (i * 25)
                wave_color.setAlpha(alpha)
                painter.setPen(QPen(wave_color, 2))
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(head_center, wave_radius, wave_radius)

        for i, acc in enumerate(self.config.get('accessories', [])):
            accessory_name = acc.get('name')
            accessory_image = self.load_accessory_image(accessory_name)
            if accessory_image:
                scale = acc.get('scale', 1.0)
                hat_width = int(head_radius * 2.0 * scale)
                hat_height = int(accessory_image.height() * (hat_width / accessory_image.width()))
                scaled_accessory = accessory_image.scaled(hat_width, hat_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                hat_x = head_center.x() + acc.get('x_offset', 0) - hat_width // 2
                hat_y = head_center.y() + acc.get('y_offset', 0) - hat_height // 2
                if self.accessory_drag_mode and i == self.selected_accessory_index:
                    painter.setPen(QPen(QColor(0, 255, 0, 200), 2, Qt.DashLine))
                    painter.setBrush(Qt.NoBrush)
                    painter.drawRect(hat_x, hat_y, hat_width, hat_height)
                    if self.accessory_resize_mode:
                        handle_size = 10
                        painter.setPen(Qt.NoPen)
                        painter.setBrush(QColor(255, 255, 255, 200))
                        corners = [
                            (hat_x, hat_y),
                            (hat_x + hat_width - handle_size, hat_y),
                            (hat_x, hat_y + hat_height - handle_size),
                            (hat_x + hat_width - handle_size, hat_y + hat_height - handle_size)
                        ]
                        for x, y in corners:
                            painter.drawEllipse(x, y, handle_size, handle_size)
                painter.drawImage(hat_x, hat_y, scaled_accessory)

class AppearanceSettings(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Appearance Settings")
        layout = QVBoxLayout(self)

        # Theme preview
        theme_group = QGroupBox("Theme Selection")
        theme_layout = QHBoxLayout(theme_group)
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Default', 'Red', 'Blue', 'Dark', 'Light', 'Purple', 'Green'])
        self.theme_combo.setCurrentText(parent.config['theme'].capitalize())
        self.theme_combo.currentTextChanged.connect(self.preview_theme)
        theme_layout.addWidget(self.theme_combo)
        preview_btn = QPushButton("Preview")
        preview_btn.clicked.connect(self.apply_preview)
        theme_layout.addWidget(preview_btn)
        layout.addWidget(theme_group)

        # Wave count
        wave_layout = QHBoxLayout()
        wave_layout.addWidget(QLabel("Wave Count:"))
        self.wave_spin = QSpinBox()
        self.wave_spin.setMinimum(1)
        self.wave_spin.setMaximum(10)
        self.wave_spin.setValue(parent.config['wave_count'])
        self.wave_spin.valueChanged.connect(parent.update_wave_count)
        wave_layout.addWidget(self.wave_spin)
        wave_layout.addStretch()
        layout.addLayout(wave_layout)

        # Colors
        color_layout = QHBoxLayout()
        head_color_btn = QPushButton("Head Color")
        head_color_btn.clicked.connect(lambda: parent.change_color('head_color'))
        color_layout.addWidget(head_color_btn)
        mouth_color_btn = QPushButton("Mouth Color")
        mouth_color_btn.clicked.connect(lambda: parent.change_color('mouth_color'))
        color_layout.addWidget(mouth_color_btn)
        wave_color_btn = QPushButton("Wave Color")
        wave_color_btn.clicked.connect(lambda: parent.change_color('wave_color'))
        color_layout.addWidget(wave_color_btn)
        layout.addLayout(color_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_changes)
        btn_layout.addWidget(apply_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def preview_theme(self, theme_name):
        self.parent.preview_theme(theme_name.lower())

    def apply_preview(self):
        self.parent.apply_theme(self.theme_combo.currentText().lower())

    def apply_changes(self):
        self.parent.apply_theme(self.theme_combo.currentText().lower())
        self.parent.save_config()
        self.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MicVis")
        self.setGeometry(100, 100, 500, 650)
        
        self.audio_worker = None
        self.audio_devices = []
        
        self.mv_pr_path, self.accessories_dir = find_or_create_mv_pr()
        self.config = self.load_config()
        self.volume_history = deque(maxlen=100)
        
        self.setup_ui()
        self.apply_theme(self.config.get('theme', 'default'))
        self.populate_accessories()
        self.update_accessories_list()
        self.refresh_audio_devices()
        
    def load_config(self):
        default_config = {
            'threshold': 300,
            'head_color': [100, 150, 255],
            'mouth_color': [255, 0, 0],
            'wave_color': [255, 255, 255],
            'wave_count': 5,
            'window_x': 100,
            'window_y': 100,
            'window_width': 800,
            'window_height': 800,
            'last_device': None,
            'theme': 'default',
            'accessories': [],
            'character_scale': 1.0
        }
        try:
            if os.path.exists(self.mv_pr_path):
                with open(self.mv_pr_path, 'r') as f:
                    loaded_config = json.load(f)
                for key in default_config:
                    if key in loaded_config:
                        default_config[key] = loaded_config[key]
                # Migrate old single accessory to list
                if 'selected_accessory' in loaded_config and loaded_config['selected_accessory'] != 'None':
                    default_config['accessories'].append({
                        'name': loaded_config['selected_accessory'],
                        'x_offset': loaded_config.get('accessory_x_offset', 0),
                        'y_offset': loaded_config.get('accessory_y_offset', 0),
                        'scale': loaded_config.get('accessory_scale', 1.0)
                    })
                # Remove old keys
                for old_key in ['selected_accessory', 'accessory_x_offset', 'accessory_y_offset', 'accessory_scale']:
                    if old_key in default_config:
                        del default_config[old_key]
                print(f"Loaded configuration from {self.mv_pr_path}")
        except Exception as e:
            print(f"Error loading config from {self.mv_pr_path}: {e}")
        return default_config
        
    def save_config(self):
        try:
            with open(self.mv_pr_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"Configuration saved to {self.mv_pr_path}")
        except Exception as e:
            print(f"Error saving config to {self.mv_pr_path}: {e}")
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
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
        
        meter_group = QGroupBox("Volume Meter")
        meter_layout = QVBoxLayout(meter_group)
        self.volume_bar = QProgressBar()
        self.volume_bar.setMaximum(1000)
        self.volume_bar.setTextVisible(False)
        meter_layout.addWidget(self.volume_bar)
        self.volume_label = QLabel("Volume: 0")
        meter_layout.addWidget(self.volume_label)
        layout.addWidget(meter_group)
        
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Overlay")
        self.start_btn.clicked.connect(self.start_overlay)
        btn_layout.addWidget(self.start_btn)
        self.stop_btn = QPushButton("Stop Overlay")
        self.stop_btn.clicked.connect(self.stop_overlay)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)
        
        settings_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self.save_config)
        settings_layout.addWidget(self.save_btn)
        self.load_btn = QPushButton("Load Settings")
        self.load_btn.clicked.connect(self.load_settings)
        settings_layout.addWidget(self.load_btn)
        layout.addLayout(settings_layout)
        
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
            'red': """
                QProgressBar {
                    border: 2px solid #cc9999;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #ffe5e5;
                }
                QProgressBar::chunk {
                    background-color: #ff5555;
                    width: 10px;
                }
            """,
            'blue': """
                QProgressBar {
                    border: 2px solid #9999cc;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #e5e5ff;
                }
                QProgressBar::chunk {
                    background-color: #5555ff;
                    width: 10px;
                }
            """,
            'dark': """
                QProgressBar {
                    border: 2px solid #777777;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #444444;
                }
                QProgressBar::chunk {
                    background-color: #00aaaa;
                    width: 10px;
                }
            """,
            'light': """
                QProgressBar {
                    border: 2px solid #cccccc;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #ffffff;
                }
                QProgressBar::chunk {
                    background-color: #66ccff;
                    width: 10px;
                }
            """,
            'purple': """
                QProgressBar {
                    border: 2px solid #aa88cc;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #f0e5ff;
                }
                QProgressBar::chunk {
                    background-color: #8855cc;
                    width: 10px;
                }
            """,
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
            'red': """
                QMainWindow, QWidget {
                    background-color: #ffe5e5;
                    color: #330000;
                }
                QPushButton {
                    background-color: #ffcccc;
                    border: 1px solid #cc9999;
                    padding: 6px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #ffaaaa;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #cc9999;
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
                    background-color: #fff0f0;
                    border: 1px solid #cc9999;
                    padding: 4px;
                    border-radius: 4px;
                }
                QComboBox::drop-down {
                    border-left: 1px solid #cc9999;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #cc9999;
                    height: 8px;
                    background: #ffcccc;
                    margin: 2px 0;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #ff5555;
                    border: 1px solid #cc9999;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 4px;
                }
                QLabel {
                    color: #330000;
                }
                QStatusBar, QLabel#status_bar {
                    background-color: #ffcccc;
                    padding: 4px;
                    border-radius: 4px;
                }
            """,
            'blue': """
                QMainWindow, QWidget {
                    background-color: #e5e5ff;
                    color: #000033;
                }
                QPushButton {
                    background-color: #ccccff;
                    border: 1px solid #9999cc;
                    padding: 6px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #aaaaff;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #9999cc;
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
                    background-color: #f0f0ff;
                    border: 1px solid #9999cc;
                    padding: 4px;
                    border-radius: 4px;
                }
                QComboBox::drop-down {
                    border-left: 1px solid #9999cc;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #9999cc;
                    height: 8px;
                    background: #ccccff;
                    margin: 2px 0;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #5555ff;
                    border: 1px solid #9999cc;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 4px;
                }
                QLabel {
                    color: #000033;
                }
                QStatusBar, QLabel#status_bar {
                    background-color: #ccccff;
                    padding: 4px;
                    border-radius: 4px;
                }
            """,
            'dark': """
                QMainWindow, QWidget {
                    background-color: #2a2a2a;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #555555;
                    border: 1px solid #777777;
                    padding: 6px;
                    border-radius: 4px;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #666666;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #777777;
                    border-radius: 6px;
                    margin-top: 1.5ex;
                    padding-top: 10px;
                    color: white;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                    color: white;
                }
                QComboBox {
                    background-color: #444444;
                    border: 1px solid #777777;
                    padding: 4px;
                    border-radius: 4px;
                    color: white;
                }
                QComboBox::drop-down {
                    border-left: 1px solid #777777;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #777777;
                    height: 8px;
                    background: #444444;
                    margin: 2px 0;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #00aaaa;
                    border: 1px solid #777777;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 4px;
                }
                QLabel {
                    color: white;
                }
                QStatusBar, QLabel#status_bar {
                    background-color: #444444;
                    padding: 4px;
                    border-radius: 4px;
                    color: white;
                }
                QSpinBox {
                    background-color: #444444;
                    border: 1px solid #777777;
                    padding: 4px;
                    border-radius: 4px;
                    color: white;
                }
            """,
            'light': """
                QMainWindow, QWidget {
                    background-color: #ffffff;
                    color: #333333;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                    padding: 6px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #cccccc;
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
                    border: 1px solid #cccccc;
                    padding: 4px;
                    border-radius: 4px;
                }
                QComboBox::drop-down {
                    border-left: 1px solid #cccccc;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #cccccc;
                    height: 8px;
                    background: #f0f0f0;
                    margin: 2px 0;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #66ccff;
                    border: 1px solid #cccccc;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 4px;
                }
                QLabel {
                    color: #333333;
                }
                QStatusBar, QLabel#status_bar {
                    background-color: #f0f0f0;
                    padding: 4pxrobot:4px;
                    border-radius: 4px;
                }
            """,
            'purple': """
                QMainWindow, QWidget {
                    background-color: #f0e5ff;
                    color: #330033;
                }
                QPushButton {
                    background-color: #e0ccff;
                    border: 1px solid #aa88cc;
                    padding: 6px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #cc99ff;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #aa88cc;
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
                    background-color: #f5efff;
                    border: 1px solid #aa88cc;
                    padding: 4px;
                    border-radius: 4px;
                }
                QComboBox::drop-down {
                    border-left: 1px solid #aa88cc;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #aa88cc;
                    height: 8px;
                    background: #e0ccff;
                    margin: 2px 0;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #8855cc;
                    border: 1px solid #aa88cc;
                    width: 18px;
                    margin: -2px 0;
                    border-radius: 4px;
                }
                QLabel {
                    color: #330033;
                }
                QStatusBar, QLabel#status_bar {
                    background-color: #e0ccff;
                    padding: 4px;
                    border-radius: 4px;
                }
            """,
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
        # Store current theme for potential revert
        self.current_theme = self.config['theme']
        self.apply_theme(theme_name)
        
    def populate_accessories(self):
        self.add_accessory_combo.clear()
        accessories = []
        if os.path.exists(self.accessories_dir):
            for root, _, files in os.walk(self.accessories_dir):
                for file in files:
                    if file.lower().endswith('.png'):
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
            self.config['accessories'].append({'name': name, 'x_offset': 0, 'y_offset': 0, 'scale': 1.0})
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
        self.overlay = OverlayWindow(self.config, self.accessories_dir)
        self.overlay.show()
        self.audio_worker = AudioWorker(device_index)
        self.audio_worker.volume_signal.connect(self.update_volume)
        self.audio_worker.error_signal.connect(self.handle_audio_error)
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
                with open(file_path, 'r') as f:
                    loaded_config = json.load(f)
                for key in self.config:
                    if key in loaded_config:
                        self.config[key] = loaded_config[key]
                self.threshold_slider.setValue(self.config['threshold'])
                self.update_accessories_list()
                if 'theme' in loaded_config:
                    self.apply_theme(loaded_config['theme'])
                self.status_bar.setText("Settings loaded successfully.")
                QMessageBox.information(self, "Success", "Settings loaded successfully.")
            except Exception as e:
                self.status_bar.setText(f"Error loading settings: {e}")
                QMessageBox.critical(self, "Error", f"Failed to load settings: {e}")
                
    def closeEvent(self, event):
        self.stop_overlay()
        self.save_config()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    main_window = MainWindow()
    main_window.show()
    if sys.platform == 'win32':
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 6)  # 6 = SW_MINIMIZE
    sys.exit(app.exec_())