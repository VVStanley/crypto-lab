# Roadmap

The roadmap is directional. `ARCHITECTURE.md` remains authoritative for current MVP constraints.

## Phase 0 — repository baseline

- project structure
- canonical architecture
- first research strategy
- Docker/Freqtrade wiring
- safe config/secrets split

## Phase 1 — research MVP

- download historical BTC/USDT data
- backtest `TrendBreakoutV1`
- define train/out-of-sample windows
- run lookahead and recursive analysis
- record baseline metrics and weaknesses
- decide whether to refine or reject the hypothesis

## Phase 2 — dry-run MVP

- deploy to a small VPS
- run continuously against live Binance market data
- add secure Telegram notifications if useful
- compare dry-run behavior with historical assumptions
- fix operational issues without changing the strategy hypothesis silently

## Phase 3 — first tiny live allocation

- create dedicated restricted Binance API key
- lock key to VPS public IP
- confirm current RUB-to-USDT allocation
- verify current exchange minimums
- enable one strategy with one open position maximum
- monitor execution, fees and state recovery

## Phase 4 — strategy lab expansion (only after MVP proves useful)

First likely extensions:

- standardized experiment result metadata;
- comparison command/report;
- multiple simultaneous dry-run containers;
- additional strategies/pairs;
- automated historical evaluation pipeline.

Only after the number of experiments/runtimes makes files + SQLite operationally painful should we consider:

- FastAPI control plane;
- PostgreSQL experiment/result registry;
- dedicated UI/dashboard;
- automated container lifecycle;
- exchange subaccount-based live isolation;
- portfolio-level risk allocation.
