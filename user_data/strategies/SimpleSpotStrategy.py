from pandas import DataFrame
import talib.abstract as ta

from freqtrade.strategy import IStrategy


class SimpleSpotStrategy(IStrategy):
    INTERFACE_VERSION = 3

    can_short = False
    timeframe = "15m"
    startup_candle_count = 200
    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    minimal_roi = {
        "0": 0.05,
        "180": 0.025,
        "480": 0.01
    }

    stoploss = -0.08
    trailing_stop = True
    trailing_stop_positive = 0.015
    trailing_stop_positive_offset = 0.03
    trailing_only_offset_is_reached = True

    order_types = {
        "entry": "limit",
        "exit": "limit",
        "emergency_exit": "market",
        "force_entry": "market",
        "force_exit": "market",
        "stoploss": "market",
        "stoploss_on_exchange": True,
        "stoploss_on_exchange_interval": 60,
        "stoploss_on_exchange_limit_ratio": 0.99
    }

    order_time_in_force = {
        "entry": "GTC",
        "exit": "GTC"
    }

    @property
    def protections(self):
        return [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 3
            },
            {
                "method": "StoplossGuard",
                "lookback_period_candles": 24,
                "trade_limit": 3,
                "stop_duration_candles": 6,
                "required_profit": 0.0,
                "only_per_pair": False
            },
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": 96,
                "trade_limit": 10,
                "stop_duration_candles": 12,
                "max_allowed_drawdown": 0.12,
                "calculation_mode": "equity"
            }
        ]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=20)
        dataframe["ema_mid"] = ta.EMA(dataframe, timeperiod=50)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=200)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["adx"] = ta.ADX(dataframe, timeperiod=14)
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        dataframe["volume_mean"] = dataframe["volume"].rolling(20).mean()
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["volume"] > 0) &
                (dataframe["volume"] > dataframe["volume_mean"]) &
                (dataframe["close"] > dataframe["ema_slow"]) &
                (dataframe["ema_fast"] > dataframe["ema_mid"]) &
                (dataframe["ema_mid"] > dataframe["ema_slow"]) &
                (dataframe["rsi"] > 52) &
                (dataframe["rsi"] < 68) &
                (dataframe["adx"] > 20) &
                (dataframe["close"] <= dataframe["ema_fast"] * 1.01)
            ),
            ["enter_long", "enter_tag"]
        ] = (1, "trend_pullback")

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["volume"] > 0) &
                (
                    (dataframe["ema_fast"] < dataframe["ema_mid"]) |
                    (dataframe["rsi"] < 45) |
                    (dataframe["close"] < dataframe["ema_mid"])
                )
            ),
            ["exit_long", "exit_tag"]
        ] = (1, "trend_break")

        return dataframe

