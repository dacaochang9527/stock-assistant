from __future__ import annotations

from datetime import date

from .models import StrategySignal


def render_daily_report(
    trade_date: date,
    tulong_signals: list[StrategySignal],
    swing_signals: list[StrategySignal],
    market_state: str = "待接入",
) -> str:
    lines = [
        f"# A股中短线选股日报 {trade_date}",
        "",
        f"## 大盘状态：{market_state}",
        "",
        "## 屠龙战术候选",
    ]
    if not tulong_signals:
        lines.append("- 今日无候选")
    for signal in tulong_signals:
        lines.extend([
            f"- {signal.code} {signal.name}",
            f"  - 信号：{signal.signal_type}",
            f"  - 原因：{signal.reason}",
            f"  - 观察价：{signal.trigger_price}",
            f"  - 失效价：{signal.invalid_price}",
            f"  - 风险：{signal.risk_note}",
        ])
    lines.extend(["", "## 波段候选"])
    if not swing_signals:
        lines.append("- 今日无候选")
    for signal in swing_signals:
        lines.extend([
            f"- {signal.code} {signal.name}",
            f"  - 类型：{signal.signal_type}",
            f"  - 原因：{signal.reason}",
            f"  - 触发价：{signal.trigger_price}",
            f"  - 失效价：{signal.invalid_price}",
            f"  - 风险：{signal.risk_note}",
        ])
    return "\n".join(lines) + "\n"
