from __future__ import annotations

from datetime import datetime

import freqtrade.vendor.qtpylib.indicators as qtpylib
import talib.abstract as ta
from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import BooleanParameter, DecimalParameter, IStrategy, IntParameter, informative


class BinanceSpotLowFrequencyStrategy(IStrategy):
    INTERFACE_VERSION = 3

    can_short = False
    timeframe = "1h"
    startup_candle_count = 800
    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    position_adjustment_enable = False

    minimal_roi = {
        "0": 0.08,
        "360": 0.045,
        "1440": 0.02,
        "2880": 0.0,
    }

    stoploss = -0.10
    trailing_stop = True
    trailing_stop_positive = 0.015
    trailing_stop_positive_offset = 0.03
    trailing_only_offset_is_reached = True

    buy_rsi_fast = IntParameter(35, 55, default=44, space="buy")
    buy_rsi_slow = IntParameter(45, 68, default=57, space="buy")
    buy_adx = IntParameter(16, 32, default=21, space="buy")
    buy_pullback_atr = DecimalParameter(0.10, 1.30, decimals=2, default=0.45, space="buy")
    buy_volume_factor = DecimalParameter(0.80, 1.60, decimals=2, default=1.00, space="buy")
    use_btc_guard = BooleanParameter(default=True, space="buy")
    use_4h_guard = BooleanParameter(default=True, space="buy")

    sell_rsi = IntParameter(35, 55, default=44, space="sell")
    sell_adx = IntParameter(10, 24, default=16, space="sell")
    sell_profit_rsi = IntParameter(68, 84, default=76, space="sell")

    cooldown_lookback = IntParameter(2, 8, default=4, space="protection")
    stop_duration = IntParameter(4, 16, default=8, space="protection")
    max_drawdown_lookback = IntParameter(48, 168, default=96, space="protection")
    max_drawdown_trade_limit = IntParameter(6, 16, default=10, space="protection")
    max_allowed_drawdown = DecimalParameter(0.08, 0.18, decimals=2, default=0.12, space="protection")
    use_stop_protection = BooleanParameter(default=True, space="protection")

    order_types = {
        "entry": "limit",
        "exit": "limit",
        "emergency_exit": "market",
        "force_entry": "market",
        "force_exit": "market",
        "stoploss": "market",
        "stoploss_on_exchange": True,
        "stoploss_on_exchange_interval": 60,
        "stoploss_on_exchange_limit_ratio": 0.99,
    }

    order_time_in_force = {
        "entry": "GTC",
        "exit": "GTC",
    }

    @property
    def protections(self):
        protections = [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": int(self.cooldown_lookback.value),
            }
        ]

        if self.use_stop_protection.value:
            protections.append(
                {
                    "method": "StoplossGuard",
                    "lookback_period_candles": 48,
                    "trade_limit": 3,
                    "stop_duration_candles": int(self.stop_duration.value),
                    "required_profit": 0.0,
                    "only_per_pair": False,
                }
            )

        protections.append(
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": int(self.max_drawdown_lookback.value),
                "trade_limit": int(self.max_drawdown_trade_limit.value),
                "stop_duration_candles": int(self.stop_duration.value),
                "max_allowed_drawdown": float(self.max_allowed_drawdown.value),
            }
        )

        return protections

    @informative("4h")
    def populate_indicators_4h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=20)
        dataframe["ema_mid"] = ta.EMA(dataframe, timeperiod=50)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=200)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    @informative("4h", "BTC/{stake}")
    def populate_indicators_btc_4h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=20)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=200)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=20)
        dataframe["ema_mid"] = ta.EMA(dataframe, timeperiod=50)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=200)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["rsi_fast"] = ta.RSI(dataframe, timeperiod=6)
        dataframe["adx"] = ta.ADX(dataframe, timeperiod=14)
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        dataframe["atr_pct"] = dataframe["atr"] / dataframe["close"]
        dataframe["volume_mean_24"] = dataframe["volume"].rolling(24).mean()

        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe["bb_lowerband"] = bollinger["lower"]
        dataframe["bb_middleband"] = bollinger["mid"]
        dataframe["bb_upperband"] = bollinger["upper"]

        stake = self.config["stake_currency"].lower()
        btc_columns = [
            f"btc_{stake}_ema_fast_4h",
            f"btc_{stake}_ema_slow_4h",
            f"btc_{stake}_rsi_4h",
        ]

        for column in btc_columns:
            if column not in dataframe.columns:
                dataframe[column] = 0.0

        for column in ["ema_fast_4h", "ema_mid_4h", "ema_slow_4h", "rsi_4h"]:
            if column not in dataframe.columns:
                dataframe[column] = 0.0

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        stake = self.config["stake_currency"].lower()
        btc_fast = f"btc_{stake}_ema_fast_4h"
        btc_slow = f"btc_{stake}_ema_slow_4h"
        btc_rsi = f"btc_{stake}_rsi_4h"

        btc_guard = (
            (dataframe[btc_fast] > dataframe[btc_slow]) &
            (dataframe[btc_rsi] > 50)
        )

        pair_4h_guard = (
            (dataframe["ema_fast_4h"] > dataframe["ema_mid_4h"]) &
            (dataframe["ema_mid_4h"] > dataframe["ema_slow_4h"]) &
            (dataframe["rsi_4h"] > 50)
        )

        rsi_rebound = (
            (dataframe["rsi_fast"] > self.buy_rsi_fast.value) &
            (dataframe["rsi_fast"].shift(1) <= self.buy_rsi_fast.value)
        )

        pullback_zone = (
            (dataframe["close"] >= dataframe["ema_fast"] - (dataframe["atr"] * self.buy_pullback_atr.value)) &
            (dataframe["close"] <= dataframe["ema_fast"]) &
            (dataframe["close"] > dataframe["ema_mid"]) &
            (dataframe["close"] > dataframe["bb_middleband"])
        )

        conditions = (
            (dataframe["volume"] > 0) &
            (dataframe["volume"] > dataframe["volume_mean_24"] * self.buy_volume_factor.value) &
            (dataframe["ema_fast"] > dataframe["ema_mid"]) &
            (dataframe["ema_mid"] > dataframe["ema_slow"]) &
            (dataframe["close"] > dataframe["ema_slow"]) &
            (dataframe["adx"] > self.buy_adx.value) &
            (dataframe["rsi"] < self.buy_rsi_slow.value) &
            (dataframe["rsi"] > 46) &
            pullback_zone &
            rsi_rebound &
            (dataframe["atr_pct"] < 0.06)
        )

        if self.use_4h_guard.value:
            conditions &= pair_4h_guard
        if self.use_btc_guard.value:
            conditions &= btc_guard

        dataframe.loc[conditions, ["enter_long", "enter_tag"]] = (1, "trend_pullback_1h")
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        stake = self.config["stake_currency"].lower()
        btc_fast = f"btc_{stake}_ema_fast_4h"
        btc_slow = f"btc_{stake}_ema_slow_4h"

        dataframe.loc[
            (
                (dataframe["volume"] > 0) &
                (
                    (
                        (dataframe["ema_fast"] < dataframe["ema_mid"]) &
                        (dataframe["adx"] < self.sell_adx.value)
                    ) |
                    (dataframe["rsi"] < self.sell_rsi.value) |
                    (dataframe["close"] < dataframe["ema_mid"]) |
                    (dataframe[btc_fast] < dataframe[btc_slow])
                )
            ),
            ["exit_long", "exit_tag"],
        ] = (1, "trend_break_1h")

        return dataframe

    def custom_stake_amount(
        self,
        pair: str,
        current_time: datetime,
        current_rate: float,
        proposed_stake: float,
        min_stake: float | None,
        max_stake: float,
        leverage: float,
        entry_tag: str | None,
        side: str,
        **kwargs,
    ) -> float:
        if not self.dp:
            return proposed_stake

        dataframe, _ = self.dp.get_analyzed_dataframe(pair=pair, timeframe=self.timeframe)
        if dataframe.empty:
            return proposed_stake

        current_candle = dataframe.iloc[-1].squeeze()
        atr_pct = float(current_candle.get("atr_pct", 0.0))
        stake = proposed_stake

        if atr_pct >= 0.05:
            stake = proposed_stake * 0.60
        elif atr_pct >= 0.035:
            stake = proposed_stake * 0.80

        if min_stake is not None:
            stake = max(stake, min_stake)
        return min(stake, max_stake)

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        **kwargs,
    ) -> str | None:
        if not self.dp:
            return None

        dataframe, _ = self.dp.get_analyzed_dataframe(pair=pair, timeframe=self.timeframe)
        if dataframe.empty:
            return None

        current_candle = dataframe.iloc[-1].squeeze()
        if current_profit > 0.04 and float(current_candle.get("rsi", 0.0)) >= self.sell_profit_rsi.value:
            return "profit_rsi_exhaustion"

        stake = self.config["stake_currency"].lower()
        btc_fast = f"btc_{stake}_ema_fast_4h"
        btc_slow = f"btc_{stake}_ema_slow_4h"
        btc_rsi = f"btc_{stake}_rsi_4h"

        if (
            current_profit > 0.01 and
            float(current_candle.get(btc_fast, 0.0)) < float(current_candle.get(btc_slow, 0.0)) and
            float(current_candle.get(btc_rsi, 0.0)) < 48
        ):
            return "btc_risk_off"

        return None
