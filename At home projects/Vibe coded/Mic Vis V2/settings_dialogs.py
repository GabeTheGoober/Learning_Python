from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QComboBox, QLabel, QSpinBox, QCheckBox, QTabWidget, QColorDialog
from PyQt5.QtCore import Qt
import os

class AppearanceSettings(QDialog):
    """Dialog for appearance settings."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Appearance Settings")
        layout = QVBoxLayout(self)

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

        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_changes)
        btn_layout.addWidget(apply_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

    def preview_theme(self, theme_name):
        """Preview a theme without applying it."""
        self.parent.preview_theme(theme_name.lower())

    def apply_preview(self):
        """Apply the previewed theme."""
        self.parent.apply_theme(self.theme_combo.currentText().lower())

    def apply_changes(self):
        """Apply and save theme changes."""
        self.parent.apply_theme(self.theme_combo.currentText().lower())
        self.parent.save_config()
        self.close()

class AdvancedSettings(QDialog):
    """Dialog for advanced settings."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Advanced Settings")
        self.setGeometry(100, 100, 500, 400)
        
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        
        # Audio Visualization Tab
        audio_viz_tab = QGroupBox("Audio Visualization")
        audio_viz_layout = QVBoxLayout(audio_viz_tab)
        
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(QLabel("Frequency Analysis:"))
        self.freq_check = QCheckBox()
        self.freq_check.setChecked(self.parent.config.get('frequency_analysis', False))
        self.freq_check.stateChanged.connect(self.toggle_frequency_analysis)
        freq_layout.addWidget(self.freq_check)
        freq_layout.addStretch()
        audio_viz_layout.addLayout(freq_layout)
        
        freq_color_layout = QHBoxLayout()
        freq_color_layout.addWidget(QLabel("Low Freq Color:"))
        self.low_color_btn = QPushButton()
        self.low_color_btn.clicked.connect(lambda: self.change_color('low_freq_color'))
        freq_color_layout.addWidget(self.low_color_btn)
        
        freq_color_layout.addWidget(QLabel("Mid Freq Color:"))
        self.mid_color_btn = QPushButton()
        self.mid_color_btn.clicked.connect(lambda: self.change_color('mid_freq_color'))
        freq_color_layout.addWidget(self.mid_color_btn)
        
        freq_color_layout.addWidget(QLabel("High Freq Color:"))
        self.high_color_btn = QPushButton()
        self.high_color_btn.clicked.connect(lambda: self.change_color('high_freq_color'))
        freq_color_layout.addWidget(self.high_color_btn)
        audio_viz_layout.addLayout(freq_color_layout)
        
        wave_layout = QHBoxLayout()
        wave_layout.addWidget(QLabel("Wave Pattern:"))
        self.wave_combo = QComboBox()
        self.wave_combo.addItems(['Circular', 'Sinusoidal', 'Particle', 'Frequency'])
        self.wave_combo.setCurrentText(self.parent.config.get('wave_pattern', 'circular').capitalize())
        self.wave_combo.currentTextChanged.connect(self.change_wave_pattern)
        wave_layout.addWidget(self.wave_combo)
        audio_viz_layout.addLayout(wave_layout)
        
        bg_layout = QHBoxLayout()
        bg_layout.addWidget(QLabel("Background Effect:"))
        self.bg_combo = QComboBox()
        self.bg_combo.addItems(['None', 'Pulse', 'Gradient'])
        self.bg_combo.setCurrentText(self.parent.config.get('background_effect', 'none').capitalize())
        self.bg_combo.currentTextChanged.connect(self.change_bg_effect)
        bg_layout.addWidget(self.bg_combo)
        audio_viz_layout.addLayout(bg_layout)
        
        bg_color_layout = QHBoxLayout()
        bg_color_layout.addWidget(QLabel("BG Effect Color:"))
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.clicked.connect(lambda: self.change_color('bg_effect_color'))
        bg_color_layout.addWidget(self.bg_color_btn)
        audio_viz_layout.addLayout(bg_color_layout)
        
        tabs.addTab(audio_viz_tab, "Audio Visualization")
        
        # Character Tab
        character_tab = QGroupBox("Character")
        character_layout = QVBoxLayout(character_tab)
        
        char_layout = QHBoxLayout()
        char_layout.addWidget(QLabel("Character Model:"))
        self.char_combo = QComboBox()
        self.populate_character_combo()
        self.char_combo.setCurrentText(self.parent.config.get('character_model', 'default'))
        self.char_combo.currentTextChanged.connect(self.change_character_model)
        char_layout.addWidget(self.char_combo)
        character_layout.addLayout(char_layout)
        
        anim_layout = QHBoxLayout()
        anim_layout.addWidget(QLabel("Animation Preset:"))
        self.anim_combo = QComboBox()
        self.anim_combo.addItems(['None', 'Bounce', 'Sway', 'Pulse'])
        self.anim_combo.setCurrentText(self.parent.config.get('animation_preset', 'none').capitalize())
        self.anim_combo.currentTextChanged.connect(self.change_animation_preset)
        anim_layout.addWidget(self.anim_combo)
        character_layout.addLayout(anim_layout)
        
        expr_layout = QHBoxLayout()
        expr_layout.addWidget(QLabel("Facial Expressions:"))
        self.expr_check = QCheckBox()
        self.expr_check.setChecked(self.parent.config.get('facial_expressions', True))
        self.expr_check.stateChanged.connect(self.toggle_facial_expressions)
        expr_layout.addWidget(self.expr_check)
        expr_layout.addStretch()
        character_layout.addLayout(expr_layout)
        
        tabs.addTab(character_tab, "Character")
        
        # Accessories Tab
        accessories_tab = QGroupBox("Accessories")
        accessories_layout = QVBoxLayout(accessories_tab)
        
        acc_anim_layout = QHBoxLayout()
        acc_anim_layout.addWidget(QLabel("Accessory Animation:"))
        self.acc_anim_combo = QComboBox()
        self.acc_anim_combo.addItems(['None', 'Bounce', 'Rotate'])
        acc_anim_layout.addWidget(self.acc_anim_combo)
        accessories_layout.addLayout(acc_anim_layout)
        
        tabs.addTab(accessories_tab, "Accessories")
        
        layout.addWidget(tabs)
        
        btn_layout = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_changes)
        btn_layout.addWidget(apply_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        self.update_color_buttons()
    
    def populate_character_combo(self):
        """Populate the character model combo box."""
        self.char_combo.addItem("Default")
        if os.path.exists(self.parent.characters_dir):
            for file in os.listdir(self.parent.characters_dir):
                if file.lower().endswith(('.png', '.jpg', '.gif')):
                    self.char_combo.addItem(os.path.splitext(file)[0])
    
    def update_color_buttons(self):
        """Update color button styles based on configuration."""
        low_color = QColor(*self.parent.config.get('low_freq_color', [0, 0, 255]))
        self.low_color_btn.setStyleSheet(f"background-color: {low_color.name()}")
        
        mid_color = QColor(*self.parent.config.get('mid_freq_color', [0, 255, 0]))
        self.mid_color_btn.setStyleSheet(f"background-color: {mid_color.name()}")
        
        high_color = QColor(*self.parent.config.get('high_freq_color', [255, 0, 0]))
        self.high_color_btn.setStyleSheet(f"background-color: {high_color.name()}")
        
        bg_color = QColor(*self.parent.config.get('bg_effect_color', [255, 255, 255, 50]))
        self.bg_color_btn.setStyleSheet(f"background-color: rgba({bg_color.red()}, {bg_color.green()}, {bg_color.blue()}, {bg_color.alpha()})")
    
    def toggle_frequency_analysis(self, state):
        """Toggle frequency analysis setting."""
        self.parent.config['frequency_analysis'] = (state == Qt.Checked)
        if hasattr(self.parent, 'audio_worker'):
            self.parent.audio_worker.set_frequency_analysis(state == Qt.Checked)
    
    def change_wave_pattern(self, pattern):
        """Change the wave pattern."""
        self.parent.config['wave_pattern'] = pattern.lower()
    
    def change_bg_effect(self, effect):
        """Change the background effect."""
        self.parent.config['background_effect'] = effect.lower()
    
    def change_character_model(self, model):
        """Change the character model."""
        self.parent.config['character_model'] = model
    
    def change_animation_preset(self, preset):
        """Change the animation preset."""
        self.parent.config['animation_preset'] = preset.lower()
    
    def toggle_facial_expressions(self, state):
        """Toggle facial expressions setting."""
        self.parent.config['facial_expressions'] = (state == Qt.Checked)
    
    def change_color(self, color_type):
        """Change a color setting."""
        color = QColorDialog.getColor(QColor(*self.parent.config[color_type]), self)
        if color.isValid():
            self.parent.config[color_type] = [color.red(), color.green(), color.blue(), color.alpha() if color.alpha() < 255 else 255]
            self.update_color_buttons()
    
    def apply_changes(self):
        """Apply and save advanced settings."""
        self.parent.save_config()
        if hasattr(self.parent, 'overlay'):
            self.parent.overlay.config = self.parent.config
            self.parent.overlay.update()
        self.close()