"""Market-data ports.

Adapters may use Binance WebSocket/REST in the next implementation batch, but
application/domain code sees only these normalized contracts.
"""

from __future__ import annotations

from typing import AsyncIterator, Protocol

from research.orderflow.domain import DepthSnapshot, StreamEvent


class MarketDataSource(Protocol):
    def stream_events(self) -> AsyncIterator[StreamEvent]: ...


class DepthSnapshotSource(Protocol):
    async def get_depth_snapshot(self, symbol: str) -> DepthSnapshot: ...
