"""Trade Match model represents the realized link between opening and closing trades."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from uuid import UUID as PythonUUID

from sqlalchemy import DateTime, ForeignKey, Index, Interval, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:  # pragma: no cover
    from .position import Position
    from .position_trade import PositionTrade


class TradeMatch(BaseModel):
    """Model representing a realized PnL event from matching trades."""

    __abstract__ = False

    position_id: Mapped[PythonUUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("position.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key linking to the Position table.",
    )

    opening_trade_id: Mapped[PythonUUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("position_trade.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key linking to the opening PositionTrade record.",
    )

    closing_trade_id: Mapped[PythonUUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("position_trade.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key linking to the closing PositionTrade record.",
    )

    matched_amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=False,
        comment="The amount of base currency matched in this specific link.",
    )

    entry_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=False,
        comment="Entry price from the opening trade for this matched portion.",
    )
    exit_price: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=False,
        comment="Exit price from the closing trade for this matched portion.",
    )

    pnl: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=False,
        comment="Realized profit or loss in the base currency for this match.",
    )
    pnl_usd: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=False,
        comment="Realized profit or loss in USD (or quote currency) for this match.",
    )

    roi: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=10, scale=6),
        nullable=True,
        comment="Return on Investment for this specific matched portion.",
    )

    holding_duration: Mapped[Optional[timedelta]] = mapped_column(
        Interval, nullable=True, comment="Holding duration as a time interval"
    )

    match_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="Timestamp when this match record was created by the logic.",
    )

    # --- Relationships ---
    position: Mapped["Position"] = relationship(back_populates="matches")

    opening_trade: Mapped["PositionTrade"] = relationship(
        foreign_keys=[opening_trade_id], back_populates="opening_matches"
    )
    closing_trade: Mapped["PositionTrade"] = relationship(
        foreign_keys=[closing_trade_id], back_populates="closing_matches"
    )

    __table_args__ = (
        UniqueConstraint(
            "position_id",
            "opening_trade_id",
            "closing_trade_id",
            name="uix_trade_match_position_opening_closing",
        ),
        Index(
            "ix_trade_match_position_id_created_at", "position_id", "match_created_at"
        ),
    )

    def __repr__(self) -> str:
        """String representation of the TradeMatch."""
        return (
            f"<TradeMatch(id={self.id}, pos_id={self.position_id}, "
            f"open_tid={self.opening_trade_id}, close_tid={self.closing_trade_id}, "
            f"amount={self.matched_amount:.4f}, pnl_usd={self.pnl_usd:.4f})>"
        )
