from __future__ import annotations

from datetime import datetime

from pandas import DataFrame

from freqtrade.persistence import Trade
from freqtrade.strategy import BooleanParameter, DecimalParameter, IStrategy, IntParameter, informative

from price_action_core import compute_price_action_indicators


class BinanceSpotLowFrequencyStrategy(IStrategy):
    """Long-only strategy whose trading signals are derived only from price action."""

    INTERFACE_VERSION = 3

    can_short = False
    timeframe = "1h"
    startup_candle_count = 300
    process_only_new_candles = True
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    position_adjustment_enable = False

    minimal_roi = {
        "0": 0.10,
        "720": 0.05,
        "2160": 0.02,
        "4320": 0.0,
    }

    stoploss = -0.10
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.04
    trailing_only_offset_is_reached = True

    buy_score_min = IntParameter(55, 80, default=60, space="buy")
    buy_risk_max = IntParameter(35, 65, default=55, space="buy")
    buy_min_risk_reward = DecimalParameter(1.3, 3.0, decimals=1, default=1.5, space="buy")
    buy_min_volume_ratio = DecimalParameter(0.8, 1.5, decimals=1, default=0.9, space="buy")
    use_btc_structure_guard = BooleanParameter(default=True, space="buy")
    use_pair_4h_structure_guard = BooleanParameter(default=True, space="buy")

    sell_score_min = IntParameter(40, 75, default=50, space="sell")
    sell_risk_min = IntParameter(65, 90, default=75, space="sell")

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
        return compute_price_action_indicators(dataframe)

    @informative("4h", "BTC/{stake}")
    def populate_indicators_btc_4h(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return compute_price_action_indicators(dataframe)

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = compute_price_action_indicators(dataframe)

        stake = self.config["stake_currency"].lower()
        defaults = {
            "pa_structure_4h": "range",
            "pa_bos_down_4h": False,
            "pa_bearish_sweep_4h": False,
            f"btc_{stake}_pa_structure_4h": "range",
            f"btc_{stake}_pa_bos_down_4h": False,
            f"btc_{stake}_pa_bearish_sweep_4h": False,
        }
        for column, default in defaults.items():
            if column not in dataframe.columns:
                dataframe[column] = default
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        stake = self.config["stake_currency"].lower()
        btc_structure = f"btc_{stake}_pa_structure_4h"
        btc_breakdown = f"btc_{stake}_pa_bos_down_4h"
        btc_sweep = f"btc_{stake}_pa_bearish_sweep_4h"

        pair_4h_guard = (
            (dataframe["pa_structure_4h"] != "bearish")
            & (~dataframe["pa_bos_down_4h"])
            & (~dataframe["pa_bearish_sweep_4h"])
        )
        btc_4h_guard = (
            (dataframe[btc_structure] != "bearish")
            & (~dataframe[btc_breakdown])
            & (~dataframe[btc_sweep])
        )
        conditions = (
            (dataframe["volume"] > 0)
            & (dataframe["pa_volume_ratio"] >= self.buy_min_volume_ratio.value)
            & (dataframe["pa_action"] == "BUY")
            & (dataframe["pa_buy_score"] >= self.buy_score_min.value)
            & (dataframe["pa_risk_score"] <= self.buy_risk_max.value)
            & (dataframe["pa_risk_reward"] >= self.buy_min_risk_reward.value)
            & (~dataframe["pa_bearish_sweep"])
            & (~dataframe["pa_bos_down"])
        )
        if self.use_pair_4h_structure_guard.value:
            conditions &= pair_4h_guard
        if self.use_btc_structure_guard.value:
            conditions &= btc_4h_guard

        dataframe.loc[conditions, "enter_long"] = 1
        dataframe.loc[conditions, "enter_tag"] = dataframe.loc[conditions, "pa_setup"]
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                (dataframe["volume"] > 0)
                & (
                    (dataframe["pa_action"] == "EXIT")
                    | (dataframe["pa_sell_score"] >= self.sell_score_min.value)
                    | (dataframe["pa_risk_score"] >= self.sell_risk_min.value)
                    | dataframe["pa_bos_down"]
                    | dataframe["pa_choch_down"]
                )
            ),
            ["exit_long", "exit_tag"],
        ] = (1, "price_action_invalidation")
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
        risk_score = float(current_candle.get("pa_risk_score", 100.0))
        volatility_pct = float(current_candle.get("pa_volatility_pct", 0.0))
        structural_stop = float(current_candle.get("pa_invalidation_price", 0.0))
        stop_distance_pct = (
            max((current_rate - structural_stop) / current_rate, 0.0)
            if current_rate > 0 and structural_stop > 0
            else 0.10
        )

        stake = proposed_stake
        if risk_score >= 50:
            stake *= 0.70
        if volatility_pct >= 0.04:
            stake *= 0.75
        if stop_distance_pct > 0.08:
            stake *= 0.60

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
        if bool(current_candle.get("pa_bearish_sweep", False)):
            return "bearish_liquidity_sweep"
        if bool(current_candle.get("pa_choch_down", False)):
            return "bearish_change_of_character"
        if bool(current_candle.get("pa_bos_down", False)):
            return "structural_support_break"
        if float(current_candle.get("pa_risk_score", 0.0)) >= 85:
            return "price_action_risk_off"
        return None
