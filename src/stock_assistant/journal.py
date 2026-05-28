from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


@dataclass(frozen=True)
class JournalEntry:
    created_at: datetime
    code: str
    name: str
    strategy: str
    signal_type: str
    action: str
    price: float
    result: str = ""
    note: str = ""


FIELDS = ["created_at", "code", "name", "strategy", "signal_type", "action", "price", "result", "note"]


def append_entry(path: str | Path, entry: JournalEntry) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    exists = p.exists()
    with p.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerow({
            "created_at": entry.created_at.isoformat(timespec="seconds"),
            "code": entry.code,
            "name": entry.name,
            "strategy": entry.strategy,
            "signal_type": entry.signal_type,
            "action": entry.action,
            "price": entry.price,
            "result": entry.result,
            "note": entry.note,
        })


def load_entries(path: str | Path) -> list[JournalEntry]:
    p = Path(path)
    if not p.exists():
        return []
    with p.open(newline="", encoding="utf-8") as f:
        rows = []
        for row in csv.DictReader(f):
            rows.append(JournalEntry(
                created_at=datetime.fromisoformat(row["created_at"]),
                code=row["code"], name=row["name"], strategy=row["strategy"],
                signal_type=row["signal_type"], action=row["action"],
                price=float(row["price"]), result=row.get("result", ""), note=row.get("note", ""),
            ))
        return rows


def render_weekly_review(entries: list[JournalEntry], week_end: date | None = None) -> str:
    week_end = week_end or date.today()
    week_start = week_end.fromordinal(week_end.toordinal() - 6)
    week_entries = [e for e in entries if week_start <= e.created_at.date() <= week_end]
    by_result: dict[str, int] = {}
    for e in week_entries:
        key = e.result or "未标记"
        by_result[key] = by_result.get(key, 0) + 1
    lines = [
        f"# 策略复盘周报 {week_start} ~ {week_end}",
        "",
        f"本周记录数：{len(week_entries)}",
        "",
        "## 结果分布",
    ]
    if not by_result:
        lines.append("- 暂无记录")
    else:
        for key, count in sorted(by_result.items()):
            lines.append(f"- {key}: {count}")
    lines.extend(["", "## 明细"])
    for e in week_entries:
        lines.append(f"- {e.created_at:%m-%d %H:%M} {e.code} {e.name} {e.strategy}/{e.signal_type} {e.action} @{e.price} {e.result} {e.note}")
    return "\n".join(lines) + "\n"
