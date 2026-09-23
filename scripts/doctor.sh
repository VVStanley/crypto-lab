#!/usr/bin/env bash
set -euo pipefail

ok() {
    echo "[OK] $1"
}

fail() {
    echo "[FAIL] $1" >&2
    exit 1
}

echo "== Crypto Strategy Lab doctor =="

docker info >/dev/null 2>&1 \
    && ok "Docker" \
    || fail "Docker is not available"

docker compose version >/dev/null 2>&1 \
    && ok "Docker Compose" \
    || fail "Docker Compose is not available"

docker compose config >/dev/null \
    && ok "Compose config" \
    || fail "Invalid Compose configuration"

docker compose run --rm bot --version >/dev/null \
    && ok "Freqtrade" \
    || fail "Freqtrade container failed"

if docker compose run --rm bot list-strategies 2>&1 | grep -q "TrendBreakoutV1"; then
    ok "TrendBreakoutV1"
else
    fail "TrendBreakoutV1 could not be loaded"
fi

markets="$(
    docker compose run --rm bot \
        list-markets \
        --exchange binance \
        --base BTC \
        --quote USDT \
        --print-list 2>&1
)" || fail "Cannot reach Binance public API"

ok "Binance public API"

echo "$markets" | grep -q "BTC/USDT" \
    && ok "BTC/USDT market" \
    || fail "BTC/USDT is unavailable"

timeframes="$(
    docker compose run --rm bot \
        list-timeframes \
        --exchange binance 2>&1
)" || fail "Cannot retrieve Binance timeframes"

echo "$timeframes" | grep -qw "4h" \
    && ok "4h timeframe" \
    || fail "4h timeframe unavailable"

echo
echo "Environment looks healthy."