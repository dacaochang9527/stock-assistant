from __future__ import annotations

import argparse
from datetime import date

from stock_assistant.akshare_provider import AkshareSinaDailyProvider
from stock_assistant.backtest import backtest_tulong_bars, summarize_trades
from stock_assistant.data_provider import AkshareDailyDataProvider, CsvDailyDataProvider
from stock_assistant.tushare_provider import TushareDailyProvider


def build_provider(name: str, data_dir: str):
    if name == "csv":
        return CsvDailyDataProvider(data_dir)
    if name == "akshare-sina":
        return AkshareSinaDailyProvider()
    if name == "akshare":
        return AkshareDailyDataProvider()
    if name == "tushare":
        return TushareDailyProvider()
    raise ValueError(f"unsupported provider: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["csv", "akshare-sina", "akshare", "tushare"], default="csv")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--start", default="2021-01-01")
    parser.add_argument("--end", default=date.today().isoformat())
    parser.add_argument("--codes", nargs="*", default=None)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    provider = build_provider(args.provider, args.data_dir)
    codes = args.codes or provider.stock_codes()
    if args.limit:
        codes = codes[:args.limit]
    trades = []
    for code in codes:
        bars = provider.history(code, start=date.fromisoformat(args.start), end=date.fromisoformat(args.end))
        trades.extend(backtest_tulong_bars(bars))
    summary = summarize_trades(trades)
    print("屠龙战术回测摘要")
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("\n最近10笔交易：")
    for trade in trades[-10:]:
        print(trade)


if __name__ == "__main__":
    main()
