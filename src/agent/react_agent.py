"""
ReAct Agent with explicit Thought-Action-Observation loop.

Implements the ReAct pattern: Reason → Act → Observe → Repeat
"""

import json
import logging
from typing import TypedDict, Literal, Annotated
from operator import add

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

from config.settings import settings

logger = logging.getLogger(__name__)


# =============================================================================
# STATE DEFINITION
# =============================================================================

class AgentState(TypedDict):
    """State for the ReAct agent."""
    messages: list                          # Conversation history
    current_step: str                       # Current pipeline step
    thought: str                            # Agent's reasoning
    action: str                             # Chosen action/tool
    action_input: dict                      # Tool parameters
    observation: str                        # Tool result
    iteration: int                          # Loop counter
    is_complete: bool                       # Termination flag
    final_result: dict                      # Final output
    claim_decision: dict                    # Store claim decision details


# =============================================================================
# SYSTEM PROMPT
# =============================================================================

SYSTEM_PROMPT = """You are a ReAct agent processing health insurance claims.

Available Actions:
1. ingest - Ingest uploaded files into the system
2. preprocess - Split documents, detect stamps/signatures, describe images
3. extract - OCR text extraction, table extraction, translation
4. analyze - NER, classification, structure claim JSON, summarize
5. decide - Make approve/query/reject decision
6. output - Generate reports and store to database
7. finish - Complete processing and return final result

For each step, you must respond in this exact JSON format:
{{
    "thought": "Your reasoning about what to do next",
    "action": "action_name",
    "action_input": {{"param": "value"}}
}}

Process claims sequentially: ingest → preprocess → extract → analyze → decide → output → finish

Current files: {files}
Current step: {step}
Previous observation: {observation}
"""


# =============================================================================
# TOOL IMPLEMENTATIONS
# =============================================================================

def execute_action(action: str, action_input: dict, state: AgentState) -> str:
    """Execute the chosen action and return observation."""
    
    files = action_input.get("files", [])
    
    if action == "ingest":
        from src.processors.ingestion import ingest_files
        result = ingest_files(files)
        return f"Ingested {len(result['documents'])} files successfully."
    
    elif action == "preprocess":
        from src.processors.preprocessing import preprocess_documents
        result = preprocess_documents(files)
        return f"Preprocessed documents. Stamps: {len(result['stamp_detections'])}, Signatures: {len(result['signature_verifications'])}"
    
    elif action == "extract":
        from src.processors.extraction import extract_data
        result = extract_data(files)
        return f"Extracted text from {len(result['extracted_text'])} docs, tables from {len(result['extracted_tables'])} docs."
    
    elif action == "analyze":
        from src.processors.intelligence import analyze_intelligence
        texts = action_input.get("texts", [])
        tables = action_input.get("tables", [])
        result = analyze_intelligence(texts, tables, files)
        return f"Analysis complete. Entities: {len(result['entities'])}, Claim JSON structured."
    
    elif action == "decide":
        from src.processors.decision import make_decision
        claim_json = action_input.get("claim_json", {})
        result = make_decision(claim_json)
        state["claim_decision"] = result  # Store decision in state
        return f"Decision: {result['decision']}. Reasons: {result['reasons'][:100]}..."
    
    elif action == "output":
        from src.processors.output import generate_output
        claim_data = action_input.get("claim_data", {})
        decision = action_input.get("decision", "query")
        reasons = action_input.get("reasons", "")
        result = generate_output(claim_data, decision, reasons)
        return f"Reports generated: {list(result['reports'].keys())}. Stored in DB: {result['stored_in_db']}"
    
    elif action == "finish":
        return "COMPLETE"
    
    else:
        return f"Unknown action: {action}"


# =============================================================================
# REACT NODES
# =============================================================================

