import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextBrowser, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class ManualWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MicVis Manual")
        self.setGeometry(200, 200, 700, 500)
        central = QWidget()
        layout = QVBoxLayout(central)
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
<h1>MicVis App Manual</h1>
<p>Welcome to MicVis, a Python-based application that creates a virtual character overlay responding to microphone input and speech recognition. This manual guides you through its features and usage.</p>

<h2>Overview</h2>
<p>The app consists of a control window for settings and an overlay window showing the character. The character blinks, opens its mouth when speaking, shows sound waves, and expresses emotions based on recognized speech.</p>

<h2>Getting Started</h2>
<ol>
<li><b>Select Microphone:</b> In "Audio Settings", choose your microphone from the dropdown. Click "Refresh" if needed.</li>
<li><b>Calibrate Sensitivity:</b> Click "Calibrate Sensitivity" and stay silent for 3 seconds to set background noise level.</li>
<li><b>Adjust Sensitivity:</b> Use the slider in "Visualization Settings" to set the threshold for detecting speech.</li>
<li><b>Enable Speech Recognition:</b> Check the "Enable Speech Recognition" box to enable emotion detection from speech.</li>
<li><b>Start Overlay:</b> Click "Start Overlay" to launch the character window.</li>
<li><b>Speak:</b> Talk into the microphone to see the character react with mouth movements and emotions.</li>
<li><b>Stop Overlay:</b> Click "Stop Overlay" to close the character window.</li>
</ol>

<h2>Speech Recognition Features</h2>
<p>When enabled, MicVis can detect emotions from your speech using keyword recognition:</p>
<ul>
<li><b>Happy:</b> Triggered by words like "happy", "joy", "great", "awesome"</li>
<li><b>Sad:</b> Triggered by words like "sad", "bad", "terrible", "sorry"</li>
<li><b>Angry:</b> Triggered by words like "angry", "mad", "furious", "hate"</li>
<li><b>Surprised:</b> Triggered by words like "wow", "surprise", "amazing", "shocking"</li>
</ul>
<p>You can customize these keywords by editing the SRecog.json file in the application directory.</p>

<h2>Customization</h2>
<h3>Appearance Settings</h3>
<p>Click "Appearance Settings" button:</p>
<ul>
<li><b>Theme Selection:</b> Choose from Default, Red, Blue, Dark, Light, Purple, or Green themes.</li>
<li><b>Wave Count:</b> Set the number of sound waves (1-10).</li>
<li><b>Wave Style:</b> Choose between Circles or Dots for the sound visualization.</li>
<li><b>Colors:</b> Change head, mouth, and wave colors using the buttons.</li>
</ul>

<h3>Face Configuration</h3>
<p>Click "Configure Face" button to fine-tune facial animations:</p>
<ul>
<li><b>Squint Freq Threshold:</b> Adjust the frequency threshold that makes the character squint</li>
<li><b>Squint Amount:</b> Control how much the character squints</li>
<li><b>Enlarge Vol Threshold Mult:</b> Set volume multiplier for eye enlargement</li>
<li><b>Enlarge Amount:</b> Control how much eyes enlarge when speaking loudly</li>
<li><b>Blink Interval:</b> Adjust how often the character blinks</li>
<li><b>Mouth Multiplier:</b> Control how much the mouth opens when speaking</li>
</ul>

<h3>Themes</h3>
<p>Click the 🎨 button to select a theme: Default, Red, Blue, Dark, Light, Purple, or Green.</p>

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
<li><b>No audio devices:</b> Check microphone connection and permissions.</li>
<li><b>Overlay not responding:</b> Check sensitivity and volume meter.</li>
<li><b>Accessories not loading:</b> Ensure PNG files are in the MV_accessories folder.</li>
<li><b>Speech recognition not working:</b>
  <ul>
    <li>Ensure you have an internet connection (required for Google speech recognition)</li>
    <li>Check that the SpeechRecognition library is installed: <code>pip install SpeechRecognition</code></li>
    <li>Verify microphone permissions in Windows settings</li>
  </ul>
</li>
<li><b>Application freezing:</b> Try increasing the audio chunk size in the code if using a low-power device.</li>
</ul>

<h2>Technical Information</h2>
<p>MicVis uses:</p>
<ul>
<li>PyAudio for audio input</li>
<li>SpeechRecognition for speech-to-text conversion</li>
<li>Google Speech Recognition API for processing (requires internet)</li>
<li>PyQt5 for the graphical interface</li>
<li>NumPy for audio processing</li>
</ul>

<p>For additional issues, check the console output for error messages or restart the application.</p>

<h2>File Structure</h2>
<ul>
<li><b>MV_pr.json:</b> Main configuration file</li>
<li><b>SRecog.json:</b> Speech recognition keywords for emotion detection</li>
<li><b>MV_accessories/:</b> Folder for accessory PNG images</li>
<li><b>MV_manual.py:</b> This manual</li>
</ul>
""")
        layout.addWidget(browser)
        self.setCentralWidget(central)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ManualWindow()
    win.show()
    sys.exit(app.exec_())