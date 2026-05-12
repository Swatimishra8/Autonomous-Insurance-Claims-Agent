"""
Routing engine for classifying claims and determining workflow routing
"""
from typing import Tuple, List
import re
from models.schemas import ExtractedFields, RouteType


class RoutingEngine:
    """Service for routing claims based on business rules"""
    
    FRAUD_KEYWORDS = ["fraud", "inconsistent", "staged", "suspicious", "fake", "fabricated"]
    FAST_TRACK_THRESHOLD = 25000
    
    def __init__(self):
        print("[RoutingEngine] Initializing routing engine")
    
    def determine_route(self, extracted_fields: ExtractedFields, missing_fields: List[str]) -> Tuple[str, str]:
        """
        Determine the appropriate route for the claim
        
        Args:
            extracted_fields: ExtractedFields object
            missing_fields: List of missing mandatory fields
            
        Returns:
            Tuple of (route_name, reasoning)
        """
        print("[RoutingEngine] Determining claim route based on business rules")
        print(f"[RoutingEngine] Missing fields count: {len(missing_fields)}")
        
        if missing_fields:
            reason = f"Missing mandatory fields: {', '.join(missing_fields)}"
            print(f"[RoutingEngine] Route decision: Manual Review - {reason}")
            return RouteType.MANUAL_REVIEW.value, reason
        
        description = extracted_fields.incident_information.incident_description or ""
        if self._contains_fraud_indicators(description):
            reason = "Incident description contains fraud-related keywords indicating potential investigation needed"
            print(f"[RoutingEngine] Route decision: Investigation Flag - {reason}")
            return RouteType.INVESTIGATION_FLAG.value, reason
        
        if extracted_fields.claim_type and extracted_fields.claim_type.lower() == "injury":
            reason = "Claim type is 'injury', requires specialist review"
            print(f"[RoutingEngine] Route decision: Specialist Queue - {reason}")
            return RouteType.SPECIALIST_QUEUE.value, reason
        
        estimated_damage = extracted_fields.asset_details.estimated_damage or extracted_fields.initial_estimate
        if estimated_damage and estimated_damage < self.FAST_TRACK_THRESHOLD:
            reason = f"Estimated damage (${estimated_damage:,.2f}) is below ${self.FAST_TRACK_THRESHOLD:,} threshold"
            print(f"[RoutingEngine] Route decision: Fast-track - {reason}")
            return RouteType.FAST_TRACK.value, reason
        
        if estimated_damage:
            reason = f"Estimated damage (${estimated_damage:,.2f}) exceeds fast-track threshold, requires detailed review"
        else:
            reason = "No estimated damage amount found, requires manual review"
        
        print(f"[RoutingEngine] Route decision: Manual Review - {reason}")
        return RouteType.MANUAL_REVIEW.value, reason
    
    def _contains_fraud_indicators(self, text: str) -> bool:
        """
        Check if text contains fraud-related keywords
        
        Args:
            text: Text to check
            
        Returns:
            True if fraud indicators found, False otherwise
        """
        text_lower = text.lower()
        
        for keyword in self.FRAUD_KEYWORDS:
            if keyword in text_lower:
                print(f"[RoutingEngine] Fraud indicator found: '{keyword}'")
                return True
        
        print("[RoutingEngine] No fraud indicators detected")
        return False
    
    def classify_claim(self, extracted_fields: ExtractedFields) -> str:
        """
        Classify the claim based on extracted information
        
        Args:
            extracted_fields: ExtractedFields object
            
        Returns:
            Classification category
        """
        print("[RoutingEngine] Classifying claim")
        
        claim_type = extracted_fields.claim_type
        if claim_type:
            print(f"[RoutingEngine] Claim classified as: {claim_type}")
            return claim_type
        
        asset_type = extracted_fields.asset_details.asset_type
        if asset_type:
            if asset_type.lower() == "vehicle":
                classification = "auto"
            else:
                classification = asset_type.lower()
            print(f"[RoutingEngine] Claim classified as: {classification} (based on asset type)")
            return classification
        
        print("[RoutingEngine] Unable to classify claim, defaulting to 'other'")
        return "other"
