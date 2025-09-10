"""
utils/state.py - State Definitions for HITL Workflows
====================================================

This module defines the state structures used in human-in-the-loop workflows.
We're extending beyond simple message lists to track approval states,
pending actions, and workflow status.
"""

from typing import Annotated, TypedDict, List, Dict, Any, Optional
from langgraph.graph.message import add_messages

class ApprovalState(TypedDict):
    """
    Enhanced state for agents that require human approval.
    
    This state tracks not just conversation history, but also:
    - Actions pending approval
    - Approval history
    - Current workflow status
    """
    # Standard conversation messages
    messages: Annotated[list, add_messages]
    
    # HITL-specific fields
    pending_action: Optional[Dict[str, Any]]  # Action waiting for approval
    approval_history: List[Dict[str, Any]]    # History of approvals/rejections
    workflow_status: str                      # "active", "waiting_approval", "completed", "failed"
    current_step: str                         # Current step in the workflow
    
    # User context (helps with approval decisions)
    user_id: Optional[str]
    risk_level: str                          # "low", "medium", "high"

def create_initial_state(user_id: str = "default_user") -> ApprovalState:
    """
    Create a clean initial state for approval workflows.
    
    Args:
        user_id: Identifier for the user (helps with approval routing)
        
    Returns:
        Initial state with empty pending actions
    """
    return ApprovalState(
        messages=[],
        pending_action=None,
        approval_history=[],
        workflow_status="active",
        current_step="initial",
        user_id=user_id,
        risk_level="low"
    )

def add_pending_action(state: ApprovalState, action: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add an action that requires approval to the state.
    
    Args:
        state: Current state
        action: Action details including type, parameters, risk_level
        
    Returns:
        State update with pending action
    """
    return {
        "pending_action": action,
        "workflow_status": "waiting_approval",
        "current_step": f"approval_required_{action.get('type', 'unknown')}"
    }

def record_approval_decision(state: ApprovalState, approved: bool, notes: str = "") -> Dict[str, Any]:
    """
    Record the human's approval decision in state.
    
    Args:
        state: Current state
        approved: Whether the action was approved
        notes: Additional notes from the approver
        
    Returns:
        State update with recorded decision
    """
    if not state.get("pending_action"):
        raise ValueError("No pending action to approve")
    
    # Create approval record
    approval_record = {
        "action": state["pending_action"],
        "approved": approved,
        "timestamp": "now",  # In real system, use datetime
        "notes": notes,
        "approver": state.get("user_id", "unknown")
    }
    
    # Update approval history
    updated_history = state.get("approval_history", []) + [approval_record]
    
    return {
        "approval_history": updated_history,
        "pending_action": None,  # Clear pending action
        "workflow_status": "active" if approved else "blocked",
        "current_step": "approved" if approved else "rejected"
    }

# Risk assessment helpers
def assess_risk_level(action_type: str, parameters: Dict[str, Any]) -> str:
    """
    Simple risk assessment for actions.
    In production, this would be more sophisticated.
    """
    high_risk_actions = ["send_email", "transfer_money", "delete_data", "publish_content"]
    medium_risk_actions = ["schedule_meeting", "create_document", "update_profile"]
    
    if action_type in high_risk_actions:
        # Check parameters for additional risk factors
        if "amount" in parameters and parameters["amount"] > 1000:
            return "high"
        if "recipient" in parameters and "external" in str(parameters["recipient"]):
            return "high"
        return "medium"
    elif action_type in medium_risk_actions:
        return "medium"
    else:
        return "low"