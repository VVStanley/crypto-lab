# Experiment 003 — LiquidityWallPressureV1 Implementation Plan

Status: **ready for chat-driven implementation**

## Working model for implementation

This plan is executed **in this ChatGPT conversation**, not by a separate coding agent.

For each implementation batch:

1. ChatGPT reads the current GitHub repository state and the approved plan.
2. ChatGPT prepares the complete files or exact replacements needed for that batch.
3. The user copies those files into the local repository.
4. The user runs the verification commands supplied for the batch and sends the diff/logs back to ChatGPT.
5. ChatGPT reviews the actual diff and verification output against the batch outcome.
6. Only after review does the user commit and push the batch.
7. The next batch starts from the pushed repository state.

ChatGPT must not assume that a generated file was installed or committed until the user shows the resulting diff/output or the pushed repository reflects it.

Implementation is intentionally grouped into **four substantial batches**. Do not split these into tiny mechanical steps unless a real defect or contradiction requires it.

---

## Verified repository baseline

Current `master` already contains:

- Freqtrade 2026.8 pinned in Compose;
- Binance Spot / BTC-USDT candle research pipeline;
- `TrendBreakoutV1` implementation and robustness tooling;
- `Experiment 001 — TrendBreakoutV1`, finalized as `experiments/001-trend-breakout-btc-4h-final.md`;
- `Experiment 002 — PullbackMeanReversionV1 / BTC-USDT / 1h`, currently design-only;
- no `research/orderflow/` subsystem;
- no strategy catalog under `docs/strategies/`;
- no Parquet/DuckDB/ClickHouse research storage;
- Make targets oriented only around the existing Freqtrade workflow.

Therefore this work is **Experiment 003**, not Experiment 002.

Strategy numbering used by project documentation after this work:

1. `TrendBreakoutV1` — completed historical research baseline;
2. `PullbackMeanReversionV1` — design / not yet tested;
3. `LiquidityWallPressureV1` — order-flow research / data collection;
4. `RandomEntryBreakevenV1` — idea / not yet researched.

---

# Goal

Build a deterministic research subsystem for Binance Spot BTC/USDT Level-2 order-book and trade-flow data that can:

```text
collect public market events
        -> persist trustworthy raw data
        -> reconstruct the local order book
        -> replay the same data offline
        -> identify liquidity-wall campaigns
        -> measure execution/refill/withdrawal/absorption pressure
        -> create versioned analytical datasets
        -> query them with SQL
        -> label future outcomes
        -> produce reproducible research reports
```

The subsystem must place **no trades**.

The purpose of the implementation is to answer one research question:

> When price approaches unusually large opposing visible liquidity, can the interaction between aggressive executed flow, wall depletion/refill, cancellations, price response, and liquidity behind the wall distinguish breakout from rejection better than a simple baseline?

Only after this research produces stable evidence may a separate future plan integrate signals with Freqtrade execution.

---

# Architectural decisions

## Execution ownership

Freqtrade remains the only trading/backtesting/execution owner.

The order-flow subsystem:

- uses public market data only;
- does not require Binance trading credentials;
- does not place/cancel orders;
- does not manage balances or positions;
- does not replace Freqtrade exchange execution.

## Persistence boundary

Use dependency inversion with narrow ports and constructor injection.

Research/domain/application logic must not depend directly on:

- filesystem paths;
- Parquet implementation details;
- DuckDB;
- ClickHouse;
- Binance websocket JSON shapes.

Do **not** create a generic `DatabaseRepository` or universal ORM abstraction.

Use responsibility-specific boundaries such as:

```text
MarketDataSource
DepthSnapshotSource
RawEventWriter
RawEventReader
DerivedDatasetWriter / Reader
Analytics service/adapter where required
```

Concrete adapters are assembled only at the composition root.

## Storage strategy

MVP:

```text
raw exchange events -> compressed immutable files
research datasets   -> Parquet
analytics           -> DuckDB SQL over Parquet
```

Future:

```text
ClickHouse adapter
```

ClickHouse is intentionally **not installed now**.

Migration must be possible by adding/replacing adapters while preserving domain/application logic and stable data contracts.

Even after a future ClickHouse migration, immutable raw event archives may remain the replay/source-of-truth layer.

## Why no MongoDB/NoSQL abstraction

The dominant workload is analytical and time-series oriented: aggregation, filtering, grouping and conditional statistics over event/features data. SQL is the natural research interface. No generic NoSQL layer is required.

