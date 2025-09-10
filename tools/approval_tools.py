"""
tools/approval_tools.py - Human-in-the-Loop Tools
================================================

This module contains tools that require human approval before execution.
Each tool uses interrupt() to pause execution and wait for human input.
"""

from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId
from langgraph.types import Command, interrupt
from typing import Annotated, Dict, Any
from utils.state import assess_risk_level, add_pending_action, record_approval_decision

@tool
def send_email_with_approval(
    recipient: str, 
    subject: str, 
    body: str,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """
    Send an email after getting human approval.
    
    This tool demonstrates the approval workflow:
    1. Prepare the action
    2. Assess risk level
    3. Request human approval via interrupt()
    4. Execute if approved, abort if rejected
    
    Args:
        recipient: Email recipient
        subject: Email subject line
        body: Email body content
        tool_call_id: Automatically injected tool call ID
    """
    # Prepare action details
    action_details = {
        "type": "send_email",
        "recipient": recipient,
        "subject": subject,
        "body": body,
        "risk_level": assess_risk_level("send_email", {"recipient": recipient})
    }
    
    # Request human approval
    approval_request = {
        "action_type": "Email Send",
        "details": f"To: {recipient}\nSubject: {subject}\nBody: {body[:100]}...",
        "risk_level": action_details["risk_level"],
        "question": "Do you approve sending this email?"
    }
    
    # This pauses execution and waits for human input
    human_response = interrupt(approval_request)
    
    # Process the human decision
    approved = human_response.get("approved", False)
    notes = human_response.get("notes", "")
    
    if approved:
        # In a real system, this would actually send the email
        result = f"✅ Email sent to {recipient} with subject '{subject}'"
        
        # Update state to record the approval and action
        state_update = {
            "approval_history": [{
                "action": action_details,
                "approved": True,
                "notes": notes,
                "result": result
            }],
            "workflow_status": "completed"
        }
        
        return Command(
            update={
                "messages": [ToolMessage(content=result, tool_call_id=tool_call_id)],
                **state_update
            }
        )
    else:
        # Action was rejected
        result = f"❌ Email to {recipient} was not sent. Reason: {notes}"
        
        state_update = {
            "approval_history": [{
                "action": action_details,
                "approved": False,
                "notes": notes,
                "result": result
            }],
            "workflow_status": "blocked"
        }
        
        return Command(
            update={
                "messages": [ToolMessage(content=result, tool_call_id=tool_call_id)],
                **state_update
            }
        )

@tool
def transfer_money_with_approval(
    amount: float,
    recipient: str,
    purpose: str,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """
    Transfer money after getting human approval.
    
    High-risk financial action that always requires approval.
    
    Args:
        amount: Amount to transfer
        recipient: Who receives the money
        purpose: Reason for transfer
        tool_call_id: Tool call identifier
    """
    # Assess risk level based on amount
    risk_level = "high" if amount > 1000 else "medium"
    
    action_details = {
        "type": "transfer_money",
        "amount": amount,
        "recipient": recipient,
        "purpose": purpose,
        "risk_level": risk_level
    }
    
    approval_request = {
        "action_type": "Money Transfer",
        "details": f"Amount: ${amount:,.2f}\nTo: {recipient}\nPurpose: {purpose}",
        "risk_level": risk_level,
        "question": f"Approve transfer of ${amount:,.2f} to {recipient}?",
        "warning": "This action involves real money!" if amount > 500 else None
    }
    
    human_response = interrupt(approval_request)
    
    approved = human_response.get("approved", False)
    notes = human_response.get("notes", "")
    
    if approved:
        # In real system: execute actual transfer
        result = f"✅ Transferred ${amount:,.2f} to {recipient} for {purpose}"
    else:
        result = f"❌ Transfer of ${amount:,.2f} to {recipient} was rejected. Reason: {notes}"
    
    # Record the decision in state
    state_update = {
        "approval_history": [{
            "action": action_details,
            "approved": approved,
            "notes": notes,
            "result": result
        }]
    }
    
    return Command(
        update={
            "messages": [ToolMessage(content=result, tool_call_id=tool_call_id)],
            **state_update
        }
    )

@tool  
def publish_content_with_approval(
    platform: str,
    content: str,
    scheduled_time: str,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """
    Publish content to social media after approval.
    
    Content publication requires review to avoid PR disasters.
    
    Args:
        platform: Where to publish (Twitter, LinkedIn, etc.)
        content: Content to publish  
        scheduled_time: When to publish
        tool_call_id: Tool call identifier
    """
    # Content risk assessment
    risk_indicators = ["urgent", "breaking", "controversial", "sale", "discount"]
    risk_level = "high" if any(word in content.lower() for word in risk_indicators) else "medium"
    
    action_details = {
        "type": "publish_content",
        "platform": platform,
        "content": content,
        "scheduled_time": scheduled_time,
        "risk_level": risk_level
    }
    
    approval_request = {
        "action_type": "Content Publication",
        "details": f"Platform: {platform}\nScheduled: {scheduled_time}\n\nContent:\n{content}",
        "risk_level": risk_level,
        "question": f"Approve publishing this content to {platform}?",
        "guidelines": "Review for: tone, accuracy, brand alignment, legal issues"
    }
    
    human_response = interrupt(approval_request)
    
    approved = human_response.get("approved", False)
    notes = human_response.get("notes", "")
    modifications = human_response.get("modifications", "")
    
    if approved:
        final_content = modifications if modifications else content
        result = f"✅ Published to {platform}: {final_content[:50]}..."
        if modifications:
            result += f"\n📝 Modified based on feedback: {notes}"
    else:
        result = f"❌ Content publication to {platform} was rejected. Reason: {notes}"
    
    state_update = {
        "approval_history": [{
            "action": action_details,
            "approved": approved,
            "notes": notes,
            "modifications": modifications,
            "result": result
        }]
    }
    
    return Command(
        update={
            "messages": [ToolMessage(content=result, tool_call_id=tool_call_id)],
            **state_update
        }
    )

@tool
def general_approval_request(
    action_description: str,
    risk_assessment: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
    additional_details: str = ""
) -> str:
    """
    Generic approval tool for any action that needs human oversight.
    
    Use this for custom approval workflows not covered by specific tools.
    
    Args:
        action_description: What the agent wants to do
        risk_assessment: Agent's assessment of risk level
        tool_call_id: Tool call identifier
        additional_details: Any extra context for the human
    """
    approval_request = {
        "action_type": "General Action",
        "details": f"{action_description}\n\nAdditional context: {additional_details}",
        "risk_level": risk_assessment,
        "question": f"Do you approve this action: {action_description}?"
    }
    
    human_response = interrupt(approval_request)
    
    approved = human_response.get("approved", False)
    notes = human_response.get("notes", "")
    
    if approved:
        result = f"✅ Action approved: {action_description}"
        if notes:
            result += f"\n📝 Notes: {notes}"
    else:
        result = f"❌ Action rejected: {action_description}\nReason: {notes}"
    
    return Command(
        update={
            "messages": [ToolMessage(content=result, tool_call_id=tool_call_id)]
        }
    )

def get_approval_tools():
    """
    Return list of all approval tools for use in agents.
    """
    return [
        send_email_with_approval,
        transfer_money_with_approval, 
        publish_content_with_approval,
        general_approval_request
    ]