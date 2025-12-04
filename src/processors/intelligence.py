"""
Intelligence Processor.

Handles NER, classification, JSON structuring, and summarization.
"""

from typing import List, Dict, Any, Optional
from config.settings import settings
from src.utils.http_client import process_files_batch, process_texts_batch


def extract_entities(
    texts: Optional[List[str]] = None,
    document_paths: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Extract named entities using HF NER API.
    
    Args:
        texts: List of text strings.
        document_paths: List of document paths (alternative input).
    
    Returns:
        List of NER results.
    """
    if texts:
        return process_texts_batch(settings.api.ner, texts)
    if document_paths:
        return process_files_batch(settings.api.ner, document_paths)
    return [{"error": "No input provided"}]


def classify_documents(
    texts: Optional[List[str]] = None,
    document_paths: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Classify documents/texts using HF classification API.
    
    Args:
        texts: List of text strings.
        document_paths: List of document paths (alternative input).
    
    Returns:
        List of classification results.
    """
    if texts:
        return process_texts_batch(settings.api.classify, texts)
    if document_paths:
        return process_files_batch(settings.api.classify, document_paths)
    return [{"error": "No input provided"}]


def summarize(
    texts: Optional[List[str]] = None,
    document_paths: Optional[List[str]] = None,
    start_page: int = 1,
    end_page: int = 1
) -> List[Dict[str, Any]]:
    """
    Summarize documents/texts using HF summarization API.
    
    Args:
        texts: List of text strings.
        document_paths: List of document paths.
        start_page: Start page for document summarization.
        end_page: End page for document summarization.
    
    Returns:
        List of summary results.
    """
    extra_data = {'start_page': str(start_page), 'end_page': str(end_page)}
    
    if texts:
        return process_texts_batch(settings.api.summarize, texts, extra_data)
    if document_paths:
        return process_files_batch(settings.api.summarize, document_paths, extra_data)
    return [{"error": "No input provided"}]


def structure_claim_json(
    entities: List[Dict[str, Any]],
    tables: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Structure extracted data into standardized claim JSON.
    
    Args:
        entities: List of entity extraction results.
        tables: List of table extraction results.
    
    Returns:
        Structured claim JSON object.
    """
    claim = {
        "patient": {},
        "provider": {},
        "policy": {},
        "diagnosis": [],
        "procedures": [],
        "amounts": {},
        "dates": {},
        "tables": tables
    }
    
    # Map entities to claim structure
    for entity_group in entities:
        if not isinstance(entity_group, dict) or "entities" not in entity_group:
            continue
            
        for entity in entity_group.get("entities", []):
            label = entity.get("label", "").upper()
            text = entity.get("text", "")
            
            if "PATIENT" in label:
                claim["patient"]["name"] = text
            elif "PROVIDER" in label or "HOSPITAL" in label:
                claim["provider"]["name"] = text
            elif "POLICY" in label:
                claim["policy"]["number"] = text
            elif "DIAGNOSIS" in label:
                claim["diagnosis"].append(text)
            elif "PROCEDURE" in label:
                claim["procedures"].append(text)
            elif "AMOUNT" in label or "COST" in label:
                claim["amounts"]["total"] = text
            elif "DATE" in label:
                claim["dates"]["claim_date"] = text
    
    return {"claim_json": claim, "raw_entities": entities, "raw_tables": tables}


def analyze_intelligence(
    extracted_texts: List[str],
    extracted_tables: List[Dict[str, Any]],
    documents: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Run full intelligence analysis pipeline.
    
    Args:
        extracted_texts: List of extracted text strings.
        extracted_tables: List of extracted tables.
        documents: Optional document paths.
    
    Returns:
        Dict with all intelligence results.
    """
    entities = extract_entities(texts=extracted_texts)
    classifications = classify_documents(texts=extracted_texts)
    claim_json = structure_claim_json(entities, extracted_tables)
    summaries = summarize(texts=extracted_texts)
    
    return {
        "entities": entities,
        "classifications": classifications,
        "claim_json": claim_json,
        "summaries": summaries
    }
