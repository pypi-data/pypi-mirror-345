from logging import Logger
from typing import Any, Optional, Tuple, Union

from ambient_base_plugin.base_plugin import (
    BasePlugin,
    api_token_manager,
    edge_server_token_manager,
    hookimpl,
)
from ambient_base_plugin.models.configuration import ConfigPayload
from ambient_base_plugin.models.message import Message
from docker import DockerClient
from docker_swarm_plugin.repositories.docker_swarm_repository import (
    DockerSwarmRepository,
)
from docker_swarm_plugin.services.cluster_config_service.cluster_config_service import (
    ClusterConfigService,
)
from docker_swarm_plugin.services.cluster_config_service.cluster_config_service_docker_impl import (  # noqa: E501
    DockerClusterConfigService,
)
from docker_swarm_plugin.services.service_config_service import ServiceConfigSvc
from fastapi import HTTPException

from ambient_client_common.repositories import local_api_repo
from ambient_client_common.repositories.docker_repo import DockerRepo

logger: Optional[Logger] = None


class DockerSwarmPlugin(BasePlugin):
    def __init__(self) -> None:
        self.docker_repo: DockerRepo = DockerRepo(client=DockerClient())
        self.logger: Optional[Logger] = None
        self.docker_swarm_repo: DockerSwarmRepository = DockerSwarmRepository()
        self.cluster_config_service: Optional[ClusterConfigService] = None
        self.service_config_svc: Optional[ServiceConfigSvc] = None
        self.config_payload: Optional[ConfigPayload] = None

    @api_token_manager
    @edge_server_token_manager
    async def get_headers(self, *args, **kwargs) -> Tuple[dict, dict]:
        """Get headers for the plugin."""
        logger.info("In get_headers")
        headers = kwargs.get("headers", {})
        local_headers = kwargs.get("local_headers", {})
        return headers, local_headers

    @hookimpl
    async def run_system_sweep(self) -> None:
        try:
            headers, local_headers = await self.get_headers()
            logger.debug("headers: {}, local_headers: {}", headers, local_headers)
            node = await local_api_repo.get_node(local_headers)
            logger.info("Running system sweep ...")
            await self.cluster_config_service.run_system_sweep(headers, local_headers)
            logger.info("Cluster system sweep completed")
            await self.service_config_svc.run_system_sweep(node)
            logger.info("Service system sweep completed")
        except Exception as e:
            logger.error(f"Error running Docker swarm system sweep: {e}")

    async def configure(
        self, config: ConfigPayload, logger: Union[Logger, Any] = None
    ) -> None:
        self.config_payload = config
        self.set_logger(logger)
        self.cluster_config_service = DockerClusterConfigService(
            docker_repo=self.docker_repo, docker_swarm_repo=self.docker_swarm_repo
        )
        self.service_config_svc = ServiceConfigSvc(
            docker_repo=self.docker_repo, config_payload=config
        )

        logger.info("Configured DockerSwarmPlugin")

    def set_logger(self, logger_: Logger) -> None:
        global logger
        logger = logger_
        self.logger = logger_

    @api_token_manager
    @edge_server_token_manager
    async def handle_event(
        self, message: Message, headers: dict, local_headers: dict, *args, **kwargs
    ) -> None:
        """Handle incoming messages

        Args:
            message (Message): Incoming message

        Returns:
            None
        """
        logger.info("Handling event [from docker swarm plugin handler] ...")
        if "CLUSTER_EVENT" in message.topic:
            return await self.cluster_config_service.handle_event(
                msg=message,
                headers=headers,
                local_headers=local_headers,
            )
        elif "SERVICE_EVENT" in message.topic:
            service_id = int(message.topic.split("/")[-2])
            logger.info(f"Handling service event for service: {service_id}")
            return await self.service_config_svc.handle_service_event(
                service_id=service_id
            )
        else:
            logger.error(f"Unsupported message topic: {message.topic}")

    async def handle_api_request(
        self, method: str, path: str, data: Optional[None] = None
    ) -> Any:
        logger.info("Handling API request ...")
        method = method.lower()
        if method.upper() == "POST" and "onboarding" in path:
            logger.info("Handling onboarding request ...")
            return await self.handle_onboarding_request()
        elif method.upper() == "GET" and "swarm_info" in path:
            return await self.get_swarm_info()
        logger.error("Unsupported method. Method: {}, Path: {}", method, path)
        raise HTTPException(status_code=405, detail="Method not allowed")
