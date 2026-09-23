#!/usr/bin/env bash
set -eu

TIMERANGE="${TIMERANGE:-20200101-}"

docker compose run --rm bot backtesting \
  --config /freqtrade/configs/base.json \
  --config /freqtrade/configs/strategies/trend_breakout_btc_4h.json \
  --config /freqtrade/configs/modes/dry-run.json \
  --strategy TrendBreakoutV1 \
  --timerange "$TIMERANGE" \
  --export trades
