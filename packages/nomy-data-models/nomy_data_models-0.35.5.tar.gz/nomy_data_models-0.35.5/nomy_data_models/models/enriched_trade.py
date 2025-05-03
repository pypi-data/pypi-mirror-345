"""Enriched trade model extending TradeBase with PnL information."""

from datetime import timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import Index, Interval, Numeric, UniqueConstraint, desc
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .trade_base import TradeBase


class EnrichedTrade(TradeBase):
    """Model for storing enriched trade data with PnL calculations."""

    __abstract__ = False

    __table_args__ = (
        UniqueConstraint(
            "txn_id",
            "chain_id",
            "wallet_address",
            "event_at",
            "is_buy",
            name="uix_enriched_trade_txn_chain_wallet_event_at_is_buy",
        ),
        Index(
            "enriched_trade_idx_wallet_address_chain_id", "wallet_address", "chain_id"
        ),
        Index(
            "ix_enriched_trade_event_at_wallet_chain",
            desc("event_at"),
            "wallet_address",
            "chain_id",
        ),
    )

    # PnL (Profit and Loss) information
    pnl_usd: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=True,
        comment="Profit/Loss in USD for this trade (if part of a matched pair)",
    )

    pnl: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=True,
        comment="Profit/Loss in quote token amount for this trade (if part of a matched pair)",
    )

    roi: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=36, scale=18),
        nullable=True,
        comment="Return on Investment as a decimal (e.g., 0.05 for 5% ROI)",
    )

    holding_duration: Mapped[Optional[timedelta]] = mapped_column(
        Interval, nullable=True, comment="Holding duration as a time interval"
    )

    fee_json: Mapped[Optional[dict]] = mapped_column(
        JSONB, nullable=True, comment="Fee information as a JSONB object"
    )

    def __repr__(self) -> str:
        """String representation of the EnrichedTrade."""
        return (
            f"<EnrichedTrade(id={self.id}, "
            f"wallet={self.wallet_address[:8]}..., "
            f"pair={self.token_symbol_pair}, "
            f"is_buy={self.is_buy}, "
            f"pnl_usd={self.pnl_usd if self.pnl_usd is not None else 'None'})>"
        )
