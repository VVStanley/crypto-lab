#!/usr/bin/env bash
set -eu

if [ "${LIVE_TRADING_CONFIRMED:-}" != "YES" ]; then
  echo "Refusing to start live trading."
  echo "Set LIVE_TRADING_CONFIRMED=YES only after completing the documented research/dry-run gates."
  exit 2
fi

if [ ! -f secrets/binance.json ]; then
  echo "Missing secrets/binance.json"
  echo "Copy configs/secrets.example.json to secrets/binance.json and fill it locally."
  exit 2
fi

if grep -q 'REPLACE_WITH_' secrets/binance.json; then
  echo "secrets/binance.json still contains placeholder credentials."
  exit 2
fi

python3 -m json.tool secrets/binance.json >/dev/null

echo "Starting LIVE Binance Spot bot with the repository's configured capital limits."
docker compose -f compose.yaml -f compose.live.yaml up -d bot
