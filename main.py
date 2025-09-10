"""
LangGraph Bootcamp - Session 4: Human-in-the-Loop Workflows
==========================================================

Building on Week 1, we're adding REAL human oversight to make agents reliable
for high-stakes decisions. This session introduces interrupt() and Command 
objects for actual approval workflows.

Project Structure:
- main.py: Main execution and testing
- agents/hitl_agent.py: Human-in-the-loop agent implementation  
- tools/approval_tools.py: Tools that require human approval
- utils/state.py: State definitions and helpers

Learning Goals:
- Implement human approval workflows
- Use interrupt() for user input  
- Build approval-based agents
- Handle approval/rejection scenarios

Real-world analogy: Adding a manager approval step to any important
business process - the system prepares everything but waits for
human sign-off before proceeding.
"""

# This file serves as the main entry point
# The actual implementation is split across modules for better organization

from agents.hitl_agent import create_approval_agent, run_approval_chat_loop
from utils.setup import load_environment

def main():
    """
    Main execution for Session 4 HITL demonstrations.
    """
    print("🛡️ Human-in-the-Loop Workflows - Session 4")
    print("=" * 50)
    
    # Load environment and validate
    if not load_environment():
        return
    
    print("\nChoose a demonstration:")
    print("1. Interactive approval agent (REAL approvals)")
    print("2. Test basic approval workflow")
    print("3. Quick approval demo")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        run_interactive_agent()
    elif choice == "2":
        demo_basic_approval()
    elif choice == "3":
        demo_quick_approval()
    else:
        print("Invalid choice, starting interactive agent...")
        run_interactive_agent()

def run_interactive_agent():
    """Run the REAL interactive approval agent."""
    print("\n🤖 Starting Real Human-in-the-Loop Agent")
    print("=" * 45)
    
    agent = create_approval_agent()
    run_approval_chat_loop(agent)

def demo_basic_approval():
    """Demonstrate basic approval workflow concepts."""
    print("\n🔍 Basic Approval Workflow Demo")
    print("=" * 35)
    
    print("This demo shows the key concepts:")
    print("1. Agent identifies high-risk actions")
    print("2. interrupt() pauses execution")
    print("3. Human makes approval decision")
    print("4. Command resumes with decision")
    print("5. Agent proceeds or aborts based on approval")
    
    proceed = input("\nStart interactive agent? (y/n): ").strip().lower()
    if proceed.startswith('y'):
        run_interactive_agent()

def demo_quick_approval():
    """Quick demo of approval patterns."""
    print("\n⚡ Quick Approval Demo")
    print("=" * 25)
    
    print("Approval Workflow Patterns:")
    print("✅ Low Risk: Auto-approve (e.g., small expenses)")
    print("⚠️  Medium Risk: Single approval (e.g., emails to clients)")
    print("🚨 High Risk: Multi-level approval (e.g., large transfers)")
    
    print("\nReal Examples to Try:")
    print("- 'Send an email to CEO about budget increase'")
    print("- 'Transfer $2000 to new vendor account'") 
    print("- 'Post breaking news announcement on social media'")
    
    proceed = input("\nStart interactive agent to test these? (y/n): ").strip().lower()
    if proceed.startswith('y'):
        run_interactive_agent()

if __name__ == "__main__":
    main()