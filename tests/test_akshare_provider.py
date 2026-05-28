import pandas as pd

from stock_assistant.akshare_provider import akshare_symbol_for_code, bars_from_akshare_daily


def test_akshare_symbol_for_code():
    assert akshare_symbol_for_code("603912") == "sh603912"
    assert akshare_symbol_for_code("000001") == "sz000001"


def test_bars_from_akshare_daily_parses_sina_daily_format():
    df = pd.DataFrame([
        {"date": "2022-12-15", "open": 9.93, "high": 10.20, "low": 9.93, "close": 10.17, "volume": 3887674.0, "amount": 39386980.0},
        {"date": "2022-12-16", "open": 10.18, "high": 10.35, "low": 9.95, "close": 10.28, "volume": 6137097.0, "amount": 62330324.0},
    ])
    bars = bars_from_akshare_daily("603912", "佳力图", df, pre_close=9.98)
    assert len(bars) == 2
    assert bars[0].prev_close == 9.98
    assert bars[0].limit_up_price == 10.98
    assert bars[1].prev_close == 10.17
