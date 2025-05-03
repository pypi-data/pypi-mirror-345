from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class Frequency(BaseModel):
    """Schema for task schedule frequency"""
    day: int = Field(..., description="Day of frequency")
    hour: int = Field(..., description="Hour of frequency")
    month: int = Field(..., description="Month of frequency")
    minute: int = Field(..., description="Minute of frequency")

    class Config:
        frozen = True
        strict = True
        populate_by_name = True


class TaskSchedule(BaseModel):
    """Schema for interface task schedule"""
    id: int = Field(..., description="Task schedule ID")
    task_type: str = Field(..., alias="taskType", description="Type of task")
    trigger_type: str = Field(..., alias="triggerType", description="Type of trigger")
    trigger_pattern: str = Field(..., alias="triggerPattern", description="Pattern of trigger")
    timezone: str = Field(..., description="Timezone for the task")
    next_reload: Optional[str] = Field(None, alias="nextReload", description="Next reload time")
    frequency: Frequency = Field(..., description="Frequency settings")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Task variables")
    start_after_preceding_task: Optional[bool] = Field(None, alias="startAfterPrecedingTask", description="Whether to start after preceding task")
    start_after_task_id: Optional[int] = Field(None, alias="startAfterTaskId", description="ID of task to start after")
    last_reload: str = Field(..., alias="lastReload", description="Last reload time")
    last_error_message: str = Field(..., alias="lastErrorMessage", description="Last error message")
    status: str = Field(..., description="Current status")
    disabled: bool = Field(..., description="Whether task is disabled")
    run_instant: bool = Field(..., alias="runInstant", description="Whether to run instantly")
    stopped_by_user: bool = Field(..., alias="stoppedByUser", description="Whether stopped by user")
    stepnr: int = Field(..., description="Step number")
    created_at: str = Field(..., alias="createdAt", description="Creation time")
    updated_at: str = Field(..., alias="updatedAt", description="Last update time")

    @field_validator('last_reload', 'created_at', 'updated_at', 'next_reload')
    def validate_datetime(cls, v: Optional[str]) -> Optional[str]:
        """Validate that the string is a valid ISO format datetime"""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid datetime format: {str(e)}")

    class Config:
        frozen = True
        strict = True
        populate_by_name = True


class Interface(BaseModel):
    """Schema for interface data"""
    id: int = Field(..., description="Interface ID")
    name: str = Field(..., description="Interface name")
    description: str = Field(..., description="Interface description")
    source_systems: List[int] = Field(..., alias="sourceSystems", description="List of source system IDs")
    target_systems: List[int] = Field(..., alias="targetSystems", description="List of target system IDs")
    task_schedule: TaskSchedule = Field(..., alias="taskSchedule", description="Task schedule details")

    class Config:
        frozen = True
        strict = True
        populate_by_name = True


class InterfaceApps(BaseModel):
    """Schema for interface apps configuration"""
    source: str = Field(..., description="Source application name")
    target: str = Field(..., description="Target application name")

    class Config:
        frozen = True
        strict = True
        populate_by_name = True


class InterfaceDetail(BaseModel):
    """Schema for detailed interface information"""
    name: str = Field(..., description="Interface name")
    type: str = Field(..., description="Interface type")
    apps: InterfaceApps = Field(..., description="Interface applications configuration")

    class Config:
        frozen = True
        strict = True
        populate_by_name = True


class MappingValue(BaseModel):
    """Schema for a single mapping value"""
    input: Dict[Any, Any] = Field(..., description="Input mapping key-value pairs")
    output: Dict[Any, Any] = Field(..., description="Output mapping key-value pairs")

    class Config:
        frozen = True
        strict = True
        populate_by_name = True


class MappingItem(BaseModel):
    """Schema for a single mapping configuration"""
    guid: str = Field(..., description="Unique identifier for the mapping")
    name: str = Field(..., description="Name of the mapping")
    values: List[MappingValue] = Field(default_factory=list, description="List of mapping values")
    default_value: Optional[str] = Field(None, alias="defaultValue", description="Default value if no mapping matches")

    class Config:
        frozen = True
        strict = True
        populate_by_name = True


class InterfaceConfig(BaseModel):
    """Schema for interface configuration"""
    mapping: List[Dict[str, Any]] = Field(default_factory=list, description="List of mappings")
    variables: Dict[str, Any] = Field(default_factory=dict, description="Configuration variables")

    class Config:
        frozen = True
        strict = True
        populate_by_name = True


class Schedule(BaseModel):
    """Schema for interface schedule configuration"""
    id: int = Field(..., description="Schedule ID")
    trigger_type: str = Field(..., alias="triggerType", description="Type of trigger")
    trigger_pattern: str = Field(..., alias="triggerPattern", description="Pattern for the trigger")
    timezone: str = Field(..., description="Timezone setting")
    next_reload: Optional[str] = Field(None, alias="nextReload", description="Next scheduled reload time")
    frequency: Frequency = Field(..., description="Frequency settings")
    start_after_preceding_task: Optional[bool] = Field(None, alias="startAfterPrecedingTask", description="Whether to start after preceding task")
    last_reload: str = Field(..., alias="lastReload", description="Last reload time")
    last_error_message: str = Field(..., alias="lastErrorMessage", description="Last error message")

    @field_validator('last_reload', 'next_reload')
    def validate_datetime(cls, v: Optional[str]) -> Optional[str]:
        """Validate that the string is a valid ISO format datetime"""
        if v is None:
            return v
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
            return v
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid datetime format: {str(e)}")

    class Config:
        frozen = True
        strict = True
        populate_by_name = True


class Scope(BaseModel):
    """Schema for interface scope data"""
    live: Optional[Dict[str, Any]] = Field(None, description="Live scope configuration")
    draft: Optional[Dict[str, Any]] = Field(None, description="Draft scope configuration")

    class Config:
        frozen = True
        strict = True
        populate_by_name = True


class DevSettings(BaseModel):
    """Schema for interface dev settings"""
    docker_image: str = Field(..., alias="dockerImage", description="Docker image name")
    sftp_mapping: List[dict] = Field(..., alias="sftpMapping", description="SFTP mapping configuration")
    runfile_path: str = Field(..., alias="runfilePath", description="Path to the runfile")
    stop_is_allowed: bool = Field(..., alias="stopIsAllowed", description="Whether stopping is allowed")

    class Config:
        frozen = True
        strict = True
        populate_by_name = True
