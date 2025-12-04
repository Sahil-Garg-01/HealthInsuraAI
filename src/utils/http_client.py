"""
HTTP client utilities for external API calls.
"""

import logging
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


def call_api_with_file(
    url: str,
    file_path: str,
    extra_data: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Make API call with file upload.
    
    Args:
        url: API endpoint URL.
        file_path: Path to file to upload.
        extra_data: Additional form data.
    
    Returns:
        API response as dict.
    """
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'filename': Path(file_path).name}
            if extra_data:
                data.update(extra_data)
            response = requests.post(url, files=files, data=data, timeout=60)
            response.raise_for_status()
            return response.json()
    except requests.RequestException as e:
        logger.error(f"API call failed for {url}: {e}")
        return {"error": str(e)}
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        return {"error": f"File not found: {file_path}"}


def call_api_with_text(
    url: str,
    text: str,
    extra_data: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Make API call with text data.
    
    Args:
        url: API endpoint URL.
        text: Text content to send.
        extra_data: Additional form data.
    
    Returns:
        API response as dict.
    """
    try:
        data = {'text': text}
        if extra_data:
            data.update(extra_data)
        response = requests.post(url, data=data, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"API call failed for {url}: {e}")
        return {"error": str(e)}


def process_files_batch(
    url: str,
    file_paths: List[str],
    extra_data: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """
    Process multiple files through an API endpoint.
    
    Args:
        url: API endpoint URL.
        file_paths: List of file paths.
        extra_data: Additional form data for each request.
    
    Returns:
        List of API responses.
    """
    return [call_api_with_file(url, path, extra_data) for path in file_paths]


def process_texts_batch(
    url: str,
    texts: List[str],
    extra_data: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """
    Process multiple texts through an API endpoint.
    
    Args:
        url: API endpoint URL.
        texts: List of text strings.
        extra_data: Additional form data for each request.
    
    Returns:
        List of API responses.
    """
    return [call_api_with_text(url, text, extra_data) for text in texts]
