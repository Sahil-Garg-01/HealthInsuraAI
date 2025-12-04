"""
Extraction Processor.

Handles text extraction, table extraction, and translation.
"""

from typing import List, Dict, Any
from config.settings import settings
from src.utils.http_client import process_files_batch, process_texts_batch


def extract_text(
    document_paths: List[str],
    start_page: int = None,
    end_page: int = None
) -> List[Dict[str, Any]]:
    """
    Extract text from documents using OCR via HF API.
    
    Args:
        document_paths: List of PDF paths.
        start_page: Start page number.
        end_page: End page number.
    
    Returns:
        List of text extraction results.
    """
    start = start_page or settings.processing.default_start_page
    end = end_page or settings.processing.default_end_page
    
    return process_files_batch(
        settings.api.extract_text,
        document_paths,
        {'start_page': str(start), 'end_page': str(end)}
    )


def extract_tables(
    document_paths: List[str],
    start_page: int = None,
    end_page: int = None
) -> List[Dict[str, Any]]:
    """
    Extract tables from documents using HF API.
    
    Args:
        document_paths: List of PDF paths.
        start_page: Start page number.
        end_page: End page number.
    
    Returns:
        List of table extraction results.
    """
    start = start_page or settings.processing.default_start_page
    end = end_page or settings.processing.default_end_page
    
    return process_files_batch(
        settings.api.extract_tables,
        document_paths,
        {'start_page': str(start), 'end_page': str(end)}
    )


def translate_texts(
    texts: List[str],
    target_language: str = None
) -> List[Dict[str, Any]]:
    """
    Translate texts to target language using HF API.
    
    Args:
        texts: List of text strings to translate.
        target_language: Target language code.
    
    Returns:
        List of translation results.
    """
    target = target_language or settings.processing.language
    return process_texts_batch(
        settings.api.translate,
        texts,
        {'target_language': target}
    )


def extract_data(documents: List[str]) -> Dict[str, Any]:
    """
    Run full extraction pipeline on documents.
    
    Args:
        documents: List of document paths.
    
    Returns:
        Dict with all extraction results.
    """
    text_results = extract_text(documents)
    table_results = extract_tables(documents)
    
    # Extract raw text for translation
    raw_texts = [
        r.get("text", "") 
        for r in text_results 
        if isinstance(r, dict) and "text" in r
    ]
    translation_results = translate_texts(raw_texts) if raw_texts else []
    
    return {
        "extracted_text": text_results,
        "extracted_tables": table_results,
        "translated_text": translation_results
    }
