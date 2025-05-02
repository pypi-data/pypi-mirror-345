"""Market price model for storing current asset prices in USD."""

from decimal import Decimal
from typing import Optional

from sqlalchemy import Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class MarketPrice(BaseModel):
    """
    Market price model for storing current asset prices in USD.

    This model stores the current market price for assets identified by their symbol.
    It does not track historical prices - each symbol will have only one entry
    that is updated (upserted) when new price data is available.

    Attributes:
        token_symbol: The unique identifier for the token (e.g., "BTC", "ETH", "SOL")
        price_usd: The current price of the token in USD
        source: The source of the price data (e.g., "coinmarketcap", "coingecko")
        market_cap_usd: Optional market capitalization in USD
        volume_24h_usd: Optional 24-hour trading volume in USD
    """

    __abstract__ = False

    # Using symbol as a unique identifier for the token
    token_symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    # Price in USD
    price_usd: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=False
    )
    price_change_24h: Mapped[Decimal] = mapped_column(
        Numeric(precision=36, scale=18), nullable=True
    )
    source: Mapped[str] = mapped_column(String(50), nullable=False)

    # Additional market data (optional)
    market_cap_usd: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=36, scale=18), nullable=True
    )
    volume_24h_usd: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=36, scale=18), nullable=True
    )

    # Ensure each symbol has only one entry
    __table_args__ = (
        UniqueConstraint("token_symbol", name="uix_market_price_token_symbol"),
    )

    def __repr__(self) -> str:
        """String representation of the market price."""
        return f"<MarketPrice(token_symbol={self.token_symbol}, price_usd={self.price_usd}, source={self.source})>"
