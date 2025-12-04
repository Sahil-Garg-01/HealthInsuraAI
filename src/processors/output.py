"""
Output Processor.

Handles report generation and database storage.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

REPORTS_DIR = Path("reports")


def generate_report(
    claim_data: Dict[str, Any],
    decision: str,
    reasons: Optional[str] = None
) -> Dict[str, str]:
    """
    Generate adjudication report in JSON and PDF formats.
    
    Args:
        claim_data: Claim data dictionary.
        decision: Approval decision string.
        reasons: Optional decision reasons.
    
    Returns:
        Dict with paths to generated report files.
    """
    REPORTS_DIR.mkdir(exist_ok=True)
    
    claim_id = claim_data.get("claim_id", "unknown")
    timestamp = datetime.now().isoformat()
    
    report_data = {
        "claim_id": claim_id,
        "decision": decision,
        "reasons": reasons,
        "claim_details": claim_data.get("claim_json", claim_data),
        "timestamp": timestamp
    }
    
    # Generate JSON report
    json_path = REPORTS_DIR / f"report_{claim_id}.json"
    with open(json_path, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    # Generate PDF placeholder (implement with reportlab for production)
    pdf_path = REPORTS_DIR / f"report_{claim_id}.pdf"
    with open(pdf_path, 'w') as f:
        f.write(f"ADJUDICATION REPORT\n{'='*40}\n")
        f.write(f"Claim ID: {claim_id}\n")
        f.write(f"Decision: {decision}\n")
        f.write(f"Timestamp: {timestamp}\n\n")
        f.write(f"Reasons:\n{reasons}\n\n")
        f.write(f"Details:\n{json.dumps(report_data['claim_details'], indent=2)}")
    
    logger.info(f"Generated reports for claim {claim_id}")
    return {"json_report": str(json_path), "pdf_report": str(pdf_path)}


def store_to_database(data: Dict[str, Any]) -> bool:
    """
    Store claim data to database.
    
    Args:
        data: Data to store.
    
    Returns:
        True if storage successful.
    """
    # Placeholder: implement with SQLAlchemy for production
    logger.info(f"Storing claim data to database: {data.get('claim_id', 'unknown')}")
    return True


def generate_output(
    claim_data: Dict[str, Any],
    decision: str,
    reasons: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run full output generation pipeline.
    
    Args:
        claim_data: Claim data dictionary.
        decision: Approval decision string.
        reasons: Optional decision reasons.
    
    Returns:
        Dict with output results.
    """
    reports = generate_report(claim_data, decision, reasons)
    stored = store_to_database(claim_data)
    
    return {
        "reports": reports,
        "stored_in_db": stored
    }
