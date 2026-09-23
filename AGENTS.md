# Agent instructions

This repository is deliberately small. Do not turn the MVP into a generic trading platform.

## Read first

1. `docs/ARCHITECTURE.md` — canonical architecture and hard constraints.
2. `experiments/001-trend-breakout-btc-4h.md` — current research hypothesis.
3. The strategy/config files directly relevant to the requested change.

## Architecture authority

`docs/ARCHITECTURE.md` is authoritative for:

- supported exchange and market type;
- configuration ownership;
- strategy ownership and versioning;
- secrets/API permissions;
- backtest/dry-run/live promotion rules;
- runtime isolation;
- technology choices;
- MVP/non-MVP boundaries.

If implementation and architecture contradict each other, stop and surface the contradiction. Do not silently invent a new architecture.

## Hard rules

- Spot only. No futures, margin, leverage or shorts in MVP.
- Trading decisions must be deterministic Python logic. No LLM/AI call in the trading loop.
- Freqtrade owns exchange execution, exchange filters, order lifecycle and persistence.
- Strategy code lives only under `user_data/strategies/` and is versioned by Git.
- Do not create strategy snapshots in a database.
- Do not put API keys, Telegram tokens or other secrets into tracked files.
- One live strategy at a time during MVP.
- Do not add FastAPI, PostgreSQL, Redis, Kafka, Kubernetes, Prometheus, Grafana or a custom trading engine without an approved architecture change.
- Do not enable live trading as part of tests or development.
- Any change that increases financial exposure must be explicit and reviewed.

## Adding a strategy

A new strategy requires exactly three artifacts at MVP stage:

1. `user_data/strategies/<StrategyName>.py`
2. `configs/strategies/<strategy-id>.json`
3. `experiments/<NNN>-<strategy-id>.md`

The experiment document must state the hypothesis, market/timeframe, parameters, test windows, risk assumptions and acceptance/rejection evidence.

Do not copy a strategy file merely to preserve an old version. Git is the version history.
