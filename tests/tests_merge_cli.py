# tests/test_merge_cli.py
from __future__ import annotations
import sys
import subprocess
from pathlib import Path
import textwrap
import glob

ROOT = Path(__file__).resolve().parents[1]

def find_wrapper() -> Path | None:
    # Look for merge_cli in repo root first; allow variants like merge_cli.py / MergeCLI.py
    candidates = list(ROOT.glob("merge_cli*.py")) + list(ROOT.glob("Merge*cli*.py"))
    return next(iter(candidates), None)

WRAPPER = find_wrapper()

def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )

def _write_dummy_scraper(path: Path) -> None:
    code = textwrap.dedent(
        r"""
        import argparse, pathlib, sys
        p = argparse.ArgumentParser()
        p.add_argument("--base-url"); p.add_argument("--page")
        p.add_argument("--start-url"); p.add_argument("--out")
        args, _ = p.parse_known_args()
        outp = pathlib.Path(args.out or "out.md")
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text("# Dummy Output\n\nOK\n", encoding="utf-8")
        print("DONE:", outp)
        """
    )
    path.write_text(code, encoding="utf-8")

def _tail(s: str, n: int = 800) -> str:
    return s[-n:] if len(s) > n else s

def test_wrapper_present():
    if WRAPPER is None:
        import pytest
        pytest.skip(f"No wrapper found in repo root (expected merge_cli*.py). Found: {list(ROOT.iterdir())}")

def test_help_runs():
    if WRAPPER is None:
        import pytest; pytest.skip("wrapper missing")
    res = _run([str(WRAPPER), "--help"], ROOT)
    if res.returncode != 0:
        print("\n--- HELP STDOUT ---\n", _tail(res.stdout))
        print("\n--- HELP STDERR ---\n", _tail(res.stderr))
    assert res.returncode == 0

def test_wiki_and_novel_flows_without_network(tmp_path: Path):
    if WRAPPER is None:
        import pytest; pytest.skip("wrapper missing")
    dummy = tmp_path / "dummy_scraper.py"
    _write_dummy_scraper(dummy)

    # WIKI
    wiki_out = tmp_path / "out" / "The_Force.md"
    res_wiki = _run(
        [str(WRAPPER), "wiki",
         "--script", str(dummy),
         "--base-url", "https://example.fandom.com",
         "--page", "The Force",
         "--out", str(wiki_out)],
        ROOT,
    )
    if res_wiki.returncode != 0:
        print("\n--- WIKI STDOUT ---\n", _tail(res_wiki.stdout))
        print("\n--- WIKI STDERR ---\n", _tail(res_wiki.stderr))
    assert res_wiki.returncode == 0
    assert wiki_out.exists()
    assert "dummy output" in wiki_out.read_text(encoding="utf-8").lower()

    # NOVEL
    novel_out = tmp_path / "out" / "Novel.md"
    res_novel = _run(
        [str(WRAPPER), "novel",
         "--script", str(dummy),
         "--start-url", "https://novel.example/ch1",
         "--out", str(novel_out)],
        ROOT,
    )
    if res_novel.returncode != 0:
        print("\n--- NOVEL STDOUT ---\n", _tail(res_novel.stdout))
        print("\n--- NOVEL STDERR ---\n", _tail(res_novel.stderr))
    assert res_novel.returncode == 0
    assert novel_out.exists()
    assert "dummy output" in novel_out.read_text(encoding="utf-8").lower()

def test_bundle_builds_md_and_epub(tmp_path: Path):
    if WRAPPER is None:
        import pytest; pytest.skip("wrapper missing")
    # Create two temporary markdown files
    (tmp_path / "a.md").write_text("# A\n\npara a\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("# B\n\npara b\n", encoding="utf-8")

    merged_md = tmp_path / "merged.md"
    book_epub = tmp_path / "book.epub"

    # Pass the glob pattern; merge_cli should internally glob inputs
    res = _run(
        [str(WRAPPER), "bundle",
         "--inputs", str(tmp_path / "*.md"),
         "--md", str(merged_md),
         "--epub", str(book_epub),
         "--title", "Collected",
         "--author", "OnlineScrapers"],
        ROOT,
    )
    if res.returncode != 0:
        print("\n--- BUNDLE STDOUT ---\n", _tail(res.stdout))
        print("\n--- BUNDLE STDERR ---\n", _tail(res.stderr))
    assert res.returncode == 0
    assert merged_md.exists()
    assert book_epub.exists() and book_epub.stat().st_size > 0