def think_node(state: AgentState) -> AgentState:
    """
    THINK: Agent reasons about current state and decides next action.
    """
    llm = ChatGoogleGenerativeAI(
        model=settings.llm.model,
        temperature=settings.llm.temperature,
        api_key=settings.llm.api_key
    )
    
    # Build prompt with current context
    files = state.get("messages", [{}])[0].get("files", []) if state.get("messages") else []
    prompt = SYSTEM_PROMPT.format(
        files=files,
        step=state.get("current_step", "start"),
        observation=state.get("observation", "None yet")
    )
    
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=f"Iteration {state['iteration']}. What is your next action?")
    ]
    
    response = llm.invoke(messages)
    
    # Parse JSON response
    try:
        content = response.content.strip()
        # Extract JSON from response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        parsed = json.loads(content)
        
        state["thought"] = parsed.get("thought", "")
        state["action"] = parsed.get("action", "finish")
        state["action_input"] = parsed.get("action_input", {})
        
        logger.info(f"THINK: {state['thought'][:200]}...")
        
    except json.JSONDecodeError:
        logger.warning(f"Failed to parse LLM response: {response.content}")
        state["thought"] = "Failed to parse response, finishing."
        state["action"] = "finish"
        state["action_input"] = {}
    
    return state


def act_node(state: AgentState) -> AgentState:
    """
    ACT: Execute the chosen action.
    """
    action = state["action"]
    action_input = state["action_input"]
    
    # Add files from initial message if not in action_input
    if "files" not in action_input and state.get("messages"):
        first_msg = state["messages"][0] if state["messages"] else {}
        action_input["files"] = first_msg.get("files", [])
    
    logger.info(f"ACT: {action} with {len(action_input.get('files', []))} files")
    
    observation = execute_action(action, action_input, state)
    state["observation"] = observation
    state["current_step"] = action
    
    return state


def observe_node(state: AgentState) -> AgentState:
    """
    OBSERVE: Process the observation and update state.
    """
    observation = state["observation"]
    
    logger.info(f"OBSERVE: {observation[:100]}...")
    
    # Check if complete
    if observation == "COMPLETE" or state["action"] == "finish":
        state["is_complete"] = True
        state["final_result"] = {
            "status": "complete",
            "steps_taken": state["iteration"],
            "last_step": state["current_step"],
            "last_observation": observation
        }
    
    state["iteration"] += 1
    
    # Safety: max 10 iterations
    if state["iteration"] > 10:
        state["is_complete"] = True
        state["final_result"] = {"status": "max_iterations_reached"}
    
    return state


def should_continue(state: AgentState) -> Literal["think", "end"]:
    """Routing function: continue loop or end."""
    if state.get("is_complete", False):
        return "end"
    return "think"


# =============================================================================
# BUILD GRAPH
# =============================================================================

def build_react_graph() -> StateGraph:
    """Build the ReAct agent graph with Think → Act → Observe loop."""
    
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("think", think_node)
    graph.add_node("act", act_node)
    graph.add_node("observe", observe_node)
    
    # Add edges: START → think → act → observe → (conditional) → think/END
    graph.add_edge(START, "think")
    graph.add_edge("think", "act")
    graph.add_edge("act", "observe")
    graph.add_conditional_edges("observe", should_continue, {"think": "think", "end": END})
    
    return graph.compile()


# =============================================================================
# PUBLIC API
# =============================================================================

def run_agent(uploaded_files: list[str]) -> dict:
    """
    Run the ReAct claim processing agent.
    
    Args:
        uploaded_files: List of file paths to process.
    
    Returns:
        Final processing result.
    """
    agent = build_react_graph()
    
    initial_state: AgentState = {
        "messages": [{"files": uploaded_files}],
        "current_step": "start",
        "thought": "",
        "action": "",
        "action_input": {},
        "observation": "",
        "iteration": 0,
        "is_complete": False,
        "final_result": {},
        "claim_decision": {}
    }
    
    logger.info(f"Starting ReAct agent for {len(uploaded_files)} files")
    
    result = agent.invoke(initial_state)
    
    return {
        "claim_decision": result.get("claim_decision", {}),
        "status": "completed" if result.get("is_complete") else "incomplete",
        "iterations": result.get("iteration", 0)
    }
