"""
Shared type definitions for the claim processing system.
"""

from typing import TypedDict, List, Dict, Any, Optional


class ClaimState(TypedDict, total=False):
    """
    Unified state object for claim processing pipeline.
    
    Contains all data flowing through the processing stages.
    """
    # Input
    uploaded_files: List[str]
    
    # Preprocessing results
    processed_documents: List[Dict[str, Any]]
    image_descriptions: List[Dict[str, Any]]
    stamp_detections: List[Dict[str, Any]]
    signature_verifications: List[Dict[str, Any]]
    
    # Extraction results
    extracted_text: List[Dict[str, Any]]
    extracted_tables: List[Dict[str, Any]]
    translated_text: List[Dict[str, Any]]
    
    # Intelligence results
    entities: List[Dict[str, Any]]
    classifications: List[Dict[str, Any]]
    claim_json: Dict[str, Any]
    summaries: List[Dict[str, Any]]
    
    # Decision results
    decision: str
    reasons: Optional[str]
    
    # Output results
    reports: Dict[str, str]
    stored_in_db: bool


class ProcessingResult(TypedDict):
    """Standard result format for processor operations."""
    success: bool
    data: Any
    error: Optional[str]
