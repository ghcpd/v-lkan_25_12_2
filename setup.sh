#!/bin/bash
# Setup script for Multi-Annotator Dataset Conflict Detection System

echo "Setting up Multi-Annotator Conflict Detection Environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

echo "Python version:"
python3 --version

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the conflict detector, run:"
echo "  python3 conflict_detector.py"
echo ""
echo "To run tests, run:"
echo "  python3 -m pytest test_conflict_detector.py -v"
