from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap, QImage
import math
import numpy as np
import os

class OverlayWindow(QWidget):
    """Displays the microphone visualization overlay."""
    def __init__(self, config, accessories_dir, characters_dir):
        super().__init__()
        self.config = config
        self.accessories_dir = accessories_dir
        self.characters_dir = characters_dir
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
        self.animation_phase = 0
        self.expression_state = 'neutral'
        self.expression_timer = 0
        
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)
        
        self.frequency_data = None
        self.frequency_timer = QTimer(self)
        self.frequency_timer.timeout.connect(self.clear_frequency_data)
        self.frequency_timer.setSingleShot(True)
        
        self.static_cache = None
        self.last_mouth_openness = -1
        self.last_is_speaking = False
        self.last_eye_state = -1
        self.last_character_scale = None
        self.accessory_images = {}
        self.character_images = {}
        
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
        """Update animation state for the overlay."""
        self.animation_phase = (self.animation_phase + 0.1) % (2 * math.pi)
        
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
            
        if self.config.get('facial_expressions', True):
            self.expression_timer += 1
            if self.is_speaking and self.volume_level > self.threshold * 2:
                if self.expression_state != 'happy' and self.expression_timer > 50:
                    self.expression_state = 'happy'
                    self.expression_timer = 0
            elif self.volume_level > self.threshold * 3:
                if self.expression_state != 'surprised':
                    self.expression_state = 'surprised'
                    self.expression_timer = 0
            elif self.expression_timer > 200:
                self.expression_state = 'neutral'
                
        self.apply_animation_preset()
        self.update()
        
    def apply_animation_preset(self):
        """Apply animation preset effects."""
        preset = self.config.get('animation_preset', 'none')
        if preset == 'bounce':
            bounce_height = 10 * math.sin(self.animation_phase * 2)
            self.config['character_y_offset'] = bounce_height
        elif preset == 'sway':
            sway_amount = 5 * math.sin(self.animation_phase)
            self.config['character_x_offset'] = sway_amount
        elif preset == 'pulse':
            pulse_amount = 0.1 * math.sin(self.animation_phase)
            self.config['character_scale'] = 1.0 + pulse_amount
        
    def set_volume(self, volume):
        """Set the current volume level."""
        self.volume_level = volume
        self.is_speaking = volume > self.threshold
        
    def set_frequency_data(self, data):
        """Set frequency data for visualization."""
        self.frequency_data = data
        self.frequency_timer.start(100)
        
    def clear_frequency_data(self):
        """Clear frequency data after timeout."""
        self.frequency_data = None
        
    def set_accessory_drag_mode(self, enabled):
        """Enable or disable accessory drag mode."""
        self.accessory_drag_mode = enabled
        self.update()
        
    def set_accessory_resize_mode(self, enabled):
        """Enable or disable accessory resize mode."""
        self.accessory_resize_mode = enabled
        self.update()
        
    def set_character_resize_mode(self, enabled):
        """Enable or disable character resize mode."""
        self.character_resize_mode = enabled
        self.static_cache = None
        self.update()
        
    def load_accessory_image(self, accessory_name):
        """Load an accessory image from the accessories directory."""
        if not accessory_name:
            return None
        if accessory_name not in self.accessory_images:
            for ext in ['.png', '.jpg', '.gif']:
                accessory_path = os.path.join(self.accessories_dir, f"{accessory_name}{ext}")
                if os.path.exists(accessory_path):
                    try:
                        image = QImage(accessory_path)
                        if not image.isNull():
                            self.accessory_images[accessory_name] = image
                            return image
                        else:
                            print(f"Failed to load accessory image: {accessory_path}")
                    except Exception as e:
                        print(f"Error loading accessory image {accessory_path}: {e}")
        return self.accessory_images.get(accessory_name)
    
    def load_character_image(self, character_name):
        """Load a character image from the characters directory."""
        if not character_name or character_name == 'default':
            return None
        if character_name not in self.character_images:
            for ext in ['.png', '.jpg', '.gif']:
                character_path = os.path.join(self.characters_dir, f"{character_name}{ext}")
                if os.path.exists(character_path):
                    try:
                        image = QImage(character_path)
                        if not image.isNull():
                            self.character_images[character_name] = image
                            return image
                        else:
                            print(f"Failed to load character image: {character_path}")
                    except Exception as e:
                        print(f"Error loading character image {character_path}: {e}")
        return self.character_images.get(character_name)
    
    def paintEvent(self, event):
        """Handle painting of the overlay window."""
        if (abs(self.mouth_openness - self.last_mouth_openness) < 0.01 and 
            self.is_speaking == self.last_is_speaking and
            self.eye_state == self.last_eye_state and
            self.config.get('character_scale') == self.last_character_scale and
            self.static_cache and self.static_cache.size() == self.size()):
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.static_cache)
            self.draw_dynamic_elements(painter)
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        self.draw_background_effect(painter)
        
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
        
    def draw_background_effect(self, painter):
        """Draw background effects based on configuration."""
        effect = self.config.get('background_effect', 'none')
        if effect == 'none':
            return
            
        bg_color = QColor(*self.config.get('bg_effect_color', [255, 255, 255, 50]))
        painter.setPen(Qt.NoPen)
        
        if effect == 'pulse' and self.is_speaking:
            pulse_size = min(self.width(), self.height()) * 0.1 * (self.volume_level / 1000)
            alpha = min(200, self.volume_level / 5)
            bg_color.setAlpha(alpha)
            painter.setBrush(bg_color)
            painter.drawEllipse(self.rect().center(), pulse_size, pulse_size)
            
        elif effect == 'gradient':
            from PyQt5.QtGui import QRadialGradient
            gradient = QRadialGradient(self.rect().center(), min(self.width(), self.height()) / 2)
            gradient.setColorAt(0, bg_color)
            gradient.setColorAt(1, Qt.transparent)
            painter.setBrush(gradient)
            painter.drawRect(self.rect())
        
    def draw_static_elements(self, painter):
        """Draw static elements of the overlay (e.g., character head)."""
        head_center = self.rect().center()
        head_radius = min(self.width(), self.height()) * 0.4 * self.config.get('character_scale', 1.0)
        
        head_center_x = head_center.x() + self.config.get('character_x_offset', 0)
        head_center_y = head_center.y() + self.config.get('character_y_offset', 0)
        head_center = QPoint(head_center_x, head_center_y)
        
        character_image = self.load_character_image(self.config.get('character_model', 'default'))
        if character_image:
            char_width = int(head_radius * 2.0)
            char_height = int(character_image.height() * (char_width / character_image.width()))
            scaled_character = character_image.scaled(char_width, char_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            char_x = head_center.x() - char_width // 2
            char_y = head_center.y() - char_height // 2
            painter.drawImage(char_x, char_y, scaled_character)
        else:
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
        """Draw dynamic elements of the overlay (e.g., mouth, waves)."""
        head_center = self.rect().center()
        head_radius = min(self.width(), self.height()) * 0.4 * self.config.get('character_scale', 1.0)
        
        head_center_x = head_center.x() + self.config.get('character_x_offset', 0)
        head_center_y = head_center.y() + self.config.get('character_y_offset', 0)
        head_center = QPoint(head_center_x, head_center_y)
        
        if not self.load_character_image(self.config.get('character_model', 'default')):
            eye_offset_x = int(head_radius * 0.3)
            eye_offset_y = int(-head_radius * 0.2)
            eye_radius = int(head_radius * 0.15)
            pupil_radius = int(eye_radius * 0.5)
            
            painter.setBrush(Qt.black)
            
            eye_y_offset = 0
            if self.expression_state == 'happy':
                eye_y_offset = -eye_radius * 0.2
            elif self.expression_state == 'sad':
                eye_y_offset = eye_radius * 0.2
                
            if self.eye_state == 0:
                painter.drawEllipse(head_center.x() - eye_offset_x, head_center.y() + eye_offset_y + eye_y_offset, 
                                   pupil_radius, pupil_radius)
                painter.drawEllipse(head_center.x() + eye_offset_x, head_center.y() + eye_offset_y + eye_y_offset, 
                                   pupil_radius, pupil_radius)
            elif self.eye_state == 1:
                half_pupil_height = int(pupil_radius * 0.5)
                painter.drawEllipse(head_center.x() - eye_offset_x, head_center.y() + eye_offset_y + int(half_pupil_height/2) + eye_y_offset, 
                                   pupil_radius, half_pupil_height)
                painter.drawEllipse(head_center.x() + eye_offset_x, head_center.y() + eye_offset_y + int(half_pupil_height/2) + eye_y_offset, 
                                   pupil_radius, half_pupil_height)
            
            mouth_width = int(head_radius * 0.7)
            mouth_height = int(head_radius * 0.4 * self.mouth_openness)
            mouth_y_offset = int(head_radius * 0.3)
            
            if self.expression_state == 'happy':
                mouth_height = int(head_radius * 0.3 * self.mouth_openness)
                mouth_y_offset = int(head_radius * 0.35)
            elif self.expression_state == 'sad':
                mouth_height = int(head_radius * 0.3 * self.mouth_openness)
                mouth_y_offset = int(head_radius * 0.25)
            elif self.expression_state == 'surprised':
                mouth_width = int(head_radius * 0.5)
                mouth_height = int(head_radius * 0.5 * self.mouth_openness)
                mouth_y_offset = int(head_radius * 0.3)
            
            mouth_color = QColor(*self.config.get('mouth_color', [255, 0, 0]))
            painter.setBrush(mouth_color)
            painter.drawEllipse(head_center.x() - int(mouth_width/2), 
                               head_center.y() + mouth_y_offset, 
                               mouth_width, mouth_height)
        
        if self.is_speaking:
            wave_pattern = self.config.get('wave_pattern', 'circular')
            wave_count = self.config.get('wave_count', 5)
            
            if wave_pattern == 'circular':
                self.draw_circular_waves(painter, head_center, head_radius, wave_count)
            elif wave_pattern == 'sinusoidal':
                self.draw_sinusoidal_waves(painter, head_center, head_radius, wave_count)
            elif wave_pattern == 'particle':
                self.draw_particle_effect(painter, head_center, head_radius)
            elif wave_pattern == 'frequency' and self.frequency_data is not None:
                self.draw_frequency_bars(painter, head_center, head_radius)
        
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
                
                animation_type = acc.get('animation', 'none')
                if animation_type == 'bounce':
                    bounce_height = 5 * math.sin(self.animation_phase * 3)
                    hat_y += bounce_height
                elif animation_type == 'rotate':
                    pass
                
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
    
    def draw_circular_waves(self, painter, center, radius, count):
        """Draw circular wave patterns."""
        max_wave_radius = int(radius * 1.5)
        wave_spread = int((max_wave_radius - radius) / count)
        wave_color = QColor(*self.config.get('wave_color', [255, 255, 255]))
        
        for i in range(count):
            wave_radius = int(radius + wave_spread * (i + 1))
            alpha = 150 - (i * 25)
            wave_color.setAlpha(alpha)
            painter.setPen(QPen(wave_color, 2))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(center, wave_radius, wave_radius)
    
    def draw_sinusoidal_waves(self, painter, center, radius, count):
        """Draw sinusoidal wave patterns."""
        wave_color = QColor(*self.config.get('wave_color', [255, 255, 255]))
        points = []
        wave_count = count * 2
        max_amplitude = radius * 0.2
        
        for i in range(361):
            angle = math.radians(i)
            distance = radius + max_amplitude * math.sin(angle * wave_count + self.animation_phase)
            x = center.x() + distance * math.cos(angle)
            y = center.y() + distance * math.sin(angle)
            points.append(QPoint(x, y))
        
        wave_color.setAlpha(150)
        painter.setPen(QPen(wave_color, 2))
        painter.setBrush(Qt.NoBrush)
        
        for i in range(len(points) - 1):
            painter.drawLine(points[i], points[i + 1])
    
    def draw_particle_effect(self, painter, center, radius):
        """Draw particle effect patterns."""
        particle_count = 30
        max_distance = radius * 1.5
        wave_color = QColor(*self.config.get('wave_color', [255, 255, 255]))
        
        for i in range(particle_count):
            angle = 2 * math.pi * i / particle_count + self.animation_phase
            distance = radius + (max_distance - radius) * (0.5 + 0.5 * math.sin(self.animation_phase * 2 + i * 0.5))
            x = center.x() + distance * math.cos(angle)
            y = center.y() + distance * math.sin(angle)
            size = 3 + 2 * math.sin(self.animation_phase + i * 0.3)
            
            alpha = 150 + int(100 * math.sin(self.animation_phase + i * 0.2))
            wave_color.setAlpha(max(0, min(255, alpha)))
            painter.setPen(Qt.NoPen)
            painter.setBrush(wave_color)
            painter.drawEllipse(int(x - size/2), int(y - size/2), int(size), int(size))
    
    def draw_frequency_bars(self, painter, center, radius):
        """Draw frequency bar visualizations."""
        if self.frequency_data is None:
            return
            
        data_len = len(self.frequency_data)
        low_end = data_len // 3
        mid_end = 2 * data_len // 3
        
        low_freq = np.mean(self.frequency_data[:low_end]) if low_end > 0 else 0
        mid_freq = np.mean(self.frequency_data[low_end:mid_end]) if mid_end > low_end else 0
        high_freq = np.mean(self.frequency_data[mid_end:]) if data_len > mid_end else 0
        
        max_val = max(low_freq, mid_freq, high_freq, 1)
        low_height = (low_freq / max_val) * radius * 0.5
        mid_height = (mid_freq / max_val) * radius * 0.5
        high_height = (high_freq / max_val) * radius * 0.5
        
        bar_width = radius * 0.1
        spacing = bar_width * 0.5
        
        low_color = QColor(*self.config.get('low_freq_color', [0, 0, 255]))
        mid_color = QColor(*self.config.get('mid_freq_color', [0, 255, 0]))
        high_color = QColor(*self.config.get('high_freq_color', [255, 0, 0]))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(low_color)
        low_x = center.x() - bar_width * 1.5 - spacing
        painter.drawRect(int(low_x), int(center.y() - low_height/2), 
                         int(bar_width), int(low_height))
        
        painter.setBrush(mid_color)
        mid_x = center.x() - bar_width/2
        painter.drawRect(int(mid_x), int(center.y() - mid_height/2), 
                         int(bar_width), int(mid_height))
        
        painter.setBrush(high_color)
        high_x = center.x() + bar_width/2 + spacing
        painter.drawRect(int(high_x), int(center.y() - high_freq/2), 
                         int(bar_width), int(high_height))