## Determinism

The same raw event input + same Git commit + same config must produce the same replayed market state, wall campaigns, features and analytical dataset.

Sequence gaps must never be silently ignored.

---

# Target project shape

Exact module names may be simplified during implementation, but the responsibility boundaries must remain clear.

```text
docs/
├── strategies/
│   ├── README.md
│   ├── 001-trend-breakout-v1.md
│   ├── 002-pullback-mean-reversion-v1.md
│   ├── 003-liquidity-wall-pressure-v1.md
│   └── 004-random-entry-breakeven-v1.md
└── plans/
    └── 003-liquidity-wall-pressure-implementation-plan.md

experiments/
├── 001-trend-breakout-btc-4h-final.md
├── 002-pullback-mean-reversion-btc-1h.md
└── 003-liquidity-wall-pressure.md

research/
└── orderflow/
    ├── domain/
    ├── application/
    ├── ports/
    ├── adapters/
    │   ├── binance/
    │   └── storage/
    └── bootstrap.py

configs/
└── research/
    └── orderflow_btcusdt.json

user_data/
└── orderflow/
    ├── raw/
    ├── derived/
    └── reports/
```

Generated `user_data/orderflow/` content must not be committed.

---

# Batch 1 — Architecture, documentation, contracts and project skeleton

## Purpose

Make the new research subsystem an explicit, coherent part of the project and establish the dependency boundaries before any live market-data collection begins.

This batch should be implemented together. It is not useful to split architecture docs, domain types, ports and DI skeleton into separate commits.

## Required changes

### 1. Update canonical architecture

Update `docs/ARCHITECTURE.md` so that it no longer assumes all research is candle/Freqtrade-only.

Add a research market-data subsystem with these rules:

- Freqtrade retains all trade-execution ownership;
- research-only collectors may ingest public exchange microstructure data unavailable to historical Freqtrade candle backtests;
- raw event data is immutable and replayable;
- live acquisition and offline replay share the same domain reconstruction logic;
- persistence is accessed through narrow ports and constructor DI;
- MVP storage is raw compressed files + Parquet + DuckDB;
- ClickHouse is a future adapter only;
- no PostgreSQL/MongoDB/Redis/Kafka/dashboard is introduced by this experiment;
- public L2 data never implies participant identity or exact individual-order ownership.

Update the architecture change policy so persistence adapters can evolve without transferring execution ownership away from Freqtrade.

### 2. Update repository guidance

Update `AGENTS.md` because its current "new strategy requires exactly three artifacts" rule assumes a Freqtrade strategy.

Keep that rule for executable Freqtrade strategies, but add the exception/boundary for research-only strategies whose first phase may consist of:

- strategy documentation;
- experiment document;
- research subsystem code/data collection;
- no Freqtrade strategy class until evidence justifies execution.

Update stale README/roadmap references where required, including the current Experiment 001 filename and the existence of Experiments 002/003.

Do not broadly rewrite documentation that is still correct.

### 3. Create the strategy catalog

Create `docs/strategies/README.md` as the human-readable index.

It should list:

- `TrendBreakoutV1` — historical research completed; summarize the final conclusion from Experiment 001;
- `PullbackMeanReversionV1` — design / not tested;
- `LiquidityWallPressureV1` — research/data collection;
- `RandomEntryBreakevenV1` — idea / not researched.

Create/update one Russian long-form strategy document per entry. These documents are for human understanding, not experiment logs.

Each strategy document should consistently contain:

```text
Идея простыми словами
Почему это может работать
Как предполагается входить
Как предполагается выходить
Основные риски/где идея может ломаться
Ожидаемая частота
Что уже проверено
Краткая аналитика результатов, если они есть
Что ещё неизвестно
Текущий статус
Связанный experiment
```

`003-liquidity-wall-pressure-v1.md` uses the approved strategy design for this plan.

`004-random-entry-breakeven-v1.md` records only the idea already discussed: random/conditionally random entries, move protective stop to approximately breakeven after favorable movement, then avoid tight trailing so ordinary pullbacks do not prematurely exit the trade. Do not invent performance evidence.

### 4. Create Experiment 003 protocol shell

Create:

```text
experiments/003-liquidity-wall-pressure.md
```

It must record:

- hypothesis;
- Binance Spot / BTC-USDT;
- research-only status;
- no trading credentials;
- research phases;
- reproducibility metadata placeholders;
- data-quality rules;
- future chronological Research/Validation/OOS split requirement;
- outcome horizons to be locked before outcome-driven tuning;
- explicit statement that profitability is unknown.

