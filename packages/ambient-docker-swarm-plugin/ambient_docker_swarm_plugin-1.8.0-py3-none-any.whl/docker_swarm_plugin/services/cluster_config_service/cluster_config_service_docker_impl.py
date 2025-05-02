import asyncio
import datetime
from typing import Awaitable

from ambient_backend_api_client.models.cluster import Cluster
from ambient_backend_api_client.models.create_custer_request import CreateCusterRequest
from ambient_base_plugin.models.message import Message
from ambient_event_bus_client.models.messages import MessageCreate
from docker_swarm_plugin.models import events, swarm_snapshot
from docker_swarm_plugin.repositories.docker_swarm_repository import (
    DockerSwarmRepository,
)
from docker_swarm_plugin.services.cluster_config_service.cluster_config_service import (
    ClusterConfigService,
)
from result import Err, Ok, Result

from ambient_client_common.repositories import backend_api_repo, local_api_repo
from ambient_client_common.repositories.docker_repo import DockerRepo
from ambient_client_common.utils import logger
from ambient_client_common.utils.consistent_hash import consistent_hash

EventHandlerResultType = Result[events.ChangesReport, str]


class DockerClusterConfigService(ClusterConfigService):
    def __init__(
        self, docker_repo: DockerRepo, docker_swarm_repo: DockerSwarmRepository
    ):
        self.docker_repo = docker_repo  # docker client helper
        self.docker_swarm_repo = docker_swarm_repo  # sql repository

    async def run_system_sweep(self, headers: dict, local_headers: dict) -> None:
        logger.info("Running docker swarm system sweep ...")

        # get swarm info
        docker_swarm_info = self.docker_repo.get_swarm_info()
        logger.debug("docker_swarm_info retrieved, grabbing latest snapshot ...")
        latest_snapshot = await self.docker_swarm_repo.get_latest_swarm_snapshot()
        logger.debug(
            "latest snapshot retrieved, checking for changes. Snapshot: {}",
            latest_snapshot,
        )
        if not latest_snapshot:
            logger.info("No previous swarm snapshot found. Creating a new one.")
        else:
            logger.info("Latest swarm snapshot found. Hash: {}", latest_snapshot.hash)

        # hash and compare with previous swarm info
        if latest_snapshot and latest_snapshot.hash == consistent_hash(
            docker_swarm_info.model_dump_json(indent=4)
        ):
            logger.info("No changes detected in the Docker Swarm cluster.")
            return

        # if different, update the database
        new_snapshot = swarm_snapshot.DockerSwarmSnapshotCreate(
            data=docker_swarm_info,
        )
        logger.info("New swarm snapshot created. Hash: {}", new_snapshot.hash)
        await self.docker_swarm_repo.save_swarm_snapshot(new_snapshot)
        logger.debug("Saved swarm snapshot to the database")
        # update the node via the local API
        node = await local_api_repo.get_node(headers=local_headers)
        logger.debug("Node retrieved from local API: {}", node.name)
        logger.debug(
            "Updating node with new swarm info: {}",
            new_snapshot.data.model_dump_json(indent=4),
        )
        await local_api_repo.patch_node(
            node.id,
            {"docker_swarm_info": new_snapshot.data.model_dump_json()},
            headers=local_headers,
        )
        logger.info("Docker Swarm system sweep completed successfully.")

    async def handle_event(
        self, msg: Message, headers: dict, local_headers: dict
    ) -> Result[str, str]:
        """Handle the event message and perform the necessary actions.

        Args:
            msg (Message): Message object containing the event data.
            headers (dict): API headers for interfacing with the backend.
            local_headers (dict): Local headers for interfacing
                with the local (client) API.

        Returns:
            Result[str, str]: Result object indicating
                success or failure of the operation.
        """

        logger.contextualize(topic=msg.topic)
        logger.info("Handling event message. [topic: {}]", msg.topic)

        # parse event message
        cluster_cmd_msg = parse_event_message(msg)
        logger.debug(
            "Parsed event message: {}", cluster_cmd_msg.model_dump_json(indent=4)
        )

        # record event in the database
        cmd_record = events.CommandRequestRecordCreate.from_cluster_command_message(
            cluster_cmd_msg
        )
        request_record = await self.docker_swarm_repo.add_cluster_command_request(
            cmd_record
        )

        logger.contextualize(request_id=request_record.id)
        logger.info("Recorded event in the database")

        # create execution record in the database
        execution_record = await self.docker_swarm_repo.add_command_execution(
            events.CommandExecutionCreate.from_cluster_command_request(request_record)
        )
        logger.contextualize(execution_id=execution_record.id)
        logger.info("Created execution record in the database")

        # get handler for event type
        handler = self.get_handler(
            cluster_cmd_msg.operation, msg.topic.split("/", 1)[-1]
        )
        if not handler:
            err_msg = f"Handler not found for operation: {cluster_cmd_msg.operation}"
            logger.error(err_msg)
            await self.docker_swarm_repo.update_command_execution(
                execution_record.id,
                status=events.Status.FAILURE.value,
                execution_complete_ts=datetime.datetime.now(),
                error=err_msg,
            )
            return Err(err_msg)
        logger.info(
            "Handler found for operation {}: {}",
            cluster_cmd_msg.operation,
            handler.__name__,
        )

        # set status of event in the database as in progress
        await self.docker_swarm_repo.update_command_execution(
            execution_record.id,
            status=events.Status.IN_PROGRESS.value,
        )
        logger.debug("Updated command execution status to IN_PROGRESS")

        # call handler with parsed message and headers
        logger.debug("executing ...")
        try:
            result: EventHandlerResultType = await asyncio.wait_for(
                handler(cluster_cmd_msg, headers),
                timeout=60,
            )
        except asyncio.TimeoutError:
            err_msg = "Event handler timed out"
            logger.error(err_msg)
            await self.docker_swarm_repo.update_command_execution(
                execution_record.id,
                status=events.Status.FAILURE.value,
                execution_complete_ts=datetime.datetime.now(),
                error=err_msg,
            )
            final_cmd_execution = await self.docker_swarm_repo.get_command_execution(
                execution_record.id
            )
            _topic = events.DockerSwarmCommandTopics.CLUSTER_COMMAND_TIMEOUT_TOPIC.value
            await local_api_repo.publish_event(
                MessageCreate(
                    topic=_topic,
                    message=final_cmd_execution.model_dump_json(indent=4),
                ),
                headers=local_headers,
            )
            return Err(err_msg)
        logger.debug("Handler executed.")

        # set status of event in the database as success or failure
        if result.is_err():
            # set status of event in the database as failure
            logger.error("Event handler failed with error: {}", result.unwrap_err())
            await self.docker_swarm_repo.update_command_execution(
                execution_record.id,
                status=events.Status.FAILURE.value,
                execution_complete_ts=datetime.datetime.now(),
                error=result.unwrap_err(),
            )
            return Err(result.unwrap_err())

        changes = result.unwrap()
        logger.debug(
            "Event handler succeeded with changes: {}",
            changes.model_dump_json(indent=4),
        )
        await self.docker_swarm_repo.update_command_execution(
            execution_record.id,
            status=events.Status.SUCCESS.value,
            execution_complete_ts=datetime.datetime.now(),
            changes=changes.model_dump_json(indent=4),
            error=None,
        )

        # publish event via the local API
        msg_create = MessageCreate(
            topic=events.DockerSwarmCommandTopics.CLUSTER_COMMAND_RESULT_TOPIC.value,
            message=changes.model_dump_json(indent=4),
        )
        logger.debug(
            "Publishing event via local API: {}", msg_create.model_dump_json(indent=4)
        )
        await local_api_repo.publish_event(msg_create, headers=local_headers)
        logger.info("Event published via local API")

        # return result of the handler
        success_msg = "Event handled successfully."
        logger.info(success_msg)
        return Ok(success_msg)

    def get_handler(
        self,
        operation_type: events.OperationType,
        topic: events.DockerSwarmCommandTopics,
    ) -> Awaitable[EventHandlerResultType]:
        if topic == events.DockerSwarmCommandTopics.CLUSTER_COMMAND_REQUEST_TOPIC:
            return self.handle_cluster_command
        return None

    async def handle_cluster_command(
        self, msg: Message, headers: dict
    ) -> Result[str, str]:
        """Apply changes to the cluster configuration."""

        cluster_cmd_event = parse_cluster_create_request(msg)
        logger.debug(
            "Parsed cluster create request: {}",
            cluster_cmd_event.model_dump_json(indent=4),
        )

        if cluster_cmd_event.operation == events.OperationType.CREATE:
            if swarm_exists(self.docker_repo):
                success_msg = "Swarm already exists. No changes applied."
                logger.info(success_msg)
                return Ok(success_msg)
            # create a new swarm
            success = init_swarm(self.docker_repo)
            if success:
                return Ok("Swarm created successfully")
            return Err("Failed to create swarm")


