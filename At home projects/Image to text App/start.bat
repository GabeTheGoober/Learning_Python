@echo off
REM Get the directory where this batch file is located
set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

REM Optional: Activate virtual environment if it exists
if exist "%ROOT_DIR%venv\Scripts\activate.bat" (
    call "%ROOT_DIR%venv\Scripts\activate.bat"
    echo [INFO] Virtual environment activated.
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/downloads/
    echo Recommended version: Python 3.8 or higher
    pause
    exit /b 1
)

REM Check Python version (require 3.8 or higher for compatibility)
for /f "tokens=2 delims= " %%v in ('python --version') do set "PY_VERSION=%%v"
for /f "tokens=1,2 delims=." %%a in ("%PY_VERSION%") do (
    set "PY_MAJOR=%%a"
    set "PY_MINOR=%%b"
)
if %PY_MAJOR% LSS 3 (
    echo [ERROR] Python version %PY_VERSION% is too old.
    echo Please install Python 3.8 or higher.
    pause
    exit /b 1
)
if %PY_MAJOR%==3 if %PY_MINOR% LSS 8 (
    echo [ERROR] Python version %PY_VERSION% is too old.
    echo Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Install required packages
echo.
echo Checking for required Python packages...

REM Define a helper to check and install modules
call :CheckModule PyQt5 PyQt5
call :CheckModule PIL Pillow
call :CheckModule pytesseract pytesseract
call :CheckModule fitz PyMuPDF
call :CheckModule reportlab reportlab
call :CheckModule cv2 opencv-python
call :CheckModule pandas pandas

REM Check if Tesseract is installed
pytesseract --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Tesseract OCR is not installed or not in your PATH.
    echo Please install Tesseract from https://github.com/tesseract-ocr/tesseract
    echo and ensure it's added to your system PATH.
    echo The app will not function without Tesseract.
    pause
)

echo.
echo [OK] All required packages are installed.
echo Starting Enhanced Image to Text App...
echo.

REM Launch the app
python image_to_text.py
if errorlevel 1 (
    echo [ERROR] Failed to start the application. Check for errors above.
    pause
    exit /b 1
)
pause
exit /b 0

:CheckModule
setlocal
set "IMPORT_NAME=%~1"
set "PACKAGE_NAME=%~2"

python -c "import %IMPORT_NAME%" 2>nul
if errorlevel 1 (
    echo [INFO] Installing %PACKAGE_NAME%...
    pip install %PACKAGE_NAME% --no-warn-script-location
    if errorlevel 1 (
        echo [ERROR] Failed to install %PACKAGE_NAME%. Check your internet connection or pip configuration.
        pause
        exit /b 1
    )
) else (
    echo [OK] %IMPORT_NAME% is already installed.
)
endlocal
goto :eof