import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

Base = declarative_base()


class SQLCommandRequest(Base):
    __tablename__ = "command_request_t"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data: Mapped[str] = mapped_column(nullable=False)
    received_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )


class SQLCommandExecution(Base):
    __tablename__ = "command_execution_t"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    command_request_id: Mapped[int] = mapped_column(
        ForeignKey("command_request_t.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(nullable=False)
    execution_start_ts: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
    execution_complete_ts: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    error: Mapped[Optional[str]] = mapped_column(nullable=True)
    changes: Mapped[Optional[str]] = mapped_column(nullable=True)

    command_request: Mapped["SQLCommandRequest"] = relationship(lazy=False)


class SQLDockerSwamSnapshot(Base):
    __tablename__ = "docker_swarm_snapshot_t"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    data: Mapped[str] = mapped_column(nullable=False)
    hash: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