### 5. Add the order-flow code skeleton

Create only the structure needed by the current plan. Avoid empty decorative layers.

Domain models should cover at minimum:

```text
DepthLevelUpdate
DepthUpdate
AggTrade
OrderBookLevel / OrderBook state representation
WallCandidate / WallCampaign
WallFeatures
WallOutcome
```

Persisted/replayed events must retain where applicable:

```text
symbol
exchange timestamp
local receive timestamp
Binance update/trade identifiers
schema version
```

Use Decimal/integer-safe representations for price/quantity identity where necessary; do not depend on binary-float equality for book price levels.

### 6. Define ports and DI

Define narrow protocols/interfaces for market-data and persistence responsibilities.

Create one composition root (`bootstrap.py` or simpler equivalent) where concrete adapters will be assembled.

Forbidden:

- global DB/storage clients;
- service locator;
- persistence inside domain objects;
- Binance-specific imports in domain logic;
- DuckDB/Parquet/ClickHouse imports in domain/application logic.

### 7. Config and ignore rules

Add a versioned research config such as:

```text
configs/research/orderflow_btcusdt.json
```

It should contain research/runtime parameters, not secrets or DB credentials.

Add `user_data/orderflow/` to generated-data ignore rules.

## Verification

The batch is complete when:

- existing Freqtrade runtime remains unchanged;
- architecture clearly supports both candle-based Freqtrade research and independent public order-flow research;
- Experiment 003 numbering no longer conflicts with existing Experiment 002;
- strategy catalog accurately reflects repository history;
- domain/application modules can be imported without Binance/DuckDB/Parquet/ClickHouse runtime dependencies;
- dependency direction is visible and enforceable;
- no collector, database server or trading behavior has accidentally been introduced.

## Expected repository state after Batch 1

```text
Existing trading lab continues to work exactly as before.

Additionally:
- Strategy catalog exists.
- Experiment 003 is formally defined.
- Order-flow subsystem has stable domain contracts and DI seams.
- Future persistence can be swapped through adapters.
- No market data has been collected yet.
```

## Chat workflow for this batch

ChatGPT should return all new/updated files for Batch 1 as a coherent package.

User installs them locally, then sends:

```bash
git status --short
git diff --check
git diff
```

and runs the existing relevant smoke checks if executable project files were touched.

After review, commit as one architecture/foundation commit.

Suggested commit intent:

```text
research: establish order-flow research architecture
```

---

# Batch 2 — Trustworthy Binance collection, immutable raw storage and deterministic replay

## Purpose

Finish the entire **data integrity path** in one batch:

```text
Binance public streams
        -> normalization
        -> raw persistence
        -> local L2 reconstruction
        -> offline deterministic replay
```

Until this batch is correct, wall detection and analytics have no trustworthy foundation.

## Binance inputs

MVP is only:

```text
Binance Spot
BTC/USDT
btcusdt@depth@100ms
btcusdt@aggTrade
```

Use the REST depth snapshot to initialize/resynchronize the local book according to Binance update-ID sequencing rules.

No API key is required.

## Collector requirements

The Binance adapter must:

- receive diff-depth and aggTrade streams;
- record exchange timestamp and local receive timestamp;
- preserve update IDs/trade IDs;
- buffer depth events while obtaining the initial snapshot;
- align snapshot and stream sequence correctly;
- discard obsolete updates;
- detect sequence gaps;
- reconnect/resynchronize after invalid state;
- expose diagnostics such as event counts, reconnects, gaps, resyncs and event latency;
- normalize exchange payloads before application/domain use;
- never write directly to a concrete storage implementation.

Ordinary unit tests must use fixtures/synthetic events rather than depend on Binance availability.

## Raw storage

Implement the `RawEventWriter/Reader` port with immutable compressed file storage.

Suggested structure:

```text
user_data/orderflow/raw/depth/BTCUSDT/YYYY-MM-DD/HH.*
user_data/orderflow/raw/trades/BTCUSDT/YYYY-MM-DD/HH.*
```

Requirements:

- append-only active segment;
- hourly rotation;
- deterministic/versioned serialization;
- preserve ordering fields and timestamps;
- flush/close safely;
- streaming time-range reader;
- malformed/truncated data detected or surfaced rather than silently ignored;
- no requirement to load an entire day into RAM.

