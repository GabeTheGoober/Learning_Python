import sys
import os
from PyInstaller.__main__ import run

# Determine if running in a bundled executable
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

# PyInstaller options
opts = [
    "G's AutoClicker.py",      # Mainscript file goes here
    '--onefile',           # Create a single executable
    '--windowed',          # For GUI applications (no console)
    "--name=G's AutoClicker",  # Name of the output executable
    '--icon=mouseclick.ico',     # Icon file (optional)
    '--add-data=mouseclick.ico;.',  # Include icon file
    '--noconfirm',         # Overwrite output directory without confirmation
    '--clean',             # Clean PyInstaller cache before building
]

# Add hidden imports for Windows
if sys.platform == 'win32':
    opts.extend([
        '--hidden-import=pyautogui',
        '--hidden-import=keyboard',
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=PyQt6.QtWinExtras',
    ])

# Run PyInstaller
run(opts)