#!/bin/bash

echo "======================================"
echo "Setting up Insurance Claims Agent"
echo "======================================"

# Check Python version
if command -v python3 &> /dev/null; then
 PYTHON_CMD=python3
elif command -v python &> /dev/null; then
 PYTHON_CMD=python
else
 echo "Error: Python is not installed"
 exit 1
fi

echo "Using Python: $PYTHON_CMD"
$PYTHON_CMD --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
 echo ""
 echo "Creating virtual environment..."
 $PYTHON_CMD -m venv venv
 echo " Virtual environment created"
else
 echo ""
 echo "Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "======================================"
echo "Setup completed successfully!"
echo "======================================"
echo ""
echo "To activate the environment, run:"
echo " source venv/bin/activate"
echo ""
echo "To start the server, run:"
echo " python main.py"
echo ""
echo "To run tests, run:"
echo " python test_agent.py"
echo ""
