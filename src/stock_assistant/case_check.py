from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, timedelta

from .data_provider import AkshareDailyDataProvider
from .akshare_provider import AkshareSinaDailyProvider
from .eastmoney import EastmoneyDirectProvider
from .eastmoney_playwright import EastmoneyPlaywrightProvider
from .tushare_provider import TushareDailyProvider
from .scanner import scan_tulong_for_bars
from .strategy_tulong import estimate_d1_support, is_d1_first_board, is_d2_pullback


@dataclass(frozen=True)
class CaseResult:
    code: str
    name: str
    d2_date: date
    is_d1: bool
    is_d2: bool
    reason: str
    signal_count: int


def check_case(code: str, name: str, d2_date: date, provider=None) -> CaseResult:
    provider = provider or AkshareDailyDataProvider()
    bars = provider.history(code, start=d2_date - timedelta(days=20), end=d2_date)
    if len(bars) < 3:
        return CaseResult(code, name, d2_date, False, False, "历史数据不足", 0)
    yesterday, d1, d2 = bars[-3], bars[-2], bars[-1]
    is_d1 = is_d1_first_board(d1, yesterday)
    if not is_d1:
        return CaseResult(code, name, d2_date, False, False, f"前一交易日 {d1.trade_date} 不符合D1首板", 0)
    support = estimate_d1_support(d1)
    is_d2, reason = is_d2_pullback(d1, d2, support)
    signals = scan_tulong_for_bars(bars)
    return CaseResult(code, name, d2_date, is_d1, is_d2, reason, len(signals))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=["jialitu", "tianan", "all"], default="all")
    parser.add_argument("--provider", choices=["eastmoney", "eastmoney-playwright", "akshare", "akshare-sina", "tushare"], default="akshare-sina")
    args = parser.parse_args()
    cases = []
    if args.case in ("jialitu", "all"):
        cases.append(("603912", "佳力图", date(2022, 12, 29)))
    if args.case in ("tianan", "all"):
        cases.append(("603725", "天安新材", date(2023, 7, 28)))
    if args.provider == "eastmoney-playwright":
        provider = EastmoneyPlaywrightProvider()
    elif args.provider == "eastmoney":
        provider = EastmoneyDirectProvider()
    elif args.provider == "akshare":
        provider = AkshareDailyDataProvider()
    elif args.provider == "akshare-sina":
        provider = AkshareSinaDailyProvider()
    else:
        provider = TushareDailyProvider()
    for code, name, d2_date in cases:
        try:
            result = check_case(code, name, d2_date, provider)
            print(result)
        except Exception as exc:
            print(f"{code} {name} {d2_date}: 数据获取失败：{type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
