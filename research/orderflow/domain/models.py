"""Stable domain models for order-flow research.

The models deliberately contain no Binance, filesystem, Parquet, DuckDB or
ClickHouse types. Price and quantity identity uses Decimal so later order-book
reconstruction never depends on binary-float equality.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import TypeAlias

SCHEMA_VERSION = 1


class BookSide(str, Enum):
    BID = "bid"
    ASK = "ask"


class AggressorSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class WallState(str, Enum):
    CANDIDATE = "candidate"
    APPROACHING = "approaching"
    UNDER_ATTACK = "under_attack"
    BREAKOUT = "breakout"
    REJECTION = "rejection"
    DISAPPEARED = "disappeared"
    EXPIRED = "expired"


class WallOutcomeKind(str, Enum):
    BREAKOUT = "breakout"
    REJECTION = "rejection"
    DISAPPEARED = "disappeared"
    EXPIRED = "expired"
    UNRESOLVED = "unresolved"


def _require_non_negative(value: Decimal, field_name: str) -> None:
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative")


def _require_positive(value: Decimal, field_name: str) -> None:
    if value <= 0:
        raise ValueError(f"{field_name} must be positive")


@dataclass(frozen=True, slots=True)
class DepthLevelUpdate:
    price: Decimal
    quantity: Decimal

    def __post_init__(self) -> None:
        _require_positive(self.price, "price")
        _require_non_negative(self.quantity, "quantity")


@dataclass(frozen=True, slots=True)
class OrderBookLevel:
    price: Decimal
    quantity: Decimal

    def __post_init__(self) -> None:
        _require_positive(self.price, "price")
        _require_positive(self.quantity, "quantity")

    @property
    def notional(self) -> Decimal:
        return self.price * self.quantity


@dataclass(frozen=True, slots=True)
class DepthSnapshot:
    """REST depth snapshot used to seed or resynchronize the local book.

    Binance Spot `/api/v3/depth` exposes `lastUpdateId`, bids and asks but no
    exchange event timestamp. `received_timestamp_ns` therefore records when
    this process received the snapshot without inventing an exchange time.
    """

    symbol: str
    received_timestamp_ns: int
    last_update_id: int
    bids: tuple[OrderBookLevel, ...]
    asks: tuple[OrderBookLevel, ...]
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol is required")
        if self.last_update_id < 0:
            raise ValueError("last_update_id must be non-negative")


@dataclass(frozen=True, slots=True)
class DepthUpdate:
    symbol: str
    event_timestamp_ms: int
    received_timestamp_ns: int
    first_update_id: int
    final_update_id: int
    bids: tuple[DepthLevelUpdate, ...]
    asks: tuple[DepthLevelUpdate, ...]
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol is required")
        if self.final_update_id < self.first_update_id:
            raise ValueError("final_update_id must be >= first_update_id")


@dataclass(frozen=True, slots=True)
class AggTrade:
    symbol: str
    event_timestamp_ms: int
    trade_timestamp_ms: int
    received_timestamp_ns: int
    aggregate_trade_id: int
    first_trade_id: int
    last_trade_id: int
    price: Decimal
    quantity: Decimal
    buyer_is_maker: bool
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol is required")
        _require_positive(self.price, "price")
        _require_positive(self.quantity, "quantity")
        if self.last_trade_id < self.first_trade_id:
            raise ValueError("last_trade_id must be >= first_trade_id")

    @property
    def aggressor_side(self) -> AggressorSide:
        # Binance's buyer-is-maker flag means the seller was the taker.
        return AggressorSide.SELL if self.buyer_is_maker else AggressorSide.BUY

    @property
    def quote_notional(self) -> Decimal:
        return self.price * self.quantity


StreamEvent: TypeAlias = DepthUpdate | AggTrade
RawMarketRecord: TypeAlias = DepthSnapshot | DepthUpdate | AggTrade


@dataclass(frozen=True, slots=True)
class OrderBookState:
    symbol: str
    event_timestamp_ms: int
    received_timestamp_ns: int
    last_update_id: int
    bids: tuple[OrderBookLevel, ...]
    asks: tuple[OrderBookLevel, ...]
    schema_version: int = SCHEMA_VERSION

    @property
    def best_bid(self) -> OrderBookLevel | None:
        return self.bids[0] if self.bids else None

    @property
    def best_ask(self) -> OrderBookLevel | None:
        return self.asks[0] if self.asks else None

    @property
    def mid_price(self) -> Decimal | None:
        if self.best_bid is None or self.best_ask is None:
            return None
        return (self.best_bid.price + self.best_ask.price) / Decimal("2")


@dataclass(frozen=True, slots=True)
class WallCandidate:
    wall_id: str
    symbol: str
    side: BookSide
    price: Decimal
    detected_timestamp_ms: int
    initial_quantity: Decimal
    initial_notional: Decimal
    relative_size: Decimal
    distance_bps: Decimal
    schema_version: int = SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class WallCampaign:
    wall_id: str
    symbol: str
    side: BookSide
    wall_price: Decimal
    state: WallState
    started_timestamp_ms: int
    updated_timestamp_ms: int
    initial_notional: Decimal
    peak_notional: Decimal
    current_notional: Decimal
    touch_count: int = 0
    schema_version: int = SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class WallFeatures:
    wall_id: str
    measured_timestamp_ms: int
    executed_notional: Decimal
    estimated_refill_notional: Decimal
    estimated_withdrawal_notional: Decimal
    refill_ratio: Decimal | None
    depletion_ratio: Decimal
    execution_rate_per_second: Decimal
    price_response_bps: Decimal
    post_wall_liquidity_notional: Decimal
    trade_flow_imbalance: Decimal
    schema_version: int = SCHEMA_VERSION


@dataclass(frozen=True, slots=True)
class OutcomeObservation:
    horizon_seconds: int
    return_bps: Decimal
    max_favorable_bps: Decimal
    max_adverse_bps: Decimal

    def __post_init__(self) -> None:
        if self.horizon_seconds <= 0:
            raise ValueError("horizon_seconds must be positive")


@dataclass(frozen=True, slots=True)
class WallOutcome:
    wall_id: str
    kind: WallOutcomeKind
    resolved_timestamp_ms: int | None
    observations: tuple[OutcomeObservation, ...]
    schema_version: int = SCHEMA_VERSION