Create reusable storage contract tests so a future ClickHouse adapter can prove equivalent application-facing behavior where appropriate.

## Local order book

Implement one canonical reconstruction algorithm used by both live collection and replay.

Rules:

- depth quantities are absolute Binance level quantities;
- zero quantity removes a price level;
- sequence validity is enforced;
- gaps invalidate the book;
- invalid state requires resync, never guessing;
- expose best bid/ask, mid, spread and bounded side-depth inspection needed by later wall analysis.

## Deterministic replay

Implement offline replay over the stored raw data.

When depth/trade timestamps collide, ordering must use preserved exchange IDs/sequence/receive metadata under one documented deterministic rule.

Replaying the same raw interval twice with the same code/config must produce the same checkpoints/hash/summary.

## Minimal operations

Add enough command/Make support to actually run and inspect this batch, for example:

```text
make orderflow-collect
make orderflow-status
make orderflow-replay DATE=...
make orderflow-check
```

Exact command names may follow repository conventions.

`orderflow-status/check` should expose at least:

- last depth event;
- last trade event;
- sequence gaps;
- reconnect/resync count;
- raw file rotation/state;
- deterministic replay check;
- schema version;
- approximate stored size.

Do not add dashboards or servers.

## Tests

This batch needs meaningful automated coverage around:

```text
message normalization
snapshot alignment
normal depth sequence
duplicate/old depth updates
gap detection/resync
raw append/read/rotation
preserved IDs/timestamps
local-book updates/removals
live/replay reconstruction parity
replay determinism
```

## Verification

Do not run a long collector immediately.

First verify unit/contract tests. Then run a short real public-data smoke collection long enough to demonstrate:

```text
WebSocket connection works
snapshot sync works
raw depth/trade files are produced
no unexpected sequence corruption
replay reads those files
same interval replays deterministically
```

## Expected repository state after Batch 2

```text
The project can record a trustworthy slice of Binance BTC/USDT L2 + aggTrades
and reproduce the same local order book offline from the recorded raw files.

No wall strategy logic exists yet.
No Parquet/DuckDB research dataset exists yet.
No trades can be placed by the subsystem.
```

## Chat workflow for this batch

ChatGPT provides the complete implementation files/patch set for collection + raw storage + replay together.

User installs them and returns:

```text
git diff
unit/contract test output
short collector log
orderflow-status/check output
short replay output
```

ChatGPT reviews data integrity before the batch is committed.

Suggested commit intent:

```text
research: add reproducible Binance order-flow capture
```

---

# Batch 3 — Liquidity-wall campaigns, pressure features and analytical storage

## Purpose

Implement the actual research engine over the now-trustworthy replayed market:

```text
reconstructed L2 + trades
        -> wall campaigns
        -> attack lifecycle
        -> execution/refill/withdrawal estimates
        -> pressure/absorption features
        -> versioned Parquet datasets
        -> DuckDB SQL analysis
```

This batch must remain **future-blind**. It creates features describing the market at/through the event, but does not tune them against future returns.

## Wall candidate definition

Do not use a fixed rule such as `$1m wall`.

Detect anomalous visible levels relative to their local market context using a small predeclared set of measures such as:

```text
level notional
local median level notional
local percentile/rank
share of nearby side depth
distance from mid in bps
```

The initial detector should favor broad research observability rather than optimized profitability.

## Wall campaign lifecycle

One physical market episode must be one campaign rather than hundreds of 100ms samples.

Model states conceptually as:

```text
CANDIDATE
   -> APPROACHING
   -> UNDER_ATTACK
   -> BREAKOUT / REJECTION / DISAPPEARED / EXPIRED
```

Support ASK and BID walls symmetrically at the research level.

Do not use future outcomes to decide whether an observed level qualifies as a wall.

## Pressure features

At minimum derive these families.

### Wall state

```text
initial_notional
peak_notional
current_notional
wall_age
relative_size
```

### Approach

```text
distance_to_wall_bps
approach_velocity
approach_growth_ratio
```

### Execution / liquidity dynamics

```text
executed_against_wall
estimated_refill
estimated_withdrawal
execution_rate
refill_rate
depletion_rate
refill_ratio
wall_depletion
```

`estimated_refill/withdrawal` must be described as estimates from aggregated L2 + trades, never participant-level facts.

### Aggressive flow

```text
aggressive_buy/sell over 1s / 5s / 15s / 60s
trade_flow_imbalance
```

