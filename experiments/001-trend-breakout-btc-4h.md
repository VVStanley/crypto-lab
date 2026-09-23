# Experiment 001 — TrendBreakoutV1 / BTC-USDT / 4h

Status: **research**

## Hypothesis

A breakout above a recent range may have a higher probability of continuation when the market is already in a positive medium-vs-long-term trend regime.

This is a hypothesis to test, not an assumption of profitability.

## Market

- Exchange: Binance
- Market: Spot
- Pair: BTC/USDT
- Timeframe: 4h
- Direction: long only

## Baseline strategy

Trend regime:

```text
EMA(50) > EMA(200)
```

Entry:

```text
EMA(50) > EMA(200)
AND close > EMA(50)
AND close > max(high of previous 20 completed candles)
AND volume > 0
```

Exit:

```text
close < EMA(50)
OR EMA(50) < EMA(200)
```

Emergency stoploss:

```text
-6%
```

No fixed ROI exit.

## Initial allocation model

Research/dry-run wallet:

```text
30 USDT
```

Maximum open trades:

```text
1
```

Nominal stake per trade:

```text
20 USDT
```

The live amount must be reviewed against the current RUB/USDT conversion immediately before launch. The intended first real-money budget is approximately 2,000–3,000 RUB total, not a permanently fixed USDT number.

## Research protocol

Do not optimize against the entire dataset and then call the same period validation.

Initial work should establish:

1. a broad historical baseline covering multiple market regimes;
2. a separate out-of-sample period;
3. sensitivity around EMA/breakout parameters;
4. Freqtrade lookahead-analysis result;
5. Freqtrade recursive-analysis result;
6. trade count;
7. net result after modeled fees;
8. max drawdown;
9. average trade;
10. whether a few isolated trades dominate the result.

## Promotion rule

Backtest success does not authorize live trading.

Promotion sequence:

```text
research -> historical evidence -> robustness checks -> dry-run -> manual live decision
```

## Reproducibility

When recording a result that influences a decision, add:

```text
Git commit: <commit>
Freqtrade image/version: <version>
Timerange: <range>
Result artifact: <path>
Conclusion: <keep / revise / reject>
```

## Evaluation windows

The historical dataset is split before inspecting strategy performance.

### Research

```text
2018-01-01 — 2022-12-31
```

Used for initial hypothesis evaluation and investigation.

### Validation

```text
2023-01-01 — 2024-12-31
```

Used to validate changes derived from the research period.

### Out-of-sample

```text
2025-01-01 — 2026-06-30
```

Must not be used for parameter tuning.


### Final holdout

```text
2026-07-01 — 2026-09-22
```
Kept untouched until the strategy has passed the previous research gates.