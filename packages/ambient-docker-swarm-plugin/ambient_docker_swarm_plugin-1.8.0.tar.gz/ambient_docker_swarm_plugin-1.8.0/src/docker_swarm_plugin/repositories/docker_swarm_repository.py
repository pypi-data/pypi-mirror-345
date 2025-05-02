from typing import Union

from docker_swarm_plugin.models import events, sql_models, swarm_snapshot
from docker_swarm_plugin.repositories.base_repository import SQLBaseRepository
from sqlalchemy import select, update

from ambient_client_common.utils import logger


class DockerSwarmRepository(SQLBaseRepository):
    async def save_swarm_snapshot(
        self, snapshot: swarm_snapshot.DockerSwarmSnapshotCreate
    ) -> swarm_snapshot.DockerSwarmSnapshot:
        """Save a Docker Swarm snapshot to the database."""
        async with self.get_session() as session:
            new_record = sql_models.SQLDockerSwamSnapshot(
                data=snapshot.data.model_dump_json(indent=4),
                created_at=snapshot.created_at,
                hash=snapshot.hash,
            )
            session.add(new_record)
            await session.commit()
            await session.refresh(new_record)
            return swarm_snapshot.DockerSwarmSnapshot.model_validate(new_record)

    async def get_latest_swarm_snapshot(
        self,
    ) -> Union[swarm_snapshot.DockerSwarmSnapshot, None]:
        """Get the latest Docker Swarm snapshot from the database."""
        async with self.get_session() as session:
            logger.debug("inside session")
            stmt = select(sql_models.SQLDockerSwamSnapshot).order_by(
                sql_models.SQLDockerSwamSnapshot.created_at.desc()
            )
            result = await session.execute(stmt)
            record = result.scalars().first()
            if record:
                logger.debug("record found")
                return swarm_snapshot.DockerSwarmSnapshot.model_validate(record)
            else:
                logger.debug("no record found")
                return None

    async def add_cluster_command_request(
        self, cluster_cmd_request: events.CommandRequestRecordCreate
    ) -> events.CommandRequestRecord:
        """Add a new cluster command request to the database."""
        async with self.get_session() as session:
            new_record = sql_models.SQLCommandRequest(
                data=cluster_cmd_request.data,
                received_at=cluster_cmd_request.received_at,
            )
            session.add(new_record)
            await session.commit()
            await session.refresh(new_record)
            return events.CommandRequestRecord.model_validate(new_record)

    async def add_command_execution(
        self, command_execution: events.CommandExecutionCreate
    ) -> events.CommandExecution:
        """Add a new command execution to the database."""
        async with self.get_session() as session:
            new_record = sql_models.SQLCommandExecution(
                command_request_id=command_execution.id,
                status=command_execution.status,
                execution_start_ts=command_execution.execution_start_ts,
            )
            session.add(new_record)
            await session.commit()
            await session.refresh(new_record)
            return events.CommandExecution.model_validate(new_record)

    async def update_command_execution(self, execution_id: int, **kwargs: dict) -> None:
        """Update an existing command execution in the database."""
        async with self.get_session() as session:
            stmt = (
                update(sql_models.SQLCommandExecution)
                .where(sql_models.SQLCommandExecution.id == execution_id)
                .values(**kwargs)
            )
            await session.execute(stmt)
            await session.commit()

    async def get_command_execution(self, execution_id: int) -> events.CommandExecution:
        """Get a command execution by its ID."""
        async with self.get_session() as session:
            stmt = select(sql_models.SQLCommandExecution).where(
                sql_models.SQLCommandExecution.id == execution_id
            )
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
            if record:
                return events.CommandExecution.model_validate(record)
            else:
                raise ValueError(f"Command execution with ID {execution_id} not found.")
