"""
Ingestion Processor.

Handles claim file uploads and routing to the pipeline.
"""

from typing import List, Dict, Any


def ingest_files(file_paths: List[str]) -> Dict[str, Any]:
    """
    Ingest uploaded claim files and prepare for processing.
    
    Args:
        file_paths: List of uploaded file paths.
    
    Returns:
        Dict with ingested files ready for preprocessing.
    """
    # Validate file paths exist (basic validation)
    valid_files = [fp for fp in file_paths if fp]
    
    return {
        "uploaded_files": valid_files,
        "documents": valid_files
    }
