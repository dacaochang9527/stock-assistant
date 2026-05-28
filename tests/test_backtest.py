from datetime import date, timedelta

from stock_assistant.backtest import backtest_tulong_bars
from stock_assistant.models import DailyBar


def b(day, open_, high, low, close, prev, volume=100, limit_up=11):
    return DailyBar("000001", "样例", date(2024, 1, 1) + timedelta(days=day), open_, high, low, close, prev, volume, volume * close, limit_up_price=limit_up)


def test_tulong_backtest_records_win_after_valid_d2_and_d3_underwater():
    bars = [
        b(0, 9.8, 10.0, 9.6, 9.9, 9.8, limit_up=10.78),
        b(1, 10.0, 11.0, 10.0, 10.98, 9.9, volume=100, limit_up=11.0),
        b(2, 10.7, 11.2, 10.4, 10.9, 10.98, volume=150, limit_up=12.08),
        b(3, 10.6, 10.95, 10.3, 10.8, 10.9, volume=120, limit_up=11.99),
        b(4, 11.3, 11.5, 11.1, 11.2, 10.8, volume=110, limit_up=11.88),
        b(5, 11.1, 11.2, 10.9, 11.0, 11.2, volume=90, limit_up=12.32),
    ]
    trades = backtest_tulong_bars(bars)
    assert len(trades) == 1
    assert trades[0].return_pct > 0
    assert trades[0].exit_reason == "D4_HIGH_OPEN_TAKE_PROFIT"
