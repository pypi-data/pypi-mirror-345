import enum


class JobTypeEnum(str, enum.Enum):
    """Job type enumeration."""

    JOB = "job"
    API = "api"
    LAB = "lab"


class AgentStatusEnum(str, enum.Enum):
    """Agent status enumeration."""

    INIT = "init"
    IDLE = "idle"
    BUSY = "busy"
    DEAD = "dead"


class JobStatusEnum(str, enum.Enum):
    """Job status enumeration."""

    RUNNING = "running"
    STOPPED = "stopped"


class TaskStatusEnum(str, enum.Enum):
    """Task status enumeration."""

    ON = "on"
    OFF = "off"
