# tests/test_merge_cli.py
# Robust, NO-INTERNET test for your wrapper. Keeps your scrapers unchanged.
from __future__ import annotations
import sys
import subprocess
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = next(iter(list(ROOT.glob("merge_cli*.py"))), None)

def _run(argv: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *argv],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )

def _write_dummy_scraper(path: Path) -> None:
    code = textwrap.dedent(
        r"""
        import argparse, pathlib
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

def test_wrapper_exists():
    assert WRAPPER is not None, f"merge_cli*.py not found in {ROOT}"

def test_help_runs():
    res = _run([str(WRAPPER), "--help"])
    if res.returncode != 0:
        print("\n--- HELP STDOUT ---\n", _tail(res.stdout))
        print("\n--- HELP STDERR ---\n", _tail(res.stderr))
    assert res.returncode == 0

def test_wiki_and_novel_without_network(tmp_path: Path):
    dummy = tmp_path / "dummy_scraper.py"
    _write_dummy_scraper(dummy)

    # WIKI flow
    wiki_out = tmp_path / "out" / "The_Force.md"
    res_wiki = _run([
        str(WRAPPER), "wiki",
        "--script", str(dummy),
        "--base-url", "https://example.fandom.com",
        "--page", "The Force",
        "--out", str(wiki_out),
    ])
    if res_wiki.returncode != 0:
        print("\n--- WIKI STDOUT ---\n", _tail(res_wiki.stdout))
        print("\n--- WIKI STDERR ---\n", _tail(res_wiki.stderr))
    assert res_wiki.returncode == 0
    assert wiki_out.exists()
    assert "dummy output" in wiki_out.read_text(encoding="utf-8").lower()

    # NOVEL flow
    novel_out = tmp_path / "out" / "Novel.md"
    res_novel = _run([
        str(WRAPPER), "novel",
        "--script", str(dummy),
        "--start-url", "https://novel.example/ch1",
        "--out", str(novel_out),
    ])
    if res_novel.returncode != 0:
        print("\n--- NOVEL STDOUT ---\n", _tail(res_novel.stdout))
        print("\n--- NOVEL STDERR ---\n", _tail(res_novel.stderr))
    assert res_novel.returncode == 0
    assert novel_out.exists()
    assert "dummy output" in novel_out.read_text(encoding="utf-8").lower()

def test_bundle_md_and_epub(tmp_path: Path):
    (tmp_path / "a.md").write_text("# A\n\npara a\n", encoding="utf-8")
    (tmp_path / "b.md").write_text("# B\n\npara b\n", encoding="utf-8")

    merged_md = tmp_path / "merged.md"
    book_epub = tmp_path / "book.epub"

    res = _run([
        str(WRAPPER), "bundle",
        "--inputs", str(tmp_path / "*.md"),
        "--md", str(merged_md),
        "--epub", str(book_epub),
        "--title", "Collected",
        "--author", "OnlineScrapers",
    ])
    if res.returncode != 0:
        print("\n--- BUNDLE STDOUT ---\n", _tail(res.stdout))
        print("\n--- BUNDLE STDERR ---\n", _tail(res.stderr))
    assert res.returncode == 0
    assert merged_md.exists()
    assert book_epub.exists() and book_epub.stat().st_size > 0
