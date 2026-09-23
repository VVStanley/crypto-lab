# Crypto Strategy Lab — Canonical Architecture

Status: **authoritative for MVP**

This document intentionally fixes the architecture so the project can evolve without repeatedly redesigning its foundations.

## 1. Product goal

Build a reproducible pipeline that lets us:

1. express a trading hypothesis as deterministic strategy code;
2. backtest it on historical data;
3. test for obvious backtest flaws and fragility;
4. run it against the live market with simulated funds;
5. promote one strategy to a very small real-money allocation;
6. add future strategies without changing the execution foundation.

The MVP validates the process before we build a platform around it.

## 2. MVP boundary

MVP supports:

- exchange: Binance;
- market: Spot;
- initial pair: BTC/USDT;
- initial timeframe: 4h;
- execution/backtest engine: Freqtrade;
- packaging/runtime: Docker Compose;
- persistence: one SQLite database per running bot instance;
- strategy language: Python;
- one live strategy at a time;
- dry-run before live;
- Git as the source of truth for strategy versions.

MVP explicitly excludes:

- futures, margin, leverage and shorts;
- custom exchange/order engine;
- automatic portfolio allocator across strategies;
- FastAPI control plane;
- PostgreSQL;
- Redis/queues;
- Kubernetes;
- custom web dashboard;
- ML/LLM trading decisions;
- automatic promotion of strategies to live;
- simultaneous live strategies sharing one wallet.

## 3. Technology decisions

### Freqtrade

Freqtrade owns:

- market data integration used by the bot;
- exchange integration;
- exchange trading filters/minimums;
- order placement/cancellation;
- trade lifecycle;
- stoploss order integration;
- dry-run wallet simulation;
- backtesting;
- runtime trade persistence.

We do not reimplement these responsibilities in MVP.

### Python

Python strategy classes own:

- indicators;
- entry signals;
- exit signals;
- strategy-level stoploss definition;
- explainable signal tags.

Strategies must remain deterministic and reproducible from candle data and configuration.

### Docker Compose

Docker Compose is the deployment mechanism for local dry-run and the first VPS deployment.

No orchestrator is added until running multiple long-lived instances becomes an actual operational problem.

### SQLite

Each bot instance gets its own SQLite database.

SQLite contains runtime/trade state. It is **not** the source of truth for strategy code or experiment definitions.

### Git

Git is the only strategy-version history.

A historical strategy is recovered by checking out the Git commit used for the experiment. We do not store Python source snapshots in a database.

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

Contains runtime allocation/universe settings for one strategy deployment:

- allowed pair(s);
- maximum open trades;
- stake allocation;
- capital cap where applicable.

The strategy's trading logic does not live here.

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

Local/VPS-only, gitignored file containing the Binance API credentials.

Secrets are passed as a final config overlay in live mode.

No secret may appear in:

- strategy Python files;
- tracked config files;
- experiment documents;
- Docker image;
- Git history.

## 5. Strategy source and versioning

Strategies live in:

```text
user_data/strategies/
```

One logical strategy should normally retain one class/file name while it evolves.

Do **not** create files such as:

```text
TrendV1.py
TrendV2.py
TrendFinal.py
TrendFinal2.py
```

merely to preserve old code.

Git preserves old implementations.

A new class/file is justified when the market hypothesis materially changes, rather than when parameters or implementation details change.

For every meaningful research result, record the Git commit in the experiment notes/results before treating the result as evidence.

## 6. Adding a new strategy

Adding a strategy must not require infrastructure changes.

Create:

```text
user_data/strategies/NewStrategy.py
configs/strategies/new-strategy.json
experiments/NNN-new-strategy.md
```

Then run the same research commands used by existing strategies.

A new strategy must define:

- hypothesis;
- pair/market;
- timeframe;
- indicators;
- entry rule;
- exit rule;
- stoploss/risk assumptions;
- why the hypothesis might have an edge;
- intended historical evaluation windows.

Do not add a new service/framework simply because a new strategy was added.

## 7. Research lifecycle

A strategy moves manually through these conceptual states:

```text
research -> backtested -> robust-enough -> dry-run -> live-candidate -> live
                          \-> rejected
```

There is no workflow database in MVP.

The experiment Markdown file records the current state and evidence.

### Required research gates before dry-run

At minimum:

