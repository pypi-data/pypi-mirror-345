"""Raw trade model for storing trade events from various exchanges."""

from sqlalchemy import UniqueConstraint

from .trade_base import TradeBase


class RawTrade(TradeBase):
    """Model for storing raw trade data from various exchanges and chain_ids."""

    __abstract__ = False

    __table_args__ = (
        UniqueConstraint(
            "txn_id",
            "chain_id",
            "wallet_address",
            "event_at",
            "is_buy",
            name="uix_raw_trade_txn_chain_wallet_event_at_is_buy",
        ),
    )

    def __repr__(self) -> str:
        """String representation of the RawTrade."""
        return (
            f"<RawTrade(id={self.id}, "
            f"wallet={self.wallet_address[:8]}..., "
            f"pair={self.token_symbol_pair}, "
            f"is_buy={self.is_buy})"
        )
