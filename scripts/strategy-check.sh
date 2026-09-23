#!/usr/bin/env bash
set -eu

TIMERANGE="${TIMERANGE:-20200101-}"

COMMON_ARGS="--config /freqtrade/configs/base.json --config /freqtrade/configs/strategies/trend_breakout_btc_4h.json --config /freqtrade/configs/modes/dry-run.json --strategy TrendBreakoutV1 --timerange $TIMERANGE"

echo "== list-strategies =="
docker compose run --rm bot list-strategies

echo "== lookahead-analysis =="
# shellcheck disable=SC2086
docker compose run --rm bot lookahead-analysis $COMMON_ARGS

echo "== recursive-analysis =="
# shellcheck disable=SC2086
docker compose run --rm bot recursive-analysis $COMMON_ARGS
