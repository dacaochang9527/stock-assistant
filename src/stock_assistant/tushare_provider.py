from __future__ import annotations

import os
from datetime import date, datetime
from pathlib import Path

import pandas as pd

from .eastmoney import calc_limit_up
from .models import DailyBar


def load_dotenv_if_available(path: str | Path = ".env") -> None:
    try:
        from dotenv import load_dotenv
    except Exception:
        return
    load_dotenv(path)


def normalize_ts_code(code: str) -> str:
    if "." in code:
        return code.upper()
    if code.startswith(("5", "6", "9")):
        return f"{code}.SH"
    return f"{code}.SZ"


def ts_code_to_code(ts_code: str) -> str:
    return ts_code.split(".")[0]


def parse_tushare_date(value: str | int) -> date:
    return datetime.strptime(str(value), "%Y%m%d").date()


def bars_from_tushare_daily(df: pd.DataFrame, name: str | None = None) -> list[DailyBar]:
    if df.empty:
        return []
    rows = df.sort_values("trade_date")
    bars: list[DailyBar] = []
    for _, row in rows.iterrows():
        ts_code = str(row["ts_code"])
        code = ts_code_to_code(ts_code)
        stock_name = name or code
        prev_close = float(row["pre_close"])
        amount_yuan = float(row["amount"]) * 1000  # tushare amount unit: 千元
        bars.append(DailyBar(
            code=code,
            name=stock_name,
            trade_date=parse_tushare_date(row["trade_date"]),
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            prev_close=prev_close,
            volume=float(row["vol"]),
            amount=amount_yuan,
            pct_chg=float(row["pct_chg"]) if "pct_chg" in row and pd.notna(row["pct_chg"]) else None,
            turnover_rate=None,
            limit_up_price=calc_limit_up(prev_close, code, stock_name),
        ))
    return bars


class TushareDailyProvider:
    def __init__(self, token: str | None = None):
        load_dotenv_if_available()
        self.token = token or os.environ.get("TUSHARE_TOKEN")
        if not self.token:
            raise RuntimeError("Missing TUSHARE_TOKEN. Put it in .env or environment.")
        try:
            import tushare as ts
        except Exception as exc:
            raise RuntimeError("tushare 未安装。请运行：.venv/bin/python -m pip install tushare") from exc
        ts.set_token(self.token)
        self.pro = ts.pro_api(self.token)
        self._names: dict[str, str] = {}

    def stock_codes(self) -> list[str]:
        df = self.pro.stock_basic(exchange="", list_status="L", fields="ts_code,symbol,name")
        self._names.update({str(row.symbol): str(row.name) for _, row in df.iterrows()})
        return [str(symbol) for symbol in df["symbol"].tolist()]

    def name_for_code(self, code: str) -> str:
        if code in self._names:
            return self._names[code]
        try:
            df = self.pro.stock_basic(ts_code=normalize_ts_code(code), fields="ts_code,symbol,name")
            if not df.empty:
                name = str(df.iloc[0]["name"])
                self._names[code] = name
                return name
        except Exception:
            pass
        return code

    def history(self, code: str, start: date | None = None, end: date | None = None) -> list[DailyBar]:
        ts_code = normalize_ts_code(code)
        start_s = (start or date(2021, 1, 1)).strftime("%Y%m%d")
        end_s = (end or date.today()).strftime("%Y%m%d")
        df = self.pro.daily(ts_code=ts_code, start_date=start_s, end_date=end_s)
        return bars_from_tushare_daily(df, name=self.name_for_code(code))
