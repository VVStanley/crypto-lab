from __future__ import annotations

import unittest
from decimal import Decimal

from research.orderflow.bootstrap import build_runtime
from research.orderflow.domain import (
    AggTrade,
    AggressorSide,
    DepthLevelUpdate,
    DepthSnapshot,
    OrderBookLevel,
    OrderBookState,
)


class _FakeMarketData:
    async def _events(self):
        if False:
            yield None

    def stream_events(self):
        return self._events()


class _FakeSnapshotSource:
    async def get_depth_snapshot(self, symbol: str) -> DepthSnapshot:
        return DepthSnapshot(
            symbol=symbol,
            received_timestamp_ns=1,
            last_update_id=1,
            bids=(OrderBookLevel(Decimal("100"), Decimal("1")),),
            asks=(OrderBookLevel(Decimal("101"), Decimal("1")),),
        )


class _FakeWriter:
    async def append(self, event) -> None:
        return None

    async def flush(self) -> None:
        return None

    async def close(self) -> None:
        return None


class _FakeReader:
    def iter_events(self, *, symbol, start, end):
        return iter(())


class OrderFlowFoundationTest(unittest.TestCase):
    def test_agg_trade_preserves_exchange_times_and_derives_side(self) -> None:
        trade = AggTrade(
            symbol="BTCUSDT",
            event_timestamp_ms=1,
            trade_timestamp_ms=2,
            received_timestamp_ns=3,
            aggregate_trade_id=4,
            first_trade_id=5,
            last_trade_id=5,
            price=Decimal("100.50"),
            quantity=Decimal("2"),
            buyer_is_maker=False,
        )

        self.assertEqual(1, trade.event_timestamp_ms)
        self.assertEqual(2, trade.trade_timestamp_ms)
        self.assertEqual(AggressorSide.BUY, trade.aggressor_side)
        self.assertEqual(Decimal("201.00"), trade.quote_notional)

    def test_depth_snapshot_does_not_invent_exchange_timestamp(self) -> None:
        snapshot = DepthSnapshot(
            symbol="BTCUSDT",
            received_timestamp_ns=123,
            last_update_id=456,
            bids=(OrderBookLevel(Decimal("100"), Decimal("1")),),
            asks=(OrderBookLevel(Decimal("101"), Decimal("1")),),
        )

        self.assertEqual(456, snapshot.last_update_id)
        self.assertFalse(hasattr(snapshot, "event_timestamp_ms"))

    def test_zero_depth_quantity_is_valid_removal(self) -> None:
        level = DepthLevelUpdate(price=Decimal("100"), quantity=Decimal("0"))
        self.assertEqual(Decimal("0"), level.quantity)

    def test_order_book_mid_price_uses_decimal(self) -> None:
        state = OrderBookState(
            symbol="BTCUSDT",
            event_timestamp_ms=1,
            received_timestamp_ns=2,
            last_update_id=3,
            bids=(OrderBookLevel(Decimal("100.10"), Decimal("1")),),
            asks=(OrderBookLevel(Decimal("100.30"), Decimal("1")),),
        )

        self.assertEqual(Decimal("100.20"), state.mid_price)

    def test_composition_root_accepts_ports_without_concrete_adapters(self) -> None:
        market_data = _FakeMarketData()
        snapshot_source = _FakeSnapshotSource()
        writer = _FakeWriter()
        reader = _FakeReader()

        runtime = build_runtime(
            market_data=market_data,
            depth_snapshots=snapshot_source,
            raw_writer=writer,
            raw_reader=reader,
        )

        self.assertIs(runtime.market_data, market_data)
        self.assertIs(runtime.depth_snapshots, snapshot_source)
        self.assertIs(runtime.raw_writer, writer)
        self.assertIs(runtime.raw_reader, reader)


if __name__ == "__main__":
    unittest.main()
