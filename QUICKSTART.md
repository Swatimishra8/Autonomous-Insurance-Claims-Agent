# Quick Start Guide

## Important: Python Version

This project requires Python 3.8 to 3.13. If you have Python 3.14+, please use Python 3.11 or 3.12 instead.

```bash
# Check your Python version
python3 --version
```

## Setup (First Time Only)

### Option 1: Automatic Setup (Recommended)

```bash
./setup.sh
```

### Option 2: Manual Setup

```bash
# Create virtual environment (use python3.11 or python3.12 if you have Python 3.14+)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate # On macOS/Linux
# OR
venv\Scripts\activate # On Windows

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

### 1. Activate Virtual Environment

```bash
source venv/bin/activate # On macOS/Linux
# OR
venv\Scripts\activate # On Windows
```

### 2. Start the Server

```bash
python main.py
```
Server will start at: `http://localhost:8000`

### 3. Run Tests (in another terminal)

```bash
# Activate venv first
source venv/bin/activate

# Run tests
python test_agent.py
```

## Quick Test with cURL
Once the server is running, test with:

```bash
curl -X POST "http://localhost:8000/process-claim" \
 -H "Content-Type: application/json" \
 -d '{
 "document_path": "sample_documents/fnol_1_fast_track.txt",
 "document_type": "txt"
 }'
```

## Expected Output
You should see JSON output with:
- `extractedFields`: All parsed data from the document
- `missingFields`: Any missing mandatory fields
- `recommendedRoute`: Routing decision (Fast-track, Manual review, etc.)
- `reasoning`: Explanation for the routing decision

## Troubleshooting

**Issue**: `ModuleNotFoundError`
**Solution**: Activate the virtual environment and install dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Issue**: Python 3.14 compatibility error with Pydantic
**Solution**: Use Python 3.11 or 3.12 instead

```bash
# Remove old venv
rm -rf venv

# Create new venv with Python 3.12 (or 3.11)
python3.12 -m venv venv
# OR
python3.11 -m venv venv

# Activate and install
source venv/bin/activate
pip install -r requirements.txt
```

**Issue**: Port 8000 already in use
**Solution**: Use a different port

```bash
uvicorn main:app --port 8001
```

**Issue**: File not found
**Solution**: Make sure you're in the project root directory

```bash
cd /path/to/synapx_assignment
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore sample documents in `sample_documents/`
- Check the API documentation at `http://localhost:8000/docs` (when server is running)
