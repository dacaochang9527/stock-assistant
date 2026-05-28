from __future__ import annotations


def is_beijing_exchange(code: str) -> bool:
    return code.startswith(("8", "4"))


def is_st_name(name: str) -> bool:
    normalized = name.upper()
    return "ST" in normalized or "退" in normalized


def pass_basic_filter(
    *,
    code: str,
    name: str,
    close: float,
    avg_amount_20d: float,
    listed_days: int | None = None,
    min_price: float = 3,
    min_avg_amount_20d: float = 100_000_000,
) -> tuple[bool, str]:
    if is_beijing_exchange(code):
        return False, "北交所股票暂不纳入"
    if is_st_name(name):
        return False, "ST/退市风险股票排除"
    if close < min_price:
        return False, "股价低于最低阈值"
    if avg_amount_20d < min_avg_amount_20d:
        return False, "20日日均成交额不足"
    if listed_days is not None and listed_days < 60:
        return False, "上市未满60个交易日"
    return True, "通过基础过滤"
