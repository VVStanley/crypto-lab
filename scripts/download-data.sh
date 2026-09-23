#!/usr/bin/env bash
set -eu

DAYS="${DAYS:-3650}"

docker compose run --rm bot download-data \
  --exchange binance \
  --pairs BTC/USDT \
  --timeframes 4h \
  --days "$DAYS"