### Price response / absorption

```text
price changes over matching windows
price_move_per_executed_notional
failed_attack_count
```

The key research distinction is:

```text
large aggressive flow + visible depletion + improving price response
vs
large aggressive flow + high refill + weak price response
```

### Surrounding book

```text
multi-level imbalance
opposite-side support
post-wall liquidity
liquidity gap behind wall
spread
```

## Derived storage

Persist derived wall campaigns/features under:

```text
user_data/orderflow/derived/
```

Use versioned Parquet schemas.

Keep durable identity fields such as:

```text
event/campaign id
symbol
wall side/price
start/end timestamps
lifecycle
feature schema version
data-quality validity
```

Future outcome labels are not calculated inside the feature generation path.

## DuckDB

Add DuckDB as the local analytical interface over Parquet.

DuckDB is **not source of truth** and must remain outside domain/application logic.

The architecture must make a later ClickHouse analytical adapter possible without changing detector/feature domain logic.

Do not implement a universal SQL dialect/query builder.

## Analysis commands

Add commands sufficient to:

```text
replay raw interval
build derived wall dataset
query/report wall counts and feature distributions
inspect selected campaigns
```

A simple CLI/text/CSV/Markdown report is sufficient. No dashboard.

## Tests

Use synthetic market episodes for at least:

```text
ordinary level ignored
large relative ASK/BID wall detected
wall grows as price approaches
visible wall depletion
wall refill under execution
wall withdrawal without matching execution
repeated attacks stay one campaign
break/disappear/reject lifecycle transitions
symmetric BID/ASK handling
thin vs dense liquidity behind wall
feature determinism
```

## Verification

Run the detector/features over the short raw sample captured in Batch 2.

At this stage success means:

- events are detected plausibly;
- features can be inspected;
- replay produces identical campaign/features on repeated runs;
- SQL can query Parquet through DuckDB;
- no future-return field influences candidate or feature generation.

Do **not** interpret a few examples as proof of edge.

## Expected repository state after Batch 3

```text
Raw Binance order flow can be deterministically converted into
human-inspectable liquidity-wall campaigns and pressure/absorption features.

The resulting dataset is versioned Parquet and is queryable with DuckDB SQL.
Persistence technology is behind ports/DI.
ClickHouse can later be introduced as an adapter rather than a rewrite.
No future-performance tuning and no trading integration exist yet.
```

## Chat workflow for this batch

ChatGPT provides the complete detector + features + Parquet/DuckDB implementation package.

User installs it and returns:

```text
git diff
test output
orderflow build-dataset output
sample wall report / SQL output
```

ChatGPT reviews the implementation and a few representative campaigns for semantic correctness before commit.

Suggested commit intent:

```text
research: derive liquidity-wall pressure datasets
```

---

# Batch 4 — Outcome labels, reproducible research report and locked Experiment 003 protocol

## Purpose

Complete the research pipeline and freeze how the strategy will be evaluated **before** using outcomes to invent entry rules.

This batch is where future price behavior is introduced, and therefore where research discipline matters most.

## Outcome labeling

Outcome calculation is a separate stage after wall features are fixed.

For each eligible wall campaign/event snapshot record at least:

```text
future_return_5s
future_return_15s
future_return_60s
future_return_5m
max_move_through_wall
max_retreat_from_wall
time_to_first_cross
time_beyond_wall
```

Predeclare simple reporting barriers such as:

```text
5 bps
10 bps
20 bps
```

Do not discover one custom barrier solely because it produces a good historical chart.

## Data-quality rules

- outcomes crossing invalid collector/replay intervals must be excluded or explicitly marked invalid;
- multiple samples from one wall campaign must not be counted as independent walls;
- all reports must show sample sizes;
- Research, Validation and OOS splits must be chronological rather than random row splits.

## Initial report

Produce a reproducible generated report containing at minimum:

```text
valid collection hours
sequence gaps / resyncs
number of wall campaigns
ASK vs BID campaigns
breakout / rejection / unresolved counts
outcome distributions
```

and conditional statistics by at least:

```text
wall relative size
execution pressure
refill ratio
depletion
price response / absorption
post-wall liquidity
```

Report future returns on the predeclared horizons and sample size beside every conditional statistic.

The first report is about **predictive structure**, not PnL.

## Lock Experiment 003 research protocol

Before using report findings to choose actual trade thresholds, update:

