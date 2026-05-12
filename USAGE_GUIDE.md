# Usage Guide: Autonomous Insurance Claims Processing Agent

## Table of Contents
1. [Getting Started](#getting-started)
2. [Using the API](#using-the-api)
3. [Understanding the Output](#understanding-the-output)
4. [Sample Scenarios](#sample-scenarios)
5. [Troubleshooting](#troubleshooting)

## Getting Started

### Step 1: Setup
Run the setup script to install dependencies:

```bash
./setup.sh
```

### Step 2: Start the Server

```bash
./run_server.sh
```
Or manually:

```bash
source venv/bin/activate
python main.py
```

### Step 3: Verify Server is Running
Open another terminal and run:

```bash
curl http://localhost:8000/health
```
Expected response:
```json
{"status": "healthy", "message": "Service is running"}
```

## Using the API

### Method 1: Process Document from Path

**Endpoint**: `POST /process-claim`

**Request**:
```bash
curl -X POST "http://localhost:8000/process-claim" \
 -H "Content-Type: application/json" \
 -d '{
 "document_path": "sample_documents/fnol_1_fast_track.txt",
 "document_type": "txt"
 }'
```

**Python Example**:
```python
import requests

response = requests.post(
 "http://localhost:8000/process-claim",
 json={
 "document_path": "sample_documents/fnol_1_fast_track.txt",
 "document_type": "txt"
 }
)

result = response.json()
print(f"Route: {result['recommendedRoute']}")
print(f"Reasoning: {result['reasoning']}")
```

### Method 2: Upload and Process

**Endpoint**: `POST /upload-and-process`

**cURL Example**:
```bash
curl -X POST "http://localhost:8000/upload-and-process" \
 -F "file=@sample_documents/fnol_1_fast_track.txt"
```

**Python Example**:
```python
import requests

with open('sample_documents/fnol_1_fast_track.txt', 'rb') as f:
 response = requests.post(
 "http://localhost:8000/upload-and-process",
 files={'file': f}
 )

result = response.json()
print(result)
```

### Method 3: Run Test Suite
Process all sample documents at once:

```bash
source venv/bin/activate
python test_agent.py
```

## Understanding the Output

### Output Structure

```json
{
 "extractedFields": {
 "policy_information": { ... },
 "incident_information": { ... },
 "claimant": { ... },
 "third_parties": [ ... ],
 "asset_details": { ... },
 "claim_type": "...",
 "attachments": [ ... ],
 "initial_estimate": ...,
 "classification": "..."
 },
 "missingFields": [ ... ],
 "recommendedRoute": "...",
 "reasoning": "..."
}
```

### Field Descriptions

#### extractedFields
Contains all data extracted from the FNOL document:

- **policy_information**: Policy details
 - `policy_number`: Unique policy identifier
 - `policyholder_name`: Name of policyholder
 - `effective_date_start`: Policy start date
 - `effective_date_end`: Policy end date

- **incident_information**: Incident details
 - `incident_date`: When incident occurred
 - `incident_time`: Time of incident
 - `incident_location`: Where it happened
 - `incident_description`: Detailed description

- **claimant**: Primary claimant information
 - `name`: Claimant's name
 - `contact_details`: Email/phone
 - `role`: "Claimant"

- **third_parties**: Array of involved third parties

- **asset_details**: Asset information
 - `asset_type`: Type of asset (vehicle, property, etc.)
 - `asset_id`: Asset identifier (VIN, property ID, etc.)
 - `estimated_damage`: Damage amount

- **claim_type**: Category of claim (auto, injury, property, etc.)

- **attachments**: List of attached documents

- **initial_estimate**: Initial damage estimate

- **classification**: Computed claim classification

#### missingFields
Array of mandatory field paths that are missing or empty:

```json
[
 "policy_information.policy_number",
 "claim_type",
 "initial_estimate"
]
```

#### recommendedRoute
One of the following routing decisions:
- `"Fast-track"`: Low-value, complete claims
- `"Manual review"`: Missing fields or high-value
- `"Investigation Flag"`: Fraud indicators present
- `"Specialist Queue"`: Injury claims

#### reasoning
Human-readable explanation for the routing decision.

## Sample Scenarios

### Scenario 1: Fast-track Claim

**Document**: `fnol_1_fast_track.txt`

**Characteristics**:
- All fields complete
- Damage: $3,500 (< $25,000)
- No fraud indicators
- Not an injury claim

**Expected Output**:
```json
{
 "recommendedRoute": "Fast-track",
 "reasoning": "Estimated damage ($3,500.00) is below $25,000 threshold"
}
```

**Command**:
```bash
curl -X POST "http://localhost:8000/process-claim" \
 -H "Content-Type: application/json" \
 -d '{"document_path": "sample_documents/fnol_1_fast_track.txt", "document_type": "txt"}'
```

### Scenario 2: Missing Fields

**Document**: `fnol_2_missing_fields.txt`

**Characteristics**:
- Missing: effective dates, time, asset ID, claim type, estimate
- Incomplete information

**Expected Output**:
```json
{
 "missingFields": [
 "policy_information.effective_date_start",
 "policy_information.effective_date_end",
 "incident_information.incident_time",
 "asset_details.asset_id",
 "asset_details.estimated_damage",
 "claim_type",
 "initial_estimate"
 ],
 "recommendedRoute": "Manual review",
 "reasoning": "Missing mandatory fields: ..."
}
```

**Command**:
```bash
curl -X POST "http://localhost:8000/process-claim" \
 -H "Content-Type: application/json" \
 -d '{"document_path": "sample_documents/fnol_2_missing_fields.txt", "document_type": "txt"}'
```

### Scenario 3: Fraud Indicators

**Document**: `fnol_3_fraud_flag.txt`

**Characteristics**:
- Description contains: "inconsistent", "staged"
- Requires investigation

**Expected Output**:
```json
{
 "recommendedRoute": "Investigation Flag",
 "reasoning": "Incident description contains fraud-related keywords indicating potential investigation needed"
}
```

**Command**:
```bash
curl -X POST "http://localhost:8000/process-claim" \
 -H "Content-Type: application/json" \
 -d '{"document_path": "sample_documents/fnol_3_fraud_flag.txt", "document_type": "txt"}'
```

### Scenario 4: Injury Claim

**Document**: `fnol_4_injury_specialist.txt`

**Characteristics**:
- Claim type: "Injury"
- Requires specialist review

**Expected Output**:
```json
{
 "recommendedRoute": "Specialist Queue",
 "reasoning": "Claim type is 'injury', requires specialist review"
}
```

**Command**:
```bash
curl -X POST "http://localhost:8000/process-claim" \
 -H "Content-Type: application/json" \
 -d '{"document_path": "sample_documents/fnol_4_injury_specialist.txt", "document_type": "txt"}'
```

### Scenario 5: High-Value Claim

**Document**: `fnol_5_high_value.txt`

**Characteristics**:
- Damage: $185,000 (> $25,000)
- Requires manual review

**Expected Output**:
```json
{
 "recommendedRoute": "Manual review",
 "reasoning": "Estimated damage ($185,000.00) exceeds fast-track threshold, requires detailed review"
}
```

**Command**:
```bash
curl -X POST "http://localhost:8000/process-claim" \
 -H "Content-Type: application/json" \
 -d '{"document_path": "sample_documents/fnol_5_high_value.txt", "document_type": "txt"}'
```

## Advanced Usage

### Custom Document Processing
To process your own FNOL documents:

1. Create a text file with the required fields
2. Use the format shown in sample documents
3. Process via API:

```bash
curl -X POST "http://localhost:8000/process-claim" \
 -H "Content-Type: application/json" \
 -d '{
 "document_path": "path/to/your/document.txt",
 "document_type": "txt"
 }'
```

### Batch Processing
Process multiple documents programmatically:

```python
import requests
import json

documents = [
 "sample_documents/fnol_1_fast_track.txt",
 "sample_documents/fnol_2_missing_fields.txt",
 "sample_documents/fnol_3_fraud_flag.txt",
]

results = []

for doc_path in documents:
 response = requests.post(
 "http://localhost:8000/process-claim",
 json={
 "document_path": doc_path,
 "document_type": "txt"
 }
 )
 
 result = response.json()
 results.append({
 "document": doc_path,
 "route": result["recommendedRoute"],
 "reasoning": result["reasoning"]
 })

with open("batch_results.json", "w") as f:
 json.dump(results, f, indent=2)

print(f"Processed {len(results)} documents")
```

### Integrating with Your System
Example integration in an existing application:

```python
import requests

class ClaimsProcessor:
 def __init__(self, api_url="http://localhost:8000"):
 self.api_url = api_url
 
 def process_claim(self, document_path):
 """Process a claim and return routing decision"""
 response = requests.post(
 f"{self.api_url}/process-claim",
 json={
 "document_path": document_path,
 "document_type": "txt"
 }
 )
 
 if response.status_code == 200:
 return response.json()
 else:
 raise Exception(f"Processing failed: {response.text}")
 
 def should_fast_track(self, document_path):
 """Check if claim should be fast-tracked"""
 result = self.process_claim(document_path)
 return result["recommendedRoute"] == "Fast-track"

processor = ClaimsProcessor()
result = processor.process_claim("sample_documents/fnol_1_fast_track.txt")
print(f"Route: {result['recommendedRoute']}")
```

## Troubleshooting

### Problem: Server won't start

**Symptoms**:
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: Port already in use

**Symptoms**:
```
[ERROR] Address already in use
```

**Solution 1**: Kill existing process
```bash
lsof -ti:8000 | xargs kill -9
```

**Solution 2**: Use different port
```bash
uvicorn main:app --port 8001
```

### Problem: File not found

**Symptoms**:
```json
{"detail": "File not found: sample_documents/fnol_1.txt"}
```

**Solution**: Use correct path relative to project root
```bash
# Check current directory
pwd

# List sample documents
ls sample_documents/
```

### Problem: Empty or incorrect output

**Symptoms**: Missing fields in extracted data

**Solution**: Check document format matches sample documents. Ensure fields use expected labels:
- "Policy Number:" not "Policy No:"
- "Incident Date:" not "Date of Incident:"
- etc.

### Problem: Test script fails

**Symptoms**:
```
ModuleNotFoundError: No module named 'models'
```

**Solution**: Ensure you're in project root and venv is activated
```bash
cd /path/to/synapx_assignment
source venv/bin/activate
python test_agent.py
```

## Getting Help

### View API Documentation
When server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Check Logs
The application prints detailed logs showing the processing workflow:

```
[DocumentExtractor] Extracting data from TXT file: ...
[DocumentExtractor] Extracted 1234 characters from document
[ValidationService] Checking for missing mandatory fields
[RoutingEngine] Determining claim route based on business rules
[Main] Field extraction completed
```

### Debugging Tips

1. Check server logs for detailed error messages
2. Verify document format matches samples
3. Test with provided sample documents first
4. Use the test script to validate installation
5. Check API documentation at `/docs` endpoint

## Next Steps

- Read [README.md](README.md) for complete documentation
- Review [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) for architecture details
- Explore sample documents in `sample_documents/`
- Modify routing rules in `services/routing_engine.py`
- Add custom extraction patterns in `services/document_extractor.py`
