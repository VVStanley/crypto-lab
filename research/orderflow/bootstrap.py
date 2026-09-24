"""Composition root for the order-flow research subsystem.

Batch 1 defines the seam only. Concrete Binance and storage adapters are added
in Batch 2 and must be assembled here rather than imported by domain logic.
"""

from __future__ import annotations

from research.orderflow.application import OrderFlowRuntime
from research.orderflow.ports import (
    DepthSnapshotSource,
    MarketDataSource,
    RawEventReader,
    RawEventWriter,
)


def build_runtime(
    *,
    market_data: MarketDataSource,
    depth_snapshots: DepthSnapshotSource,
    raw_writer: RawEventWriter,
    raw_reader: RawEventReader,
) -> OrderFlowRuntime:
    return OrderFlowRuntime(
        market_data=market_data,
        depth_snapshots=depth_snapshots,
        raw_writer=raw_writer,
        raw_reader=raw_reader,
    )
