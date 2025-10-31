# tests/test_quick.py
from __future__ import annotations
import sys, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "merge_cli.py"

def _run(argv: list[str]):
    return subprocess.run([sys.executable, *argv], cwd=ROOT, text=True, capture_output=True, timeout=45)

def test_help_runs():
    assert WRAPPER.exists(), f"merge_cli.py not found in {ROOT}"
    res = _run([str(WRAPPER), "--help"])
    assert res.returncode == 0

def test_bundle_md_and_epub(tmp_path: Path):
    (tmp_path / "a.md").write_text("# A\n\npara a\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("# B\n\npara b\n", encoding="utf-8")
    merged = tmp_path / "merged.md"
    book = tmp_path / "book.epub"
    res = _run([str(WRAPPER), "bundle", "--inputs", str(tmp_path / "*.md"),
                "--md", str(merged), "--epub", str(book)])
    assert res.returncode == 0
    assert merged.exists() and merged.stat().st_size > 0
    assert book.exists() and book.stat().st_size > 0
