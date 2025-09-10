"""
LangGraph Bootcamp - Session 5: Custom State Design
===================================================

Building on Sessions 1-4, we're designing sophisticated state structures
that can handle complex multi-step workflows beyond simple conversations.

Learning Goals:
- Design complex state schemas
- Implement custom reducers  
- Build multi-step workflows
- Handle state transitions and validation

Real-world analogy: Upgrading from a simple todo list to a full project
management system that tracks dependencies, resources, and progress.
"""

from agents.workflow_agent import (
    create_document_processor, 
    create_project_manager, 
    create_onboarding_agent,
    run_workflow_session
)
from utils.setup import load_environment
from datetime import datetime

def main():
    """
    Main execution for Session 5 custom state demonstrations.
    """
    print("🏗️ Custom State Design - Session 5")
    print("=" * 40)
    
    if not load_environment():
        return
    
    print("\nChoose a workflow demonstration:")
    print("1. Document Processing Pipeline")
    print("2. Project Management Workflow") 
    print("3. User Onboarding Flow")
    print("4. Interactive State Design Lab")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        run_document_demo()
    elif choice == "2":
        run_project_demo()
    elif choice == "3":
        run_onboarding_demo()
    elif choice == "4":
        run_state_design_lab()
    else:
        print("Invalid choice, starting document processor...")
        run_document_demo()

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
    
    run_workflow_session(agent, thread_id)

def run_project_demo():
    """
    Run an interactive project management workflow demonstration.
    """
    print("\n📊 Project Management Workflow Demo")
    print("=" * 40)
    
    print("This workflow demonstrates:")
    print("- Task creation and assignment")
    print("- Project progress tracking")
    print("- Team member management")
    print("- Resource allocation")
    
    # Create and run the project manager
    agent = create_project_manager()
    thread_id = f"proj_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"\nStarting project management workflow (Thread: {thread_id})")
    print("\nTry these commands:")
    print("- 'Create a new project called Website Redesign'")
    print("- 'Add task: Design homepage layout with high priority'")
    print("- 'Assign task to John with 8 hour estimate'")
    print("- 'Update workflow step from planning to execution'")
    print("- 'Show project status and progress'")
    
    run_workflow_session(agent, thread_id)

def run_onboarding_demo():
    """
    Run an interactive user onboarding workflow demonstration.
    """
    print("\n👋 User Onboarding Workflow Demo")
    print("=" * 35)
    
    print("This workflow demonstrates:")
    print("- Step-by-step user onboarding")
    print("- Preference collection and storage")
    print("- Progress tracking through onboarding")
    print("- Personalized user experience")
    
    # Create and run the onboarding agent
    agent = create_onboarding_agent()
    thread_id = f"onboard_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"\nStarting user onboarding workflow (Thread: {thread_id})")
    print("\nTry these commands:")
    print("- 'Start onboarding for new user'")
    print("- 'Collect user preference: theme = dark, category = ui'")
    print("- 'Move to next onboarding step'")
    print("- 'Set user preference: notifications = email, category = communication'")
    print("- 'Complete onboarding process'")
    
    run_workflow_session(agent, thread_id)

def run_state_design_lab():
    """
    Interactive lab for experimenting with state design patterns.
    """
    print("\n🧪 State Design Laboratory")
    print("=" * 30)
    
    print("This lab teaches state design patterns through examples:")
    print("\n1. Basic State Structure:")
    print("   - Beyond simple message lists")
    print("   - Structured data organization")
    print("   - Custom field definitions")
    
    print("\n2. Custom Reducers:")
    print("   - How state updates are merged")
    print("   - Append vs merge vs custom logic")
    print("   - Practical reducer examples")
    
    print("\n3. State Validation:")
    print("   - Business rule enforcement")
    print("   - Data integrity checks")
    print("   - Error prevention patterns")
    
    print("\n4. Complex Workflows:")
    print("   - Multi-stage processes")
    print("   - Conditional branching")
    print("   - Progress tracking")
    
    choice = input("\nWhich topic interests you most? (1-4): ").strip()
    
    if choice == "1":
        demo_basic_state_structure()
    elif choice == "2":
        demo_custom_reducers()
    elif choice == "3":
        demo_state_validation()
    elif choice == "4":
        demo_complex_workflows()
    else:
        print("Running overview of all concepts...")
        demo_state_design_overview()

