# Crypto Strategy Lab — Canonical Architecture

Status: **authoritative for MVP**

This document intentionally fixes the architecture so the project can evolve without repeatedly redesigning its foundations.

## 1. Product goal

Build a reproducible pipeline that lets us:

1. express a trading hypothesis as deterministic strategy/research code;
2. test it on historical or recorded market data appropriate to that hypothesis;
3. test for obvious backtest/research flaws and fragility;
4. run validated executable strategies against the live market with simulated funds;
5. promote one strategy to a very small real-money allocation;
6. add future strategies without changing the execution foundation.

The MVP validates the process before we build a platform around it.

## 2. MVP boundary

MVP supports:

- exchange: Binance;
- market: Spot;
- initial pair: BTC/USDT;
- candle execution/backtest engine: Freqtrade;
- research-only public market-data collectors when a hypothesis needs data Freqtrade candle history cannot reproduce;
- packaging/runtime: Docker Compose for the trading bot;
- Freqtrade runtime persistence: one SQLite database per running bot instance;
- research raw-data archive: immutable compressed files;
- derived analytical datasets: Parquet;
- local analytical SQL: DuckDB;
- strategy/research language: Python;
- one live strategy at a time;
- dry-run before live;
- Git as the source of truth for strategy/research code and experiment definitions.

MVP explicitly excludes:

- futures, margin, leverage and shorts;
- custom exchange/order engine;
- automatic portfolio allocator across strategies;
- FastAPI control plane;
- PostgreSQL;
- MongoDB;
- Redis/queues;
- Kafka;
- Kubernetes;
- custom web dashboard;
- ML/LLM trading decisions;
- automatic promotion of strategies to live;
- simultaneous live strategies sharing one wallet;
- ClickHouse deployment before the research volume demonstrates a concrete need.

## 3. Technology decisions

### Freqtrade

Freqtrade owns all trading execution responsibilities:

- market data integration used by the trading bot;
- exchange integration;
- exchange trading filters/minimums;
- order placement/cancellation;
- trade lifecycle;
- stoploss order integration;
- dry-run wallet simulation;
- candle backtesting;
- runtime trade persistence.

Research-only collectors do **not** replace Freqtrade execution. They may ingest public microstructure data for experiments that cannot be reproduced from OHLCV candles.

### Python

Executable Freqtrade strategy classes own:

- indicators;
- entry signals;
- exit signals;
- strategy-level stoploss definition;
- explainable signal tags.

Research-only Python code may own:

- public market-data normalization;
- deterministic market reconstruction;
- feature extraction;
- event detection;
- outcome labeling;
- reproducible analysis.

No LLM/AI call belongs in a trading or signal-generation loop.

### Docker Compose

Docker Compose is the deployment mechanism for local dry-run and the first VPS deployment of the trading bot.

No orchestrator is added until running multiple long-lived instances becomes an actual operational problem.

Research collectors may be packaged later when long-running collection is needed; that does not transfer execution ownership away from Freqtrade.

### SQLite

Each Freqtrade bot instance gets its own SQLite database.

SQLite contains bot runtime/trade state. It is **not** the source of truth for strategy code, research datasets or experiment definitions.

### Research storage

Order-flow research separates raw evidence from derived analytics.

MVP storage:

```text
raw public exchange events + sync snapshots -> immutable compressed files
derived research datasets                -> Parquet
analytical queries          -> DuckDB SQL over Parquet
```

Raw archives are append-only evidence used for deterministic replay. Every REST depth snapshot actually used to seed or resynchronize the local book must be persisted together with subsequent normalized stream events; otherwise an offline replay would not have the same starting state. Derived datasets may be rebuilt from the raw archive when feature logic changes.

Persistence is accessed through narrow ports and constructor dependency injection. Domain/application logic must not depend directly on filesystem, Parquet, DuckDB or future ClickHouse details.

ClickHouse is a future infrastructure adapter, not a current dependency. A future migration must not require rewriting market reconstruction, wall detection, feature semantics or experiment protocol.

Even after a future analytical-database migration, immutable raw archives may remain the replay/source-of-truth layer.

### Git

Git is the source of truth for strategy/research code and experiment definitions.

A historical implementation is recovered by checking out the Git commit used for the experiment. We do not store Python source snapshots in a database.

