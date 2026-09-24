"""Application dependency bundle.

Concrete Binance/storage adapters are intentionally absent from Batch 1.
Batch 2 will construct them at the composition root without changing this
application-facing dependency shape.
"""

from __future__ import annotations

from dataclasses import dataclass

from research.orderflow.ports import (
    DepthSnapshotSource,
    MarketDataSource,
    RawEventReader,
    RawEventWriter,
)


@dataclass(frozen=True, slots=True)
class OrderFlowRuntime:
    market_data: MarketDataSource
    depth_snapshots: DepthSnapshotSource
    raw_writer: RawEventWriter
    raw_reader: RawEventReader
