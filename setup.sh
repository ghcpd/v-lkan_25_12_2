#!/bin/bash

# Setup script for Multi-Annotator Conflict Detection System
# This script sets up the development environment on Linux/Mac

set -e  # Exit on error

echo "=========================================="
echo "Multi-Annotator Conflict Detection Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $PYTHON_VERSION"

# Check if version is 3.9+
REQUIRED_VERSION="3.9"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo "Warning: Python 3.9 or higher is recommended. You have $PYTHON_VERSION"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "Virtual environment created successfully."
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "Dependencies installed successfully."
else
    echo "Error: requirements.txt not found."
    exit 1
fi

# Create output directories
echo ""
echo "Creating output directories..."
mkdir -p output
mkdir -p reports
echo "Directories created."

# Run tests to verify installation
echo ""
echo "Running tests to verify installation..."
python -m pytest test_conflict_detector.py -v

# Check if tests passed
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Setup completed successfully!"
    echo "=========================================="
    echo ""
    echo "To get started:"
    echo "  1. Activate the virtual environment: source venv/bin/activate"
    echo "  2. Run the application: python main.py --help"
    echo "  3. Process your dataset: python main.py --input tickets_label.jsonl --output output/results.jsonl"
    echo ""
else
    echo ""
    echo "Warning: Some tests failed. Please check the output above."
    exit 1
fi
