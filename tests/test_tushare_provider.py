import pandas as pd

from stock_assistant.tushare_provider import bars_from_tushare_daily, normalize_ts_code, ts_code_to_code


def test_ts_code_conversion():
    assert normalize_ts_code("603912") == "603912.SH"
    assert normalize_ts_code("000001") == "000001.SZ"
    assert ts_code_to_code("603912.SH") == "603912"


def test_bars_from_tushare_daily_sorts_and_parses_prev_close():
    df = pd.DataFrame([
        {"ts_code": "603912.SH", "trade_date": "20221221", "open": 11.20, "high": 12.44, "low": 11.20, "close": 12.02, "pre_close": 12.44, "vol": 384033, "amount": 454377.104, "pct_chg": -3.38},
        {"ts_code": "603912.SH", "trade_date": "20221220", "open": 12.44, "high": 12.44, "low": 12.01, "close": 12.44, "pre_close": 11.31, "vol": 289093, "amount": 359055.463, "pct_chg": 9.99},
    ])
    bars = bars_from_tushare_daily(df, name="佳力图")
    assert [str(bar.trade_date) for bar in bars] == ["2022-12-20", "2022-12-21"]
    assert bars[0].amount == 359055463.0
    assert bars[0].limit_up_price == 12.44
    assert bars[1].prev_close == 12.44
