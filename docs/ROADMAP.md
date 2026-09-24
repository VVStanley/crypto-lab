# Roadmap

The roadmap is directional. `ARCHITECTURE.md` remains authoritative for current MVP constraints.

## Phase 0 — repository baseline

Completed foundations:

- project structure;
- canonical architecture;
- Docker/Freqtrade wiring;
- safe config/secrets split;
- reproducible candle research workflow.

## Phase 1 — strategy research

### Experiment 001 — TrendBreakoutV1

Completed Research -> Validation -> OOS sequence.

Final decision:

```text
REJECT FOR PROMOTION
RETAIN AS BASELINE
```

The experiment remains valuable as the first complete example of the project's research discipline.

### Experiment 002 — PullbackMeanReversionV1

Status:

```text
design — not tested
```

Purpose: test a different, potentially more frequent payoff source than the slow 4h trend-breakout baseline.

### Experiment 003 — LiquidityWallPressureV1

Status:

```text
research architecture / data collection
```

Purpose: test whether Level-2 liquidity-wall pressure, execution, refill/withdrawal, absorption and post-wall liquidity contain a stable breakout/rejection signal.

Implementation sequence:

1. architecture/domain/DI foundation;
2. trustworthy Binance public-data collection + deterministic replay;
3. wall detector/features + Parquet/DuckDB analytics;
4. future-outcome labels + chronological research report.

No trading execution is introduced until the signal survives the research gates.

## Phase 2 — dry-run MVP

After an executable strategy passes historical/recorded-data research gates:

- deploy to a small VPS;
- run continuously against live Binance market data;
- add secure Telegram notifications if useful;
- compare dry-run behavior with historical assumptions;
- fix operational issues without silently changing the strategy hypothesis.

## Phase 3 — first tiny live allocation

- create dedicated restricted Binance API key;
- lock key to VPS public IP;
- confirm current RUB-to-USDT allocation;
- verify current exchange minimums;
- enable one strategy with one open position maximum;
- monitor execution, fees and state recovery.

## Phase 4 — strategy lab expansion (only after observed need)

Possible extensions:

- standardized experiment result metadata;
- comparison command/report;
- multiple simultaneous dry-run containers;
- additional strategies/pairs;
- automated historical evaluation pipeline.

If order-flow data volume eventually makes local Parquet + DuckDB operationally limiting, add a ClickHouse storage/analytics adapter behind the existing ports. Do not migrate merely because ClickHouse is available.

Only after actual usage makes the current architecture painful should we consider:

- FastAPI control plane;
- PostgreSQL experiment/result registry;
- ClickHouse deployment;
- dedicated UI/dashboard;
- automated container lifecycle;
- exchange subaccount-based live isolation;
- portfolio-level risk allocation.
