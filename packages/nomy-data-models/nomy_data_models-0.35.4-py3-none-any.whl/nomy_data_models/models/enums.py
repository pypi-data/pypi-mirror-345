"""Common enums used across multiple models in the Nomy data processing system."""

import enum
from enum import Enum


class MarketType(str, enum.Enum):
    """Enum for different market types."""

    SPOT = "spot"
    PERPETUAL = "perp"


class PositionDirection(str, Enum):
    """Enum for position direction."""

    BUY = "buy"
    SELL = "sell"


class TradeDirection(str, Enum):
    """Enum for trade direction."""

    OPEN_LONG = "open_long"
    OPEN_SHORT = "open_short"
    CLOSE_LONG = "close_long"
    CLOSE_SHORT = "close_short"


class PositionStatus(str, Enum):
    """Enum for position status."""

    OPEN = "open"
    CLOSED = "closed"
    LIQUIDATED = "liquidated"


class PositionTradeType(str, Enum):
    """Enum for position trade type relative to a position."""

    OPENING = "opening"
    CLOSING = "closing"


class DataState(str, enum.Enum):
    """Enum for data quality states."""

    EMPTY = "empty"
    PARTIAL = "partial"
    COMPLETE = "complete"
    ERROR = "error"


class SyncState(str, enum.Enum):
    """Enum for synchronization states."""

    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    FAILED = "failed"


class ProcessingState(str, enum.Enum):
    """Enum for service processing states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
