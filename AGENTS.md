# Agent instructions

This repository is deliberately small. Do not turn the MVP into a generic trading platform.

## Read first

1. `docs/ARCHITECTURE.md` — canonical architecture and hard constraints.
2. The experiment document directly relevant to the requested change.
3. The strategy/research files and configs directly relevant to the requested change.
4. For Experiment 003, also read `docs/plans/003-liquidity-wall-pressure-implementation-plan.md`.

Do not assume Experiment 001 is the current implementation target merely because it is the first experiment.

## Architecture authority

`docs/ARCHITECTURE.md` is authoritative for:

- supported exchange and market type;
- execution ownership;
- configuration ownership;
- strategy/research ownership and versioning;
- public research-data acquisition;
- persistence boundaries;
- secrets/API permissions;
- backtest/research/dry-run/live promotion rules;
- runtime isolation;
- technology choices;
- MVP/non-MVP boundaries.

If implementation and architecture contradict each other, stop and surface the contradiction. Do not silently invent a new architecture.

## Hard rules

- Spot only. No futures, margin, leverage or shorts in MVP.
- Trading decisions must be deterministic Python logic. No LLM/AI call in the trading loop.
- Freqtrade owns exchange execution, exchange filters, order lifecycle and trading runtime persistence.
- Research-only market-data collectors never place/cancel orders or manage balances/positions.
- Public L2 data must not be described as identifying a whale, market maker or individual order owner.
- Executable Freqtrade strategy code lives under `user_data/strategies/` and is versioned by Git.
- Research subsystem code lives under `research/` and must preserve the dependency boundaries from `docs/ARCHITECTURE.md`.
- Do not create strategy source snapshots in a database.
- Do not put API keys, Telegram tokens or other secrets into tracked files.
- One live strategy at a time during MVP.
- Do not add FastAPI, PostgreSQL, MongoDB, Redis, Kafka, Kubernetes, Prometheus, Grafana, ClickHouse deployment or a custom trading engine without an approved architecture change.
- Do not enable live trading as part of tests or development.
- Any change that increases financial exposure must be explicit and reviewed.

## Adding an executable Freqtrade strategy

When a hypothesis can be honestly implemented/backtested using the existing Freqtrade data model, the usual artifacts are:

1. `user_data/strategies/<StrategyName>.py`
2. `configs/strategies/<strategy-id>.json`
3. `experiments/<NNN>-<strategy-id>.md`

The experiment document must state the hypothesis, market/timeframe, parameters, test windows, risk assumptions and acceptance/rejection evidence.

## Adding a research-only strategy

A hypothesis that requires market data unavailable to the Freqtrade historical candle pipeline may begin without a Freqtrade strategy class.

Its first phase may contain:

- `docs/strategies/<NNN>-<strategy>.md` for the human-readable description;
- `experiments/<NNN>-<strategy>.md` for protocol/evidence;
- `research/<subsystem>/` for deterministic data collection/replay/analysis code;
- `configs/research/` for non-secret research settings.

Do not invent execution rules before the research evidence justifies them.

## Order-flow dependency rules

For `research/orderflow/`:

- domain/application logic must not import Binance payload/client types;
- domain/application logic must not import filesystem, Parquet, DuckDB or ClickHouse adapters;
- persistence/exchange access goes through narrow ports;
- concrete adapters are wired only at the composition root;
- no global database/storage clients or service locator;
- use Decimal/integer-safe price/quantity identity where exact book levels matter;
- sequence gaps must be surfaced, never silently repaired by guessing;
- live collection and offline replay must converge on the same normalized domain events.

Do not copy a strategy file merely to preserve an old version. Git is the version history.