```text
experiments/003-liquidity-wall-pressure.md
```

with the observed collection/data-quality facts and freeze:

```text
Git commit
raw schema version
feature schema version
collector start
valid-data start
wall-detector configuration
Research window
Validation window
OOS window
outcome horizons
movement barriers
data-quality exclusions
report artifact paths
```

Initial time guidance:

```text
first ~24h    burn-in / data-quality only
next period   Research
next period   Validation
next period   OOS
```

Do not blindly hardcode 21/14/14 days before observing event frequency. The duration may be adjusted **before outcome-driven strategy tuning**, using only operational facts such as valid hours and event counts. Record why it was chosen.

## End-of-batch decision

At the end of this plan the project does **not** yet automatically trade `LiquidityWallPressureV1`.

Instead we should be able to answer with evidence:

```text
Do wall-pressure features contain a stable short-horizon signal?
Which feature interactions appear promising?
How frequent are valid events?
How large are the subsequent moves?
Is the effect large enough to plausibly survive fees/spread/latency?
Does it persist chronologically outside Research?
```

Only if that evidence is encouraging should a new plan define:

- exact entry rule;
- confirmed-breakout vs anticipatory entry;
- rejection-long behavior around BID walls;
- exit/stop/breakeven rules;
- realistic execution simulation;
- Freqtrade integration/dry-run.

## Verification

The batch is complete when one command sequence can reproducibly take a fixed raw interval to a final report without Binance network access:

```text
raw archive
 -> replay
 -> walls
 -> features
 -> outcomes
 -> Parquet
 -> DuckDB report
```

Repeated execution from the same inputs must reproduce the same derived result (ignoring intentionally variable report metadata such as generation timestamp).

## Expected repository state after Batch 4

```text
Experiment 003 has a complete research laboratory.

The repository can:
- continuously collect BTC/USDT public L2 + trade flow;
- verify collector health/data integrity;
- replay historical captured events deterministically;
- reconstruct the order book;
- detect wall campaigns;
- quantify execution/refill/withdrawal/absorption pressure;
- persist versioned analytical datasets;
- query them using SQL through DuckDB;
- calculate future outcomes separately;
- produce reproducible research reports;
- preserve a migration boundary for future ClickHouse;
- keep all trading execution inside Freqtrade.

It still cannot place a trade from LiquidityWallPressureV1, by design.
```

## Chat workflow for this batch

ChatGPT provides the remaining outcome/report/protocol files and code.

User installs them and returns:

```text
git diff
test output
final reproducibility/report command output
generated report or representative excerpt
```

ChatGPT reviews the complete Experiment 003 research system before commit.

Suggested commit intent:

```text
research: complete liquidity-wall evaluation pipeline
```

---

# Explicitly deferred work

Do not implement as part of these four batches:

- Freqtrade trading strategy for wall signals;
- live/dry-run orders based on wall signals;
- stoploss/take-profit for LiquidityWallPressureV1;
- the RandomEntryBreakeven experiment implementation;
- ML/classifiers;
- automated parameter optimization;
- multi-symbol collection;
- multi-exchange aggregation;
- futures or short execution;
- ClickHouse deployment;
- MongoDB/PostgreSQL/Redis/Kafka;
- web dashboard/control plane;
- participant/whale/market-maker identity inference.

---

# Final Definition of Done

This implementation plan is complete only when the following statement is true:

> From immutable recorded Binance BTC/USDT public market events, the repository can deterministically reconstruct the L2 market, identify and measure liquidity-wall attack campaigns, create versioned analytical datasets, query them with SQL, attach future outcomes in a separate stage, and reproduce an Experiment 003 research report — without trading credentials, without placing orders, and without coupling domain/research logic to DuckDB or any future ClickHouse implementation.

The final technical pipeline is:

```text
Binance public depth + aggTrade
              |
              v
      normalized raw events
              |
              v
 compressed immutable archive
              |
              v
      deterministic replay
              |
              v
       local L2 order book
              |
              v
       wall campaigns
              |
              v
 execution / refill / withdrawal
 absorption / price-response features
              |
              v
      versioned Parquet dataset
              |
              v
        DuckDB SQL analysis
              |
              v
       separate outcome labels
              |
              v
 reproducible Experiment 003 report
```

Future ClickHouse migration should require new/replaced infrastructure adapters and schema migration work, **not** a rewrite of collection orchestration, order-book domain logic, wall detection, feature semantics, or research protocol.
