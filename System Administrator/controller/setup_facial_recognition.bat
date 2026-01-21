@echo off
REM Quick Setup Script for Facial Recognition System (Windows)
REM This script installs dependencies and downloads models

echo ============================================================
echo Facial Recognition System - Quick Setup
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo X Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

REM Install pip packages
echo [STEP 1/2] Installing Python dependencies...
pip install -r facial_recognition_requirements.txt

if %errorlevel% neq 0 (
    echo X Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully
echo.

REM Download models
echo [STEP 2/2] Downloading face detection and recognition models...
python download_models.py

if %errorlevel% neq 0 (
    echo X Failed to download models
    pause
    exit /b 1
)
echo [OK] Models downloaded successfully
echo.

echo ============================================================
echo [OK] Facial Recognition Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Ensure your .env file has database credentials configured
echo 2. Run the facial recognition controller:
echo    python facial_recognition_controller.py
echo 3. Access the UI at:
echo    http://127.0.0.1:8000/System%%20Administrator/boundary/facial_recognition.html
echo.
echo For more information, see FACIAL_RECOGNITION_README.md
echo ============================================================
echo.
pause
