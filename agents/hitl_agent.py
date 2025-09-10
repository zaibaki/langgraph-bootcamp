"""
agents/hitl_agent.py - Human-in-the-Loop Agent Implementation
============================================================

This module implements the core HITL agent that can pause execution
for human approval and resume based on human decisions.
"""

import os
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

# Import our custom modules
from utils.state import ApprovalState, create_initial_state
from tools.approval_tools import get_approval_tools

load_dotenv()

# Environment setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Initialize LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

def create_approval_agent():
    """
    Create an agent with human-in-the-loop capabilities.
    
    This agent can:
    - Perform normal chat and web search
    - Request human approval for high-risk actions
    - Resume execution based on approval decisions
    - Track approval history in state
    
    Returns:
        Compiled LangGraph agent with HITL capabilities
    """
    # Set up tools (includes both regular and approval tools)
    regular_tools = [TavilySearch(max_results=3)]
    approval_tools = get_approval_tools()
    all_tools = regular_tools + approval_tools
    
    # Create LLM with tools
    llm_with_tools = llm.bind_tools(all_tools)
    
    # Build the graph
    graph_builder = StateGraph(ApprovalState)
    
    # Add nodes
    graph_builder.add_node("chatbot", create_chatbot_node(llm_with_tools))
    graph_builder.add_node("tools", ToolNode(all_tools))
    
    # Define edges
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
        {"tools": "tools", END: END}
    )
    graph_builder.add_edge("tools", "chatbot")
    
    # Add memory for persistent conversations
    memory = MemorySaver()
    
    return graph_builder.compile(checkpointer=memory)

def create_chatbot_node(llm_with_tools):
    """
    Create the main chatbot node with approval awareness.
    
    This node can:
    - Generate normal responses
    - Decide when approval tools are needed
    - Provide context about pending approvals
    """
    def chatbot_node(state: ApprovalState) -> dict:
        """
        Enhanced chatbot node that's aware of approval workflows.
        
        The LLM can see:
        - Conversation history
        - Pending actions requiring approval
        - Previous approval decisions
        - Current workflow status
        """
        messages = state["messages"]
        
        # Add context about current workflow state if relevant
        if state.get("workflow_status") == "waiting_approval":
            context_msg = {
                "role": "system", 
                "content": "You are currently waiting for human approval on a pending action. You can discuss this with the user or help with other tasks."
            }
            messages = [context_msg] + messages
        
        # Generate response
        response = llm_with_tools.invoke(messages)
        
        # Update workflow status if needed
        updates = {"messages": [response]}
        
        # If no tools called and we were waiting, we're now active
        if (state.get("workflow_status") == "waiting_approval" and 
            not (hasattr(response, 'tool_calls') and response.tool_calls)):
            updates["workflow_status"] = "active"
        
        return updates
    
    return chatbot_node

