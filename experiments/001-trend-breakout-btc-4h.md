# Experiment 001 — TrendBreakoutV1 / BTC-USDT / 4h

Status: **research — final robustness gate pending**

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

Startup history:

```text
499 candles
```

`startup_candle_count = 499` is locked for the current Research configuration after recursive-analysis showed materially better EMA(200) initialization stability than 220 candles, while the Research backtest result remained unchanged.

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

Current Research baseline:

```text
Git commit: eb39bb019f8988cff03150a795d1248206665f1f
Freqtrade version: 2026.8
Timerange: 20180101-20230101
Backtest artifact: user_data/backtest_results/backtest-result-2026-09-23_08-22-47.zip
Strategy check log: user_data/logs/experiment-001-strategy-check-499.txt
Conclusion: keep
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

Used to validate the configuration finalized during Research.

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
- Median profit per trade: -0.89%
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

### Lookahead analysis

The dedicated Freqtrade lookahead-analysis completed successfully on the Research period.

Result:

- Signals checked: 20
- Lookahead bias: No
- Biased entry signals: 0
- Biased exit signals: 0
- Biased indicators: none reported

The analysis uses its own market-order test configuration and enlarged analysis capital so wallet sizing does not prevent bias detection. These settings are test-only and do not change normal backtest, dry-run, or live trading configuration.

### Recursive analysis and startup decision

With the original `startup_candle_count = 220`:

- `ema_fast` difference: -0.001%
- `ema_slow` difference: -0.657%

With `startup_candle_count = 499`:

- `ema_fast` difference: approximately 0.000%
- `ema_slow` difference: +0.002%

At 999 and 1999 startup candles, the measured EMA(200) difference was 0.000%.

Decision:

```text
startup_candle_count = 499
```

The Research backtest with 499 candles produced the same 62 trades and the same headline metrics as the 220-candle baseline. Therefore the change improves indicator initialization stability without improving or degrading the observed Research result.

The post-change lookahead-analysis again reported no bias.

### Profit concentration

The strategy is intentionally trend-following, so a right-skewed return distribution is expected: many small losing or modest trades can be offset by occasional large trends.

Observed Research distribution:

- Winning trades: 28
- Losing trades: 34
- Average winning trade: approximately +14.02%
- Average losing trade: approximately -3.11%
- Median trade: approximately -0.89%
- Gross winning profit: +78.224 USDT
- Gross losses: -21.043 USDT

The two largest winners together earned approximately 26.40 USDT, which is greater than the total gross losses over the Research period. This confirms that large winners are an important part of the strategy's edge.

Contribution of the largest winning trades:

| Removed winners | Removed profit | Share of observed net profit | Remaining accounting profit | Remaining result vs 30 USDT start |
| --- | ---: | ---: | ---: | ---: |
| TOP-1 | 17.573 USDT | 30.7% | +39.607 USDT | +132.0% |
| TOP-3 | 33.631 USDT | 58.8% | +23.549 USDT | +78.5% |
| TOP-5 | 46.159 USDT | 80.7% | +11.021 USDT | +36.7% |
| TOP-10 | 66.099 USDT | 115.6% | -8.918 USDT | -29.7% |

These rows are contribution-removal diagnostics, not fully re-simulated counterfactual backtests. Removing earlier profits could alter later stake sizing and therefore the exact path.

The largest five winning trades were approximately:

| Open | Close | Trade return | Profit |
| --- | --- | ---: | ---: |
| 2020-12-12 | 2021-01-11 | +88.07% | +17.573 USDT |
| 2021-02-02 | 2021-02-23 | +44.84% | +8.828 USDT |
| 2019-05-01 | 2019-05-17 | +36.20% | +7.230 USDT |
| 2019-06-12 | 2019-06-27 | +35.20% | +7.029 USDT |
| 2020-11-04 | 2020-11-26 | +27.59% | +5.499 USDT |

Yearly realized profit:

| Year | Trades | Wins | Losses | Profit |
| --- | ---: | ---: | ---: | ---: |
| 2018 | 7 | 3 | 4 | +0.492 USDT |
| 2019 | 15 | 7 | 8 | +14.962 USDT |
| 2020 | 15 | 9 | 6 | +17.400 USDT |
| 2021 | 19 | 8 | 11 | +26.486 USDT |
| 2022 | 6 | 1 | 5 | -2.158 USDT |

Interpretation:

- the result is not solely dependent on the single +88% trade;
- removing the best 1, 3, or 5 trades still leaves a positive accounting result;
- removing the best 10 trades makes the remaining sample negative;
- 4 of the 5 Research calendar years were profitable, although 2021 was highly concentrated in its two largest winners;
- the strategy therefore depends on successfully participating in occasional strong BTC trends, which is consistent with its design;
- short dry-run windows may be misleading because a strategy like this can spend long periods producing small losses before a large trend appears.

The concentration check does not invalidate the hypothesis, but it confirms that performance should not be judged by win rate or by a short live sample.

## Current research conclusion

The current TrendBreakoutV1 Research configuration is:

```text
BTC/USDT
4h
EMA fast: 50
EMA slow: 200
Breakout: 20 completed candles
Stoploss: -6%
startup_candle_count: 499
Spot / long only
```

Completed Research checks:

- broad 2018–2022 baseline;
- fee-inclusive backtest;
- drawdown measurement;
- lookahead-analysis;
- recursive-analysis;
- startup-candle stabilization;
- profit-concentration analysis.

Current interpretation:

TrendBreakoutV1 shows the return shape expected from a simple trend-following system: more losing trades than winning trades, but materially larger winners. The Research result is not a one-trade artifact, although it does depend on catching a relatively small number of large trends.

The strategy must not be treated as proven profitable or as having an expected future return of +190.6%.

### Remaining Research gate

The experiment's predefined protocol still requires a limited parameter-sensitivity check around the EMA and breakout values.

That check must use only the Research window and must answer whether the current result is reasonably stable around nearby parameter values, rather than search for the most profitable combination.

Do not inspect Validation, Out-of-sample, or Final holdout performance until this final Research gate is completed and the configuration is locked.
