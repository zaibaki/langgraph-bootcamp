"""
state/validators.py - State Validation and Constraints
=====================================================

This module provides validation logic for complex state transitions
and enforces business rules on state changes.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from state.schemas import (
    DocumentProcessingState, ProjectManagementState, OnboardingState,
    WorkflowStatus, TaskStatus, Priority, WorkflowMetadata
)

class StateValidationError(Exception):
    """Custom exception for state validation errors."""
    pass

class WorkflowValidator:
    """Base class for workflow state validation."""
    
    def __init__(self):
        self.validation_rules = {}
        self.setup_rules()
    
    def setup_rules(self):
        """Override in subclasses to define validation rules."""
        pass
    
    def validate(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate state and return validation results.
        
        Returns:
            Dict with 'valid' boolean and 'errors' list
        """
        errors = []
        
        try:
            # Run all validation rules
            for rule_name, rule_func in self.validation_rules.items():
                try:
                    rule_func(state)
                except StateValidationError as e:
                    errors.append(f"{rule_name}: {str(e)}")
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "validated_at": datetime.now().isoformat()
        }

class DocumentProcessingValidator(WorkflowValidator):
    """Validator for document processing workflows."""
    
    def setup_rules(self):
        self.validation_rules = {
            "workflow_metadata_required": self._validate_workflow_metadata,
            "document_processing_sequence": self._validate_processing_sequence,
            "file_constraints": self._validate_file_constraints,
            "status_consistency": self._validate_status_consistency
        }
    
    def _validate_workflow_metadata(self, state: DocumentProcessingState):
        """Ensure workflow metadata is present and valid."""
        workflow_meta = state.get("workflow_metadata")
        if not workflow_meta:
            raise StateValidationError("Workflow metadata is required")
        
        if workflow_meta.completed_steps > workflow_meta.total_steps:
            raise StateValidationError("Completed steps cannot exceed total steps")
        
        if workflow_meta.error_count < 0:
            raise StateValidationError("Error count cannot be negative")
    
    def _validate_processing_sequence(self, state: DocumentProcessingState):
        """Validate that processing steps follow correct sequence."""
        current_step = state.get("current_step", "")
        overall_status = state.get("overall_status", WorkflowStatus.PENDING)
        
        valid_sequences = {
            "awaiting_upload": [WorkflowStatus.PENDING],
            "validating": [WorkflowStatus.IN_PROGRESS],
            "processing": [WorkflowStatus.IN_PROGRESS],
            "reviewing": [WorkflowStatus.WAITING_APPROVAL, WorkflowStatus.IN_PROGRESS],
            "completed": [WorkflowStatus.COMPLETED],
            "failed": [WorkflowStatus.FAILED]
        }
        
        if current_step in valid_sequences:
            valid_statuses = valid_sequences[current_step]
            if overall_status not in valid_statuses:
                raise StateValidationError(
                    f"Step '{current_step}' incompatible with status '{overall_status}'"
                )
    
    def _validate_file_constraints(self, state: DocumentProcessingState):
        """Validate file-related constraints."""
        current_doc = state.get("current_document")
        if current_doc:
            # File size constraints
            max_size_bytes = 50 * 1024 * 1024  # 50MB
            if current_doc.size_bytes > max_size_bytes:
                raise StateValidationError(f"File size exceeds limit: {current_doc.size_bytes} bytes")
            
            # File type constraints
            allowed_types = [".pdf", ".docx", ".txt", ".md"]
            if not any(current_doc.filename.endswith(ext) for ext in allowed_types):
                raise StateValidationError(f"Unsupported file type: {current_doc.file_type}")
    
    def _validate_status_consistency(self, state: DocumentProcessingState):
        """Ensure status fields are consistent."""
        overall_status = state.get("overall_status")
        errors = state.get("errors", [])
        
        if overall_status == WorkflowStatus.FAILED and len(errors) == 0:
            raise StateValidationError("Failed status requires error messages")
        
        if overall_status == WorkflowStatus.COMPLETED:
            workflow_meta = state.get("workflow_metadata")
            if workflow_meta and workflow_meta.completed_steps < workflow_meta.total_steps:
                raise StateValidationError("Cannot complete workflow with incomplete steps")

