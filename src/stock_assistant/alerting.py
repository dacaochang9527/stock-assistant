from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


@dataclass(frozen=True)
class Alert:
    key: str
    title: str
    body: str
    created_at: datetime


class AlertDeduper:
    def __init__(self, dedupe_minutes: int = 30):
        self.window = timedelta(minutes=dedupe_minutes)
        self._sent_at: dict[str, datetime] = {}

    def should_send(self, key: str, now: datetime | None = None) -> bool:
        now = now or datetime.now()
        last = self._sent_at.get(key)
        if last is not None and now - last < self.window:
            return False
        self._sent_at[key] = now
        return True


class Notifier:
    def send(self, alert: Alert) -> None:
        raise NotImplementedError


class FileNotifier(Notifier):
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def send(self, alert: Alert) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(f"[{alert.created_at:%Y-%m-%d %H:%M:%S}] {alert.title}\n{alert.body}\n\n")
