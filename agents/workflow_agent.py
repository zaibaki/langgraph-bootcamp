"""
agents/workflow_agent.py - Multi-Step Workflow Agent
====================================================

This module implements agents that can handle complex multi-step workflows
with sophisticated state management and validation.
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()

# Environment setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Initialize LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# ============================================================================
# WORKFLOW MANAGEMENT TOOLS
# ============================================================================

@tool
def update_workflow_step(
    current_step: str,
    next_step: str,
    completion_notes: str = ""
) -> str:
    """
    Update the workflow to the next step with validation.
    
    Args:
        current_step: The step we're completing
        next_step: The step to move to next
        completion_notes: Notes about the step completion
    """
    return f"Workflow updated: {current_step} -> {next_step}. Notes: {completion_notes}"

@tool  
def add_task_to_project(
    task_title: str,
    task_description: str,
    priority_level: str,
    assignee: str = "",
    estimated_hours: float = 0.0
) -> str:
    """
    Add a new task to the current project.
    
    Args:
        task_title: Title of the task
        task_description: Detailed description
        priority_level: Priority (low, medium, high, critical)
        assignee: Who is assigned to this task
        estimated_hours: Estimated time to complete
    """
    result = f"Task added: '{task_title}' (Priority: {priority_level})"
    if assignee:
        result += f" assigned to {assignee}"
    if estimated_hours > 0:
        result += f" (Est: {estimated_hours}h)"
    
    return result

@tool
def validate_document_upload(
    filename: str,
    file_type: str,
    file_size_mb: float
) -> str:
    """
    Validate an uploaded document for processing.
    
    Args:
        filename: Name of the uploaded file
        file_type: Type/extension of the file
        file_size_mb: Size of the file in MB
    """
    # Validation logic
    valid_types = ['.pdf', '.docx', '.txt', '.md']
    max_size_mb = 50
    
    if not any(filename.endswith(ext) for ext in valid_types):
        return f"Invalid file type. Supported: {', '.join(valid_types)}"
    
    if file_size_mb > max_size_mb:
        return f"File too large. Max size: {max_size_mb}MB"
    
    return f"Document validated: {filename} ({file_size_mb}MB, {file_type})"

@tool
def collect_user_preference(
    preference_key: str,
    preference_value: str,
    preference_category: str = "general"
) -> str:
    """
    Collect and store a user preference during onboarding.
    
    Args:
        preference_key: The preference identifier
        preference_value: The user's preference value
        preference_category: Category for organization
    """
    return f"Preference saved: {preference_key} = {preference_value} (Category: {preference_category})"

# ============================================================================
# WORKFLOW NODE IMPLEMENTATIONS
# ============================================================================

def create_workflow_chatbot_node():
    """
    Create a chatbot node that's aware of workflow state.
    """
    def workflow_chatbot_node(state):
        """
        Enhanced chatbot that understands workflow context.
        """
        messages = state["messages"]
        
        # Add workflow context to the conversation
        workflow_meta = state.get("workflow_metadata")
        current_step = state.get("current_step", "unknown")
        
        if workflow_meta:
            context_msg = {
                "role": "system",
                "content": f"You are helping with a {workflow_meta.workflow_type} workflow. "
                          f"Current step: {current_step}. "
                          f"Progress: {workflow_meta.completed_steps}/{workflow_meta.total_steps} steps completed. "
                          f"Be helpful and guide the user through the process."
            }
            messages = [context_msg] + messages
        
        # Get LLM response
        response = llm_with_tools.invoke(messages)
        
        return {"messages": [response]}
    
    return workflow_chatbot_node

# ============================================================================
# STATE SCHEMAS (simplified versions)
# ============================================================================

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class DocumentProcessingState(TypedDict):
    """State for document processing workflows."""
    messages: Annotated[List, add_messages]
    current_step: str
    overall_status: str
    workflow_metadata: Optional[Dict[str, Any]]
    processed_documents: Dict[str, Any]
    processing_log: List[str]
    errors: List[str]

class ProjectManagementState(TypedDict):
    """State for project management workflows."""
    messages: Annotated[List, add_messages]
    project_id: str
    project_name: str
    current_step: str
    workflow_metadata: Optional[Dict[str, Any]]
    tasks: Dict[str, Any]
    team_members: Dict[str, Any]
    progress_metrics: Dict[str, float]

class OnboardingState(TypedDict):
    """State for user onboarding workflows."""
    messages: Annotated[List, add_messages]
    current_step: str
    workflow_metadata: Optional[Dict[str, Any]]
    user_profile: Optional[Dict[str, Any]]
    completed_steps: List[str]
    user_preferences: Dict[str, Any]
    verification_status: Dict[str, bool]

# ============================================================================
# AGENT FACTORY FUNCTIONS
# ============================================================================

def create_workflow_agent(workflow_type: str = "document_processing"):
    """
    Create a workflow agent for the specified workflow type.
    
    Args:
        workflow_type: Type of workflow (document_processing, project_management, onboarding)
    """
    # Set up tools
    base_tools = [TavilySearch(max_results=2)]
    workflow_tools = [
        update_workflow_step,
        add_task_to_project,
        validate_document_upload,
        collect_user_preference
    ]
    all_tools = base_tools + workflow_tools
    
    # Create LLM with tools
    global llm_with_tools
    llm_with_tools = llm.bind_tools(all_tools)
    
    # Choose state schema based on workflow type
    if workflow_type == "document_processing":
        state_schema = DocumentProcessingState
    elif workflow_type == "project_management":
        state_schema = ProjectManagementState
    elif workflow_type == "onboarding":
        state_schema = OnboardingState
    else:
        raise ValueError(f"Unknown workflow type: {workflow_type}")
    
    # Build the graph
    graph_builder = StateGraph(state_schema)
    
    # Add nodes
    graph_builder.add_node("chatbot", create_workflow_chatbot_node())
    graph_builder.add_node("tools", ToolNode(all_tools))
    
    # Define flow
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
        {"tools": "tools", END: END}
    )
    graph_builder.add_edge("tools", "chatbot")
    
    # Add persistent memory
    memory = MemorySaver()
    
    return graph_builder.compile(checkpointer=memory)

def create_document_processor():
    """Create a document processing workflow agent."""
    return create_workflow_agent("document_processing")

def create_project_manager():
    """Create a project management workflow agent."""
    return create_workflow_agent("project_management")

def create_onboarding_agent():
    """Create a user onboarding workflow agent."""
    return create_workflow_agent("onboarding")

# ============================================================================
# WORKFLOW EXECUTION HELPERS
# ============================================================================

def run_workflow_session(agent, thread_id: str):
    """
    Run an interactive workflow session with the agent.
    
    Args:
        agent: The workflow agent
        thread_id: Thread identifier for conversation persistence
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    print("Workflow session started. Type 'quit' to exit, 'status' to see current state.")
    print("=" * 60)
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Workflow session ended!")
            break
        
        if user_input.lower() == 'status':
            show_workflow_status(agent, config)
            continue
            
        if not user_input:
            continue
        
        try:
            # Process user input
            input_state = {"messages": [{"role": "user", "content": user_input}]}
            
            events = list(agent.stream(input_state, config, stream_mode="values"))
            
            if events:
                final_event = events[-1]
                if "messages" in final_event and final_event["messages"]:
                    last_message = final_event["messages"][-1]
                    if hasattr(last_message, 'content'):
                        print(f"Agent: {last_message.content}")
                        
        except Exception as e:
            print(f"Error: {e}")