def demo_basic_state_structure():
    """Demonstrate basic state structure concepts."""
    print("\n🏗️ Basic State Structure Demo")
    print("=" * 32)
    
    print("Traditional simple state:")
    print("```python")
    print("class SimpleState(TypedDict):")
    print("    messages: List  # Just conversation history")
    print("```")
    
    print("\nEnhanced workflow state:")
    print("```python")
    print("class WorkflowState(TypedDict):")
    print("    messages: Annotated[List, add_messages]")
    print("    current_step: str")
    print("    workflow_metadata: Dict[str, Any]")
    print("    user_profile: Optional[UserProfile]")
    print("    task_progress: Dict[str, float]")
    print("    errors: List[str]")
    print("```")
    
    print("\nBenefits of structured state:")
    print("- Clear data organization")
    print("- Type safety and validation")
    print("- Easy progress tracking")
    print("- Extensible for new features")

def demo_custom_reducers():
    """Demonstrate custom reducer concepts."""
    print("\n⚙️ Custom Reducers Demo")
    print("=" * 23)
    
    print("Default behavior (overwrites):")
    print("Old: {'count': 5}")
    print("New: {'count': 3}")
    print("Result: {'count': 3}  # Old value lost!")
    
    print("\nWith append reducer:")
    print("Old: {'logs': ['step1', 'step2']}")
    print("New: {'logs': ['step3']}")
    print("Result: {'logs': ['step1', 'step2', 'step3']}")
    
    print("\nWith merge reducer:")
    print("Old: {'prefs': {'theme': 'dark'}}")
    print("New: {'prefs': {'lang': 'en'}}")
    print("Result: {'prefs': {'theme': 'dark', 'lang': 'en'}}")

def demo_state_validation():
    """Demonstrate state validation concepts."""
    print("\n✅ State Validation Demo")
    print("=" * 25)
    
    print("Common validation patterns:")
    print("1. Required fields: Ensure critical data is present")
    print("2. Format validation: Email, phone, date formats")
    print("3. Business rules: Account balance > withdrawal amount")
    print("4. Cross-field validation: End date > start date")
    
    print("\nExample validation:")
    print("```python")
    print("def validate_expense_request(state):")
    print("    if state['amount'] > state['budget_remaining']:")
    print("        raise ValidationError('Exceeds budget')")
    print("```")

def demo_complex_workflows():
    """Demonstrate complex workflow concepts."""
    print("\n🔄 Complex Workflows Demo")
    print("=" * 27)
    
    print("Complex workflows typically involve:")
    print("- Multiple stages with dependencies")
    print("- Conditional branching based on data")
    print("- Parallel execution tracking")
    print("- Rollback and retry capabilities")
    
    print("\nExample: Document approval workflow")
    print("1. Upload → 2. Validate → 3. Review")
    print("                ↓")
    print("        If invalid: → Fix & resubmit")
    print("                ↓")
    print("        If approved: → Publish")
    print("        If rejected: → Archive")

def demo_state_design_overview():
    """Overview of all state design concepts."""
    print("\n📋 State Design Overview")
    print("=" * 25)
    
    print("Key principles for state design:")
    print("1. Structure: Organize data logically")
    print("2. Reducers: Control how updates merge")
    print("3. Validation: Enforce business rules")
    print("4. Evolution: Plan for future changes")
    
    print("\nChoose a workflow demo to see these principles in action!")

if __name__ == "__main__":
    main()