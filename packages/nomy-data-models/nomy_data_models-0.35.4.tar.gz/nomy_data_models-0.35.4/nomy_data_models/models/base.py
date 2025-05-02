"""Base model with common audit fields."""

from datetime import datetime
from typing import Any, Dict, Optional, TypeVar
from uuid import UUID as PythonUUID
from uuid import uuid4

from sqlalchemy import DateTime, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from nomy_data_models.utils.string import to_snake_case

T = TypeVar("T", bound="BaseModel")


class Base(DeclarativeBase):
    """Base class for all models."""

    def dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update model from dictionary."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class BaseModel(Base):
    """Base model with common audit fields that all other models will inherit from."""

    __abstract__ = True

    # Automatically convert table names to snake_case
    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        """Generate table name automatically in snake_case."""
        return to_snake_case(cls.__name__)

    # Primary key with UUID
    id: Mapped[PythonUUID] = mapped_column(
        UUID, primary_key=True, default=uuid4, nullable=False
    )

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )

    # Audit trail
    created_by: Mapped[Optional[str]] = mapped_column(String(length=255), nullable=True)
    updated_by: Mapped[Optional[str]] = mapped_column(String(length=255), nullable=True)

    def __repr__(self) -> str:
        """String representation of the base model."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    @classmethod
    def from_dict(cls: type[T], data: Dict[str, Any]) -> T:
        """Create model instance from dictionary."""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})
