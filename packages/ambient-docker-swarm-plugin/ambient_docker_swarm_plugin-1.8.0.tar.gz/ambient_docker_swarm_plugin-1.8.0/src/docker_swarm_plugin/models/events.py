"""Event models for Docker Swarm plugin."""

import datetime
from enum import Enum
from typing import List, Union

from ambient_backend_api_client.models.cluster import Cluster
from pydantic import BaseModel, Field


class OperationType(str, Enum):
    """Operation types for cluster events."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class Status(str, Enum):
    """Status types for cluster events."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILURE = "failure"


class CommandMessage(BaseModel):
    """Message for cluster command events."""

    data: Union[Cluster, None]
    operation: OperationType
    source: str


class ClusterCreateMessage(CommandMessage):
    data: Union[Cluster, None]


class DockerSwarmCommandTopics(str, Enum):
    """Topics for Docker Swarm command events."""

    CLUSTER_COMMAND_REQUEST_TOPIC = "docker_swarm/cluster_command"
    CLUSTER_COMMAND_TIMEOUT_TOPIC = "docker_swarm/cluster_command/timeout"
    CLUSTER_COMMAND_RESULT_TOPIC = "docker_swarm/cluster_command/result"


class CommandRequestRecordCreate(BaseModel):
    """Message for cluster command request events."""

    class Config:
        from_attributes = True

    data: str
    received_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    @classmethod
    def from_cluster_command_message(
        cls, message: CommandMessage
    ) -> "CommandRequestRecordCreate":
        """Convert a ClusterCommandMessage to a ClusterCommandRequestMessage."""
        return cls(
            id=message.cluster.id if message.cluster else 0,
            data="" if not message.cluster else message.cluster.model_dump_json(),
        )


class CommandRequestRecord(CommandRequestRecordCreate):
    id: int


class ChangesReport(BaseModel):
    added: List[dict] = []
    removed: List[dict] = []
    updated: List[dict] = []


class CommandExecutionCreate(BaseModel):
    id: Union[int, None] = None
    command_request_id: int
    status: Status = Field(default=Status.PENDING)
    execution_start_ts: datetime.datetime = Field(default_factory=datetime.datetime.now)
    execution_complete_ts: Union[datetime.datetime, None] = None
    error: Union[str, None] = None
    changes: Union[ChangesReport, None] = None

    @classmethod
    def from_cluster_command_request(
        cls, command_request: CommandRequestRecord
    ) -> "CommandExecutionCreate":
        """Convert a ClusterCommandRequestRecord to a ClusterCommandExecutionCreate."""
        return cls(
            command_request_id=command_request.id,
            status=Status.PENDING,
            execution_start_ts=datetime.datetime.now(),
        )


class CommandExecution(CommandExecutionCreate):
    """Message for cluster command execution events."""

    id: int
    command_request: CommandRequestRecordCreate
