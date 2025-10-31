# tests/test_merge_cli.py
# Pytest that exercises merge_cli.py end-to-end WITHOUT network or touching your real scrapers.
from __future__ import annotations
import os
import sys
import subprocess
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "merge_cli.py"

def _write_dummy_scraper(path: Path) -> None:
    """
    Creates a tiny script that accepts common flags from the wrapper and writes a Markdown file.
    This simulates your existing wiki/novel scrapers without changing them.
    """
    code = textwrap.dedent(
        r"""
        import argparse, pathlib, sys
        p = argparse.ArgumentParser()
        # accept a few common flags your wrapper might send
        p.add_argument("--base-url")
        p.add_argument("--page")
        p.add_argument("--start-url")
        p.add_argument("--out")
        # tolerate anything extra
        args, rest = p.parse_known_args()

        out = args.out or "out.md"
        outp = pathlib.Path(out)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text("# Dummy Output\n\nOK\n", encoding="utf-8")
        print("DONE:", outp)
        """
    )
    path.write_text(code, encoding="utf-8")

def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        timeout=40,
        check=False,
    )

def test_wrapper_help_runs():
    res = _run([str(WRAPPER), "--help"], ROOT)
    assert res.returncode == 0, res.stderr

def test_wiki_and_novel_end_to_end(tmp_path: Path):
    # Arrange: dummy scraper script
    dummy = tmp_path / "dummy_scraper.py"
    _write_dummy_scraper(dummy)

    # ---- WIKI flow ----
    wiki_out = tmp_path / "out" / "The_Force.md"
    res_wiki = _run(
        [
            str(WRAPPER),
            "wiki",
            "--script", str(dummy),
            "--base-url", "https://example.fandom.com",
            "--page", "The Force",
            "--out", str(wiki_out),
        ],
        ROOT,
    )
    if res_wiki.returncode != 0:
        print("\n--- WIKI STDOUT ---\n", res_wiki.stdout)
        print("\n--- WIKI STDERR ---\n", res_wiki.stderr)
    assert res_wiki.returncode == 0
    assert wiki_out.exists()
    assert "Dummy Output" in wiki_out.read_text(encoding="utf-8")

    # ---- NOVEL flow ----
    novel_out = tmp_path / "out" / "Novel.md"
    res_novel = _run(
        [
            str(WRAPPER),
            "novel",
            "--script", str(dummy),
            "--start-url", "https://novel.example/ch1",
            "--out", str(novel_out),
        ],
        ROOT,
    )
    if res_novel.returncode != 0:
        print("\n--- NOVEL STDOUT ---\n", res_novel.stdout)
        print("\n--- NOVEL STDERR ---\n", res_novel.stderr)
    assert res_novel.returncode == 0
    assert novel_out.exists()
    assert "Dummy Output" in novel_out.read_text(encoding="utf-8")

def test_bundle_merges_md_and_writes_epub(tmp_path: Path):
    # Prepare 2 tiny markdown files
    md1 = tmp_path / "a.md"; md1.write_text("# A\n\npara a\n", encoding="utf-8")
    md2 = tmp_path / "b.md"; md2.write_text("# B\n\npara b\n", encoding="utf-8")

    merged_md = tmp_path / "merged.md"
    book_epub = tmp_path / "book.epub"

    res = _run(
        [
            str(WRAPPER),
            "bundle",
            "--inputs", str(tmp_path / "*.md"),
            "--md", str(merged_md),
            "--epub", str(book_epub),
            "--title", "Collected",
            "--author", "OnlineScrapers",
        ],
        ROOT,
    )
    if res.returncode != 0:
        print("\n--- BUNDLE STDOUT ---\n", res.stdout)
        print("\n--- BUNDLE STDERR ---\n", res.stderr)
    assert res.returncode == 0
    assert merged_md.exists()
    # EPUB is a zip; file existence is enough for smoke
    assert book_epub.exists() and book_epub.stat().st_size > 0
