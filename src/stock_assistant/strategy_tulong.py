from __future__ import annotations

from dataclasses import dataclass

from .indicators import is_limit_up
from .models import DailyBar, StrategySignal

MAIN_BOARD_10CM_PREFIXES = ("600", "601", "603", "605", "000", "001", "002", "003")
EXCLUDED_NAME_PARTS = ("ST", "*ST", "退")


@dataclass(frozen=True)
class D1Evaluation:
    passed: bool
    reject_reason: str = ""
    d1_quality_score: float = 0.0
    d1_quality_notes: str = ""


def safe_float(value, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def hhmm_to_int(value) -> int:
    text = str(value).strip()
    if not text or text.lower() == "nan" or text == "None":
        return 240000
    try:
        return int(text)
    except ValueError:
        return 240000


def is_main_board_10cm(code: str) -> bool:
    normalized = str(code).strip().zfill(6)
    return normalized.startswith(MAIN_BOARD_10CM_PREFIXES)


def is_excluded_name(name: str) -> bool:
    text = str(name).upper()
    return any(part.upper() in text for part in EXCLUDED_NAME_PARTS)


def is_first_board_from_zt_row(row) -> tuple[bool, str]:
    stat = str(row.get("涨停统计", "") or "")
    limit_boards = safe_float(row.get("连板数"))
    if stat.startswith("1/") or limit_boards == 1:
        return True, ""
    return False, f"非首板({stat},连板{limit_boards:g})"


def evaluate_d1_quality(row) -> tuple[float, str]:
    first_seal_i = hhmm_to_int(row.get("首次封板时间"))
    breaks = safe_float(row.get("炸板次数"))
    fund = safe_float(row.get("封板资金"))
    amount = safe_float(row.get("成交额"))
    turnover = safe_float(row.get("换手率"))

    score = 50.0
    notes: list[str] = []

    if first_seal_i <= 93000:
        score += 8
        notes.append("D1早盘封板")
    elif first_seal_i <= 100000:
        score += 5
        notes.append("D1较早封板")
    elif first_seal_i >= 140000:
        score -= 5
        notes.append("D1尾盘封板降权")

    if breaks == 0:
        score += 5
        notes.append("D1未炸板")
    elif breaks <= 2:
        score += 1
        notes.append(f"D1炸板{int(breaks)}次")
    else:
        score -= 6
        notes.append(f"D1炸板{int(breaks)}次偏多")

    if fund >= 80_000_000:
        score += 5
        notes.append("封板资金较足")
    elif fund < 10_000_000:
        score -= 4
        notes.append("封板资金偏弱")

    if 200_000_000 <= amount <= 3_000_000_000:
        score += 3
        notes.append("D1成交额可跟踪")
    elif amount and amount < 100_000_000:
        score -= 4
        notes.append("D1成交额偏小")
    elif amount > 5_000_000_000:
        score -= 3
        notes.append("D1成交额过大偏拥挤")

    if 3 <= turnover <= 20:
        score += 2
        notes.append("D1换手适中")
    elif turnover > 35:
        score -= 4
        notes.append("D1换手过高")

    return score, "；".join(notes)


def evaluate_d1_board(row) -> D1Evaluation:
    code = str(row.get("代码", "")).zfill(6)
    name = str(row.get("名称", ""))
    reasons: list[str] = []

    if not is_main_board_10cm(code):
        reasons.append("20cm/北交所/非主板前缀")
    if is_excluded_name(name):
        reasons.append("ST/退市风险")

    first_board, first_board_reason = is_first_board_from_zt_row(row)
    if not first_board:
        reasons.append(first_board_reason)

    score, notes = evaluate_d1_quality(row)
    if reasons:
        return D1Evaluation(False, "；".join(reasons), score, notes)
    return D1Evaluation(True, "", score, notes)


def estimate_d1_support(d1: DailyBar, recent_platform_high: float | None = None) -> float:
    candidates = [d1.open, d1.prev_close]
    if recent_platform_high is not None:
        candidates.append(recent_platform_high)
    return max(candidates)


def is_d1_first_board(today: DailyBar, yesterday: DailyBar) -> bool:
    return (
        is_limit_up(today.close, today.limit_up_price)
        and not is_limit_up(yesterday.close, yesterday.limit_up_price)
        and today.low < today.limit_up_price * 0.98 if today.limit_up_price else False
    )


def is_d2_pullback(d1: DailyBar, d2: DailyBar, d1_support: float) -> tuple[bool, str]:
    volume_ratio = d2.volume / d1.volume if d1.volume else float("inf")
    open_gap = (d2.open / d1.close) - 1 if d1.close else 0
    high_above_open = (d2.high / d2.open) - 1 if d2.open else 0
    close_below_high = 1 - (d2.close / d2.high) if d2.high else 0

    if volume_ratio > 2:
        return False, f"D2成交量/D1={volume_ratio:.2f}，超过2倍"
    if open_gap > 0.04 and d2.close < d2.open:
        return False, "D2高开低走，疑似出货"
    if high_above_open < 0.02:
        return False, "D2盘中冲高不足"
    if close_below_high < 0.02:
        return False, "D2冲高回落特征不足"
    if d2.close < d1_support:
        return False, "D2收盘跌破D1支撑位"
    return True, f"D2冲高回落，量比{volume_ratio:.2f}，未破支撑"


def build_d3_watch_signal(d1: DailyBar, d2: DailyBar, d1_support: float) -> StrategySignal:
    return StrategySignal(
        code=d2.code,
        name=d2.name,
        strategy="tulong",
        signal_type="D3_WATCH_UNDERWATER",
        reason="D1首板后，D2冲高回落且量能未超过2倍，次日观察水下低吸机会",
        trigger_price=d2.close,
        invalid_price=d1_support,
        risk_note="若D3跌破D1支撑位，策略失效；D4/D5必须按规则退出",
    )
