"""
workflows/document_processor.py - Document Processing Workflow
=============================================================

This demonstrates a complex multi-step workflow for document processing
with sophisticated state management, validation, and error handling.
"""

from datetime import datetime
from agents.workflow_agent import create_document_processor, run_workflow_session
from state.schemas import (
    create_document_processing_state, UserProfile, DocumentInfo, 
    WorkflowStatus, WorkflowMetadata
)

def run_document_demo():
    """
    Run an interactive document processing workflow demonstration.
    """
    print("\n📄 Document Processing Workflow Demo")
    print("=" * 40)
    
    print("This workflow demonstrates:")
    print("- Multi-step document processing pipeline")
    print("- State validation and error handling")
    print("- Custom reducers for log aggregation")
    print("- Workflow progress tracking")
    
    # Initialize user profile
    user_profile = UserProfile(
        name="Document Processor",
        email="processor@company.com",
        role="content_manager",
        permissions=["upload", "process", "approve"]
    )
    
    # Create initial workflow state
    processing_config = {
        "auto_validation": True,
        "require_approval": False,
        "max_file_size_mb": 50,
        "allowed_types": [".pdf", ".docx", ".txt", ".md"]
    }
    
    initial_state = create_document_processing_state(user_profile, processing_config)
    
    # Create and run the document processor
    agent = create_document_processor()
    thread_id = f"doc_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"\nStarting document processing workflow (Thread: {thread_id})")
    print("\nTry these commands:")
    print("- 'Upload a new document called report.pdf that is 2.5MB'")
    print("- 'Validate the uploaded document'")
    print("- 'Process the document to extract text'") 
    print("- 'Review processing results'")
    print("- 'Complete the workflow'")
    
    run_workflow_session(agent, initial_state, thread_id)

def simulate_document_workflow():
    """
    Simulate a complete document workflow for testing.
    """
    print("\n🔄 Simulating Complete Document Workflow")
    print("=" * 45)
    
    # Create workflow components
    user = UserProfile(
        name="Test User",
        email="test@example.com", 
        role="analyst"
    )
    
    initial_state = create_document_processing_state(user)
    agent = create_document_processor()
    config = {"configurable": {"thread_id": "doc_simulation"}}
    
    # Simulate workflow steps
    workflow_steps = [
        "Upload document 'quarterly_report.pdf' (3.2MB)",
        "Validate document format and size",
        "Extract text and metadata from document",
        "Analyze content for key information",
        "Generate processing summary",
        "Mark workflow as completed"
    ]
    
    print("Simulating workflow steps:")
    for i, step in enumerate(workflow_steps, 1):
        print(f"\n{i}. {step}")
        
        # Simulate processing each step
        input_state = {"messages": [{"role": "user", "content": step}]}
        
        try:
            events = list(agent.stream(input_state, config, stream_mode="values"))
            if events and events[-1].get("messages"):
                last_msg = events[-1]["messages"][-1]
                if hasattr(last_msg, 'content'):
                    print(f"   Response: {last_msg.content[:100]}...")
        except Exception as e:
            print(f"   Error: {e}")
    
    # Show final state
    final_state = agent.get_state(config)
    if final_state and final_state.values:
        workflow_meta = final_state.values.get("workflow_metadata")
        if workflow_meta:
            print(f"\nWorkflow Summary:")
            print(f"- Status: {workflow_meta.workflow_type}")
            print(f"- Progress: {workflow_meta.completed_steps}/{workflow_meta.total_steps}")
            print(f"- Duration: Started at {workflow_meta.started_at}")

class DocumentWorkflowManager:
    """
    Manager class for document processing workflows.
    Demonstrates how to wrap workflow agents in higher-level abstractions.
    """
    
    def __init__(self):
        self.agent = create_document_processor()
        self.active_workflows = {}
    
    def start_workflow(self, user_profile: UserProfile, config: dict = None) -> str:
        """Start a new document processing workflow."""
        workflow_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        initial_state = create_document_processing_state(user_profile, config)
        thread_config = {"configurable": {"thread_id": workflow_id}}
        
        # Initialize the workflow
        self.agent.get_state(thread_config)
        
        self.active_workflows[workflow_id] = {
            "user": user_profile,
            "started_at": datetime.now().isoformat(),
            "config": config or {}
        }
        
        return workflow_id
    
    def process_step(self, workflow_id: str, action: str) -> dict:
        """Process a single step in the workflow."""
        if workflow_id not in self.active_workflows:
            return {"error": "Workflow not found"}
        
        thread_config = {"configurable": {"thread_id": workflow_id}}
        input_state = {"messages": [{"role": "user", "content": action}]}
        
        try:
            events = list(self.agent.stream(input_state, thread_config, stream_mode="values"))
            
            if events:
                final_event = events[-1]
                return {
                    "success": True,
                    "response": final_event.get("messages", [])[-1].content if final_event.get("messages") else "",
                    "state": self.get_workflow_status(workflow_id)
                }
            else:
                return {"error": "No response from workflow"}
                
        except Exception as e:
            return {"error": str(e)}
    
    def get_workflow_status(self, workflow_id: str) -> dict:
        """Get current status of a workflow."""
        if workflow_id not in self.active_workflows:
            return {"error": "Workflow not found"}
        
        thread_config = {"configurable": {"thread_id": workflow_id}}
        state = self.agent.get_state(thread_config)
        
        if not state or not state.values:
            return {"error": "No state found"}
        
        workflow_meta = state.values.get("workflow_metadata")
        return {
            "workflow_id": workflow_id,
            "current_step": workflow_meta.current_step if workflow_meta else "unknown",
            "progress": f"{workflow_meta.completed_steps}/{workflow_meta.total_steps}" if workflow_meta else "0/0",
            "status": state.values.get("overall_status", "unknown"),
            "started_at": self.active_workflows[workflow_id]["started_at"]
        }
    
    def list_workflows(self) -> list:
        """List all active workflows."""
        return [
            {
                "workflow_id": wf_id,
                "user": wf_data["user"].name,
                "started_at": wf_data["started_at"],
                "status": self.get_workflow_status(wf_id)
            }
            for wf_id, wf_data in self.active_workflows.items()
        ]

def demo_workflow_manager():
    """Demonstrate the workflow manager functionality."""
    print("\n🔧 Document Workflow Manager Demo")
    print("=" * 35)
    
    manager = DocumentWorkflowManager()
    
    # Start a workflow
    user = UserProfile(name="Manager Demo User", email="demo@test.com", role="user")
    workflow_id = manager.start_workflow(user)
    
    print(f"Started workflow: {workflow_id}")
    
    # Process some steps
    steps = [
        "Upload document 'test.pdf' (1MB)",
        "Validate the document",
        "Extract content from document"
    ]
    
    for step in steps:
        print(f"\nProcessing: {step}")
        result = manager.process_step(workflow_id, step)
        
        if result.get("success"):
            print(f"Response: {result['response'][:100]}...")
            print(f"Status: {result['state']['status']}")
        else:
            print(f"Error: {result.get('error')}")
    
    # Show final status
    print(f"\nFinal workflow status:")
    status = manager.get_workflow_status(workflow_id)
    for key, value in status.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    choice = input("Choose demo (1=Interactive, 2=Simulation, 3=Manager): ")
    
    if choice == "1":
        run_document_demo()
    elif choice == "2":
        simulate_document_workflow()
    elif choice == "3":
        demo_workflow_manager()
    else:
        run_document_demo()