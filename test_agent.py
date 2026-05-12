"""
Test script for Autonomous Insurance Claims Processing Agent
Tests all sample FNOL documents and displays results
"""
import asyncio
import json
from pathlib import Path

from models.schemas import ClaimProcessingRequest
from services.document_extractor import DocumentExtractor
from services.validation_service import ValidationService
from services.routing_engine import RoutingEngine


async def process_claim_local(document_path: str, document_type: str = "txt"):
    """
    Process a claim document locally (without HTTP API)
    
    Args:
        document_path: Path to FNOL document
        document_type: Type of document (pdf or txt)
    
    Returns:
        Processing result dictionary
    """
    print(f"\n{'='*80}")
    print(f"Processing: {document_path}")
    print(f"{'='*80}")
    
    document_extractor = DocumentExtractor()
    validation_service = ValidationService()
    routing_engine = RoutingEngine()
    
    try:
        print("\n[1] Extracting fields from document...")
        extracted_fields = await document_extractor.extract_from_file(
            document_path, 
            document_type
        )
        
        print("\n[2] Validating extracted fields...")
        missing_fields = validation_service.identify_missing_fields(extracted_fields)
        consistency_check = validation_service.validate_consistency(extracted_fields)
        
        print("\n[3] Determining routing decision...")
        recommended_route, reasoning = routing_engine.determine_route(
            extracted_fields, 
            missing_fields
        )
        classification = routing_engine.classify_claim(extracted_fields)
        
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
        
        result = {
            "document": document_path,
            "extractedFields": extracted_fields_dict,
            "missingFields": missing_fields,
            "recommendedRoute": recommended_route,
            "reasoning": reasoning,
            "consistency": consistency_check
        }
        
        print("\n" + "="*80)
        print("PROCESSING RESULT")
        print("="*80)
        print(f"\nDocument: {document_path}")
        print(f"\nPolicy Information:")
        print(f"   - Policy Number: {extracted_fields.policy_information.policy_number}")
        print(f"   - Policyholder: {extracted_fields.policy_information.policyholder_name}")
        
        print(f"\nIncident Information:")
        print(f"   - Date: {extracted_fields.incident_information.incident_date}")
        print(f"   - Location: {extracted_fields.incident_information.incident_location}")
        desc = extracted_fields.incident_information.incident_description or ""
        print(f"   - Description: {desc[:100]}...")
        
        print(f"\nFinancial Details:")
        print(f"   - Estimated Damage: ${extracted_fields.asset_details.estimated_damage}")
        print(f"   - Initial Estimate: ${extracted_fields.initial_estimate}")
        
        print(f"\nClaim Details:")
        print(f"   - Claim Type: {extracted_fields.claim_type}")
        print(f"   - Classification: {classification}")
        print(f"   - Asset Type: {extracted_fields.asset_details.asset_type}")
        
        if missing_fields:
            print(f"\nMissing Fields ({len(missing_fields)}):")
            for field in missing_fields:
                print(f"   - {field}")
        else:
            print(f"\nAll mandatory fields present")
        
        print(f"\nRouting Decision: {recommended_route}")
        print(f"   Reasoning: {reasoning}")
        
        if not consistency_check["is_consistent"]:
            print(f"\nConsistency Issues:")
            for issue in consistency_check["inconsistencies"]:
                print(f"   - {issue}")
        
        return result
        
    except Exception as e:
        print(f"\nError processing claim: {str(e)}")
        return {
            "document": document_path,
            "error": str(e)
        }


async def test_all_samples():
    """Test all sample FNOL documents"""
    print("\n" + "="*80)
    print("AUTONOMOUS INSURANCE CLAIMS PROCESSING AGENT - TEST SUITE")
    print("="*80)
    
    sample_dir = Path("sample_documents")
    
    if not sample_dir.exists():
        print(f"\nError: Sample documents directory not found: {sample_dir}")
        return
    
    sample_files = [
        ("fnol_1_fast_track.txt", "txt", "Fast-track claim (low damage)"),
        ("fnol_2_missing_fields.txt", "txt", "Missing mandatory fields"),
        ("fnol_3_fraud_flag.txt", "txt", "Fraud indicators detected"),
        ("fnol_4_injury_specialist.txt", "txt", "Injury claim (specialist)"),
        ("fnol_5_high_value.txt", "txt", "High-value property claim"),
        ("fnol_acord_realistic.txt", "txt", "ACORD standard form")
    ]
    
    results = []
    
    for filename, doc_type, description in sample_files:
        file_path = sample_dir / filename
        
        if not file_path.exists():
            print(f"\nWarning: File not found: {file_path}")
            continue
        
        print(f"\n\n{'#'*80}")
        print(f"# TEST CASE: {description}")
        print(f"{'#'*80}")
        
        result = await process_claim_local(str(file_path), doc_type)
        results.append(result)
        
        await asyncio.sleep(0.5)
    
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for i, result in enumerate(results, 1):
        if "error" in result:
            print(f"\n{i}. {result['document']}: ERROR - {result['error']}")
        else:
            route = result['recommendedRoute']
            missing = len(result['missingFields'])
            print(f"\n{i}. {Path(result['document']).name}:")
            print(f"   Route: {route}")
            print(f"   Missing Fields: {missing}")
            print(f"   Status: Processed successfully")
    
    output_file = "test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nFull results saved to: {output_file}")
    print("\n" + "="*80)
    print("TEST SUITE COMPLETED")
    print("="*80 + "\n")


async def test_api_endpoints():
    """
    Test API endpoints using requests library
    NOTE: Server must be running for this test
    """
    try:
        import requests
    except ImportError:
        print("\nrequests library not installed. Skipping API tests.")
        print("   Install with: pip install requests")
        return
    
    print("\n" + "="*80)
    print("TESTING API ENDPOINTS")
    print("="*80)
    
    base_url = "http://localhost:8000"
    
    print(f"\n1. Testing health check endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"   Health check passed: {response.json()}")
        else:
            print(f"   Health check failed: Status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   Could not connect to server: {e}")
        print(f"   Please ensure the server is running: python main.py")
        return
    
    print(f"\n2. Testing claim processing endpoint...")
    test_payload = {
        "document_path": "sample_documents/fnol_1_fast_track.txt",
        "document_type": "txt"
    }
    
    try:
        response = requests.post(
            f"{base_url}/process-claim",
            json=test_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Claim processed successfully")
            print(f"   Route: {result['recommendedRoute']}")
            print(f"   Reasoning: {result['reasoning']}")
        else:
            print(f"   Processing failed: Status {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   Request failed: {e}")
    
    print("\n" + "="*80)


def main():
    """Main test function"""
    print("\nStarting Autonomous Insurance Claims Processing Agent Tests\n")
    
    asyncio.run(test_all_samples())
    
    print("\n" + "="*80)
    print("Additional Information")
    print("="*80)
    print("\nTo test the API endpoints:")
    print("1. Start the server in another terminal: python main.py")
    print("2. Run: python test_agent.py --api")
    print("\nOr use cURL commands as shown in README.md")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    import sys
    
    if "--api" in sys.argv:
        asyncio.run(test_api_endpoints())
    else:
        main()
