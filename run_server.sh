#!/bin/bash

echo "======================================"
echo "Starting Insurance Claims Agent Server"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
 echo " Virtual environment not found!"
 echo "Please run setup first: ./setup.sh"
 exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
 echo " Dependencies not installed!"
 echo "Installing dependencies..."
 pip install -r requirements.txt
fi

echo ""
echo "Starting server on http://localhost:8000"
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo ""
echo "Press CTRL+C to stop the server"
echo "======================================"
echo ""

# Start the server
python main.py
