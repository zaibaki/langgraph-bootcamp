"""
state/schemas.py - Custom State Definitions and Reducers
=======================================================

This module defines sophisticated state structures for complex workflows.
It demonstrates patterns for organizing state beyond simple message lists.
"""

from typing import Annotated, TypedDict, List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from langgraph.graph.message import add_messages

# ============================================================================
# ENUMS FOR STATE VALUES
# ============================================================================

class WorkflowStatus(Enum):
    """Standard workflow status values."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Priority(Enum):
    """Task/item priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskStatus(Enum):
    """Individual task status."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    DONE = "done"

# ============================================================================
# DATACLASSES FOR STRUCTURED STATE COMPONENTS
# ============================================================================

@dataclass
class UserProfile:
    """User information structure."""
    name: str
    email: str
    role: str
    permissions: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class TaskInfo:
    """Individual task information."""
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: Priority
    assignee: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    due_date: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DocumentInfo:
    """Document processing information."""
    id: str
    filename: str
    file_type: str
    size_bytes: int
    upload_time: str
    processing_stage: str
    validation_results: Dict[str, Any] = field(default_factory=dict)
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    error_messages: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowMetadata:
    """Metadata about the workflow execution."""
    workflow_id: str
    workflow_type: str
    started_at: str
    updated_at: str
    current_step: str
    total_steps: int
    completed_steps: int
    error_count: int = 0
    retry_count: int = 0
    timeout_at: Optional[str] = None

# ============================================================================
# CUSTOM REDUCER FUNCTIONS
# ============================================================================

def merge_user_profile(existing: Optional[UserProfile], new: Optional[UserProfile]) -> Optional[UserProfile]:
    """
    Custom reducer for user profile updates.
    Merges new profile data with existing, preserving important fields.
    """
    if not existing:
        return new
    if not new:
        return existing
    
    # Create updated profile, preserving creation time but updating modification time
    updated = UserProfile(
        name=new.name if new.name else existing.name,
        email=new.email if new.email else existing.email,
        role=new.role if new.role else existing.role,
        permissions=list(set(existing.permissions + new.permissions)),  # Merge and dedupe
        preferences={**existing.preferences, **new.preferences},  # Merge dicts
        created_at=existing.created_at  # Preserve original creation time
    )
    return updated

def update_tasks_dict(existing: Dict[str, TaskInfo], new: Dict[str, TaskInfo]) -> Dict[str, TaskInfo]:
    """
    Custom reducer for task dictionary updates.
    Merges new tasks with existing, updating timestamps.
    """
    if not existing:
        return new or {}
    if not new:
        return existing
    
    updated = existing.copy()
    current_time = datetime.now().isoformat()
    
    for task_id, new_task in new.items():
        if task_id in updated:
            # Update existing task, preserving creation time
            existing_task = updated[task_id]
            updated_task = TaskInfo(
                id=new_task.id,
                title=new_task.title or existing_task.title,
                description=new_task.description or existing_task.description,
                status=new_task.status if new_task.status != TaskStatus.TODO else existing_task.status,
                priority=new_task.priority if new_task.priority != Priority.LOW else existing_task.priority,
                assignee=new_task.assignee or existing_task.assignee,
                dependencies=list(set(existing_task.dependencies + new_task.dependencies)),
                estimated_hours=new_task.estimated_hours or existing_task.estimated_hours,
                actual_hours=new_task.actual_hours or existing_task.actual_hours,
                due_date=new_task.due_date or existing_task.due_date,
                created_at=existing_task.created_at,  # Preserve original
                updated_at=current_time,  # Update modification time
                metadata={**existing_task.metadata, **new_task.metadata}
            )
            updated[task_id] = updated_task
        else:
            # Add new task
            updated[task_id] = new_task
    
    return updated

def append_to_processing_log(existing: List[str], new: List[str]) -> List[str]:
    """
    Custom reducer for processing logs.
    Appends new log entries with timestamps.
    """
    if not existing:
        existing = []
    if not new:
        return existing
    
    timestamp = datetime.now().isoformat()
    timestamped_entries = [f"[{timestamp}] {entry}" for entry in new]
    return existing + timestamped_entries

def merge_workflow_metadata(existing: Optional[WorkflowMetadata], new: Optional[WorkflowMetadata]) -> Optional[WorkflowMetadata]:
    """
    Custom reducer for workflow metadata.
    Updates metadata while preserving start time and incrementing counters.
    """
    if not existing:
        return new
    if not new:
        return existing
    
    return WorkflowMetadata(
        workflow_id=existing.workflow_id,
        workflow_type=existing.workflow_type,
        started_at=existing.started_at,  # Preserve start time
        updated_at=datetime.now().isoformat(),  # Update current time
        current_step=new.current_step or existing.current_step,
        total_steps=new.total_steps or existing.total_steps,
        completed_steps=max(existing.completed_steps, new.completed_steps or 0),
        error_count=existing.error_count + (new.error_count or 0),
        retry_count=existing.retry_count + (new.retry_count or 0),
        timeout_at=new.timeout_at or existing.timeout_at
    )

# ============================================================================
# COMPLEX STATE SCHEMAS
# ============================================================================

class DocumentProcessingState(TypedDict):
    """
    State for document processing workflows.
    
    Demonstrates complex state with multiple data types,
    custom reducers, and structured organization.
    """
    # Standard conversation messages
    messages: Annotated[List, add_messages]
    
    # Document information
    current_document: Optional[DocumentInfo]
    processed_documents: Dict[str, DocumentInfo]
    
    # Processing workflow
    workflow_metadata: Annotated[Optional[WorkflowMetadata], merge_workflow_metadata]
    processing_log: Annotated[List[str], append_to_processing_log]
    
    # User and context
    user_profile: Annotated[Optional[UserProfile], merge_user_profile]
    processing_config: Dict[str, Any]
    
    # Status tracking
    overall_status: WorkflowStatus
    current_step: str
    errors: List[Dict[str, Any]]

class ProjectManagementState(TypedDict):
    """
    State for project management workflows.
    
    Demonstrates task tracking, dependencies, and
    resource management in state.
    """
    # Standard conversation
    messages: Annotated[List, add_messages]
    
    # Project structure
    project_id: str
    project_name: str
    project_description: str
    
    # Task management
    tasks: Annotated[Dict[str, TaskInfo], update_tasks_dict]
    task_dependencies: Dict[str, List[str]]
    
    # People and resources
    team_members: Dict[str, UserProfile]
    resource_allocation: Dict[str, Any]
    
    # Timeline and progress
    project_timeline: Dict[str, str]  # milestone -> date
    progress_metrics: Dict[str, float]
    
    # Workflow control
    workflow_metadata: Annotated[Optional[WorkflowMetadata], merge_workflow_metadata]
    current_phase: str
    approval_chain: List[str]

class OnboardingState(TypedDict):
    """
    State for user onboarding workflows.
    
    Demonstrates step-by-step process tracking
    with conditional logic and personalization.
    """
    # Conversation and interaction
    messages: Annotated[List, add_messages]
    
    # User information collection
    user_profile: Annotated[Optional[UserProfile], merge_user_profile]
    onboarding_responses: Dict[str, Any]
    
    # Process tracking
    completed_steps: List[str]
    current_step: str
    available_next_steps: List[str]
    
    # Personalization
    user_preferences: Dict[str, Any]
    recommended_features: List[str]
    customization_options: Dict[str, Any]
    
    # Verification and setup
    verification_status: Dict[str, bool]  # email, phone, identity, etc.
    integration_setup: Dict[str, Any]
    
    # Workflow management
    workflow_metadata: Annotated[Optional[WorkflowMetadata], merge_workflow_metadata]
    onboarding_config: Dict[str, Any]

# ============================================================================
# STATE FACTORY FUNCTIONS
# ============================================================================

def create_document_processing_state(user_profile: UserProfile, config: Dict[str, Any] = None) -> DocumentProcessingState:
    """Create initial state for document processing workflow."""
    workflow_id = f"doc_proc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return DocumentProcessingState(
        messages=[],
        current_document=None,
        processed_documents={},
        workflow_metadata=WorkflowMetadata(
            workflow_id=workflow_id,
            workflow_type="document_processing",
            started_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            current_step="init",
            total_steps=5,
            completed_steps=0
        ),
        processing_log=[],
        user_profile=user_profile,
        processing_config=config or {},
        overall_status=WorkflowStatus.PENDING,
        current_step="awaiting_upload",
        errors=[]
    )

def create_project_management_state(project_name: str, project_description: str, manager: UserProfile) -> ProjectManagementState:
    """Create initial state for project management workflow."""
    project_id = f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    workflow_id = f"pm_{project_id}"
    
    return ProjectManagementState(
        messages=[],
        project_id=project_id,
        project_name=project_name,
        project_description=project_description,
        tasks={},
        task_dependencies={},
        team_members={"manager": manager},
        resource_allocation={},
        project_timeline={},
        progress_metrics={"completion": 0.0, "on_time": 1.0, "quality": 0.0},
        workflow_metadata=WorkflowMetadata(
            workflow_id=workflow_id,
            workflow_type="project_management",
            started_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            current_step="planning",
            total_steps=6,
            completed_steps=0
        ),
        current_phase="initiation",
        approval_chain=[]
    )

def create_onboarding_state(user_email: str) -> OnboardingState:
    """Create initial state for user onboarding workflow."""
    workflow_id = f"onboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return OnboardingState(
        messages=[],
        user_profile=UserProfile(name="", email=user_email, role="new_user"),
        onboarding_responses={},
        completed_steps=[],
        current_step="welcome",
        available_next_steps=["collect_basic_info"],
        user_preferences={},
        recommended_features=[],
        customization_options={},
        verification_status={"email": False, "phone": False, "identity": False},
        integration_setup={},
        workflow_metadata=WorkflowMetadata(
            workflow_id=workflow_id,
            workflow_type="user_onboarding",
            started_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            current_step="welcome",
            total_steps=8,
            completed_steps=0
        ),
        onboarding_config={"skip_optional": False, "fast_track": False}
    )