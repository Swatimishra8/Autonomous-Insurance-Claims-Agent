# Autonomous Insurance Claims Processing Agent
An AI-powered FastAPI application that processes FNOL (First Notice of Loss) documents, extracts key information, validates data, and automatically routes claims to the appropriate workflow based on business rules.

## Features

- **Document Parsing**: Extracts structured data from PDF and TXT FNOL documents
- **Field Extraction**: Automatically identifies and extracts:
 - Policy Information (policy number, policyholder name, effective dates)
 - Incident Information (date, time, location, description)
 - Involved Parties (claimant, third parties, contact details)
 - Asset Details (asset type, ID, estimated damage)
 - Claim metadata (type, attachments, initial estimate)
- **Validation**: Identifies missing or inconsistent mandatory fields
- **Intelligent Routing**: Automatically routes claims based on business rules:
 - **Fast-track**: Damage < $25,000
 - **Manual Review**: Missing mandatory fields or high-value claims
 - **Investigation Flag**: Fraud indicators detected
 - **Specialist Queue**: Injury claims
- **RESTful API**: Easy integration with existing systems

## Project Structure

```
synapx_assignment/
 main.py # FastAPI application entry point
 requirements.txt # Python dependencies
 models/
 __init__.py
 schemas.py # Pydantic data models
 services/
 __init__.py
 document_extractor.py # PDF/TXT parsing service
 validation_service.py # Field validation service
 routing_engine.py # Claim routing logic
 sample_documents/ # Sample FNOL documents
 fnol_1_fast_track.txt
 fnol_2_missing_fields.txt
 fnol_3_fraud_flag.txt
 fnol_4_injury_specialist.txt
 fnol_5_high_value.txt
 test_agent.py # Test script with examples

```

## Installation

### Prerequisites

- Python 3.8 to 3.13 (Python 3.14+ not yet supported by Pydantic)
- pip (Python package manager)

**Note**: If you're using Python 3.14+, please use Python 3.11 or 3.12 for best compatibility.

### Setup Steps

1. **Clone or navigate to the repository**:
 ```bash
 cd synapx_assignment
 ```

2. **Create a virtual environment** (recommended):
 ```bash
 python -m venv venv
 ```

3. **Activate the virtual environment**:
 - On macOS/Linux:
 ```bash
 source venv/bin/activate
 ```
 - On Windows:
 ```bash
 venv\Scripts\activate
 ```

4. **Install dependencies**:
 ```bash
 pip install -r requirements.txt
 ```

## Running the Application

### Start the FastAPI Server

```bash
python main.py
```
The server will start at `http://0.0.0.0:8000`
You should see output like:
```
[Main] Application initialized successfully
[Main] Starting server on http://0.0.0.0:8000
```

### Alternative: Using Uvicorn Directly

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### 1. Health Check
```bash
GET /health
```

### 2. Root Information
```bash
GET /
```

### 3. Process Claim from File Path
```bash
POST /process-claim
Content-Type: application/json

{
 "document_path": "sample_documents/fnol_1_fast_track.txt",
 "document_type": "txt"
}
```

### 4. Upload and Process Claim
```bash
POST /upload-and-process
Content-Type: multipart/form-data

file: <FNOL document file>
```

## API Response Format

```json
{
 "extractedFields": {
 "policy_information": {
 "policy_number": "POL-2024-001234",
 "policyholder_name": "John Anderson",
 "effective_date_start": "01/01/2024",
 "effective_date_end": "12/31/2024"
 },
 "incident_information": {
 "incident_date": "04/15/2024",
 "incident_time": "2:30 PM",
 "incident_location": "123 Main Street, Springfield, IL 62701",
 "incident_description": "Minor rear-end collision..."
 },
 "claimant": {
 "name": "John Anderson",
 "contact_details": "john.anderson@email.com, (555) 123-4567",
 "role": "Claimant"
 },
 "third_parties": [...],
 "asset_details": {
 "asset_type": "Vehicle",
 "asset_id": "VIN-ABC123456789",
 "estimated_damage": 3500.0
 },
 "claim_type": "Auto",
 "attachments": ["photos_rear_bumper.jpg", "photos_taillight.jpg"],
 "initial_estimate": 3500.0,
 "classification": "auto"
 },
 "missingFields": [],
 "recommendedRoute": "Fast-track",
 "reasoning": "Estimated damage ($3,500.00) is below $25,000 threshold"
}
```

## Testing the Application

### Run the Test Script
A comprehensive test script is provided to test all sample documents:

```bash
python test_agent.py
```
This will:
1. Process all 5 sample FNOL documents
2. Display extracted fields, missing data, and routing decisions
3. Save results to `test_results.json`

### Manual Testing with cURL

**Test 1: Fast-track claim**
```bash
curl -X POST "http://localhost:8000/process-claim" \
 -H "Content-Type: application/json" \
 -d '{
 "document_path": "sample_documents/fnol_1_fast_track.txt",
 "document_type": "txt"
 }'
```

**Test 2: Missing fields**
```bash
curl -X POST "http://localhost:8000/process-claim" \
 -H "Content-Type: application/json" \
 -d '{
 "document_path": "sample_documents/fnol_2_missing_fields.txt",
 "document_type": "txt"
 }'
```

**Test 3: Fraud flag**
```bash
curl -X POST "http://localhost:8000/process-claim" \
 -H "Content-Type: application/json" \
 -d '{
 "document_path": "sample_documents/fnol_3_fraud_flag.txt",
 "document_type": "txt"
 }'
```

