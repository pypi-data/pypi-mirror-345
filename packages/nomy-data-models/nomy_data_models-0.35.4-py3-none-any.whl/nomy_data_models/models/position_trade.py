"""Position Trade model represents individual trades linked to a position."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID as PythonUUID

from sqlalchemy import Boolean, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel
from .enums import PositionTradeType

if TYPE_CHECKING:  # pragma: no cover
    from .position import Position
    from .raw_trade import RawTrade
    from .trade_match import TradeMatch


class PositionTrade(BaseModel):
    """Model linking a trade event to a position's lifecycle."""

    __abstract__ = False

    position_id: Mapped[PythonUUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("position.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key linking to the Position table.",
    )

    raw_trade_id: Mapped[PythonUUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("raw_trade.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key linking to the original RawTrade record.",
    )

    raw_trade_txn_id: Mapped[str] = mapped_column(
        String(length=128),
        nullable=False,
        comment="Transaction ID from the referenced RawTrade record.",
    )

    trade_type: Mapped[PositionTradeType] = mapped_column(
        SQLEnum(PositionTradeType, name="position_trade_type_enum", create_type=False),
        nullable=False,
        index=True,
        comment="Indicates if trade opens/increases or closes/decreases the position.",
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=False,
        comment="Base amount of this specific trade event.",
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=False,
        comment="Execution price of this trade event.",
    )
    event_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Timestamp when the trade event occurred.",
    )

    fees_trading: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=True,
        comment="Trading fees associated with this trade, in quote currency.",
    )
    fees_gas: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=True,
        comment="Gas/network fees associated with this trade, in quote currency.",
    )
    fees_total: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=True,
        comment="Total fees (trading + gas + other) for this trade, in quote currency.",
    )

    is_taker: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        nullable=True,
        comment="Flag indicating if the trade was a taker order.",
    )
    extra_data: Mapped[Optional[dict]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Any additional source-specific data for this trade.",
    )

    unmatched_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=False,
        index=True,
        comment="The portion of this trade's amount not yet matched by an opposing trade.",
    )
    is_fully_matched: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="True if unmatched_amount is zero, indicating the trade is fully offset.",
    )

    # --- Relationships ---
    position: Mapped["Position"] = relationship(back_populates="trades")
    raw_trade: Mapped["RawTrade"] = relationship(foreign_keys=[raw_trade_id])

    # Matches where this trade was the opening trade
    opening_matches: Mapped[list["TradeMatch"]] = relationship(
        "TradeMatch",
        foreign_keys="TradeMatch.opening_trade_id",
        back_populates="opening_trade",
        cascade="all, delete-orphan",
    )
    # Matches where this trade was the closing trade
    closing_matches: Mapped[list["TradeMatch"]] = relationship(
        "TradeMatch",
        foreign_keys="TradeMatch.closing_trade_id",
        back_populates="closing_trade",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "position_id",
            "raw_trade_txn_id",
            "event_at",
            "trade_type",
            name="uix_position_trade_position_raw_txn_event_type",
        ),
        Index(
            "ix_position_trade_position_id_type_event_at",
            "position_id",
            "trade_type",
            "event_at",
        ),
        Index(  # Index to find unmatched trades efficiently
            "ix_position_trade_unmatched",
            "position_id",
            "trade_type",
            "is_fully_matched",
            "event_at",
            postgresql_where=(is_fully_matched == False),  # noqa F821 # type: ignore
        ),
    )

    def __repr__(self) -> str:
        """String representation of the PositionTrade."""
        return (
            f"<PositionTrade(id={self.id}, pos_id={self.position_id}, "
            f"type={self.trade_type.value}, amount={self.amount:.4f}, "
            f"price={self.price:.4f}, unmatched={self.unmatched_amount:.4f})>"
        )
