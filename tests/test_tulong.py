from datetime import date, timedelta

from stock_assistant.models import DailyBar
from stock_assistant.strategy_tulong import build_d3_watch_signal, estimate_d1_support, is_d1_first_board, is_d2_pullback


def bar(offset, open_, high, low, close, prev_close, volume=100, limit_up=11):
    return DailyBar(
        code="603912",
        name="佳力图",
        trade_date=date(2022, 12, 28) + timedelta(days=offset),
        open=open_, high=high, low=low, close=close, prev_close=prev_close,
        volume=volume, amount=volume * close, limit_up_price=limit_up,
    )


def test_d1_first_board_requires_today_limit_and_yesterday_not_limit():
    yesterday = bar(0, 9.8, 10.0, 9.6, 9.9, 9.8, limit_up=10.78)
    today = bar(1, 10.0, 11.0, 10.0, 10.98, 9.9, limit_up=11.0)
    assert is_d1_first_board(today, yesterday)


def test_d2_pullback_rejects_volume_more_than_twice_d1():
    d1 = bar(1, 10, 11, 10, 10.98, 9.9, volume=100, limit_up=11)
    d2 = bar(2, 10.8, 11.3, 10.5, 10.9, 10.98, volume=250, limit_up=12.08)
    ok, reason = is_d2_pullback(d1, d2, estimate_d1_support(d1))
    assert not ok
    assert "超过2倍" in reason


def test_d2_pullback_accepts_valid_washout_and_builds_d3_signal():
    d1 = bar(1, 10, 11, 10, 10.98, 9.9, volume=100, limit_up=11)
    d2 = bar(2, 10.7, 11.2, 10.4, 10.9, 10.98, volume=150, limit_up=12.08)
    support = estimate_d1_support(d1)
    ok, reason = is_d2_pullback(d1, d2, support)
    assert ok, reason
    signal = build_d3_watch_signal(d1, d2, support)
    assert signal.signal_type == "D3_WATCH_UNDERWATER"
    assert signal.trigger_price == d2.close
    assert signal.invalid_price == support