class ProjectManagementValidator(WorkflowValidator):
    """Validator for project management workflows."""
    
    def setup_rules(self):
        self.validation_rules = {
            "task_dependencies": self._validate_task_dependencies,
            "resource_allocation": self._validate_resource_allocation,
            "timeline_consistency": self._validate_timeline_consistency,
            "team_member_validity": self._validate_team_members
        }
    
    def _validate_task_dependencies(self, state: ProjectManagementState):
        """Validate task dependency graph for cycles and validity."""
        tasks = state.get("tasks", {})
        dependencies = state.get("task_dependencies", {})
        
        # Check for circular dependencies
        def has_cycle(task_id, visited, recursion_stack):
            visited.add(task_id)
            recursion_stack.add(task_id)
            
            for dep_task in dependencies.get(task_id, []):
                if dep_task not in visited:
                    if has_cycle(dep_task, visited, recursion_stack):
                        return True
                elif dep_task in recursion_stack:
                    return True
            
            recursion_stack.remove(task_id)
            return False
        
        visited = set()
        for task_id in tasks:
            if task_id not in visited:
                if has_cycle(task_id, visited, set()):
                    raise StateValidationError(f"Circular dependency detected involving task {task_id}")
        
        # Validate dependency references
        for task_id, deps in dependencies.items():
            if task_id not in tasks:
                raise StateValidationError(f"Dependency reference to non-existent task: {task_id}")
            for dep_id in deps:
                if dep_id not in tasks:
                    raise StateValidationError(f"Task {task_id} depends on non-existent task: {dep_id}")
    
    def _validate_resource_allocation(self, state: ProjectManagementState):
        """Validate resource allocation doesn't exceed availability."""
        tasks = state.get("tasks", {})
        team_members = state.get("team_members", {})
        
        # Check task assignments reference valid team members
        for task_id, task in tasks.items():
            if task.assignee and task.assignee not in team_members:
                raise StateValidationError(f"Task {task_id} assigned to non-existent member: {task.assignee}")
        
        # Check for over-allocation (simplified - would be more complex in reality)
        member_workload = {}
        for task in tasks.values():
            if task.assignee and task.status in [TaskStatus.TODO, TaskStatus.IN_PROGRESS]:
                member_workload[task.assignee] = member_workload.get(task.assignee, 0) + (task.estimated_hours or 0)
        
        # Assume 40 hours per week capacity
        max_hours_per_member = 40
        for member, hours in member_workload.items():
            if hours > max_hours_per_member:
                raise StateValidationError(f"Member {member} over-allocated: {hours}h (max: {max_hours_per_member}h)")
    
    def _validate_timeline_consistency(self, state: ProjectManagementState):
        """Validate project timeline consistency."""
        timeline = state.get("project_timeline", {})
        
        # Basic date format validation
        for milestone, date_str in timeline.items():
            try:
                datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError:
                raise StateValidationError(f"Invalid date format for milestone '{milestone}': {date_str}")
    
    def _validate_team_members(self, state: ProjectManagementState):
        """Validate team member information."""
        team_members = state.get("team_members", {})
        
        for member_id, member in team_members.items():
            if not member.name or not member.email:
                raise StateValidationError(f"Team member {member_id} missing required information")

class OnboardingValidator(WorkflowValidator):
    """Validator for user onboarding workflows."""
    
    def setup_rules(self):
        self.validation_rules = {
            "step_progression": self._validate_step_progression,
            "required_info_collection": self._validate_required_info,
            "verification_consistency": self._validate_verification_status,
            "onboarding_completeness": self._validate_completeness
        }
    
    def _validate_step_progression(self, state: OnboardingState):
        """Validate onboarding step progression."""
        completed_steps = state.get("completed_steps", [])
        current_step = state.get("current_step", "")
        available_next = state.get("available_next_steps", [])
        
        # Define step dependencies
        step_prerequisites = {
            "welcome": [],
            "collect_basic_info": ["welcome"],
            "verify_email": ["collect_basic_info"],
            "setup_preferences": ["verify_email"],
            "choose_features": ["setup_preferences"],
            "setup_integrations": ["choose_features"],
            "final_review": ["setup_integrations"],
            "completed": ["final_review"]
        }
        
        # Check if current step prerequisites are met
        if current_step in step_prerequisites:
            required_steps = step_prerequisites[current_step]
            for required_step in required_steps:
                if required_step not in completed_steps:
                    raise StateValidationError(
                        f"Step '{current_step}' requires completion of '{required_step}'"
                    )
    
    def _validate_required_info(self, state: OnboardingState):
        """Validate that required information is collected."""
        user_profile = state.get("user_profile")
        completed_steps = state.get("completed_steps", [])
        
        if "collect_basic_info" in completed_steps:
            if not user_profile or not user_profile.name or not user_profile.email:
                raise StateValidationError("Basic user information required after collect_basic_info step")
    
    def _validate_verification_status(self, state: OnboardingState):
        """Validate verification status consistency."""
        verification_status = state.get("verification_status", {})
        completed_steps = state.get("completed_steps", [])
        
        # Email verification should be completed if verify_email step is done
        if "verify_email" in completed_steps:
            if not verification_status.get("email", False):
                raise StateValidationError("Email verification should be completed")
    
    def _validate_completeness(self, state: OnboardingState):
        """Validate onboarding completeness for final steps."""
        current_step = state.get("current_step", "")
        verification_status = state.get("verification_status", {})
        user_profile = state.get("user_profile")
        
        if current_step == "completed":
            # Check minimum requirements for completion
            if not verification_status.get("email", False):
                raise StateValidationError("Email verification required for completion")
            
            if not user_profile or not user_profile.name:
                raise StateValidationError("User profile required for completion")