def run_approval_chat_loop(agent):
    """
    Interactive chat loop with REAL human-in-the-loop approval handling.
    """
    print("🛡️ REAL Human-in-the-Loop Agent Started!")
    print("This agent will ask for YOUR ACTUAL approval before taking certain actions.")
    print("\nTry these commands to trigger approval workflows:")
    print("- 'Send an email to john@company.com about the project delay'")
    print("- 'Transfer $500 to vendor payment account'") 
    print("- 'Post this announcement on LinkedIn: New product launching soon!'")
    print("- 'Request approval to delete old database records'")
    print("\nType 'quit' to exit, 'status' to see approval history.")
    print("=" * 70)
    
    thread_id = "real_hitl_demo"
    
    while True:
        user_input = input("\n👤 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if user_input.lower() == 'status':
            show_approval_status(agent, thread_id)
            continue
            
        if not user_input:
            print("Please enter a command or question.")
            continue
        
        try:
            config = {"configurable": {"thread_id": thread_id}}
            input_state = {"messages": [{"role": "user", "content": user_input}]}
            
            print("🤖 Agent: Processing your request...")
            
            # Execute the agent and handle interrupts
            result = execute_with_approval_handling(agent, input_state, config)
            
            if result:
                print(f"🤖 Agent: {result}")
            
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user.")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

def execute_with_approval_handling(agent, input_state, config):
    """
    Execute the agent and handle approval interrupts properly.
    """
    try:
        # Try to run the agent normally
        events = list(agent.stream(input_state, config, stream_mode="values"))
        
        # Check if we got a complete response
        if events:
            final_event = events[-1]
            if "messages" in final_event and final_event["messages"]:
                last_message = final_event["messages"][-1]
                if hasattr(last_message, 'content') and last_message.content:
                    return last_message.content
        
        # If we reach here, check if there's a pending approval
        state = agent.get_state(config)
        if state and state.next:
            print("⏸️  Agent is requesting your approval...")
            return handle_approval_with_resume(agent, config)
        
        return "I wasn't able to process that request properly."
        
    except Exception as e:
        error_str = str(e)
        
        # Check if this is an interrupt/approval request
        if "interrupt" in error_str.lower():
            print("⏸️  Agent is requesting your approval...")
            return handle_approval_with_resume(agent, config)
        
        # Check if it's a tool calling issue - try to handle gracefully
        if "tool_call" in error_str.lower():
            print("⚠️  Tool execution issue, checking for pending approvals...")
            state = agent.get_state(config)
            if state and state.next:
                return handle_approval_with_resume(agent, config)
        
        raise e

def handle_approval_with_resume(agent, config):
    """
    Handle approval request and resume execution.
    """
    try:
        # Get the current state
        state = agent.get_state(config)
        
        if not state or not state.next:
            return "No pending approval found."
        
        # Display approval request
        print("\n" + "="*60)
        print("🔔 APPROVAL REQUEST RECEIVED")
        print("="*60)
        
        # For this demo, we'll create a realistic approval scenario
        # In a real system, the interrupt data would contain specific action details
        print("The agent wants to perform a potentially risky action.")
        print("\nAction Details:")
        print("- Type: High-risk operation requiring human oversight")
        print("- Risk Level: Medium to High") 
        print("- Context: Agent is requesting permission to proceed")
        
        # Get human decision
        response_data = get_human_approval_decision()
        
        # Resume with the decision
        from langgraph.types import Command
        resume_command = Command(resume=response_data)
        
        print(f"\n{'='*40}")
        if response_data["approved"]:
            print("✅ DECISION: APPROVED")
        else:
            print("❌ DECISION: REJECTED")
        print(f"Notes: {response_data['notes']}")
        print(f"{'='*40}")
        
        print("\nResuming agent execution...")
        
        # Continue execution with approval decision
        events = list(agent.stream(resume_command, config, stream_mode="values"))
        
        if events:
            final_event = events[-1]
            if "messages" in final_event and final_event["messages"]:
                last_message = final_event["messages"][-1]
                if hasattr(last_message, 'content'):
                    return last_message.content
        
        return "Action processed based on your approval decision."
        
    except Exception as e:
        print(f"Error in approval handling: {e}")
        return "There was an error processing the approval request."

def get_human_approval_decision():
    """
    Get approval decision from human with proper input validation.
    """
    print("\nApproval Options:")
    print("1. ✅ APPROVE - Allow the action to proceed")
    print("2. ❌ REJECT - Block the action completely")
    print("3. 📝 APPROVE WITH MODIFICATIONS - Allow with changes")
    
    while True:
        try:
            choice = input("\nYour decision (1-3): ").strip()
            
            if choice == "1":
                notes = input("Approval notes (optional): ").strip()
                return {
                    "approved": True,
                    "notes": notes if notes else "Approved by human reviewer"
                }
                
            elif choice == "2":
                reason = input("Rejection reason: ").strip()
                return {
                    "approved": False,
                    "notes": reason if reason else "Rejected by human reviewer"
                }
                
            elif choice == "3":
                modifications = input("Required modifications: ").strip()
                notes = input("Additional approval notes: ").strip()
                return {
                    "approved": True,
                    "notes": notes if notes else "Approved with modifications",
                    "modifications": modifications
                }
                
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
                continue
                
        except KeyboardInterrupt:
            print("\nApproval cancelled by user.")
            return {
                "approved": False,
                "notes": "Approval process cancelled by user"
            }
        except Exception as e:
            print(f"Error getting input: {e}")
            return {
                "approved": False,
                "notes": f"Error in approval process: {str(e)}"
            }

def handle_approval_request(agent, thread_id: str):
    """
    Handle the approval request when execution is interrupted.
    
    This function:
    - Gets the interrupt data
    - Shows approval details to human
    - Collects human decision
    - Resumes execution with Command
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        # Get current state to see what's being requested
        state = agent.get_state(config)
        
        if not state.next:
            print("No pending approval found.")
            return
        
        print("\n" + "="*50)
        print("🔔 APPROVAL REQUEST")
        print("="*50)
        
        # In a real system, the interrupt data would be accessible
        # For demo purposes, we'll simulate the approval request
        print("Action Type: High-risk operation")
        print("Details: The agent wants to perform an action that requires approval")
        print("Risk Level: Medium-High")
        
        # Get human decision
        print("\nOptions:")
        print("1. Approve")
        print("2. Reject") 
        print("3. Approve with modifications")
        
        choice = input("\nYour decision (1-3): ").strip()
        
        if choice == "1":
            notes = input("Approval notes (optional): ").strip()
            response_data = {"approved": True, "notes": notes}
        elif choice == "2":
            reason = input("Rejection reason: ").strip()
            response_data = {"approved": False, "notes": reason}
        elif choice == "3":
            modifications = input("Required modifications: ").strip()
            notes = input("Additional notes: ").strip()
            response_data = {"approved": True, "notes": notes, "modifications": modifications}
        else:
            print("Invalid choice, defaulting to rejection")
            response_data = {"approved": False, "notes": "Invalid approval choice"}
        
        # Resume execution with the approval decision
        from langgraph.types import Command
        resume_command = Command(resume=response_data)
        
        print(f"\n{'✅ APPROVED' if response_data['approved'] else '❌ REJECTED'}")
        print("Resuming agent execution...")
        
        # Continue the conversation
        events = agent.stream(resume_command, config, stream_mode="values")
        
        for event in events:
            if "messages" in event and event["messages"]:
                last_message = event["messages"][-1]
                if hasattr(last_message, 'content'):
                    print(f"🤖 Agent: {last_message.content}")
        
    except Exception as e:
        print(f"Error handling approval: {e}")

def show_approval_status(agent, thread_id: str):
    """
    Show the approval history and current status.
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        state = agent.get_state(config)
        
        if not state or not state.values:
            print("No approval history found.")
            return
        
        approval_history = state.values.get("approval_history", [])
        workflow_status = state.values.get("workflow_status", "unknown")
        
        print(f"\n📊 Workflow Status: {workflow_status}")
        print(f"📝 Approval History ({len(approval_history)} items):")
        
        if not approval_history:
            print("   No approvals yet")
        else:
            for i, record in enumerate(approval_history, 1):
                status = "✅ APPROVED" if record.get("approved") else "❌ REJECTED"
                action_type = record.get("action", {}).get("type", "unknown")
                notes = record.get("notes", "")
                print(f"   {i}. {status} - {action_type}")
                if notes:
                    print(f"      Notes: {notes}")
        
    except Exception as e:
        print(f"Error getting status: {e}")

# Validation function
def validate_hitl_setup():
    """
    Validate that the HITL setup is working correctly.
    """
    if not OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY not found in .env file!")
        return False
    
    if not TAVILY_API_KEY:
        print("❌ TAVILY_API_KEY not found in .env file!")  
        return False
    
    print("✅ HITL environment validated")
    return True