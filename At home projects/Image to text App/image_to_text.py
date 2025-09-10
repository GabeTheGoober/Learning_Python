import sys
import os
import tempfile
import shutil
from PIL import Image
import pytesseract
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                             QTabWidget, QFileDialog, QMessageBox, QProgressBar,
                             QListWidget, QCheckBox, QSpinBox, QGroupBox, QComboBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QIcon
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import fitz  # PyMuPDF for PDF preview

class OCRWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, image_paths, language='eng'):
        super().__init__()
        self.image_paths = image_paths
        self.language = language

    def run(self):
        try:
            results = []
            total = len(self.image_paths)
            
            for i, image_path in enumerate(self.image_paths):
                # Update progress
                self.progress.emit(int((i / total) * 100))
                
                # Perform OCR
                text = pytesseract.image_to_string(Image.open(image_path), lang=self.language)
                results.append(text)
            
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

class PDFWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, texts, output_path, font_size=12):
        super().__init__()
        self.texts = texts
        self.output_path = output_path
        self.font_size = font_size

    def run(self):
        try:
            c = canvas.Canvas(self.output_path, pagesize=letter)
            width, height = letter
            
            # Register a font (using default Helvetica for simplicity)
            # You could add custom font support here
            
            total = len(self.texts)
            for i, text in enumerate(self.texts):
                # Update progress
                self.progress.emit(int((i / total) * 100))
                
                # Start a new page for each text (except the first)
                if i > 0:
                    c.showPage()
                
                # Set font
                c.setFont("Helvetica", self.font_size)
                
                # Split text into lines that fit the page
                lines = []
                for line in text.split('\n'):
                    words = line.split()
                    current_line = []
                    for word in words:
                        test_line = ' '.join(current_line + [word])
                        if c.stringWidth(test_line, "Helvetica", self.font_size) < width - 100:
                            current_line.append(word)
                        else:
                            if current_line:
                                lines.append(' '.join(current_line))
                            current_line = [word]
                    if current_line:
                        lines.append(' '.join(current_line))
                
                # Draw text on page
                y_position = height - 50
                for line in lines:
                    if y_position < 50:  # Need a new page
                        c.showPage()
                        c.setFont("Helvetica", self.font_size)
                        y_position = height - 50
                    
                    c.drawString(50, y_position, line)
                    y_position -= self.font_size + 2
            
            c.save()
            self.finished.emit(self.output_path)
        except Exception as e:
            self.error.emit(str(e))

class ImageToTextApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image to Text Converter")
        self.setGeometry(100, 100, 900, 700)
        
        # Initialize variables
        self.image_paths = []
        self.ocr_results = []
        self.is_book_mode = False
        self.current_language = 'eng'
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Image to Text Converter")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Mode selection
        mode_group = QGroupBox("Conversion Mode")
        mode_layout = QHBoxLayout(mode_group)
        
        self.single_mode_btn = QPushButton("Single Text Mode")
        self.single_mode_btn.setCheckable(True)
        self.single_mode_btn.setChecked(True)
        self.single_mode_btn.clicked.connect(self.set_single_mode)
        
        self.book_mode_btn = QPushButton("Book Mode")
        self.book_mode_btn.setCheckable(True)
        self.book_mode_btn.clicked.connect(self.set_book_mode)
        
        mode_layout.addWidget(self.single_mode_btn)
        mode_layout.addWidget(self.book_mode_btn)
        layout.addWidget(mode_group)
        
        # Language selection
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("OCR Language:"))
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English (eng)", "Spanish (spa)", "French (fre)", "German (ger)", 
                                 "Italian (ita)", "Portuguese (por)", "Chinese (chi_sim)", "Japanese (jpn)"])
        lang_layout.addWidget(self.lang_combo)
        
        layout.addLayout(lang_layout)
        
        # Image selection area
        select_group = QGroupBox("Image Selection")
        select_layout = QVBoxLayout(select_group)
        
        self.image_list = QListWidget()
        select_layout.addWidget(self.image_list)
        
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Images")
        self.add_btn.clicked.connect(self.add_images)
        
        self.clear_btn = QPushButton("Clear List")
        self.clear_btn.clicked.connect(self.clear_images)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.clear_btn)
        select_layout.addLayout(btn_layout)
        
        layout.addWidget(select_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Convert button
        self.convert_btn = QPushButton("Convert to Text")
        self.convert_btn.clicked.connect(self.convert_images)
        layout.addWidget(self.convert_btn)
        
        # Result area - will be shown after conversion
        self.result_tabs = QTabWidget()
        self.result_tabs.setVisible(False)
        layout.addWidget(self.result_tabs)
        
        # PDF options (for book mode)
        self.pdf_group = QGroupBox("PDF Options")
        pdf_layout = QHBoxLayout(self.pdf_group)
        
        pdf_layout.addWidget(QLabel("Font Size:"))
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 24)
        self.font_size.setValue(12)
        pdf_layout.addWidget(self.font_size)
        
        self.compile_pdf_btn = QPushButton("Compile as PDF")
        self.compile_pdf_btn.clicked.connect(self.compile_pdf)
        pdf_layout.addWidget(self.compile_pdf_btn)
        
        self.pdf_group.setVisible(False)
        layout.addWidget(self.pdf_group)
        
    def set_single_mode(self):
        self.single_mode_btn.setChecked(True)
        self.book_mode_btn.setChecked(False)
        self.is_book_mode = False
        self.clear_results()
        
    def set_book_mode(self):
        self.single_mode_btn.setChecked(False)
        self.book_mode_btn.setChecked(True)
        self.is_book_mode = True
        self.clear_results()
        
    def add_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", 
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if files:
            self.image_paths.extend(files)
            self.update_image_list()
            
    def clear_images(self):
        self.image_paths.clear()
        self.update_image_list()
        
    def update_image_list(self):
        self.image_list.clear()
        for path in self.image_paths:
            self.image_list.addItem(os.path.basename(path))
            
    def clear_results(self):
        self.result_tabs.clear()
        self.result_tabs.setVisible(False)
        self.pdf_group.setVisible(False)
        self.ocr_results = []
        
    def convert_images(self):
        if not self.image_paths:
            QMessageBox.warning(self, "No Images", "Please select at least one image.")
            return
            
        # Get selected language
        lang_text = self.lang_combo.currentText()
        self.current_language = lang_text[lang_text.find('(')+1:lang_text.find(')')]
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.convert_btn.setEnabled(False)
        
        # Create and start OCR worker
        self.ocr_worker = OCRWorker(self.image_paths, self.current_language)
        self.ocr_worker.progress.connect(self.progress_bar.setValue)
        self.ocr_worker.finished.connect(self.ocr_finished)
        self.ocr_worker.error.connect(self.ocr_error)
        self.ocr_worker.start()
        
    def ocr_finished(self, results):
        self.ocr_results = results
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)
        
        # Display results
        self.result_tabs.clear()
        
        if self.is_book_mode:
            # Book mode - create a tab for each page
            for i, text in enumerate(results):
                tab = QTextEdit()
                tab.setPlainText(text)
                self.result_tabs.addTab(tab, f"Page {i+1}")
            
            self.pdf_group.setVisible(True)
        else:
            # Single mode - combine all text
            tab = QTextEdit()
            combined_text = "\n\n".join(results)
            tab.setPlainText(combined_text)
            self.result_tabs.addTab(tab, "Extracted Text")
            
        self.result_tabs.setVisible(True)
        
        QMessageBox.information(self, "Conversion Completed", 
                               "Text extraction completed successfully!")
        
    def ocr_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)
        QMessageBox.critical(self, "OCR Error", f"An error occurred during OCR:\n{error_msg}")
        
    def compile_pdf(self):
        if not self.ocr_results:
            QMessageBox.warning(self, "No Text", "No text available to compile.")
            return
            
        # Get output path
        output_path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF", "", "PDF Files (*.pdf)"
        )
        
        if not output_path:
            return
            
        # Show progress
        self.progress_bar.setVisible(True)
        self.compile_pdf_btn.setEnabled(False)
        
        # Create and start PDF worker
        self.pdf_worker = PDFWorker(self.ocr_results, output_path, self.font_size.value())
        self.pdf_worker.progress.connect(self.progress_bar.setValue)
        self.pdf_worker.finished.connect(self.pdf_finished)
        self.pdf_worker.error.connect(self.pdf_error)
        self.pdf_worker.start()
        
    def pdf_finished(self, output_path):
        self.progress_bar.setVisible(False)
        self.compile_pdf_btn.setEnabled(True)
        QMessageBox.information(self, "PDF Created 📄", 
                               f"PDF successfully created at:\n{output_path}")
        
    def pdf_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.compile_pdf_btn.setEnabled(True)
        QMessageBox.critical(self, "PDF Error", f"An error occurred creating PDF:\n{error_msg}")

def main():
    # Check if Tesseract is installed (It should already be in the same directory as this script)
    try:
        pytesseract.get_tesseract_version()
    except:
        QMessageBox.critical(None, "Tesseract Error", 
                           "Tesseract OCR is not installed or not in your PATH.\n"
                           "Please install it from https://github.com/tesseract-ocr/tesseract")
        return
    
    app = QApplication(sys.argv)
    window = ImageToTextApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()