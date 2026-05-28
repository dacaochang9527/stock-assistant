from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from .journal import load_entries, render_weekly_review


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--journal", default="data/journal.csv")
    parser.add_argument("--week-end", default=date.today().isoformat())
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    report = render_weekly_review(load_entries(args.journal), date.fromisoformat(args.week_end))
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
