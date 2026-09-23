# Crypto Strategy Lab

Minimal research-to-live pipeline for deterministic crypto trading strategies.

The MVP is intentionally narrow:

- Binance Spot only
- BTC/USDT only
- no leverage, futures, shorts, ML or LLM decisions
- Freqtrade is the trading/backtesting engine
- one live strategy at a time
- strategies are Python code versioned in Git
- runtime state is isolated in SQLite
- secrets never enter Git

## Authority

`docs/ARCHITECTURE.md` is the canonical architecture document.

Before changing infrastructure, configuration layout, strategy lifecycle, secret handling, live-trading safety, or runtime isolation, update and review `docs/ARCHITECTURE.md` first.

Coding agents must read `AGENTS.md` before working in this repository.

## First strategy

`TrendBreakoutV1` is a research baseline, not a proven profitable strategy.

It uses:

- 4h candles
- EMA 50 / EMA 200 trend filter
- breakout above the previous 20-candle high
- exit on loss of EMA 50 or bearish EMA regime
- fixed 6% emergency stoploss
- no ROI take-profit

The purpose of V1 is to give the project a simple, explainable strategy with which to validate the research pipeline.

## Quick start

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

Run a backtest:

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

## Live trading

Do not start live mode until the strategy has completed the research gates in `docs/ARCHITECTURE.md`.

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
│   └── ROADMAP.md
├── configs/
│   ├── base.json
│   ├── modes/
│   │   ├── dry-run.json
│   │   └── live.json
│   ├── strategies/
│   │   └── trend_breakout_btc_4h.json
│   └── secrets.example.json
├── experiments/
│   └── 001-trend-breakout-btc-4h.md
├── scripts/
│   ├── backtest.sh
│   ├── download-data.sh
│   ├── live.sh
│   └── strategy-check.sh
├── secrets/                  # ignored by Git
└── user_data/
    ├── strategies/
    │   └── TrendBreakoutV1.py
    ├── data/                 # ignored/generated
    ├── db/                   # ignored/generated
    └── backtest_results/     # ignored/generated
```
