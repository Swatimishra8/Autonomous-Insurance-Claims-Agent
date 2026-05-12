"""
Main FastAPI application for Autonomous Insurance Claims Processing Agent
"""
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
import os
import json
from typing import Dict, Any

from models.schemas import ClaimProcessingRequest, ClaimProcessingResult
from services.document_extractor import DocumentExtractor
from services.validation_service import ValidationService
from services.routing_engine import RoutingEngine


app = FastAPI(
    title="Autonomous Insurance Claims Processing Agent",
    description="AI-powered agent for processing FNOL (First Notice of Loss) documents",
    version="1.0.0"
)

document_extractor = DocumentExtractor()
validation_service = ValidationService()
routing_engine = RoutingEngine()

print("[Main] Application initialized successfully")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Autonomous Insurance Claims Processing Agent API",
        "version": "1.0.0",
        "endpoints": {
            "process_claim": "/process-claim",
            "upload_and_process": "/upload-and-process",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    print("[Main] Health check requested")
    return {"status": "healthy", "message": "Service is running"}


@app.post("/process-claim", response_model=ClaimProcessingResult)
async def process_claim(request: ClaimProcessingRequest):
    """
    Process an FNOL document and return extracted data with routing decision
    
    Args:
        request: ClaimProcessingRequest with document_path and document_type
        
    Returns:
        ClaimProcessingResult with extracted fields, missing fields, route, and reasoning
    """
    print(f"\n[Main] ===== Starting claim processing =====")
    print(f"[Main] Document path: {request.document_path}")
    print(f"[Main] Document type: {request.document_type}")
    
    if not os.path.exists(request.document_path):
        print(f"[Main] ERROR: File not found at {request.document_path}")
        raise HTTPException(status_code=404, detail=f"File not found: {request.document_path}")
    
    try:
        print("[Main] Step 1: Extracting fields from document...")
        extracted_fields = await document_extractor.extract_from_file(
            request.document_path, 
            request.document_type
        )
        print("[Main] Field extraction completed")
        
        print("[Main] Step 2: Validating extracted fields...")
        missing_fields = validation_service.identify_missing_fields(extracted_fields)
        print(f"[Main] Validation completed - {len(missing_fields)} missing fields")
        
        consistency_check = validation_service.validate_consistency(extracted_fields)
        print(f"[Main] Consistency check: {consistency_check}")
        
        print("[Main] Step 3: Determining routing decision...")
        recommended_route, reasoning = routing_engine.determine_route(
            extracted_fields, 
            missing_fields
        )
        print(f"[Main] Routing decision: {recommended_route}")
        
        classification = routing_engine.classify_claim(extracted_fields)
        print(f"[Main] Claim classification: {classification}")
        
        extracted_fields_dict = {
            "policy_information": {
                "policy_number": extracted_fields.policy_information.policy_number,
                "policyholder_name": extracted_fields.policy_information.policyholder_name,
                "effective_date_start": extracted_fields.policy_information.effective_date_start,
                "effective_date_end": extracted_fields.policy_information.effective_date_end
            },
            "incident_information": {
                "incident_date": extracted_fields.incident_information.incident_date,
                "incident_time": extracted_fields.incident_information.incident_time,
                "incident_location": extracted_fields.incident_information.incident_location,
                "incident_description": extracted_fields.incident_information.incident_description
            },
            "claimant": {
                "name": extracted_fields.claimant.name if extracted_fields.claimant else None,
                "contact_details": extracted_fields.claimant.contact_details if extracted_fields.claimant else None,
                "role": extracted_fields.claimant.role if extracted_fields.claimant else None
            },
            "third_parties": [
                {
                    "name": party.name,
                    "contact_details": party.contact_details,
                    "role": party.role
                } for party in extracted_fields.third_parties
            ],
            "asset_details": {
                "asset_type": extracted_fields.asset_details.asset_type,
                "asset_id": extracted_fields.asset_details.asset_id,
                "estimated_damage": extracted_fields.asset_details.estimated_damage
            },
            "claim_type": extracted_fields.claim_type,
            "attachments": extracted_fields.attachments,
            "initial_estimate": extracted_fields.initial_estimate,
            "classification": classification
        }
        
        result = ClaimProcessingResult(
            extracted_fields=extracted_fields_dict,
            missing_fields=missing_fields,
            recommended_route=recommended_route,
            reasoning=reasoning
        )
        
        print("[Main] ===== Claim processing completed successfully =====\n")
        return result
        
    except Exception as e:
        print(f"[Main] ERROR during processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing claim: {str(e)}")


@app.post("/upload-and-process")
async def upload_and_process(file: UploadFile = File(...)):
    """
    Upload an FNOL document and process it
    
    Args:
        file: Uploaded file (PDF or TXT)
        
    Returns:
        ClaimProcessingResult with extracted fields, missing fields, route, and reasoning
    """
    print(f"\n[Main] ===== File upload and processing started =====")
    print(f"[Main] Uploaded file: {file.filename}")
    
    if not file.filename.lower().endswith(('.pdf', '.txt')):
        print(f"[Main] ERROR: Invalid file type")
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
    
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    print(f"[Main] Saving file to: {file_path}")
    
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        print(f"[Main] File saved successfully")
        
        file_type = "pdf" if file.filename.lower().endswith('.pdf') else "txt"
        
        request = ClaimProcessingRequest(
            document_path=file_path,
            document_type=file_type
        )
        
        result = await process_claim(request)
        
        return result
        
    except Exception as e:
        print(f"[Main] ERROR during upload and processing: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing uploaded file: {str(e)}")
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"[Main] Temporary file cleaned up: {file_path}")
            except Exception as e:
                print(f"[Main] Warning: Could not remove temporary file: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("[Main] Starting server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
