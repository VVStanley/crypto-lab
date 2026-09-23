"""Initial research baseline for Crypto Strategy Lab.

This strategy is intentionally simple and explainable. It is not claimed to be
profitable. See experiments/001-trend-breakout-btc-4h.md before changing it.
"""

from pandas import DataFrame
import talib.abstract as ta

from freqtrade.strategy import IStrategy


class TrendBreakoutV1(IStrategy):
    """4h long-only BTC trend + breakout research strategy."""

    INTERFACE_VERSION = 3

    timeframe = "4h"
    can_short = False
    process_only_new_candles = True
    startup_candle_count = 499

    # Exit decisions are signal-driven. The stoploss is an emergency risk bound.
    minimal_roi = {}
    stoploss = -0.06

    use_exit_signal = True
    exit_profit_only = False

    ema_fast_period = 50
    ema_slow_period = 200
    breakout_period = 20

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=self.ema_fast_period)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=self.ema_slow_period)

        # Shift by one candle so today's close is compared only with the range
        # that was fully known before the current candle completed.
        dataframe["prior_breakout_high"] = (
            dataframe["high"].rolling(self.breakout_period).max().shift(1)
        )

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        entry = (
            (dataframe["ema_fast"] > dataframe["ema_slow"])
            & (dataframe["close"] > dataframe["ema_fast"])
            & (dataframe["close"] > dataframe["prior_breakout_high"])
            & (dataframe["volume"] > 0)
        )

        dataframe.loc[entry, ["enter_long", "enter_tag"]] = (
            1,
            "trend_breakout_20",
        )
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        exit_condition = (
            (dataframe["close"] < dataframe["ema_fast"])
            | (dataframe["ema_fast"] < dataframe["ema_slow"])
        ) & (dataframe["volume"] > 0)

        dataframe.loc[exit_condition, ["exit_long", "exit_tag"]] = (
            1,
            "trend_lost",
        )
        return dataframe
