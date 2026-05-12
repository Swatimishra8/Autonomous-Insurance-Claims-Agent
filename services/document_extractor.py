"""
Document extraction service for parsing FNOL documents (PDF/TXT)
"""
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import PyPDF2
from models.schemas import ExtractedFields, PolicyInformation, IncidentInformation, InvolvedParty, AssetDetails


class DocumentExtractor:
    """Service for extracting information from FNOL documents"""
    
    def __init__(self):
        print("[DocumentExtractor] Initializing document extractor service")
        self.fraud_keywords = ["fraud", "inconsistent", "staged", "suspicious", "fake"]
    
    async def extract_from_file(self, file_path: str, file_type: str = "pdf") -> ExtractedFields:
        """
        Extract fields from FNOL document
        
        Args:
            file_path: Path to the document
            file_type: Type of document ('pdf' or 'txt')
            
        Returns:
            ExtractedFields object with parsed data
        """
        print(f"[DocumentExtractor] Extracting data from {file_type.upper()} file: {file_path}")
        
        if file_type.lower() == "pdf":
            text = await self._extract_text_from_pdf(file_path)
        else:
            text = await self._extract_text_from_txt(file_path)
        
        print(f"[DocumentExtractor] Extracted {len(text)} characters from document")
        
        extracted_fields = await self._parse_text(text)
        print(f"[DocumentExtractor] Successfully parsed document fields")
        
        return extracted_fields
    
    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text content from PDF file"""
        print(f"[DocumentExtractor] Reading PDF file: {file_path}")
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += page_text
                    print(f"[DocumentExtractor] Extracted text from page {page_num + 1}")
                return text
        except Exception as e:
            print(f"[DocumentExtractor] Error reading PDF: {str(e)}")
            raise
    
    async def _extract_text_from_txt(self, file_path: str) -> str:
        """Extract text content from TXT file"""
        print(f"[DocumentExtractor] Reading TXT file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                return text
        except Exception as e:
            print(f"[DocumentExtractor] Error reading TXT: {str(e)}")
            raise
    
    async def _parse_text(self, text: str) -> ExtractedFields:
        """Parse text and extract structured fields"""
        print("[DocumentExtractor] Parsing text to extract structured fields")
        
        policy_info = self._extract_policy_information(text)
        incident_info = self._extract_incident_information(text)
        claimant = self._extract_claimant(text)
        third_parties = self._extract_third_parties(text)
        asset_details = self._extract_asset_details(text)
        claim_type = self._extract_claim_type(text)
        attachments = self._extract_attachments(text)
        initial_estimate = self._extract_initial_estimate(text)
        
        extracted_fields = ExtractedFields(
            policy_information=policy_info,
            incident_information=incident_info,
            claimant=claimant,
            third_parties=third_parties,
            asset_details=asset_details,
            claim_type=claim_type,
            attachments=attachments,
            initial_estimate=initial_estimate
        )
        
        return extracted_fields
    
    def _extract_policy_information(self, text: str) -> PolicyInformation:
        """Extract policy information from text"""
        print("[DocumentExtractor] Extracting policy information")
        
        policy_number = self._extract_field(text, r'Policy\s*(?:Number|No\.?|#):\s*([A-Z0-9\-]+)', 1)
        if not policy_number:
            policy_number = self._extract_field(text, r'POLICY\s*NUMBER:\s*([A-Z0-9\-]+)', 1)
        
        policyholder_name = self._extract_field(text, r'Policyholder\s*(?:Name)?:\s*([A-Za-z\s\.]+)', 1)
        if not policyholder_name:
            policyholder_name = self._extract_field(text, r'NAME OF INSURED.*?:\s*([A-Za-z\s\.]+)', 1)
        if not policyholder_name:
            policyholder_name = self._extract_field(text, r'INSURED.*?NAME.*?:\s*([A-Za-z\s\.]+)', 1)
        
        effective_date_start = self._extract_field(text, r'Effective\s*Date\s*(?:Start)?:\s*(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})', 1)
        effective_date_end = self._extract_field(text, r'Effective\s*Date\s*End:\s*(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})', 1)
        
        print(f"[DocumentExtractor] Policy Number: {policy_number}, Policyholder: {policyholder_name}")
        
        return PolicyInformation(
            policy_number=policy_number,
            policyholder_name=policyholder_name,
            effective_date_start=effective_date_start,
            effective_date_end=effective_date_end
        )
    
    def _extract_incident_information(self, text: str) -> IncidentInformation:
        """Extract incident information from text"""
        print("[DocumentExtractor] Extracting incident information")
        
        incident_date = self._extract_field(text, r'Incident\s*Date:\s*(\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2})', 1)
        if not incident_date:
            incident_date = self._extract_field(text, r'DATE OF LOSS.*?:\s*(\d{2}/\d{2}/\d{4})', 1)
        
        incident_time = self._extract_field(text, r'Incident\s*Time:\s*(\d{1,2}:\d{2}\s*(?:AM|PM)?)', 1)
        if not incident_time:
            incident_time = self._extract_field(text, r'TIME:\s*(\d{1,2}:\d{2}\s*(?:AM|PM))', 1)
        
        incident_location = self._extract_field(text, r'(?:Incident\s*)?Location:\s*([^\n]+)', 1)
        if not incident_location:
            incident_location = self._extract_field(text, r'STREET:\s*([^\n]+)', 1)
        if not incident_location:
            street_match = re.search(r'LOCATION OF LOSS\s+STREET:\s*([^\n]+)', text, re.IGNORECASE)
            city_match = re.search(r'CITY, STATE, ZIP:\s*([^\n]+)', text, re.IGNORECASE)
            if street_match:
                incident_location = street_match.group(1).strip()
                if city_match:
                    incident_location += ", " + city_match.group(1).strip()
        
        description_match = re.search(r'(?:Incident\s*)?Description:\s*([^\n]+(?:\n(?!\w+:)[^\n]+)*)', text, re.IGNORECASE)
        if not description_match:
            description_match = re.search(r'DESCRIPTION OF ACCIDENT[:\s]+([^\n]+(?:\n(?![A-Z\s]+:)[^\n]+)*)', text, re.IGNORECASE | re.MULTILINE)
        incident_description = description_match.group(1).strip() if description_match else None
        
        print(f"[DocumentExtractor] Incident Date: {incident_date}, Location: {incident_location}")
        
        return IncidentInformation(
            incident_date=incident_date,
            incident_time=incident_time,
            incident_location=incident_location,
            incident_description=incident_description
        )
    
    def _extract_claimant(self, text: str) -> Optional[InvolvedParty]:
        """Extract claimant information from text"""
        print("[DocumentExtractor] Extracting claimant information")
        
        claimant_name = self._extract_field(text, r'Claimant\s*(?:Name)?:\s*([A-Za-z\s\.]+)', 1)
        claimant_contact = self._extract_field(text, r'Claimant\s*Contact:\s*([^\n]+)', 1)
        
        if claimant_name or claimant_contact:
            print(f"[DocumentExtractor] Found claimant: {claimant_name}")
            return InvolvedParty(
                name=claimant_name,
                contact_details=claimant_contact,
                role="Claimant"
            )
        return None
    
    def _extract_third_parties(self, text: str) -> List[InvolvedParty]:
        """Extract third party information from text"""
        print("[DocumentExtractor] Extracting third party information")
        
        third_parties = []
        third_party_name = self._extract_field(text, r'Third\s*Party\s*(?:Name)?:\s*([A-Za-z\s\.]+)', 1)
        third_party_contact = self._extract_field(text, r'Third\s*Party\s*Contact:\s*([^\n]+)', 1)
        
        if third_party_name or third_party_contact:
            print(f"[DocumentExtractor] Found third party: {third_party_name}")
            third_parties.append(InvolvedParty(
                name=third_party_name,
                contact_details=third_party_contact,
                role="Third Party"
            ))
        
        return third_parties
    
    def _extract_asset_details(self, text: str) -> AssetDetails:
        """Extract asset details from text"""
        print("[DocumentExtractor] Extracting asset details")
        
        asset_type = self._extract_field(text, r'Asset\s*Type:\s*([A-Za-z]+)', 1)
        if not asset_type:
            if re.search(r'AUTOMOBILE|VEHICLE|VEH\s*#|V\.I\.N\.', text, re.IGNORECASE):
                asset_type = "Vehicle"
        
        asset_id = self._extract_field(text, r'Asset\s*(?:ID|Number):\s*([A-Z0-9\-]+)', 1)
        if not asset_id:
            asset_id = self._extract_field(text, r'V\.I\.N\.:\s*([A-Z0-9]+)', 1)
        if not asset_id:
            asset_id = self._extract_field(text, r'VIN:\s*([A-Z0-9]+)', 1)
        
        estimated_damage_str = self._extract_field(text, r'Estimated\s*Damage:\s*\$?([0-9,]+(?:\.\d{2})?)', 1)
        if not estimated_damage_str:
            estimated_damage_str = self._extract_field(text, r'ESTIMATE\s*AMOUNT:\s*\$?([0-9,]+(?:\.\d{2})?)', 1)
        estimated_damage = self._parse_amount(estimated_damage_str) if estimated_damage_str else None
        
        print(f"[DocumentExtractor] Asset Type: {asset_type}, Estimated Damage: ${estimated_damage}")
        
        return AssetDetails(
            asset_type=asset_type,
            asset_id=asset_id,
            estimated_damage=estimated_damage
        )
    
    def _extract_claim_type(self, text: str) -> Optional[str]:
        """Extract claim type from text"""
        print("[DocumentExtractor] Extracting claim type")
        
        claim_type = self._extract_field(text, r'Claim\s*Type:\s*([A-Za-z]+)', 1)
        
        if not claim_type:
            if re.search(r'LINE OF BUSINESS:\s*Personal\s*Auto', text, re.IGNORECASE):
                claim_type = "Auto"
            elif re.search(r'AUTOMOBILE|AUTO\s+LOSS', text, re.IGNORECASE):
                claim_type = "Auto"
        
        if not claim_type:
            injury_keywords = r'(?:injury|injured|whiplash|hospital|medical|transported|pain|hurt|wounded)'
            if re.search(injury_keywords, text, re.IGNORECASE):
                claim_type = "Injury"
        
        print(f"[DocumentExtractor] Claim Type: {claim_type}")
        return claim_type
    
    def _extract_attachments(self, text: str) -> List[str]:
        """Extract attachments list from text"""
        print("[DocumentExtractor] Extracting attachments")
        
        attachments = []
        attachments_match = re.search(r'Attachments?:\s*([^\n]+)', text, re.IGNORECASE)
        if attachments_match:
            attachments_str = attachments_match.group(1).strip()
            if attachments_str.lower() not in ['none', 'n/a', 'na']:
                attachments = [a.strip() for a in attachments_str.split(',')]
        
        print(f"[DocumentExtractor] Found {len(attachments)} attachments")
        return attachments
    
    def _extract_initial_estimate(self, text: str) -> Optional[float]:
        """Extract initial estimate from text"""
        print("[DocumentExtractor] Extracting initial estimate")
        
        initial_estimate_str = self._extract_field(text, r'Initial\s*Estimate:\s*\$?([0-9,]+(?:\.\d{2})?)', 1)
        initial_estimate = self._parse_amount(initial_estimate_str) if initial_estimate_str else None
        
        print(f"[DocumentExtractor] Initial Estimate: ${initial_estimate}")
        return initial_estimate
    
    def _extract_field(self, text: str, pattern: str, group: int = 0) -> Optional[str]:
        """Helper method to extract field using regex pattern"""
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(group).strip()
            return value if value else None
        return None
    
    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string to float"""
        try:
            cleaned = amount_str.replace(',', '').replace('$', '')
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
