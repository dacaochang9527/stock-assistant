from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path

from .alerting import Alert, AlertDeduper, FileNotifier


def load_watchlist(path: str | Path) -> list[dict[str, str]]:
    p = Path(path)
    if not p.exists():
        return []
    with p.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def evaluate_tulong_d3(row: dict[str, str], current_price: float, now: datetime) -> Alert | None:
    trigger = float(row["trigger_price"])
    invalid = float(row["invalid_price"])
    code = row["code"]
    name = row.get("name", code)
    if current_price < invalid:
        return Alert(
            key=f"{code}:tulong:invalid",
            title=f"屠龙策略失效 {code} {name}",
            body=f"当前价 {current_price:.2f} 跌破失效价 {invalid:.2f}，按策略不做T/不补仓。",
            created_at=now,
        )
    if current_price < trigger:
        return Alert(
            key=f"{code}:tulong:d3_underwater",
            title=f"屠龙D3水下观察 {code} {name}",
            body=f"当前价 {current_price:.2f} 低于观察价 {trigger:.2f}，失效价 {invalid:.2f}。",
            created_at=now,
        )
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--watchlist", default="data/watchlists/tulong_d3.csv")
    parser.add_argument("--prices", default="data/watchlists/current_prices.csv")
    parser.add_argument("--out", default="reports/alerts.log")
    args = parser.parse_args()
    watch = load_watchlist(args.watchlist)
    prices = {row["code"]: float(row["price"]) for row in load_watchlist(args.prices)}
    deduper = AlertDeduper()
    notifier = FileNotifier(args.out)
    now = datetime.now()
    for row in watch:
        code = row["code"]
        if code not in prices:
            continue
        alert = evaluate_tulong_d3(row, prices[code], now)
        if alert and deduper.should_send(alert.key, now):
            notifier.send(alert)
            print(alert.title)


if __name__ == "__main__":
    main()
