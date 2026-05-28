from datetime import datetime, timedelta

from stock_assistant.alerting import AlertDeduper


def test_alert_deduper_blocks_same_key_inside_window():
    d = AlertDeduper(dedupe_minutes=30)
    t = datetime(2024, 1, 1, 10, 0)
    assert d.should_send("k", t)
    assert not d.should_send("k", t + timedelta(minutes=5))
    assert d.should_send("k", t + timedelta(minutes=31))
