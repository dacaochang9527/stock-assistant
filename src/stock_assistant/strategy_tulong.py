from __future__ import annotations

from .indicators import is_limit_up
from .models import DailyBar, StrategySignal


def estimate_d1_support(d1: DailyBar, recent_platform_high: float | None = None) -> float:
    candidates = [d1.open, d1.prev_close]
    if recent_platform_high is not None:
        candidates.append(recent_platform_high)
    return max(candidates)


def is_d1_first_board(today: DailyBar, yesterday: DailyBar) -> bool:
    return (
        is_limit_up(today.close, today.limit_up_price)
        and not is_limit_up(yesterday.close, yesterday.limit_up_price)
        and today.low < today.limit_up_price * 0.98 if today.limit_up_price else False
    )


def is_d2_pullback(d1: DailyBar, d2: DailyBar, d1_support: float) -> tuple[bool, str]:
    volume_ratio = d2.volume / d1.volume if d1.volume else float("inf")
    open_gap = (d2.open / d1.close) - 1 if d1.close else 0
    high_above_open = (d2.high / d2.open) - 1 if d2.open else 0
    close_below_high = 1 - (d2.close / d2.high) if d2.high else 0

    if volume_ratio > 2:
        return False, f"D2成交量/D1={volume_ratio:.2f}，超过2倍"
    if open_gap > 0.04 and d2.close < d2.open:
        return False, "D2高开低走，疑似出货"
    if high_above_open < 0.02:
        return False, "D2盘中冲高不足"
    if close_below_high < 0.02:
        return False, "D2冲高回落特征不足"
    if d2.close < d1_support:
        return False, "D2收盘跌破D1支撑位"
    return True, f"D2冲高回落，量比{volume_ratio:.2f}，未破支撑"


def build_d3_watch_signal(d1: DailyBar, d2: DailyBar, d1_support: float) -> StrategySignal:
    return StrategySignal(
        code=d2.code,
        name=d2.name,
        strategy="tulong",
        signal_type="D3_WATCH_UNDERWATER",
        reason="D1首板后，D2冲高回落且量能未超过2倍，次日观察水下低吸机会",
        trigger_price=d2.close,
        invalid_price=d1_support,
        risk_note="若D3跌破D1支撑位，策略失效；D4/D5必须按规则退出",
    )