## 4. Configuration ownership

Configuration is intentionally split by responsibility.

### `configs/base.json`

Contains stable project-wide Freqtrade settings:

- Spot trading mode;
- USDT stake currency;
- Binance exchange selection;
- static pairlist mechanism;
- safe common behavior.

It must not contain secrets or strategy-specific tuning.

### `configs/strategies/*.json`

Contains runtime allocation/universe settings for one executable Freqtrade strategy deployment:

- allowed pair(s);
- maximum open trades;
- stake allocation;
- capital cap where applicable.

The strategy's trading logic does not live here.

### `configs/research/*.json`

Contains versioned, non-secret research runtime settings such as:

- exchange/market/symbol identity;
- public stream names;
- raw/derived output roots;
- serialization/schema version;
- research horizons or detector parameters once they are explicitly locked.

It must not contain API secrets or database credentials.

### `configs/modes/dry-run.json`

Contains mode-specific simulated-money settings:

- `dry_run: true`;
- simulated wallet size;
- dry-run SQLite location.

### `configs/modes/live.json`

Contains live-only safety/runtime settings:

- `dry_run: false`;
- live SQLite location;
- exchange stoploss order policy.

Changing live allocation is a financial-risk change and must be explicit.

### `secrets/binance.json`

Local/VPS-only, gitignored file containing Binance trading API credentials.

Secrets are passed as a final config overlay in live mode.

No secret may appear in:

- strategy Python files;
- research collectors;
- tracked config files;
- experiment documents;
- Docker image;
- Git history.

Public order-flow research must not require trading credentials.

## 5. Strategy source and versioning

Executable Freqtrade strategies live in:

```text
user_data/strategies/
```

Research-only hypotheses may exist before executable strategy code. Their human-readable descriptions live under:

```text
docs/strategies/
```

and their evidence/protocol lives under:

```text
experiments/
```

One logical strategy should normally retain one class/file name while it evolves.

Do **not** create files such as:

```text
TrendV1.py
TrendV2.py
TrendFinal.py
TrendFinal2.py
```

merely to preserve old code. Git preserves old implementations.

A new class/file is justified when the market hypothesis materially changes, rather than when parameters or implementation details change.

For every meaningful research result, record the Git commit in the experiment notes/results before treating the result as evidence.

## 6. Adding a new hypothesis or strategy

### Executable candle/Freqtrade strategy

When the hypothesis can be implemented and honestly backtested with the existing Freqtrade data model, create the executable strategy/config/experiment artifacts and run the standard Freqtrade research gates.

Typical artifacts:

```text
user_data/strategies/NewStrategy.py
configs/strategies/new-strategy.json
experiments/NNN-new-strategy.md
```

### Research-only strategy

When the hypothesis requires market data that Freqtrade historical candles cannot reproduce, it may begin with:

```text
docs/strategies/NNN-strategy.md
experiments/NNN-strategy.md
research/<subsystem>/...
configs/research/...
```

No Freqtrade strategy class should be invented merely to satisfy a file convention before the signal itself has been validated.

A research subsystem is justified only when the required evidence cannot be obtained honestly through the existing pipeline.

## 7. Research lifecycle

An executable strategy moves manually through these conceptual states:

```text
research -> backtested -> robust-enough -> dry-run -> live-candidate -> live
                          \-> rejected
```

A research-only microstructure hypothesis first moves through:

```text
research-design
    -> data-quality proven
    -> research evidence
    -> validation
    -> out-of-sample
    -> executable-strategy design (only if justified)
    -> dry-run/live gates
```

There is no workflow database in MVP. Experiment Markdown files record state and evidence.

### Candle/Freqtrade research gates before dry-run

At minimum:

1. backtest on a broad historical period;
2. evaluate on data not used to choose the initial hypothesis/parameters;
3. run Freqtrade `lookahead-analysis`;
4. run Freqtrade `recursive-analysis`;
5. inspect trade count, net result, max drawdown and average trade;
6. verify the result is not dependent on one tiny parameter value;
7. account for fees and realistic execution assumptions.

### Microstructure/order-flow research gates before executable strategy design

At minimum:

