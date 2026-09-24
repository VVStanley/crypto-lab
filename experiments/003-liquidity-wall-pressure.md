# Experiment 003 — LiquidityWallPressureV1 / BTC-USDT / L2 + aggTrade

Status: **research design / data collection foundation**

## Why this experiment exists

Experiment 001 tested a slow 4h trend-breakout hypothesis and was rejected for promotion after its predefined OOS period produced negative expectancy.

Experiment 002 explores a different candle-based 1h pullback/mean-reversion hypothesis.

Experiment 003 tests a different information source entirely: short-horizon market microstructure visible through the Binance Spot Level-2 order book and executed trade flow.

The goal is not to infer who is trading. Public L2 data does not identify a whale, market maker or individual owner of a price level.

The goal is to measure how unusually large visible liquidity behaves while price approaches and trades against it.

## Hypothesis

> When price approaches unusually large opposing visible liquidity, the probability and magnitude of breakout versus rejection may depend on the interaction between aggressive executed flow, wall depletion/refill, visible-liquidity withdrawal, price response, and the depth available immediately beyond the wall.

This is a hypothesis to test, not an assumption of profitability.

## Market/data boundary

- Exchange: Binance
- Market: Spot
- Symbol: BTC/USDT (`BTCUSDT` on public market-data endpoints)
- Direction for research: both ASK-wall and BID-wall events are measured symmetrically
- Trading direction: none in this experiment
- Trading credentials: none
- Execution: none
- Primary public inputs:
  - diff-depth stream at 100 ms;
  - aggregate trade stream (`aggTrade`);
  - public REST depth snapshot for synchronization/resynchronization.

## Research-only boundary

Experiment 003 does **not**:

- place orders;
- manage positions;
- define a final entry/exit strategy;
- use a Binance trading API key;
- replace Freqtrade execution;
- claim participant identity from the public order book.

Only if the signal survives Research/Validation/OOS evidence will a later experiment/plan define executable trading rules.

## What is a liquidity wall here

A wall is an unusually large **visible aggregated quantity at a price level relative to nearby/current book liquidity**.

It is not assumed to be one order or one participant.

The detector must eventually use relative market context rather than a hardcoded permanent dollar threshold.

Candidate dimensions include:

- level notional;
- local percentile/rank;
- ratio to neighboring levels;
- share of bounded nearby depth;
- distance from current mid-price.

The exact detector parameters are **not yet locked** and must be frozen before outcome-driven tuning.

## Wall lifecycle

A wall is treated as one market campaign/event, not hundreds of independent rows merely because the depth stream updates every 100 ms.

Conceptual states:

```text
CANDIDATE
    -> APPROACHING
    -> UNDER_ATTACK
    -> BREAKOUT / REJECTION / DISAPPEARED / EXPIRED
```

The implementation must avoid counting every micro-update of one wall attack as an independent observation.

## Core feature families

The research should eventually measure at least:

### Wall size and persistence

- initial/peak/current visible notional;
- wall age;
- relative size;
- distance from price;
- number of attacks/touches.

### Execution pressure

- executed notional against the wall;
- execution/depletion rate;
- aggressive BUY/SELL flow over short windows.

### Estimated refill and withdrawal

Depth changes are combined with actual trades to estimate:

- visible liquidity replenishment;
- visible liquidity withdrawal/cancellation.

These values are estimates from aggregated public feeds, not exact order-level attribution.

### Price response / absorption

Compare aggressive flow with actual price movement.

Examples:

```text
large aggressive BUY + strong upward response
```

versus:

```text
large aggressive BUY + almost no upward response
```

The second pattern may indicate absorption/rejection pressure.

### Liquidity behind the wall

Measure the amount/distribution of visible liquidity immediately beyond the wall. A thin region behind a broken wall may behave differently from a dense sequence of additional levels.

## Raw-data integrity rules

Research conclusions are invalid unless the recorded market data can be trusted.

Required rules:

1. preserve Binance update/trade identifiers;
2. preserve exchange timestamp and local receive timestamp;
3. initialize/resynchronize from a public REST depth snapshot;
4. persist every REST depth snapshot actually used to seed/resynchronize the local book;
5. preserve both aggregate-trade event time and trade time, plus local receive time;
6. enforce Binance update sequencing;
7. never silently bridge a sequence gap;
8. mark invalid intervals and resynchronize;
9. store normalized stream events and synchronization snapshots immutably;
10. allow deterministic offline replay from the raw archive without refetching a historical snapshot;
11. version persisted schemas.

