"""
Decision Processor.

Makes approval/reject/query decisions based on claim data using LLM reasoning.
"""

import logging
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from config.settings import settings

logger = logging.getLogger(__name__)

DECISION_PROMPT = """
Based on the following claim data, decide whether to approve, query, or reject the claim.
Provide detailed reasons for your decision.

Claim Data: {claim_data}

Respond in the format:
Decision: [approve/query/reject]
Reasons: [detailed explanation]
"""


def _parse_decision(response_text: str) -> tuple[str, str]:
    """
    Parse LLM response into decision and reasons.
    
    Args:
        response_text: Raw LLM response.
    
    Returns:
        Tuple of (decision, reasons).
    """
    text = response_text.strip().lower()
    
    if "approve" in text:
        decision = "approve"
    elif "reject" in text:
        decision = "reject"
    else:
        decision = "query"
    
    reasons = response_text
    if "Reasons:" in response_text:
        reasons = response_text.split("Reasons:", 1)[1].strip()
    
    return decision, reasons


def make_decision(claim_json: Dict[str, Any]) -> Dict[str, str]:
    """
    Make approval decision using LLM reasoning.
    
    Args:
        claim_json: Structured claim data.
    
    Returns:
        Dict with decision and reasons.
    """
    llm = ChatOpenAI(
        model=settings.llm.model,
        temperature=settings.llm.temperature,
        api_key=settings.llm.api_key
    )
    
    prompt = DECISION_PROMPT.format(claim_data=claim_json)
    response = llm.invoke([HumanMessage(content=prompt)])
    
    decision, reasons = _parse_decision(response.content)
    
    logger.info(f"Decision made: {decision}")
    return {"decision": decision, "reasons": reasons}
