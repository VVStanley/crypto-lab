# Experiment 002 — PullbackMeanReversionV1 / BTC-USDT / 1h

Status: **design — not tested**

## Why this experiment exists

Experiment 001 tested a slow 4h trend-breakout hypothesis.

Its main weakness was structural: many ordinary trades depended on occasional very large trend winners. In the later OOS period those large winners did not appear and the strategy's expectancy became negative.

Experiment 002 should test a **different source of edge**, not retune TrendBreakoutV1.

The goal is to investigate whether shorter-term BTC pullbacks can provide more frequent, smaller opportunities without requiring one huge multi-week trend to pay for the rest of the trades.

## Hypothesis

When BTC remains in a broad non-bearish regime, a sharp short-term downward overshoot can sometimes revert toward its recent local mean.

Instead of buying a breakout into strength, the strategy will wait for:

1. an acceptable long-term regime;
2. a short-term downside overshoot;
3. evidence that price has started to recover from that overshoot.

The hypothesis is:

> Buying the recovery from selected short-term pullbacks may produce a repeatable positive expectancy after fees while generating more observations than the 4h breakout strategy.

This is only a hypothesis and has not been tested.

## Market

- Exchange: Binance
- Market: Spot
- Pair: BTC/USDT
- Timeframe: **1h**
- Direction: long only
- No leverage
- No futures
- No averaging down
- One open position maximum for the initial experiment

## Initial strategy shape

The first implementation should stay intentionally small and explainable.

### Regime

Candidate:

```text
close > EMA(200)
```

Only look for long entries while BTC remains above its long-term 1h trend filter.

### Pullback / overshoot

Use a simple local statistical range such as Bollinger Bands around a 20-candle mean.

Candidate overshoot:

```text
previous close < previous lower Bollinger Band
```

### Recovery entry

Do not buy merely because price is falling.

Candidate entry:

```text
previous close < previous lower band
AND current close > current lower band
AND current close > EMA(200)
```

This attempts to enter after evidence of recovery instead of trying to catch the exact bottom.

### Exit

The first hypothesis should test reversion toward the local mean, for example:

```text
close >= Bollinger middle band
```

A regime-loss exit and an emergency stop must be fixed before the first performance backtest.

The exact baseline must be frozen **before** inspecting its historical profitability.

## Why this is different from Experiment 001

Experiment 001:

```text
wait for strength
-> buy breakout
-> try to ride a large trend
```

Experiment 002:

```text
wait for temporary weakness inside an acceptable regime
-> wait for recovery
-> buy the pullback
-> exit near the local mean
```

Expected structural difference:

| Property | Experiment 001 | Experiment 002 hypothesis |
| --- | --- | --- |
| Timeframe | 4h | 1h |
| Entry style | breakout | pullback recovery |
| Main payoff source | rare large trends | repeated smaller reversions |
| Expected frequency | low | higher |
| Typical holding time | days/weeks | hours/days |
| Dependence on one huge winner | high | should be lower if hypothesis is valid |

The goal is **not** to force more trades. Higher frequency is useful only if those trades retain positive expectancy after fees.

## Research discipline

Do not use hyperopt initially.

Do not search a large parameter grid.

The first baseline should use simple conventional parameters chosen before inspecting performance.

Then use the same discipline as Experiment 001:

1. implementation correctness;
2. lookahead-analysis;
3. recursive/startup analysis where relevant;
4. broad Research baseline;
5. trade-distribution and concentration analysis;
6. limited one-parameter-at-a-time sensitivity;
7. locked Validation;
8. later-period challenge/OOS evaluation without retuning;
9. Final holdout only if previous gates justify opening it.

## Evaluation-window note

For Experiment 002, the market behavior of `2025-01-01 — 2026-06-30` is no longer completely unknown to us because it was inspected during Experiment 001.

Therefore it must not be described as a pristine blind OOS period for the **choice of Experiment 002's hypothesis**.

We can still use it later as a known challenge period after the Experiment 002 configuration is locked.

The existing Final holdout remains untouched:

```text
2026-07-01 — 2026-09-22
```

It must remain unopened until Experiment 002 passes its preceding gates.

## What would make this experiment interesting

Useful questions:

- Is expectancy positive outside Research?
- Is profit factor meaningfully above 1?
- Does the result survive modest nearby parameter changes?
- Is performance distributed across enough trades and market periods?
- How much of total P&L comes from TOP-1 / TOP-3 / TOP-5 trades?
- Are modeled fees already included?
- What is wallet drawdown?
- Does the strategy remain operationally realistic on 1h candles?
- Does later locked evidence support or reject the original hypothesis?

Experiment 002 should be judged on its own evidence, not promoted merely because it beats TrendBreakoutV1.
