"""
Preprocessing Processor.

Handles document splitting, image description, stamp detection, and signature verification.
"""

from typing import List, Dict, Any
from config.settings import settings
from src.utils.http_client import process_files_batch


def split_documents(documents: List[str]) -> List[Dict[str, Any]]:
    """
    Split multi-page documents by type.
    
    Args:
        documents: List of document paths.
    
    Returns:
        List of document metadata with type classification.
    """
    return [{"type": "unknown", "path": doc} for doc in documents]


def describe_images(
    document_paths: List[str],
    start_page: int = None,
    end_page: int = None
) -> List[Dict[str, Any]]:
    """
    Generate image descriptions from PDFs using HF API.
    
    Args:
        document_paths: List of PDF paths.
        start_page: Optional start page.
        end_page: Optional end page.
    
    Returns:
        List of image description results.
    """
    extra_data = {}
    if start_page is not None:
        extra_data['start_page'] = str(start_page)
    if end_page is not None:
        extra_data['end_page'] = str(end_page)
    
    return process_files_batch(
        settings.api.describe_image,
        document_paths,
        extra_data or None
    )


def detect_stamps(document_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Detect official stamps in documents using HF API.
    
    Args:
        document_paths: List of PDF paths.
    
    Returns:
        List of stamp detection results.
    """
    return process_files_batch(settings.api.stamp, document_paths)


def verify_signatures(document_paths: List[str]) -> List[Dict[str, Any]]:
    """
    Verify signatures in documents using HF API.
    
    Args:
        document_paths: List of PDF paths.
    
    Returns:
        List of signature verification results.
    """
    return process_files_batch(settings.api.signature, document_paths)


def preprocess_documents(documents: List[str]) -> Dict[str, Any]:
    """
    Run full preprocessing pipeline on documents.
    
    Args:
        documents: List of document paths.
    
    Returns:
        Dict with all preprocessing results.
    """
    return {
        "processed_documents": split_documents(documents),
        "image_descriptions": describe_images(documents),
        "stamp_detections": detect_stamps(documents),
        "signature_verifications": verify_signatures(documents)
    }
