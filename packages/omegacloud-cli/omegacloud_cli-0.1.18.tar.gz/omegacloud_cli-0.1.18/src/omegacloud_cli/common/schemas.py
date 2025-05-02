from typing import Dict, List, Optional

from pydantic import BaseModel

from omegacloud_cli.common.enums import (
    AgentStatusEnum,
    JobStatusEnum,
    JobTypeEnum,
    TaskStatusEnum,
)


class StorageDefinitionModel(BaseModel):
    id: str
    name: str


# class RunnerConfigModel(BaseModel):
#     size: str
#     disk_size: int
#     storage: List[str]
#     environment: Dict[str, str]
#     cmd: str


class TaskInitRequestModel(BaseModel):
    size: Optional[str] = None
    disk_size: Optional[int] = None
    storage: Optional[List[str]] = None
    environment: Optional[Dict[str, str]] = None
    services: Optional[Dict[str, Dict[str, str]]] = None
    setup_cmd: Optional[List[str]] = None
    run_cmd: Optional[List[str]] = None
    build_cmd: Optional[List[str]] = None
    schedule: Optional[str] = None
    fixed_agent_id: Optional[str] = None


class AgentInitRequestModel(BaseModel):
    size: str
    disk_size: int
    storage: List[str]
    environment: Dict[str, str]
    services: Optional[Dict[str, Dict[str, str]]] = None
    job_type: JobTypeEnum
    setup_cmd: List[str]
    run_cmd: List[str]
    build_cmd: List[str]
    fixed_name: Optional[str] = None


class AgentSetupRequestModel(BaseModel):
    agent_id: str
    base_job_dir: str
    storage: List[StorageDefinitionModel]


class ExecRequestModel(BaseModel):
    environment: Dict[str, str]
    cmd: str
    ports: Optional[List[int]] = None
    volumes: Optional[Dict[str, str]] = None
    log_queue: Optional[str] = None
    process_queue: Optional[str] = None
    wait: Optional[bool] = False


class TaskStatusResponseModel(BaseModel):
    """Response model for task status operations."""

    # task
    task_id: Optional[str] = None
    task_status: Optional[TaskStatusEnum] = None
    task_schedule: Optional[str] = None
    task_logs: Optional[List[str]] = None

    # job
    job_status: Optional[JobStatusEnum] = None
    job_logs: Optional[List[str]] = None

    # billing
    compute_cost: Optional[float] = None
    storage_cost: Optional[float] = None


class AgentStatusResponseModel(BaseModel):
    """Response model for status operations."""

    # agent
    agent_id: Optional[str] = None
    agent_status: Optional[AgentStatusEnum] = None
    agent_status_text: Optional[str] = None
    agent_logs: Optional[List[str]] = None

    # job
    job_type: Optional[JobTypeEnum] = None
    job_url: Optional[str] = None
    job_status: Optional[JobStatusEnum] = None
    job_logs: Optional[List[str]] = None

    # billing
    compute_cost: Optional[float] = None
    storage_cost: Optional[float] = None


class ComputeOption(BaseModel):
    code: str
    title: str
    description: str
    price_tag: str
    price: float
