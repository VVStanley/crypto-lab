# Experiment 001 — TrendBreakoutV1 / BTC-USDT / 4h

Status: **rejected for promotion — retained as research baseline**

## Hypothesis

A breakout above a recent range may have a higher probability of continuation when the market is already in a positive medium-vs-long-term trend regime.

This was a hypothesis to test, not an assumption of profitability.

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

Startup history:

```text
499 candles
```

## What this strategy was trying to do

TrendBreakoutV1 was deliberately simple.

It did not try to predict every BTC move or win most trades. It waited for a positive medium-vs-long-term trend and then bought a breakout above the previous 20 completed 4h candles.

The intended payoff shape was:

```text
many small losing/modest trades
            +
a small number of very large winners
            =
possible positive long-run result
```

So the strategy depended on catching large directional BTC moves rather than being correct frequently.

## Evaluation windows

- Research: `2018-01-01 — 2022-12-31`
- Validation: `2023-01-01 — 2024-12-31`
- Out-of-sample: `2025-01-01 — 2026-06-30`
- Final holdout: `2026-07-01 — 2026-09-22`

The Final holdout was **not opened** after the strategy failed the preceding OOS gate.

## Research result

Locked configuration:

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

Research:

- Trades: 62
- Total return: +190.60%
- Average trade: +4.62%
- Win rate: 45.2%
- Profit factor: 3.72
- Expectancy: +0.92
- Best trade: +88.07%
- Wallet max drawdown: 19.16%

Robustness checks completed:

- fee-inclusive backtest;
- no lookahead bias detected;
- recursive/startup analysis;
- `startup_candle_count = 499`;
- profit-concentration analysis;
- nearby single-parameter sensitivity.

Research decision:

```text
KEEP FOR VALIDATION
```

## Validation result

Timerange:

```text
2023-01-01 — 2024-12-31
```

Validation:

- Trades: 37
- Total return: +60.51%
- Average trade: +2.49%
- Win rate: 29.7%
- Profit factor: 2.48
- Expectancy: +0.49
- Best trade: +33.26%
- Wallet max drawdown: 11.57%
- Maximum consecutive losses: 8
- BTC market change: +467.58%

Approximate concentration diagnostic:

| Removed winners | Remaining accounting profit |
| --- | ---: |
| TOP-1 | +11.552 USDT |
| TOP-3 | +0.257 USDT |
| TOP-5 | -6.136 USDT |

Validation stayed profitable, but the result became much more concentrated in a few large winners.

Validation decision:

```text
CONTINUE TO OOS WITHOUT CHANGING PARAMETERS
```

No strategy parameter was changed after Validation.

## Out-of-sample result

Timerange:

```text
2025-01-01 — 2026-06-30
```

OOS:

- Trades: 23
- Total return: -5.74%
- Average trade: -0.36%
- Win rate: 39.1%
- Profit factor: 0.73
- Expectancy: -0.07
- SQN: -0.61
- Best trade: +7.89%
- Worst trade: -4.75%
- Closed-trade max drawdown: 12.83%
- Wallet max drawdown: 14.53%
- Wallet drawdown duration: about 367 days
- BTC market change: -36.92%

All 23 trades exited through the normal `trend_lost` condition.

The key structural change was that ordinary losing/modest trades remained, while the very large winners that paid for them in Research and Validation disappeared. The best OOS winner was only +7.89%.

The measured edge therefore crossed from positive to negative:

```text
Profit factor: 0.73
Expectancy: -0.07
```

## Cross-period summary

| Stage | Period | Trades | Total return | Profit factor | Expectancy |
| --- | --- | ---: | ---: | ---: | ---: |
| Research | 2018–2022 | 62 | +190.60% | 3.72 | +0.92 |
| Validation | 2023–2024 | 37 | +60.51% | 2.48 | +0.49 |
| OOS | 2025–2026 H1 | 23 | -5.74% | 0.73 | -0.07 |

The progression matters more than the attractive Research result.

## Final experiment decision

```text
REJECT FOR PROMOTION
RETAIN AS BASELINE
```

TrendBreakoutV1 must not be promoted to dry-run/live as the selected first strategy.

This does not prove that trend following can never work. It means this specific locked hypothesis/configuration did not demonstrate enough robustness across the predefined evaluation sequence.

Do not retune TrendBreakoutV1 using the already-observed 2025–2026 OOS period and then treat that same period as fresh evidence.

## What Experiment 001 taught us

1. A strategy can look excellent in Research and still fail later.
2. Historical return alone is not enough.
3. TrendBreakoutV1 depends heavily on rare large winners.
4. Missing a few large trend trades could materially change real-world results.
5. Win rate is not the primary metric for this strategy class.
6. The strategy reduced losses relative to BTC during the falling OOS market, but still failed the requirement of positive OOS expectancy.
7. The Final holdout should remain untouched after an earlier gate fails.

Experiment 001 remains useful as a simple trend-following baseline for future comparisons.
