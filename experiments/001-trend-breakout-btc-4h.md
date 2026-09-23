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

## Research results

### Baseline backtest

Freqtrade version:

```text
2026.8
```

Timerange:

```text
2018-01-01 — 2022-12-31
```

Result:

- Trades: 62
- Average profit per trade: +4.62%
- Total profit: +57.181 USDT
- Total profit: +190.60%
- Starting balance: 30 USDT
- Final balance: 87.181 USDT
- CAGR: 23.77%
- Win rate: 45.2%
- Profit factor: 3.72
- Expectancy: 0.92
- Best trade: +88.07%
- Worst trade: -6.19%
- Average trade duration: 6 days, 20:19
- Closed-trade max drawdown: 3.87%
- Wallet-balance max drawdown: 19.16%
- Wallet-balance drawdown duration: 197 days, 12:00
- Market change over the same period: +23.29%

The baseline is interesting enough to continue researching, but the result must not be treated as expected future return.

A large winning trade contributed materially to the result, so concentration of profit in the best trades must be checked before promotion.

### Lookahead analysis

The dedicated Freqtrade lookahead-analysis completed successfully on the Research period.

Result:

- Signals checked: 20
- Lookahead bias: No
- Biased entry signals: 0
- Biased exit signals: 0
- Biased indicators: none reported

The analysis uses its own market-order test configuration and enlarged analysis capital so wallet sizing does not prevent bias detection. These settings are test-only and do not change normal backtest, dry-run, or live trading configuration.

### Recursive analysis

Result:

- Indicator lookahead bias: No
- `ema_fast` difference at `startup_candle_count = 220`: -0.001%
- `ema_slow` difference at `startup_candle_count = 220`: -0.657%
- `ema_slow` difference at 399 startup candles: +0.475%
- `ema_slow` difference at 499 startup candles: +0.002%
- `ema_slow` difference at 999 startup candles: 0.000%

The current `startup_candle_count = 220` is enough to run the strategy, but EMA(200) is not yet as stable there as it is with a larger startup window.

This must be reviewed and finalized during the Research stage before opening the Validation window.

## Current research conclusion

TrendBreakoutV1 has passed the initial lookahead-bias checks and produced a positive historical baseline on the predefined Research period.

The strategy is not yet promoted to Validation.

Before Validation:

1. decide whether `startup_candle_count` should be increased for EMA(200) stability;
2. if the strategy runtime changes, rerun the Research baseline and bias checks;
3. inspect trade-result concentration, including dependence on the best few trades;
4. record the final Research-stage decision without using Validation, Out-of-sample, or Final holdout performance for tuning.

Do not inspect later evaluation windows until the Research-stage configuration is finalized.
