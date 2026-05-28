from __future__ import annotations

from .models import DailyBar, StrategySignal


def detect_breakout_signal(
    bars: list[DailyBar],
    ma20: float,
    volume_ma5: float,
    lookback_days: int = 20,
) -> StrategySignal | None:
    if len(bars) < lookback_days + 1:
        return None
    today = bars[-1]
    previous = bars[-lookback_days-1:-1]
    previous_high_close = max(bar.close for bar in previous)
    if today.close <= ma20:
        return None
    if today.close / ma20 - 1 > 0.15:
        return None
    if today.close <= previous_high_close:
        return None
    volume_ratio = today.volume / volume_ma5 if volume_ma5 else 0
    if not (1.2 <= volume_ratio <= 3.0):
        return None
    if today.pct_chg is not None and today.pct_chg > 7:
        return None
    return StrategySignal(
        code=today.code,
        name=today.name,
        strategy="swing",
        signal_type="BREAKOUT",
        reason=f"突破近{lookback_days}日高收盘价，量比{volume_ratio:.2f}",
        trigger_price=today.close,
        invalid_price=ma20,
        risk_note="跌破MA20或放量冲高回落则信号失效",
    )
