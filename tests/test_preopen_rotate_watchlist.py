from datetime import datetime
from pathlib import Path
import importlib.util
import sys


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "tulong" / "runtime" / "preopen_rotate_watchlist.py"


def load_module():
    spec = importlib.util.spec_from_file_location("preopen_rotate_watchlist", MODULE_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_timestamp_score_prefers_yyyymmdd_hhmmss_suffix(tmp_path):
    mod = load_module()
    older = tmp_path / "0529D3_watch_scan_20260529_214437.csv"
    newer = tmp_path / "0529D3_watch_scan_20260530_001500.csv"
    legacy = tmp_path / "0529D3_watch_scan_214437.csv"
    for path in (older, newer, legacy):
        path.write_text("code,name\n", encoding="utf-8")

    assert mod.timestamp_score(older)[0] == "20260529_214437"
    assert mod.timestamp_score(newer)[0] == "20260530_001500"
    assert mod.timestamp_score(legacy)[0] == ""
    assert sorted([older, newer], key=mod.timestamp_score, reverse=True)[0] == newer


def test_find_latest_source_uses_full_timestamp(monkeypatch, tmp_path):
    mod = load_module()
    monkeypatch.setattr(mod, "WATCHLIST_DIR", tmp_path)
    active = tmp_path / "tulong_active_watchlist.csv"
    monkeypatch.setattr(mod, "ACTIVE_WATCHLIST", active)

    old = tmp_path / "0529D3_watch_scan_20260529_214437.csv"
    new = tmp_path / "0529D3_watch_scan_20260530_001500.csv"
    legacy = tmp_path / "0529D3_watch_scan_214437.csv"
    for path in (old, new, legacy, active):
        path.write_text("code,name\n", encoding="utf-8")

    found = mod.find_latest_source(datetime(2026, 5, 29, 8, 50), "D3", "watch")
    assert found == new