# ============================================================================
# MAIN VALIDATION FUNCTION
# ============================================================================

def validate_state_transition(state: Dict[str, Any], state_type) -> Dict[str, Any]:
    """
    Main function to validate state transitions based on state type.
    
    Args:
        state: Current state to validate
        state_type: Type of state (DocumentProcessingState, etc.)
        
    Returns:
        Validation results dictionary
    """
    if state_type == DocumentProcessingState:
        validator = DocumentProcessingValidator()
    elif state_type == ProjectManagementState:
        validator = ProjectManagementValidator()
    elif state_type == OnboardingState:
        validator = OnboardingValidator()
    else:
        return {
            "valid": False,
            "errors": [f"Unknown state type: {state_type}"],
            "validated_at": datetime.now().isoformat()
        }
    
    return validator.validate(state)

# ============================================================================
# STATE SCHEMA VALIDATOR TOOL
# ============================================================================

class StateSchemaValidator:
    """Interactive tool for testing and validating state schemas."""
    
    def run_validation_tests(self):
        """Run interactive validation tests."""
        print("State Schema Validation Tool")
        print("=" * 30)
        
        print("\nChoose validation test:")
        print("1. Document Processing State")
        print("2. Project Management State")
        print("3. Onboarding State")
        print("4. Custom State Validation")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            self._test_document_validation()
        elif choice == "2":
            self._test_project_validation()
        elif choice == "3":
            self._test_onboarding_validation()
        elif choice == "4":
            self._test_custom_validation()
        else:
            print("Invalid choice")
    
    def _test_document_validation(self):
        """Test document processing state validation."""
        print("\nTesting Document Processing Validation")
        print("=" * 40)
        
        # Test valid state
        valid_state = {
            "workflow_metadata": type('obj', (object,), {
                "completed_steps": 2,
                "total_steps": 5,
                "error_count": 0
            })(),
            "current_step": "processing",
            "overall_status": WorkflowStatus.IN_PROGRESS,
            "errors": []
        }
        
        result = validate_state_transition(valid_state, DocumentProcessingState)
        print(f"Valid state test: {'✅ PASSED' if result['valid'] else '❌ FAILED'}")
        if not result['valid']:
            print(f"Errors: {result['errors']}")
        
        # Test invalid state
        invalid_state = {
            "workflow_metadata": type('obj', (object,), {
                "completed_steps": 6,  # More than total
                "total_steps": 5,
                "error_count": -1  # Negative error count
            })(),
            "current_step": "completed",
            "overall_status": WorkflowStatus.PENDING,  # Inconsistent status
            "errors": []
        }
        
        result = validate_state_transition(invalid_state, DocumentProcessingState)
        print(f"Invalid state test: {'✅ PASSED' if not result['valid'] else '❌ FAILED'}")
        if not result['valid']:
            print(f"Expected errors found: {result['errors']}")
    
    def _test_project_validation(self):
        """Test project management state validation."""
        print("\nTesting Project Management Validation")
        print("=" * 40)
        print("Project validation tests would check task dependencies, resource allocation, etc.")
        print("Implementation similar to document validation above.")
    
    def _test_onboarding_validation(self):
        """Test onboarding state validation."""
        print("\nTesting Onboarding Validation")
        print("=" * 40)
        print("Onboarding validation tests would check step progression, verification status, etc.")
        print("Implementation similar to document validation above.")
    
    def _test_custom_validation(self):
        """Test custom validation rules."""
        print("\nCustom State Validation")
        print("=" * 25)
        print("This would allow testing custom validation rules for domain-specific workflows.")
        print("Users could define their own state schemas and validation logic.")