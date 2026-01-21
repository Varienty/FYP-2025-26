#!/bin/bash
# Quick Setup Script for Facial Recognition System
# This script installs dependencies and downloads models

echo "============================================================"
echo "Facial Recognition System - Quick Setup"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Install pip packages
echo "📦 Installing Python dependencies..."
pip3 install -r facial_recognition_requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Download models
echo "📥 Downloading face detection and recognition models..."
python3 download_models.py

if [ $? -eq 0 ]; then
    echo "✓ Models downloaded successfully"
else
    echo "❌ Failed to download models"
    exit 1
fi
echo ""

echo "============================================================"
echo "✓ Facial Recognition Setup Complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Ensure your .env file has database credentials configured"
echo "2. Run the facial recognition controller:"
echo "   python3 facial_recognition_controller.py"
echo "3. Access the UI at:"
echo "   http://127.0.0.1:8000/System%20Administrator/boundary/facial_recognition.html"
echo ""
echo "For more information, see FACIAL_RECOGNITION_README.md"
echo "============================================================"