1. prove raw data completeness/sequence integrity;
2. prove deterministic replay;
3. define event/features without future information;
4. lock research parameters/horizons before outcome-driven tuning;
5. use chronological Research/Validation/OOS windows;
6. compare against a simple baseline, not only selected successful examples;
7. measure effect size, stability, event count and latency sensitivity;
8. account for fees, spread and realistic execution before treating a predictive effect as tradeable.

A positive research report is not sufficient evidence for live trading.

### Required gate before live

A live candidate must spend a meaningful observation period in dry-run and its behavior must be compared with the assumptions from historical/recorded-data tests.

Promotion is always manual.

## 8. Research market-data subsystem

The order-flow subsystem introduced for `LiquidityWallPressureV1` is research-only.

It may:

- consume public Binance Spot depth/trade streams;
- obtain public REST depth snapshots for reconstruction;
- normalize exchange payloads into project-owned domain events;
- preserve immutable raw stream events and the synchronization snapshots actually used;
- replay them offline;
- reconstruct a local Level-2 market-by-price book;
- detect/measure research events;
- build versioned derived datasets and reports.

It must not:

- use trading credentials;
- place/cancel orders;
- manage balances/positions;
- bypass Freqtrade execution;
- infer participant identity from public L2 data;
- claim that a visible price level belongs to a whale/market maker/single order.

Public Binance L2 is treated as aggregated visible quantity per price level. Participant identity and exact individual-order ownership are outside the evidence available to this subsystem.

### Dependency direction

Research code follows ports/adapters with constructor injection. Import/dependency direction is:

```text
application -> ports -> domain
adapters    -> ports -> domain
bootstrap   -> application + concrete adapters
```

Domain never imports outward infrastructure. Ports may reference project-owned domain types; application code consumes the ports; adapters implement them.

Domain/application code must not import:

- Binance client libraries or Binance JSON payload types;
- DuckDB;
- Parquet implementation libraries;
- ClickHouse clients;
- concrete filesystem adapters.

Do not create a universal `DatabaseRepository`, service locator or global database/storage singleton. Use narrow responsibility-specific ports.

### Live acquisition and replay

Live acquisition and historical replay must feed the same normalized domain events into the same reconstruction/feature logic.

Sequence gaps are data-quality failures. They must invalidate/resynchronize the affected order book rather than being silently guessed through.

The same raw input + Git commit + locked config must reproduce the same derived result.

## 9. Initial live-risk policy

MVP real-money exposure is intentionally tiny.

Target user budget: approximately **2,000–3,000 RUB equivalent** total capital for the first live experiment.

Runtime trading is denominated in USDT, not RUB. Therefore the exact USDT allocation must be reviewed immediately before live launch using the current conversion rate and Binance minimum order/filter requirements.

The repository starts with conservative example USDT limits. They are not a promise that a given RUB amount will always map to the same USDT value.

Hard MVP limits:

- one live strategy;
- one pair;
- one open trade maximum;
- no leverage;
- no borrowing;
- no futures;
- no automatic capital increase;
- no strategy may override the project into a different market type.

Increasing capital requires an explicit config change and review of accumulated evidence.

## 10. Binance connectivity and API permissions

### Public research/backtest

Public market-data access does not require storing live trading credentials in the repository.

Order-flow collectors must remain on public endpoints unless a future approved architecture change explicitly requires otherwise.

### Live

Use a dedicated API key for the bot.

Required capabilities:

- read account/order information (`USER_DATA`-type access);
- place/cancel Spot orders (`TRADE`).

Security requirements:

- enable only the trading/read permissions required for Spot operation;
- **withdrawals must remain disabled**;
- futures permission disabled;
- borrowing/margin-specific permissions disabled;
- universal transfer permission disabled unless a future architecture explicitly requires it;
- restrict the key to the fixed public IP of the VPS;
- never share the secret in chat, tickets, logs or Git;
- rotate/revoke the key if exposure is suspected.

The deployment must not proceed if the VPS cannot have a stable allowlisted public IP.

## 11. Order/exchange rules

We do not hardcode Binance minimum quantity, notional or precision values for live execution.

Exchange rules are dynamic and must be obtained/handled through the exchange integration. Freqtrade/its exchange layer is responsible for honoring live trading filters.

For live Binance Spot, the configuration uses stoploss-on-exchange so protective stoploss orders are not dependent solely on the bot process remaining alive. This setting must be revalidated against current Freqtrade/Binance behavior before the first live launch.

