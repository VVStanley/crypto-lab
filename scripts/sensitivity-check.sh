#!/usr/bin/env bash
set -eu

# This check is intentionally locked to the Experiment 001 Research window.
TIMERANGE="20180101-20230101"

docker compose run --rm bot backtesting \
  --config /freqtrade/configs/base.json \
  --config /freqtrade/configs/strategies/trend_breakout_btc_4h.json \
  --config /freqtrade/configs/modes/dry-run.json \
  --timeframe 4h \
  --strategy-list \
    TrendBreakoutV1 \
    TrendBreakoutV1EmaFast40 \
    TrendBreakoutV1EmaFast60 \
    TrendBreakoutV1EmaSlow180 \
    TrendBreakoutV1EmaSlow220 \
    TrendBreakoutV1Breakout15 \
    TrendBreakoutV1Breakout25 \
  --timerange "$TIMERANGE" \
  --cache none \
  --export trades
