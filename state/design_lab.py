"""
state/design_lab.py - Interactive State Design Laboratory
========================================================

This module provides an interactive environment for learning and experimenting
with custom state design patterns in LangGraph.
"""

from typing import Dict, Any, List
from datetime import datetime
import json

class StateDesignLab:
    """Interactive laboratory for experimenting with state design."""
    
    def __init__(self):
        self.experiments = []
        self.current_state = {}
    
    def run_interactive_session(self):
        """Run an interactive state design session."""
        print("State Design Laboratory")
        print("=" * 25)
        print("Learn state design patterns through hands-on experimentation")
        
        while True:
            print("\nChoose an experiment:")
            print("1. Basic State Structure")
            print("2. Custom Reducers")
            print("3. State Validation")
            print("4. Complex Workflows")
            print("5. State Debugging")
            print("6. Export Examples")
            print("0. Exit Lab")
            
            choice = input("\nEnter choice (0-6): ").strip()
            
            if choice == "0":
                print("Exiting State Design Lab")
                break
            elif choice == "1":
                self.experiment_basic_structure()
            elif choice == "2":
                self.experiment_custom_reducers()
            elif choice == "3":
                self.experiment_state_validation()
            elif choice == "4":
                self.experiment_complex_workflows()
            elif choice == "5":
                self.experiment_state_debugging()
            elif choice == "6":
                self.export_examples()
            else:
                print("Invalid choice")
    
    def experiment_basic_structure(self):
        """Experiment with basic state structures."""
        print("\n🏗️ Basic State Structure Experiment")
        print("=" * 35)
        
        print("Let's design a state schema for your workflow.")
        
        workflow_type = input("What type of workflow? (e.g., 'order_processing', 'user_registration'): ").strip()
        
        if not workflow_type:
            workflow_type = "example_workflow"
        
        print(f"\nDesigning state for: {workflow_type}")
        print("\nCore fields every workflow needs:")
        print("- messages: conversation history")
        print("- workflow_metadata: progress tracking") 
        print("- current_step: where we are in the process")
        print("- overall_status: current workflow status")
        
        # Collect custom fields
        custom_fields = []
        print("\nWhat specific data does your workflow need to track?")
        print("(Enter one field per line, press Enter on empty line when done)")
        
        while True:
            field = input("Field name (or Enter to finish): ").strip()
            if not field:
                break
            
            field_type = input(f"Type for '{field}' (str/int/list/dict): ").strip()
            description = input(f"Description of '{field}': ").strip()
            
            custom_fields.append({
                "name": field,
                "type": field_type,
                "description": description
            })
        
        # Generate state schema
        print(f"\n Generated State Schema for {workflow_type}:")
        print("=" * 50)
        print("from typing import Annotated, TypedDict, List, Dict, Any")
        print("from langgraph.graph.message import add_messages")
        print()
        print(f"class {workflow_type.title().replace('_', '')}State(TypedDict):")
        print('    """Custom state for', workflow_type, 'workflow."""')
        print("    messages: Annotated[List, add_messages]")
        print("    workflow_metadata: Optional[WorkflowMetadata]")
        print("    current_step: str")
        print("    overall_status: WorkflowStatus")
        
        for field in custom_fields:
            type_mapping = {
                "str": "str", 
                "int": "int",
                "list": "List[Any]",
                "dict": "Dict[str, Any]"
            }
            python_type = type_mapping.get(field["type"], "Any")
            print(f"    {field['name']}: {python_type}  # {field['description']}")
        
        # Save experiment
        experiment = {
            "type": "basic_structure",
            "workflow_type": workflow_type,
            "custom_fields": custom_fields,
            "timestamp": datetime.now().isoformat()
        }
        self.experiments.append(experiment)
        
        print(f"\nExperiment saved! You've designed a state schema with {len(custom_fields)} custom fields.")
    
    def experiment_custom_reducers(self):
        """Experiment with custom reducer functions."""
        print("\n⚙️ Custom Reducers Experiment")
        print("=" * 30)
        
        print("Custom reducers control how state updates are merged.")
        print("Let's explore different patterns:")
        
        print("\n1. Append Reducer (for lists):")
        print("   - Adds new items to existing list")
        print("   - Use case: logs, notifications, task lists")
        
        print("\n2. Merge Reducer (for dictionaries):")
        print("   - Merges new dict with existing dict")
        print("   - Use case: user preferences, metadata")
        
        print("\n3. Max Reducer (for numbers):")
        print("   - Keeps the larger of old vs new value")
        print("   - Use case: progress counters, scores")
        
        print("\n4. Custom Logic Reducer:")
        print("   - Implements complex business logic")
        print("   - Use case: validation, conditional updates")
        
        reducer_type = input("\nWhich reducer pattern interests you? (1-4): ").strip()
        
        if reducer_type == "1":
            self.demo_append_reducer()
        elif reducer_type == "2":
            self.demo_merge_reducer()
        elif reducer_type == "3":
            self.demo_max_reducer()
        elif reducer_type == "4":
            self.demo_custom_reducer()
        else:
            print("Invalid choice")
    
    def demo_append_reducer(self):
        """Demonstrate append reducer pattern."""
        print("\nAppend Reducer Demo:")
        print("=" * 20)
        
        print("def append_to_list(existing: List, new: List) -> List:")
        print("    if not existing:")
        print("        return new or []")
        print("    return existing + (new or [])")
        print()
        print("# Usage in state:")
        print("notifications: Annotated[List[str], append_to_list]")
        
        # Interactive demo
        current_list = []
        print(f"\nCurrent list: {current_list}")
        
        while True:
            new_items = input("Add items (comma-separated, or 'done'): ").strip()
            if new_items.lower() == 'done':
                break
            
            items = [item.strip() for item in new_items.split(',') if item.strip()]
            current_list.extend(items)
            print(f"Updated list: {current_list}")
        
        print(f"Final result: {current_list}")
    
    def demo_merge_reducer(self):
        """Demonstrate merge reducer pattern."""
        print("\nMerge Reducer Demo:")
        print("=" * 19)
        
        print("def merge_dicts(existing: Dict, new: Dict) -> Dict:")
        print("    if not existing:")
        print("        return new or {}")
        print("    return {**existing, **new}")
        
        # Interactive demo
        current_dict = {}
        print(f"\nCurrent dict: {current_dict}")
        
        while True:
            key = input("Add key (or 'done'): ").strip()
            if key.lower() == 'done':
                break
            
            value = input(f"Value for '{key}': ").strip()
            current_dict[key] = value
            print(f"Updated dict: {current_dict}")
    
    def demo_max_reducer(self):
        """Demonstrate max reducer pattern."""
        print("\nMax Reducer Demo:")
        print("=" * 17)
        
        print("def keep_max(existing: float, new: float) -> float:")
        print("    return max(existing or 0, new or 0)")
        
        current_value = 0
        print(f"\nCurrent value: {current_value}")
        
        while True:
            new_val = input("New value (or 'done'): ").strip()
            if new_val.lower() == 'done':
                break
            
            try:
                new_num = float(new_val)
                current_value = max(current_value, new_num)
                print(f"Updated value: {current_value}")
            except ValueError:
                print("Please enter a number")
    
    def demo_custom_reducer(self):
        """Demonstrate custom business logic reducer."""
        print("\nCustom Logic Reducer Demo:")
        print("=" * 27)
        
        print("Example: Smart task priority reducer")
        print("def update_task_priority(existing: str, new: str) -> str:")
        print("    priority_order = ['low', 'medium', 'high', 'critical']")
        print("    existing_idx = priority_order.index(existing or 'low')")
        print("    new_idx = priority_order.index(new or 'low')")
        print("    return priority_order[max(existing_idx, new_idx)]")
        
        priorities = ['low', 'medium', 'high', 'critical']
        current_priority = 'low'
        
        print(f"\nCurrent priority: {current_priority}")
        
        while True:
            new_priority = input(f"New priority {priorities} (or 'done'): ").strip()
            if new_priority.lower() == 'done':
                break
            
            if new_priority in priorities:
                existing_idx = priorities.index(current_priority)
                new_idx = priorities.index(new_priority)
                current_priority = priorities[max(existing_idx, new_idx)]
                print(f"Updated priority: {current_priority}")
            else:
                print(f"Invalid priority. Choose from: {priorities}")
    
    def experiment_state_validation(self):
        """Experiment with state validation patterns."""
        print("\n✅ State Validation Experiment")
        print("=" * 30)
        
        print("State validation ensures data integrity and business rules.")
        print("Common validation patterns:")
        print("1. Required field validation")
        print("2. Data type validation") 
        print("3. Business rule validation")
        print("4. Cross-field validation")
        
        # Create a sample state to validate
        sample_state = {
            "user_name": "",
            "user_email": "invalid-email",
            "age": -5,
            "account_balance": 1000,
            "withdrawal_amount": 1500
        }
        
        print(f"\nSample state to validate: {sample_state}")
        
        # Run validation examples
        errors = []
        
        # Required field validation
        if not sample_state["user_name"]:
            errors.append("user_name is required")
        
        # Format validation
        if "@" not in sample_state["user_email"]:
            errors.append("user_email must be valid email format")
        
        # Range validation
        if sample_state["age"] < 0:
            errors.append("age cannot be negative")
        
        # Business rule validation
        if sample_state["withdrawal_amount"] > sample_state["account_balance"]:
            errors.append("withdrawal_amount cannot exceed account_balance")
        
        print(f"\nValidation errors found: {len(errors)}")
        for error in errors:
            print(f"  - {error}")
        
        print("\nValidation helps prevent invalid state transitions!")
    
    def experiment_complex_workflows(self):
        """Experiment with complex workflow state patterns."""
        print("\n🔄 Complex Workflows Experiment")
        print("=" * 32)
        
        print("Complex workflows often need:")
        print("- Multi-stage processes")
        print("- Conditional branching")
        print("- Parallel execution tracking")
        print("- Rollback capabilities")
        
        # Design a complex workflow
        workflow_name = input("\nWhat complex workflow would you like to model? ").strip()
        
        if not workflow_name:
            workflow_name = "multi_stage_approval"
        
        print(f"\nDesigning: {workflow_name}")
        print("Let's identify the key components:")
        
        # Collect stages
        stages = []
        print("\nWhat are the main stages? (press Enter when done)")
        while True:
            stage = input(f"Stage {len(stages) + 1}: ").strip()
            if not stage:
                break
            stages.append(stage)
        
        # Collect state requirements
        print(f"\nFor {workflow_name} with stages {stages}:")
        print("Consider what state you need:")
        print("- Current stage and completion status")
        print("- Stage-specific data and results")
        print("- Error handling and retry logic")
        print("- Approval chains and dependencies")
        
        # Generate workflow state template
        print(f"\nGenerated state template:")
        print("=" * 30)
        print(f"class {workflow_name.title().replace('_', '')}State(TypedDict):")
        print("    messages: Annotated[List, add_messages]")
        print("    current_stage: str")
        print("    completed_stages: List[str]")
        print("    stage_results: Dict[str, Any]")
        print("    workflow_metadata: WorkflowMetadata")
        
        for stage in stages:
            clean_stage = stage.lower().replace(' ', '_')
            print(f"    {clean_stage}_data: Optional[Dict[str, Any]]")
        
        experiment = {
            "type": "complex_workflow",
            "workflow_name": workflow_name,
            "stages": stages,
            "timestamp": datetime.now().isoformat()
        }
        self.experiments.append(experiment)
    
    def experiment_state_debugging(self):
        """Experiment with state debugging techniques."""
        print("\n🐛 State Debugging Experiment")
        print("=" * 28)
        
        print("Debugging state issues requires:")
        print("1. State inspection tools")
        print("2. State history tracking")
        print("3. Validation logging")
        print("4. State diff analysis")
        
        # Create debugging scenarios
        print("\nCommon state debugging scenarios:")
        print("- State not updating as expected")
        print("- Reducer functions not working")
        print("- Validation errors")
        print("- Memory leaks from large state")
        
        print("\nDebugging tools you can use:")
        print("1. agent.get_state(config) - inspect current state")
        print("2. print(state) in nodes - debug state changes")
        print("3. State validation functions - check integrity")
        print("4. LangSmith tracing - visualize state flow")
        
        # Interactive debugging demo
        debug_state = {
            "counter": 0,
            "items": [],
            "last_update": datetime.now().isoformat()
        }
        
        print(f"\nDebugging this state: {debug_state}")
        print("Try these debugging commands:")
        print("- 'inspect counter' - look at specific field")
        print("- 'history' - show state changes")
        print("- 'validate' - run validation")
        print("- 'done' - finish debugging")
        
        while True:
            cmd = input("Debug command: ").strip().lower()
            
            if cmd == 'done':
                break
            elif cmd.startswith('inspect'):
                field = cmd.split()[-1] if len(cmd.split()) > 1 else 'all'
                if field == 'all':
                    print(f"Full state: {debug_state}")
                elif field in debug_state:
                    print(f"{field}: {debug_state[field]}")
                else:
                    print(f"Field '{field}' not found")
            elif cmd == 'history':
                print("State change history: [simulated]")
                print("  1. counter: 0 -> 5")
                print("  2. items: [] -> ['item1']")
            elif cmd == 'validate':
                print("Validation: ✅ All fields valid")
            else:
                print("Unknown command")
    
    def export_examples(self):
        """Export generated examples and patterns."""
        print("\n📄 Export Examples")
        print("=" * 18)
        
        if not self.experiments:
            print("No experiments to export. Try some experiments first!")
            return
        
        print(f"You have {len(self.experiments)} experiments:")
        for i, exp in enumerate(self.experiments, 1):
            print(f"{i}. {exp['type']} - {exp.get('workflow_type', 'N/A')}")
        
        export_choice = input("\nExport all? (y/n): ").strip().lower()
        
        if export_choice.startswith('y'):
            filename = f"state_design_experiments_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            export_data = {
                "generated_at": datetime.now().isoformat(),
                "experiments": self.experiments,
                "summary": {
                    "total_experiments": len(self.experiments),
                    "experiment_types": list(set(exp["type"] for exp in self.experiments))
                }
            }
            
            # In a real implementation, this would write to a file
            print(f"\nExported to: {filename}")
            print("Export contains:")
            print(f"- {len(self.experiments)} experiments")
            print(f"- Generated state schemas")
            print(f"- Custom reducer patterns")
            print(f"- Validation examples")
            
            # Show sample export
            print("\nSample export data:")
            print(json.dumps(export_data, indent=2)[:500] + "...")
        
        print("\nUse these patterns in your own workflows!")

if __name__ == "__main__":
    lab = StateDesignLab()
    lab.run_interactive_session()