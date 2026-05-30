from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date

from .models import DailyBar
from .strategy_tulong import estimate_d1_support, is_d1_first_board, is_d2_pullback


ENTRY_ONLY_NO_EXIT_RULE = "ENTRY_ONLY_NO_EXIT_RULE"

# 退出策略可插拔接口：入参 (d4, d5, d3, support)，返回 (exit_date, exit_price, exit_reason)。
# 验证阶段不预设任何 D4/D5 退出规则；待持仓退出策略验证稳定后再注入具体实现。
ExitStrategy = Callable[[DailyBar, "DailyBar | None", DailyBar, float], tuple[date, float, str]]


@dataclass(frozen=True)
class BacktestTrade:
    code: str
    name: str
    entry_date: date
    entry_price: float
    exit_date: date | None
    exit_price: float | None
    return_pct: float | None
    exit_reason: str
    d1_date: date
    d2_date: date
    support: float


def choose_d3_entry(d3: DailyBar, d2: DailyBar, support: float) -> float | None:
    if d3.low < support:
        return None
    if d3.low >= d2.close:
        return None
    # 粗回测：用 min(D2收盘价, D3开盘价) 近似水下可成交价格。
    return min(d2.close, d3.open)


def backtest_tulong_bars(
    bars: list[DailyBar],
    exit_strategy: ExitStrategy | None = None,
) -> list[BacktestTrade]:
    """回测 D1→D2→D3 入场链路。

    退出策略可插拔：默认不预设 D4/D5 退出规则，仅记录入场（exit_reason=ENTRY_ONLY_NO_EXIT_RULE）。
    需要评估完整持仓周期时，由调用方传入 exit_strategy。
    """
    trades: list[BacktestTrade] = []
    for idx in range(1, len(bars) - 2):
        yesterday, d1, d2, d3 = bars[idx - 1], bars[idx], bars[idx + 1], bars[idx + 2]
        d4 = bars[idx + 3] if idx + 3 < len(bars) else None
        d5 = bars[idx + 4] if idx + 4 < len(bars) else None
        if not is_d1_first_board(d1, yesterday):
            continue
        support = estimate_d1_support(d1)
        ok, _ = is_d2_pullback(d1, d2, support)
        if not ok:
            continue
        entry_price = choose_d3_entry(d3, d2, support)
        if entry_price is None:
            continue
        if exit_strategy is not None and d4 is not None:
            exit_date, exit_price, exit_reason = exit_strategy(d4, d5, d3, support)
            return_pct: float | None = exit_price / entry_price - 1
        else:
            exit_date, exit_price, return_pct, exit_reason = None, None, None, ENTRY_ONLY_NO_EXIT_RULE
        trades.append(BacktestTrade(
            code=d1.code, name=d1.name, entry_date=d3.trade_date, entry_price=entry_price,
            exit_date=exit_date, exit_price=exit_price, return_pct=return_pct,
            exit_reason=exit_reason, d1_date=d1.trade_date, d2_date=d2.trade_date, support=support,
        ))
    return trades


def summarize_trades(trades: list[BacktestTrade]) -> dict[str, float | int]:
    exited = [t for t in trades if t.return_pct is not None]
    if not exited:
        return {
            "count": len(trades),
            "exited": 0,
            "win_rate": 0.0,
            "avg_return": 0.0,
            "best": 0.0,
            "worst": 0.0,
        }
    returns = [t.return_pct for t in exited]
    return {
        "count": len(trades),
        "exited": len(exited),
        "win_rate": sum(r > 0 for r in returns) / len(returns),
        "avg_return": sum(returns) / len(returns),
        "best": max(returns),
        "worst": min(returns),
    }