1. backtest on a broad historical period;
2. evaluate on data not used to choose the initial hypothesis/parameters;
3. run Freqtrade `lookahead-analysis`;
4. run Freqtrade `recursive-analysis`;
5. inspect trade count, net result, max drawdown and average trade;
6. verify the result is not dependent on one tiny parameter value;
7. account for fees and realistic execution assumptions.

A positive backtest is not sufficient evidence for live trading.

### Required gate before live

A live candidate must spend a meaningful observation period in dry-run and its behavior must be compared with the assumptions from historical tests.

Promotion is always manual.

## 8. Initial live-risk policy

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

## 9. Binance connectivity and API permissions

### Research/backtest

Public market-data access does not require storing live trading credentials in the repository.

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

Binance currently recommends IP restrictions for API keys, and its Spot API documents that trading permission is not enabled by default.

The deployment must not proceed if the VPS cannot have a stable allowlisted public IP.

## 10. Order/exchange rules

We do not hardcode Binance minimum quantity, notional or precision values.

Exchange rules are dynamic and must be obtained/handled through the exchange integration. Binance exposes current symbol/execution rules via exchange information endpoints, and Freqtrade/its exchange layer is responsible for honoring them.

For live Binance Spot, the configuration uses stoploss-on-exchange so protective stoploss orders are not dependent solely on the bot process remaining alive. This setting must be revalidated against the current Freqtrade/Binance behavior before the first live launch.

## 11. Runtime isolation

### MVP

One long-lived bot instance is run at a time for live trading.

Dry-run and live use separate SQLite files.

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

Before simultaneous live strategies are introduced, design real capital isolation (for example exchange-supported subaccounts where available/appropriate) and a clear allocation model.

That work is outside MVP.

## 12. Monitoring

MVP monitoring is intentionally simple:

- Docker/Freqtrade logs;
- Freqtrade SQLite trade history;
- Freqtrade built-in monitoring/Telegram can be enabled when credentials are configured securely.

Do not introduce a custom dashboard in MVP.

A common comparison report is a future convenience layer over reproducible backtest and dry-run results, not a prerequisite for validating the first strategy.

## 13. Deployment

### Local workstation

Use for:

- strategy development;
- historical data download;
- backtesting;
- lookahead/recursive analysis.

### VPS

Use for long-running dry-run and live trading.

Requirements:

- Linux;
- Docker Engine + Compose plugin;
- stable network;
- correct NTP/system clock;
- fixed public IP for Binance API allowlisting;
- automatic container restart;
- SSH access;
- firewall with no unnecessary public Freqtrade UI/API exposure.

Freqtrade UI/API must not be exposed directly to the public internet in MVP. If later enabled, access it through a private network/VPN or SSH tunnel.

## 14. First strategy: `TrendBreakoutV1`

The first strategy is deliberately simple and explainable.

Hypothesis:

> A breakout above a recent range has a better chance of continuation when the medium-term trend is already above the long-term trend.

Current baseline:

- pair: BTC/USDT;
- timeframe: 4h;
- trend: EMA 50 > EMA 200;
- breakout: close above the highest high of the previous 20 completed candles;
- entry requires positive volume;
- exit on close below EMA 50 or EMA 50 below EMA 200;
- emergency stoploss: 6%;
- no shorting;
- no fixed ROI exit.

These numbers are research hypotheses, not production truths. Parameter changes must be evaluated as experiments rather than silently optimized against all available history.

## 15. Change policy

Architecture changes require updating this document first when they affect any of:

- market type/exchange;
- persistence model;
- strategy/config ownership;
- runtime topology;
- secret management;
- live-risk boundaries;
- execution responsibility;
- promotion workflow;
- technology stack.

A feature request alone is not justification to add infrastructure.

The default decision is to keep MVP architecture unchanged until observed usage demonstrates a concrete limitation.

## 16. Definition of Done for MVP

MVP is complete when we can:

1. add a new Python strategy without changing infrastructure;
2. run repeatable historical tests;
3. run lookahead and recursive analyses;
4. preserve strategy history through Git;
5. run the selected strategy continuously in dry-run;
6. inspect its actions/trades after restart;
7. safely configure Binance credentials outside Git;
8. manually promote one validated strategy to live;
9. constrain first live exposure to the agreed small capital allocation;
10. stop/restart the bot without losing trade state.
