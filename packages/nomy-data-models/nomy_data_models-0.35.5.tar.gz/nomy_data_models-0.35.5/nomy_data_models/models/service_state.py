"""ServiceState model for tracking service processing states."""

from typing import Optional

from sqlalchemy import Enum, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel
from .enums import ProcessingState


class ServiceState(BaseModel):
    """Model for tracking service processing states."""

    __abstract__ = False

    # Base identifiers
    service_name: Mapped[str] = mapped_column(
        String(length=100),
        nullable=False,
        primary_key=True,
        comment="Name of the service",
    )
    instance_id: Mapped[str] = mapped_column(
        String(length=100),
        nullable=False,
        primary_key=True,
        comment="Instance identifier for the service run",
    )

    # State tracking
    service_state: Mapped[ProcessingState] = mapped_column(
        Enum(ProcessingState),
        nullable=False,
        default=ProcessingState.PENDING,
        comment="Current state of the service",
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        String(length=1000), nullable=True, comment="Error message if service failed"
    )
    service_result: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, comment="Result data from the service processing"
    )

    def __repr__(self) -> str:
        """String representation of the ServiceState."""
        return (
            f"<ServiceState(service={self.service_name}, "
            f"instance={self.instance_id}, "
            f"state={self.service_state.value})>"
        )
