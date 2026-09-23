"""Research-only parameter sensitivity variants for TrendBreakoutV1.

These classes exist only to test local parameter robustness on the locked
Research window. They must not be used for dry-run or live trading.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from TrendBreakoutV1 import TrendBreakoutV1


class _TrendBreakoutV1SensitivityBase(TrendBreakoutV1):
    """Base class for research-only sensitivity variants."""

    sensitivity_tag = "sensitivity"

    def populate_entry_trend(self, dataframe, metadata):
        dataframe = super().populate_entry_trend(dataframe, metadata)
        dataframe.loc[dataframe["enter_long"] == 1, "enter_tag"] = self.sensitivity_tag
        return dataframe


class TrendBreakoutV1EmaFast40(_TrendBreakoutV1SensitivityBase):
    ema_fast_period = 40
    sensitivity_tag = "sensitivity_ema_fast_40"


class TrendBreakoutV1EmaFast60(_TrendBreakoutV1SensitivityBase):
    ema_fast_period = 60
    sensitivity_tag = "sensitivity_ema_fast_60"


class TrendBreakoutV1EmaSlow180(_TrendBreakoutV1SensitivityBase):
    ema_slow_period = 180
    sensitivity_tag = "sensitivity_ema_slow_180"


class TrendBreakoutV1EmaSlow220(_TrendBreakoutV1SensitivityBase):
    ema_slow_period = 220
    sensitivity_tag = "sensitivity_ema_slow_220"


class TrendBreakoutV1Breakout15(_TrendBreakoutV1SensitivityBase):
    breakout_period = 15
    sensitivity_tag = "sensitivity_breakout_15"


class TrendBreakoutV1Breakout25(_TrendBreakoutV1SensitivityBase):
    breakout_period = 25
    sensitivity_tag = "sensitivity_breakout_25"
