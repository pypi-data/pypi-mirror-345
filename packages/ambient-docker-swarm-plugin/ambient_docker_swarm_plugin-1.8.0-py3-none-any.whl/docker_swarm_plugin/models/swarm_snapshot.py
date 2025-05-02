import copy
import datetime
from typing import Union

from pydantic import BaseModel, Field, model_validator

from ambient_client_common.models.docker_models import DockerSwarmInfo
from ambient_client_common.utils import logger
from ambient_client_common.utils.consistent_hash import consistent_hash


class DockerSwarmSnapshotCreate(BaseModel):
    """Docker Swarm snapshot model."""

    id: Union[int, None] = None
    data: DockerSwarmInfo
    hash: Union[str, None] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    @model_validator(mode="after")
    def validate_hash(cls, values):
        """Validate the hash of the snapshot."""
        logger.debug("in validate_hash, values: {}", values)
        logger.debug("in validate_hash, type of values: {}", type(values))

        if hasattr(values, "hash") and values.hash:
            # If hash is already provided, skip validation
            logger.debug("Hash already provided, skipping validation")
            return values
        # data = values.get("data")
        data = None
        if isinstance(values, dict):
            data = values.get("data")
        else:
            data = values.data
        if data:
            # Generate a hash for the snapshot data
            logger.debug("Generating hash for data: {}", data)
            values.hash = consistent_hash(data.model_dump_json(indent=4))
        else:
            logger.error("Data is required to generate a hash")
            raise ValueError("Data is required to generate a hash")
        return values

    @model_validator(mode="before")
    def json_load_data_if_string(cls, values):
        """Load data from JSON string if it is a string."""
        logger.debug("in json_load_data_if_string, values: {}", values)
        new_values = {}
        if not isinstance(values, dict):
            new_values = {
                "id": values.id,
                "data": values.data,
                "hash": values.hash,
                "created_at": values.created_at,
            }
            logger.debug("new values: {}", new_values)
        else:
            new_values = copy.deepcopy(values)
        logger.debug("new values: {} [Type: {}]", new_values, type(new_values))
        if isinstance(new_values["data"], str):
            # If data is a string, parse it as JSON
            try:
                new_values["data"] = DockerSwarmInfo.model_validate_json(
                    new_values["data"]
                )
                logger.debug("new values after data parsing: {}", new_values)
            except Exception as e:
                logger.error("Failed to parse data as JSON: {}", e)
                raise ValueError("Failed to parse data as JSON")
        return new_values


class DockerSwarmSnapshot(DockerSwarmSnapshotCreate):
    """Docker Swarm snapshot model with ID."""

    class Config:
        from_attributes = True

    id: int
