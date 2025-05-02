"""WalletState model for tracking wallet data quality and completeness."""

import enum as PythonEnum
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel
from .enums import DataState, SyncState


class WalletState(BaseModel):
    """Model for tracking wallet data quality and completeness state."""

    __abstract__ = False

    __table_args__ = (
        UniqueConstraint("wallet_address", "chain_id", name="uix_wallet_chain_id"),
    )

    # Base identifiers
    wallet_address: Mapped[str] = mapped_column(
        String(length=42),
        nullable=False,
        index=True,
        primary_key=True,
        comment="Wallet address being tracked",
    )
    chain_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
        primary_key=True,
        comment="Blockchain network (e.g., 1, 3)",
    )

    # All Data States stored as JSONB
    data_states: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="All state tracking for various data types (raw_trades, enriched_trades, etc.)",
    )

    sync_state: Mapped[SyncState] = mapped_column(
        SQLEnum(SyncState), nullable=False, comment="Current sync status"
    )

    def __repr__(self) -> str:
        """String representation of the WalletState."""
        return (
            f"<WalletState(wallet={self.wallet_address[:8]}..., "
            f"chain_id={self.chain_id}, "
            f"sync_state={self.sync_state.value})>"
        )
