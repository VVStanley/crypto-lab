"""Persistence ports for raw and derived research data."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, Protocol

from research.orderflow.domain import RawMarketRecord, WallCampaign, WallFeatures, WallOutcome


class RawEventWriter(Protocol):
    async def append(self, event: RawMarketRecord) -> None: ...

    async def flush(self) -> None: ...

    async def close(self) -> None: ...


class RawEventReader(Protocol):
    def iter_events(
        self,
        *,
        symbol: str,
        start: datetime,
        end: datetime,
    ) -> Iterable[RawMarketRecord]: ...


class DerivedDatasetWriter(Protocol):
    def write_campaigns(self, campaigns: Iterable[WallCampaign]) -> None: ...

    def write_features(self, features: Iterable[WallFeatures]) -> None: ...

    def write_outcomes(self, outcomes: Iterable[WallOutcome]) -> None: ...


class DerivedDatasetReader(Protocol):
    def iter_campaigns(
        self,
        *,
        symbol: str,
        start: datetime,
        end: datetime,
    ) -> Iterable[WallCampaign]: ...