def show_workflow_status(agent, config):
    """Show the current workflow state and progress."""
    try:
        state = agent.get_state(config)
        
        if not state or not state.values:
            print("No workflow state found.")
            return
        
        values = state.values
        workflow_meta = values.get("workflow_metadata")
        
        print(f"\nWorkflow Status")
        print("=" * 20)
        
        if workflow_meta:
            print(f"Type: {workflow_meta.get('workflow_type', 'unknown')}")
            print(f"Current Step: {workflow_meta.get('current_step', 'unknown')}")
            if 'completed_steps' in workflow_meta and 'total_steps' in workflow_meta:
                print(f"Progress: {workflow_meta['completed_steps']}/{workflow_meta['total_steps']}")
        
        current_step = values.get("current_step", "unknown")
        overall_status = values.get("overall_status", "unknown")
        
        print(f"Current Step: {current_step}")
        print(f"Overall Status: {overall_status}")
        
        # Show workflow-specific information
        if "tasks" in values and values["tasks"]:
            print(f"\nTasks: {len(values['tasks'])} total")
            for task_id in list(values["tasks"].keys())[:3]:
                task = values["tasks"][task_id]
                task_title = task.get("title", task_id)
                task_status = task.get("status", "unknown")
                print(f"  - {task_title}: {task_status}")
        
        if "processed_documents" in values and values["processed_documents"]:
            print(f"\nProcessed Documents: {len(values['processed_documents'])}")
        
        if "completed_steps" in values:
            completed = values["completed_steps"]
            if isinstance(completed, list):
                print(f"\nCompleted Steps: {len(completed)}")
                for step in completed[-3:]:
                    print(f"  - {step}")
        
    except Exception as e:
        print(f"Error showing status: {e}")

# ============================================================================
# VALIDATION AND TESTING HELPERS
# ============================================================================

def validate_workflow_setup():
    """Validate that workflow agent setup is working correctly."""
    if not OPENAI_API_KEY:
        print("OPENAI_API_KEY not found in .env file!")
        return False
    
    if not TAVILY_API_KEY:
        print("TAVILY_API_KEY not found in .env file!")
        return False
    
    print("Workflow agent environment validated")
    return True

def test_workflow_agents():
    """Test that workflow agents can be created successfully."""
    try:
        # Test document processor creation
        doc_agent = create_document_processor()
        print("Document processor created successfully")
        
        # Test project manager creation
        proj_agent = create_project_manager()
        print("Project manager created successfully")
        
        # Test onboarding agent creation
        onboard_agent = create_onboarding_agent()
        print("Onboarding agent created successfully")
        
        return True
        
    except Exception as e:
        print(f"Error testing workflow agents: {e}")
        return False

if __name__ == "__main__":
    print("Testing Workflow Agent Setup")
    print("=" * 30)
    
    # Validate environment
    if not validate_workflow_setup():
        print("Please fix environment setup before proceeding.")
        exit(1)
    
    # Test agent creation
    if test_workflow_agents():
        print("\nAll agents created successfully!")
        print("Run: python main.py to start interactive demos")
        
        # Optional interactive test
        test_choice = input("\nRun quick interactive test? (y/n): ").strip().lower()
        if test_choice.startswith('y'):
            print("\nStarting document processor test...")
            agent = create_document_processor()
            thread_id = f"test_{datetime.now().strftime('%H%M%S')}"
            
            print("Try: 'Upload document test.pdf that is 2MB'")
            run_workflow_session(agent, thread_id)
    else:
        print("Please fix the errors above before proceeding.")
        exit(1)