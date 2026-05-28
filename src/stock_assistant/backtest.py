from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .models import DailyBar
from .strategy_tulong import estimate_d1_support, is_d1_first_board, is_d2_pullback


@dataclass(frozen=True)
class BacktestTrade:
    code: str
    name: str
    entry_date: date
    entry_price: float
    exit_date: date
    exit_price: float
    return_pct: float
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


def choose_exit(d4: DailyBar, d5: DailyBar | None, d3: DailyBar, support: float) -> tuple[date, float, str]:
    if d4.open < support or d4.low < support:
        return d4.trade_date, min(d4.open, support), "D4_SUPPORT_BROKEN_STOP"
    if d4.open >= d3.close * 1.04:
        return d4.trade_date, d4.open, "D4_HIGH_OPEN_TAKE_PROFIT"
    if d4.high > d4.open:
        return d4.trade_date, (d4.high + d4.open) / 2, "D4_INTRADAY_RALLY_EXIT"
    if d5 is None:
        return d4.trade_date, d4.close, "D4_LAST_BAR_EXIT"
    if d5.low < support:
        return d5.trade_date, min(d5.open, support), "D5_SUPPORT_BROKEN_STOP"
    return d5.trade_date, d5.close, "D5_FORCE_EXIT"


def backtest_tulong_bars(bars: list[DailyBar]) -> list[BacktestTrade]:
    trades: list[BacktestTrade] = []
    for idx in range(1, len(bars) - 3):
        yesterday, d1, d2, d3, d4 = bars[idx - 1], bars[idx], bars[idx + 1], bars[idx + 2], bars[idx + 3]
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
        exit_date, exit_price, exit_reason = choose_exit(d4, d5, d3, support)
        trades.append(BacktestTrade(
            code=d1.code, name=d1.name, entry_date=d3.trade_date, entry_price=entry_price,
            exit_date=exit_date, exit_price=exit_price,
            return_pct=exit_price / entry_price - 1,
            exit_reason=exit_reason, d1_date=d1.trade_date, d2_date=d2.trade_date, support=support,
        ))
    return trades


def summarize_trades(trades: list[BacktestTrade]) -> dict[str, float | int]:
    if not trades:
        return {"count": 0, "win_rate": 0.0, "avg_return": 0.0, "best": 0.0, "worst": 0.0}
    returns = [t.return_pct for t in trades]
    return {
        "count": len(trades),
        "win_rate": sum(r > 0 for r in returns) / len(returns),
        "avg_return": sum(returns) / len(returns),
        "best": max(returns),
        "worst": min(returns),
    }
