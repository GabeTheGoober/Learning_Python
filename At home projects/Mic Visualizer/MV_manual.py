import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class ManualWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MicVis Manual")
        self.setGeometry(200, 200, 600, 400)
        central = QWidget()
        layout = QVBoxLayout(central)
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
<h1>MicVis App Manual</h1>
<p>Welcome to MicVis, a Python-based application that creates a virtual character overlay responding to microphone input. This manual guides you through its features and usage.</p>

<h2>Overview</h2>
<p>The app consists of a control window for settings and an overlay window showing the character. The character blinks, opens its mouth when speaking, and shows sound waves.</p>

<h2>Getting Started</h2>
<ol>
<li><b>Select Microphone:</b> In "Audio Settings", choose your microphone from the dropdown. Click "Refresh" if needed.</li>
<li><b>Calibrate Sensitivity:</b> Click "Calibrate Sensitivity" and stay silent for 3 seconds to set background noise level.</li>
<li><b>Adjust Sensitivity:</b> Use the slider in "Visualization Settings" to set the threshold for detecting speech.</li>
<li><b>Start Overlay:</b> Click "Start Overlay" to launch the character window.</li>
<li><b>Speak:</b> Talk into the microphone to see the character react.</li>
<li><b>Stop Overlay:</b> Click "Stop Overlay" to close the character window.</li>
</ol>

<h2>Customization</h2>
<h3>Appearance Settings</h3>
<p>Click "Appearance Settings" button:</p>
<ul>
<li><b>Wave Count:</b> Set the number of sound waves (1-10).</li>
<li><b>Colors:</b> Change head, mouth, and wave colors using the buttons.</li>
</ul>

<h3>Themes</h3>
<p>Click the 🎨 button to select a theme: Default, Red, Blue, or Dark.</li>

<h3>Accessories</h3>
<p>Add PNG images to the "MV_accessories" folder (or subfolders) in the app's directory.</p>
<ul>
<li><b>Add Accessory:</b> Select from the dropdown and click "Add".</li>
<li><b>Remove:</b> Select in the list and click "Remove Selected".</li>
<li><b>Position/Size:</b> Select accessory, enable "Move" or "Resize", then drag/resize in overlay.</li>
</ul>
<p><b>Resize Character:</b> Enable "Resize Character" and drag corners in overlay.</p>

<h2>Saving and Loading</h2>
<p>Click "Save Settings" to save config to MV_pr.json.</p>
<p>Click "Load Settings" to load from a JSON file.</p>

<h2>Troubleshooting</h2>
<ul>
<li>No devices: Check microphone connection.</li>
<li>Overlay not responding: Check sensitivity and volume meter.</li>
<li>Accessories not loading: Ensure PNG files in correct folder.</li>
</ul>

<p>For issues, check console or restart app.</p>
""")
        layout.addWidget(browser)
        self.setCentralWidget(central)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ManualWindow()
    win.show()
    sys.exit(app.exec_())