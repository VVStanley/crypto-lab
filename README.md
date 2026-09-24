# Crypto Strategy Lab

Minimal research-to-live pipeline for deterministic crypto trading strategies.

The MVP is intentionally narrow:

- Binance Spot only
- BTC/USDT only
- no leverage, futures, shorts, ML or LLM decisions
- Freqtrade remains the trading/backtesting/execution engine
- one live strategy at a time
- Git is the source of truth for strategy/research code and experiment definitions
- trading runtime state is isolated in SQLite
- research-only collectors may record public market microstructure data when candles are insufficient
- secrets never enter Git

## Authority

`docs/ARCHITECTURE.md` is the canonical architecture document.

Before changing infrastructure, configuration layout, strategy lifecycle, research-data ownership, secret handling, live-trading safety, persistence boundaries or runtime isolation, update and review `docs/ARCHITECTURE.md` first.

Coding agents must read `AGENTS.md` before working in this repository.

## Strategy catalog

Human-readable descriptions and current status live in:

```text
docs/strategies/README.md
```

Current strategy/research catalog:

1. `TrendBreakoutV1` — completed research baseline; rejected for promotion after OOS failure.
2. `PullbackMeanReversionV1` — design / not tested.
3. `LiquidityWallPressureV1` — order-flow research/data collection.
4. `RandomEntryBreakevenV1` — idea / not researched.

Experiment evidence/protocol remains under `experiments/`.

## Existing candle/Freqtrade workflow

Requirements:

- Docker Engine
- Docker Compose plugin (`docker compose`)
- Git

Pull the Freqtrade image:

```bash
make pull
```

Download BTC/USDT 4h candles:

```bash
make download
```

Run the existing TrendBreakout backtest:

```bash
make backtest
```

Run basic strategy safety analyses:

```bash
make strategy-check
```

Start dry-run:

```bash
make dry-run
```

Watch logs:

```bash
make logs
```

Stop the bot:

```bash
make stop
```

## Order-flow research

Experiment 003 introduces a separate **research-only** subsystem under:

```text
research/orderflow/
```

It exists because historical OHLCV candles cannot reconstruct the Level-2 order-book behavior required by `LiquidityWallPressureV1`.

The subsystem is deliberately separated from execution:

```text
public Binance market data
        -> immutable raw archive
        -> deterministic replay
        -> wall/features research
        -> Parquet/DuckDB analytics
```

It does not place orders, use trading credentials or replace Freqtrade.

Batch 1 establishes only the architecture/domain/DI foundation. Binance collection and storage adapters are added in the next implementation batch.

## Live trading

Do not start live mode until the selected executable strategy has completed the research gates in `docs/ARCHITECTURE.md`.

When ready:

1. Create a dedicated Binance API key with the permissions described in `docs/ARCHITECTURE.md`.
2. Restrict the key to the fixed public IP of the VPS.
3. Copy `configs/secrets.example.json` to `secrets/binance.json` and fill it locally.
4. Verify the allocated capital in `configs/modes/live.json` against the current RUB/USDT conversion and exchange minimums.
5. Start with the explicit safety acknowledgement:

```bash
LIVE_TRADING_CONFIRMED=YES make live
```

`secrets/` is gitignored.

## Project layout

```text
.
├── AGENTS.md
├── README.md
├── compose.yaml
├── compose.live.yaml
├── Makefile
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ROADMAP.md
│   ├── plans/
│   │   └── 003-liquidity-wall-pressure-implementation-plan.md
│   └── strategies/
│       ├── README.md
│       ├── 001-trend-breakout-v1.md
│       ├── 002-pullback-mean-reversion-v1.md
│       ├── 003-liquidity-wall-pressure-v1.md
│       └── 004-random-entry-breakeven-v1.md
├── configs/
│   ├── base.json
│   ├── modes/
│   ├── strategies/
│   ├── research/
│   │   └── orderflow_btcusdt.json
│   └── secrets.example.json
├── experiments/
│   ├── 001-trend-breakout-btc-4h-final.md
│   ├── 002-pullback-mean-reversion-btc-1h.md
│   └── 003-liquidity-wall-pressure.md
├── research/
│   └── orderflow/
│       ├── domain/
│       ├── application/
│       ├── ports/
│       └── bootstrap.py
├── scripts/
├── secrets/                  # ignored by Git
└── user_data/
    ├── strategies/
    ├── data/                 # ignored/generated
    ├── db/
    ├── backtest_results/     # ignored/generated
    └── orderflow/            # ignored/generated research data
```