## Storage/reproducibility baseline

MVP:

```text
raw stream events + sync snapshots -> immutable compressed files
derived wall/features             -> Parquet
analysis              -> DuckDB SQL
```

Persistence must remain behind narrow ports/DI so future ClickHouse adoption does not rewrite domain/research logic.

Reproducibility metadata for every meaningful result:

```text
Git commit: <commit>
Config: configs/research/orderflow_btcusdt.json
Raw data interval(s): <paths/range>
Raw schema version: <version>
Derived schema version: <version>
Research code version: <commit>
Report artifact: <path>
Conclusion: <keep / revise / reject>
```

## Outcome horizons

Initial forward horizons are locked in the versioned research config before outcome-driven tuning:

```text
5 seconds
15 seconds
60 seconds
300 seconds
```

For each wall event, later labeling may include:

- forward return at each locked horizon;
- maximum favorable move;
- maximum adverse/rejection move;
- time to first cross of the wall;
- time spent beyond the wall.

Changing these horizons after seeing results must be documented as a new research decision, not silently treated as the same baseline.

## Research phases

### Phase A — data-quality burn-in

Purpose: prove collector/replay correctness only.

During burn-in, inspect:

- sequence gaps;
- resyncs;
- reconnects;
- event latency;
- raw file integrity;
- replay determinism;
- book sanity.

Do **not** tune wall detector parameters using future price outcomes during this phase.

### Phase B — Research

After data quality is proven:

1. freeze an initial wall-detector/feature baseline;
2. define a chronological Research window;
3. inspect feature/outcome relationships;
4. compare against simple wall-attack baselines;
5. avoid searching large parameter grids.

### Phase C — Validation

Freeze the Research choices and evaluate on the next chronological unseen interval.

No parameter retuning from Validation performance.

### Phase D — OOS

Evaluate the locked design on a later untouched chronological interval.

Only stable effects that survive this sequence can justify executable-strategy design.

## Evaluation-window policy

Exact dates cannot be fixed until enough proprietary collected L2 history exists.

Once data-quality burn-in is complete and sufficient continuous history has accumulated, record explicit chronological windows here **before** using later windows to tune decisions.

Required shape:

```text
Burn-in:    <date range>  -- data quality only
Research:   <date range>
Validation: <later date range>
OOS:        <later untouched date range>
```

Do not randomly shuffle wall events across train/test periods because adjacent microstructure events are time-dependent.

## Primary research questions

1. How many independent valid wall campaigns occur per day?
2. Do execution/depletion features distinguish future breakout/rejection better than wall size alone?
3. Does refill ratio add information beyond executed flow?
4. Is high aggressive flow with weak price response associated with rejection/absorption?
5. Does thin post-wall liquidity increase movement magnitude after a confirmed break?
6. Are effects symmetric for ASK and BID walls?
7. Are observed effects stable through time?
8. How long does any predictive effect survive?
9. Is the effect large enough to plausibly survive spread, fees, slippage and ordinary VPS latency?

## Baselines

Do not compare only selected successful examples.

At minimum compare candidate feature combinations against:

- all valid wall attacks;
- wall-size-only grouping;
- simple local book imbalance where useful;
- direction/event frequency baseline.

A visually convincing wall sequence is not evidence by itself.

## Promotion criteria

This experiment is not promoted because a chart looks good or because classification accuracy is high.

Evidence must show:

- enough independent events;
- effect size meaningfully different from baseline;
- stability across chronological periods;
- realistic signal lifetime;
- no obvious future-information leakage;
- plausible room after trading costs/latency.

Only then create a separate execution/risk design for a Freqtrade-integrated strategy.

## Current reproducibility baseline

```text
Git commit: to be recorded after Batch 1 is committed
Config: configs/research/orderflow_btcusdt.json
Raw data: none yet
Derived data: none yet
Profitability evidence: none
```

## Current conclusion

```text
RESEARCH DESIGN ONLY
PROFITABILITY UNKNOWN
```

Next implementation milestone: trustworthy Binance public-data collection, immutable raw storage, local order-book reconstruction and deterministic replay.