**Test 4: Injury specialist**
```bash
curl -X POST "http://localhost:8000/process-claim" \
 -H "Content-Type: application/json" \
 -d '{
 "document_path": "sample_documents/fnol_4_injury_specialist.txt",
 "document_type": "txt"
 }'
```

**Test 5: High value (manual review)**
```bash
curl -X POST "http://localhost:8000/process-claim" \
 -H "Content-Type: application/json" \
 -d '{
 "document_path": "sample_documents/fnol_5_high_value.txt",
 "document_type": "txt"
 }'
```

### Testing with Python Requests

```python
import requests
import json

response = requests.post(
 "http://localhost:8000/process-claim",
 json={
 "document_path": "sample_documents/fnol_1_fast_track.txt",
 "document_type": "txt"
 }
)

result = response.json()
print(json.dumps(result, indent=2))
```

## Routing Rules
The system applies the following routing logic in order:

1. **Manual Review** - If any mandatory fields are missing
2. **Investigation Flag** - If description contains fraud keywords: "fraud", "inconsistent", "staged", "suspicious", "fake"
3. **Specialist Queue** - If claim type is "injury"
4. **Fast-track** - If estimated damage < $25,000
5. **Manual Review** - Default for high-value claims or unclear cases

### Mandatory Fields

- `policy_information.policy_number`
- `policy_information.policyholder_name`
- `incident_information.incident_date`
- `incident_information.incident_location`
- `incident_information.incident_description`
- `asset_details.asset_type`
- `asset_details.estimated_damage`
- `claim_type`
- `initial_estimate`

## Sample Documents
The project includes 6 sample FNOL documents covering different scenarios:

1. **fnol_1_fast_track.txt**: Low-value auto claim ($3,500) → Fast-track
2. **fnol_2_missing_fields.txt**: Missing required fields → Manual review
3. **fnol_3_fraud_flag.txt**: Contains fraud indicators → Investigation flag
4. **fnol_4_injury_specialist.txt**: Personal injury claim → Specialist queue
5. **fnol_5_high_value.txt**: High-value property claim ($185,000) → Manual review
6. **fnol_acord_realistic.txt**: Realistic ACORD form (standard industry format) → Injury specialist

**Note**: The system is specifically designed to handle standard ACORD Automobile Loss Notice forms (ACORD 2) commonly used in the insurance industry.

## Architecture & Approach

### Design Principles

1. **Modular Architecture**: Separation of concerns with distinct services for extraction, validation, and routing
2. **Type Safety**: Pydantic models for robust data validation
3. **Async Support**: FastAPI async endpoints for scalability
4. **Extensibility**: Easy to add new routing rules or extraction patterns

### Key Components

#### 1. Document Extractor (`services/document_extractor.py`)
- Parses PDF and TXT files
- Uses regex patterns to extract structured fields
- Handles various date/time formats
- Robust error handling

#### 2. Validation Service (`services/validation_service.py`)
- Checks for missing mandatory fields
- Validates data consistency (e.g., matching estimates)
- Returns detailed validation reports

#### 3. Routing Engine (`services/routing_engine.py`)
- Implements business rules for claim routing
- Detects fraud indicators
- Classifies claims by type
- Provides reasoning for routing decisions

#### 4. Data Models (`models/schemas.py`)
- Pydantic models for type safety
- Enums for claim types, asset types, and routes
- Structured output format

## Workflow

```
1. Document Upload/Path → 2. Text Extraction → 3. Field Parsing
 ↓
 4. Validation
 ↓
 5. Routing Decision
 ↓
 6. JSON Response
```

## Logging
The application includes comprehensive logging throughout the workflow:

```
[DocumentExtractor] Extracting data from TXT file: ...
[DocumentExtractor] Extracted 1234 characters from document
[ValidationService] Checking for missing mandatory fields
[RoutingEngine] Determining claim route based on business rules
[Main] Field extraction completed
```

## Extensions & Future Enhancements
Potential improvements:

- **ML Integration**: Use NLP models for better text extraction
- **Database Integration**: Store processed claims in a database
- **Authentication**: Add API key/JWT authentication
- **Webhook Support**: Notify external systems of routing decisions
- **OCR Support**: Process scanned/image-based PDFs
- **Batch Processing**: Handle multiple claims simultaneously
- **Dashboard**: Web UI for monitoring claims
- **Advanced Analytics**: Pattern detection and reporting

## Troubleshooting

### Common Issues

1. **Module not found errors**:
 ```bash
 pip install -r requirements.txt
 ```

2. **File not found**:
 - Ensure document paths are relative to the project root
 - Check that sample_documents directory exists

3. **Port already in use**:
 ```bash
 # Use a different port
 uvicorn main:app --port 8001
 ```

4. **PDF parsing issues**:
 - Ensure PyPDF2 is installed
 - Some encrypted PDFs may not be readable

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for FastAPI
- **Pydantic**: Data validation using Python type hints
- **PyPDF2**: PDF text extraction
- **python-multipart**: File upload support
- **python-dateutil**: Date parsing utilities
- **aiofiles**: Async file operations

## License
This project is created as an assessment submission.

## Author
Created for Synapx Assignment - Autonomous Insurance Claims Processing Agent

## Contact
For questions or issues, please refer to the project documentation or create an issue in the repository.