## 12. Runtime isolation

### MVP trading

One long-lived bot instance is run at a time for live trading.

Dry-run and live use separate SQLite files.

### Research data

Research raw/derived data is separate from Freqtrade runtime SQLite state and is stored under generated `user_data/` paths that are not committed.

### Future multi-strategy dry-run

When simultaneous dry-run comparison becomes useful, each bot instance must have:

- its own container/service;
- its own config overlay;
- its own virtual wallet;
- its own SQLite database;
- its own logs/identity;
- a distinct API/UI port only if API/UI is enabled.

The strategy code/image may be shared.

### Future multi-strategy live

Do not point multiple independent live bots at one undivided Spot balance and pretend the balance is isolated.

Before simultaneous live strategies are introduced, design real capital isolation and a clear allocation model.

That work is outside MVP.

## 13. Monitoring

MVP trading monitoring is intentionally simple:

- Docker/Freqtrade logs;
- Freqtrade SQLite trade history;
- Freqtrade built-in monitoring/Telegram can be enabled when credentials are configured securely.

Research collectors should expose textual/data-quality diagnostics sufficient to identify gaps, resyncs and stale data. Do not introduce a custom dashboard in MVP.

## 14. Deployment

### Local workstation

Use for:

- strategy development;
- historical candle download;
- backtesting;
- lookahead/recursive analysis;
- order-flow replay and analysis;
- short collector/data-quality development runs.

### VPS

Use for:

- long-running dry-run/live Freqtrade bot;
- later long-running public order-flow collection when the collector has passed local data-quality checks.

Requirements for trading remain:

- Linux;
- Docker Engine + Compose plugin;
- stable network;
- correct NTP/system clock;
- fixed public IP for Binance API allowlisting;
- automatic container restart;
- SSH access;
- firewall with no unnecessary public Freqtrade UI/API exposure.

Freqtrade UI/API must not be exposed directly to the public internet in MVP.

## 15. Experiment baselines

### Experiment 001 — `TrendBreakoutV1`

The first strategy was a deliberately simple 4h trend-following baseline using EMA 50/200 plus a 20-candle breakout and a 6% emergency stop.

It passed Research and Validation but failed the predefined OOS gate with negative expectancy/profit factor. It is retained as a comparison baseline and is **rejected for promotion**. See `experiments/001-trend-breakout-btc-4h-final.md`.

### Experiment 002 — `PullbackMeanReversionV1`

A 1h pullback/recovery hypothesis designed to test a different payoff source with potentially more frequent observations. Status: design / not tested. See `experiments/002-pullback-mean-reversion-btc-1h.md`.

### Experiment 003 — `LiquidityWallPressureV1`

A research-only order-flow hypothesis that studies breakout versus rejection around unusually large visible liquidity using depth/trade dynamics. It requires recorded L2 + trade-flow data before an executable trading strategy can be justified. See `experiments/003-liquidity-wall-pressure.md`.

Human-readable strategy summaries live in `docs/strategies/`.

## 16. Change policy

Architecture changes require updating this document first when they affect any of:

- market type/exchange;
- persistence model or persistence ownership;
- strategy/config ownership;
- research data acquisition;
- dependency boundaries;
- runtime topology;
- secret management;
- live-risk boundaries;
- execution responsibility;
- promotion workflow;
- technology stack.

A persistence-adapter change does **not** by itself justify changing domain/application behavior or Freqtrade execution ownership.

A feature request alone is not justification to add infrastructure.

The default decision is to keep the MVP architecture unchanged until observed usage demonstrates a concrete limitation.

## 17. Definition of Done for MVP

MVP is complete when we can:

1. add a new executable Python strategy without changing the trading infrastructure;
2. define a research-only hypothesis without prematurely inventing execution code;
3. run repeatable historical/recorded-data tests appropriate to the hypothesis;
4. preserve strategy/research history through Git;
5. run the selected executable strategy continuously in dry-run;
6. inspect its actions/trades after restart;
7. safely configure Binance trading credentials outside Git;
8. manually promote one validated strategy to live;
9. constrain first live exposure to the agreed small capital allocation;
10. stop/restart the bot without losing trade state;
11. record and deterministically replay public microstructure data when a hypothesis requires it, without coupling research logic to one analytical database.
