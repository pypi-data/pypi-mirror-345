from abc import ABC, abstractmethod

from ambient_base_plugin.models.message import Message
from result import Result


class ClusterConfigService(ABC):
    @abstractmethod
    async def handle_event(
        self, msg: Message, headers: dict, local_headers: dict
    ) -> Result[str, str]:
        """Apply changes to the cluster configuration."""

    @abstractmethod
    async def run_system_sweep(headers: dict, local_headers: dict) -> Result[str, str]:
        """Run a system sweep on the cluster."""