def parse_cluster_create_request(msg: Message) -> events.ClusterCreateMessage:
    """Parse the cluster create request message."""
    try:
        cluster_create_msg = events.ClusterCreateMessage.model_validate_json(
            msg.message
        )
        return cluster_create_msg
    except Exception as e:
        logger.error(f"Error parsing cluster create request message: {e}")
        raise e


def swarm_exists(docker_repo: DockerRepo) -> bool:
    """Check if a Docker Swarm cluster exists."""
    try:
        swarm_info = docker_repo.get_swarm_info()
        return swarm_info is not None and swarm_info.Cluster is not None
    except Exception as e:
        logger.error(f"Error checking swarm existence: {e}")
        return False


def init_swarm(docker_repo: DockerRepo) -> Result[str, str]:
    """Initialize a Docker Swarm cluster."""
    try:
        docker_repo.create_cluster(advertise_addr=None)
        return Ok("Swarm initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing swarm: {e}")
        return Err(f"Error initializing swarm: {e}")


def parse_event_message(msg: Message) -> events.CommandMessage:
    """Parse the event message to extract cluster information."""
    try:
        cluster = events.CommandMessage.model_validate_json(msg.message)
        return cluster
    except Exception as e:
        logger.error(f"Error parsing event message: {e}")
        raise e


async def create_online_cluster(
    request: CreateCusterRequest,
    headers: dict,
) -> Cluster:
    """Create a cluster in the backend API."""
    try:
        cluster = await backend_api_repo.create_cluster(
            headers=headers,
            data=request,
        )
        return cluster
    except Exception as e:
        logger.error(f"Error creating cluster: {e}")
        raise e
