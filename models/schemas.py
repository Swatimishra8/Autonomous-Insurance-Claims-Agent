"""
Pydantic models for FNOL (First Notice of Loss) data structures
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class ClaimType(str, Enum):
    """Enumeration for claim types"""
    PROPERTY = "property"
    AUTO = "auto"
    INJURY = "injury"
    LIABILITY = "liability"
    OTHER = "other"


class AssetType(str, Enum):
    """Enumeration for asset types"""
    VEHICLE = "vehicle"
    PROPERTY = "property"
    EQUIPMENT = "equipment"
    OTHER = "other"


class RouteType(str, Enum):
    """Enumeration for routing decisions"""
    FAST_TRACK = "Fast-track"
    MANUAL_REVIEW = "Manual review"
    INVESTIGATION_FLAG = "Investigation Flag"
    SPECIALIST_QUEUE = "Specialist Queue"


class PolicyInformation(BaseModel):
    """Policy information schema"""
    policy_number: Optional[str] = None
    policyholder_name: Optional[str] = None
    effective_date_start: Optional[str] = None
    effective_date_end: Optional[str] = None


class IncidentInformation(BaseModel):
    """Incident information schema"""
    incident_date: Optional[str] = None
    incident_time: Optional[str] = None
    incident_location: Optional[str] = None
    incident_description: Optional[str] = None


class InvolvedParty(BaseModel):
    """Schema for involved parties"""
    name: Optional[str] = None
    contact_details: Optional[str] = None
    role: Optional[str] = None


class AssetDetails(BaseModel):
    """Asset details schema"""
    asset_type: Optional[str] = None
    asset_id: Optional[str] = None
    estimated_damage: Optional[float] = None


class ExtractedFields(BaseModel):
    """Complete extracted fields from FNOL document"""
    policy_information: PolicyInformation = Field(default_factory=PolicyInformation)
    incident_information: IncidentInformation = Field(default_factory=IncidentInformation)
    claimant: Optional[InvolvedParty] = None
    third_parties: List[InvolvedParty] = Field(default_factory=list)
    asset_details: AssetDetails = Field(default_factory=AssetDetails)
    claim_type: Optional[str] = None
    attachments: List[str] = Field(default_factory=list)
    initial_estimate: Optional[float] = None


class ClaimProcessingResult(BaseModel):
    """Output schema for claim processing result"""
    extracted_fields: Dict[str, Any]
    missing_fields: List[str]
    recommended_route: str
    reasoning: str


class ClaimProcessingRequest(BaseModel):
    """Request schema for claim processing"""
    document_path: str = Field(..., description="Path to the FNOL document (PDF or TXT)")
    document_type: str = Field(default="pdf", description="Document type: 'pdf' or 'txt'")
