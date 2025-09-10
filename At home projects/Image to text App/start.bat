@echo off
REM Get the directory where this batch file is located
set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

REM Optional: Activate virtual environment if it exists
if exist "%ROOT_DIR%venv\Scripts\activate.bat" (
    call "%ROOT_DIR%venv\Scripts\activate.bat"
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/downloads/
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

echo.
echo [OK] All required packages are installed.
echo Starting Image to Text App...
echo.

REM Launch the app
python image_to_text.py
pause
exit /b 0

:CheckModule
setlocal
set "IMPORT_NAME=%~1"
set "PACKAGE_NAME=%~2"

python -c "import %IMPORT_NAME%" 2>nul
if errorlevel 1 (
    echo [INFO] Installing %PACKAGE_NAME%...
    pip install %PACKAGE_NAME%
    if errorlevel 1 (
        echo [ERROR] Failed to install %PACKAGE_NAME%
        pause
        exit /b 1
    )
) else (
    echo [OK] %IMPORT_NAME% is already installed.
)
endlocal
goto :eof