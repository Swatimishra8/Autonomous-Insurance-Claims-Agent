"""
Validation service for identifying missing or inconsistent fields
"""
from typing import List, Dict, Any
from models.schemas import ExtractedFields


class ValidationService:
    """Service for validating extracted fields and identifying missing data"""
    
    MANDATORY_FIELDS = [
        "policy_information.policy_number",
        "policy_information.policyholder_name",
        "incident_information.incident_date",
        "incident_information.incident_location",
        "incident_information.incident_description",
        "asset_details.asset_type",
        "asset_details.estimated_damage",
        "claim_type",
        "initial_estimate"
    ]
    
    def __init__(self):
        print("[ValidationService] Initializing validation service")
    
    def identify_missing_fields(self, extracted_fields: ExtractedFields) -> List[str]:
        """
        Identify missing mandatory fields in extracted data
        
        Args:
            extracted_fields: ExtractedFields object
            
        Returns:
            List of missing field names
        """
        print("[ValidationService] Checking for missing mandatory fields")
        missing_fields = []
        
        fields_dict = self._convert_to_dict(extracted_fields)
        
        for field_path in self.MANDATORY_FIELDS:
            value = self._get_nested_value(fields_dict, field_path)
            
            if value is None or value == "" or (isinstance(value, list) and len(value) == 0):
                missing_fields.append(field_path)
                print(f"[ValidationService] Missing field detected: {field_path}")
        
        print(f"[ValidationService] Total missing fields: {len(missing_fields)}")
        return missing_fields
    
    def validate_consistency(self, extracted_fields: ExtractedFields) -> Dict[str, Any]:
        """
        Validate consistency of extracted fields
        
        Args:
            extracted_fields: ExtractedFields object
            
        Returns:
            Dictionary with consistency validation results
        """
        print("[ValidationService] Validating data consistency")
        inconsistencies = []
        
        if extracted_fields.initial_estimate and extracted_fields.asset_details.estimated_damage:
            if abs(extracted_fields.initial_estimate - extracted_fields.asset_details.estimated_damage) > 1000:
                inconsistency_msg = (
                    f"Initial estimate (${extracted_fields.initial_estimate}) differs significantly "
                    f"from estimated damage (${extracted_fields.asset_details.estimated_damage})"
                )
                inconsistencies.append(inconsistency_msg)
                print(f"[ValidationService] Inconsistency detected: {inconsistency_msg}")
        
        if extracted_fields.claim_type and extracted_fields.asset_details.asset_type:
            if extracted_fields.claim_type.lower() == "auto" and extracted_fields.asset_details.asset_type.lower() == "property":
                inconsistency_msg = "Claim type is 'auto' but asset type is 'property'"
                inconsistencies.append(inconsistency_msg)
                print(f"[ValidationService] Inconsistency detected: {inconsistency_msg}")
        
        print(f"[ValidationService] Total inconsistencies found: {len(inconsistencies)}")
        
        return {
            "is_consistent": len(inconsistencies) == 0,
            "inconsistencies": inconsistencies
        }
    
    def _convert_to_dict(self, extracted_fields: ExtractedFields) -> Dict[str, Any]:
        """Convert ExtractedFields to dictionary for easier access"""
        return {
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
                "contact_details": extracted_fields.claimant.contact_details if extracted_fields.claimant else None
            },
            "third_parties": extracted_fields.third_parties,
            "asset_details": {
                "asset_type": extracted_fields.asset_details.asset_type,
                "asset_id": extracted_fields.asset_details.asset_id,
                "estimated_damage": extracted_fields.asset_details.estimated_damage
            },
            "claim_type": extracted_fields.claim_type,
            "attachments": extracted_fields.attachments,
            "initial_estimate": extracted_fields.initial_estimate
        }
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get nested value from dictionary using dot notation path"""
        keys = field_path.split('.')
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        
        return value
