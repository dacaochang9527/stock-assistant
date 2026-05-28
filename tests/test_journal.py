from datetime import date, datetime

from stock_assistant.journal import JournalEntry, render_weekly_review


def test_weekly_review_counts_results():
    entries = [JournalEntry(datetime(2024, 1, 5, 10), "000001", "样例", "tulong", "D3", "observe", 10, result="有效")]
    report = render_weekly_review(entries, week_end=date(2024, 1, 7))
    assert "有效: 1" in report
    assert "本周记录数：1" in report
