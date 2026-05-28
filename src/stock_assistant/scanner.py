from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path

from .data_provider import AkshareDailyDataProvider, CsvDailyDataProvider, DailyDataProvider
from .akshare_provider import AkshareSinaDailyProvider
from .eastmoney import EastmoneyDirectProvider
from .eastmoney_playwright import EastmoneyPlaywrightProvider
from .tushare_provider import TushareDailyProvider
from .indicators import moving_average
from .reporter import render_daily_report
from .strategy_swing import detect_breakout_signal
from .strategy_tulong import build_d3_watch_signal, estimate_d1_support, is_d1_first_board, is_d2_pullback


def scan_tulong_for_bars(bars):
    signals = []
    if len(bars) < 3:
        return signals
    yesterday, d1, d2 = bars[-3], bars[-2], bars[-1]
    if not is_d1_first_board(d1, yesterday):
        return signals
    support = estimate_d1_support(d1)
    ok, _reason = is_d2_pullback(d1, d2, support)
    if ok:
        signals.append(build_d3_watch_signal(d1, d2, support))
    return signals


def scan_swing_for_bars(bars):
    if len(bars) < 25:
        return []
    closes = [bar.close for bar in bars]
    volumes = [bar.volume for bar in bars]
    ma20 = moving_average(closes, 20)[-1]
    vma5 = moving_average(volumes, 5)[-1]
    if ma20 is None or vma5 is None:
        return []
    signal = detect_breakout_signal(bars, ma20=ma20, volume_ma5=vma5)
    return [signal] if signal else []


def run_scan(provider: DailyDataProvider, report_date: date, limit: int | None = None) -> str:
    tulong_signals = []
    swing_signals = []
    codes = provider.stock_codes()
    if limit:
        codes = codes[:limit]
    for code in codes:
        bars = provider.history(code, end=report_date)
        if not bars:
            continue
        tulong_signals.extend(scan_tulong_for_bars(bars))
        swing_signals.extend(scan_swing_for_bars(bars))
    return render_daily_report(report_date, tulong_signals, swing_signals, market_state="待接入市场情绪过滤器")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--provider", choices=["csv", "akshare", "akshare-sina", "eastmoney", "eastmoney-playwright", "tushare"], default="csv")
    parser.add_argument("--data-dir", default="data/raw")
    parser.add_argument("--codes", nargs="*", default=None, help="股票代码列表；eastmoney provider 必须显式传入")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    report_date = date.fromisoformat(args.date)
    if args.provider == "csv":
        provider = CsvDailyDataProvider(args.data_dir)
    elif args.provider == "akshare":
        provider = AkshareDailyDataProvider()
    elif args.provider == "akshare-sina":
        provider = AkshareSinaDailyProvider()
    elif args.provider == "eastmoney":
        provider = EastmoneyDirectProvider()
    elif args.provider == "eastmoney-playwright":
        provider = EastmoneyPlaywrightProvider()
    else:
        provider = TushareDailyProvider()
    if args.codes:
        provider.stock_codes = lambda: args.codes  # type: ignore[method-assign]
    report = run_scan(provider, report_date, limit=args.limit)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
