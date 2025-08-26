import sys
import os
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QTextBrowser, QPushButton
from PyQt5.QtCore import Qt

class ManualDialog(QDialog):
    """Displays the MicVis user manual."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MicVis Manual")
        self.setGeometry(100, 100, 600, 400)
        
        # Set up layout
        layout = QVBoxLayout(self)
        
        # Text browser for manual content
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        manual_content = """
            <h1>MicVis User Manual</h1>
            <h2>Welcome to MicVis</h2>
            <p>MicVis is a microphone visualization tool that displays a character responding to audio input with customizable visuals.</p>
            
            <h2>Setup</h2>
            <ul>
                <li><b>Install Dependencies</b>: Ensure you have the required libraries installed. Run <code>pip install -r requirements.txt</code> to install PyQt5, pyaudio, numpy, and scipy.</li>
                <li><b>Add Accessories</b>: Place accessory images (.png, .jpg, .gif) in the <code>MV_accessories</code> folder.</li>
                <li><b>Add Characters</b>: Place character images (.png, .jpg, .gif) in the <code>MV_characters</code> folder.</li>
                <li><b>Configuration</b>: The app automatically creates <code>MV_pr.json</code> for settings. Do not delete this file.</li>
            </ul>
            
            <h2>Usage</h2>
            <ol>
                <li><b>Select Microphone</b>: Choose an audio input device from the dropdown. Click "Refresh" to update the list.</li>
                <li><b>Calibrate Sensitivity</b>: Click "Calibrate Sensitivity" to set an appropriate threshold based on background noise.</li>
                <li><b>Customize Appearance</b>: Use "Appearance Settings" to change themes, colors, and wave count.</li>
                <li><b>Advanced Settings</b>: Configure wave patterns, background effects, character models, and animations.</li>
                <li><b>Add Accessories</b>: Select accessories from the dropdown and click "Add". Adjust their position and scale using drag/resize modes.</li>
                <li><b>Start Overlay</b>: Click "Start Overlay" to display the visualization. Speak to see the character respond.</li>
                <li><b>Save/Load Settings</b>: Save your configuration or load a previous one using the respective buttons.</li>
            </ol>
            
            <h2>Troubleshooting</h2>
            <ul>
                <li><b>No Audio Devices Found</b>: Ensure your microphone is connected and recognized by your system.</li>
                <li><b>Overlay Not Responding</b>: Check the sensitivity threshold and ensure the correct microphone is selected.</li>
                <li><b>Images Not Loading</b>: Verify that images in <code>MV_accessories</code> and <code>MV_characters</code> are valid .png, .jpg, or .gif files.</li>
                <li><b>Performance Issues</b>: Reduce wave count or disable frequency analysis in Advanced Settings.</li>
            </ul>
            
            <h2>Support</h2>
            <p>For further assistance, contact the developer or check the project repository at <a href="https://github.com/your-repo/micvis">github.com/your-repo/micvis</a>.</p>
        """
        browser.setHtml(manual_content)
        layout.addWidget(browser)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        # Apply stylesheet for consistency
        self.setStyleSheet("""
            QDialog {
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
            QTextBrowser {
                background-color: white;
                border: 1px solid #bbbbbb;
                border-radius: 4px;
                padding: 10px;
            }
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ManualDialog()
    dialog.show()
    sys.exit(app.exec_())