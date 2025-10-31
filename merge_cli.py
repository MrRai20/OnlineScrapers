# path: merge_cli.py
"""
Unified CLI wrapper for OnlineScrapers.
- Keeps existing scrapers unchanged.
- Calls them via subprocess.
- Optional 'bundle' to merge produced Markdown files into a single EPUB/MD.

Usage:
  # Run  existing WIKI scraper (adjust script name/args if needed)
  python merge_cli.py wiki --script FandomScraper.py --base-url https://starwars.fandom.com --page "The Force" --out out/The_Force.md

  # Run  existing NOVEL scraper (adjust script/args)
  python merge_cli.py novel --script ScraperPocketHunting.py --start-url https://example.com/ch1 --out out/Novel.md

  # Bundle multiple Markdown files into one EPUB
  python merge_cli.py bundle --inputs out/*.md --epub out/Book.epub

Notes:
- This wrapper shells out to  current scripts (no internal changes).
- If  scripts already accept flags, pass them via --extra.
- If they are interactive, the wrapper will just launch them; output path is up to the script.
"""
from __future__ import annotations

import argparse
import glob
import html
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Iterable

# ---------- tiny utils ----------

def run_script(script: Path, args: list[str]) -> int:
    """Run an existing Python script in a subprocess, streaming output."""
    if not script.exists():
        print(f"[wrapper] Script not found: {script}", file=sys.stderr)
        return 2
    cmd = [sys.executable, str(script), *args]
    print("[wrapper] Running:", " ".join(shlex.quote(x) for x in cmd))
    proc = subprocess.Popen(cmd)
    try:
        return proc.wait()
    except KeyboardInterrupt:
        proc.kill()
        return 130

def read_texts(paths: Iterable[Path]) -> list[str]:
    out: list[str] = []
    for p in paths:
        try:
            out.append(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[wrapper] Skipping {p}: {e}", file=sys.stderr)
    return out

# ---------- minimal EPUB builder (no third-party deps) ----------

from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime
import hashlib

def _uuid_from(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def _mk_xhtml(title: str, paragraphs: list[str]) -> str:
    body = [f"<h1>{html.escape(title)}</h1>"]
    for p in paragraphs:
        if not p.strip():
            body.append("<p></p>")
        else:
            body.append(f"<p>{html.escape(p)}</p>")
    body_html = "\n".join(body)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml"><head><meta charset="utf-8"/></head>
<body>{body_html}</body></html>"""

def write_epub(title: str, author: str, paragraphs: list[str], out_path: Path) -> None:
    uid = _uuid_from(title + author + str(len(paragraphs)))
    container = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>"""
    content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package version="2.0" unique-identifier="BookId" xmlns="http://www.idpf.org/2007/opf">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>{html.escape(title)}</dc:title>
    <dc:creator>{html.escape(author)}</dc:creator>
    <dc:language>en</dc:language>
    <dc:identifier id="BookId">urn:uuid:{uid}</dc:identifier>
    <dc:date>{datetime.utcnow().isoformat()}</dc:date>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <item id="chap1" href="chap1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine toc="ncx"><itemref idref="chap1"/></spine>
</package>"""
    toc = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
  <head><meta name="dtb:uid" content="{uid}"/></head>
  <docTitle><text>{html.escape(title)}</text></docTitle>
  <navMap><navPoint id="navPoint-1" playOrder="1">
    <navLabel><text>Chapter 1</text></navLabel><content src="chap1.xhtml"/>
  </navPoint></navMap>
</ncx>"""
    xhtml = _mk_xhtml(title, paragraphs)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(out_path, "w", ZIP_DEFLATED) as z:
        z.writestr("mimetype", "application/epub+zip")
        z.writestr("META-INF/container.xml", container)
        z.writestr("OEBPS/content.opf", content_opf)
        z.writestr("OEBPS/toc.ncx", toc)
        z.writestr("OEBPS/chap1.xhtml", xhtml)

# ---------- CLI ----------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Unified wrapper for existing scrapers")
    sub = p.add_subparsers(dest="cmd", required=True)

    # WIKI
    pw = sub.add_parser("wiki", help="Run existing wiki scraper script")
    pw.add_argument("--script", default="FandomScraper.py", help="Path to your wiki script")
    pw.add_argument("--base-url", help="Base URL (passed to your script if it accepts it)")
    pw.add_argument("--page", help="Page title (passed if supported)")
    pw.add_argument("--out", help="Output path (passed if supported)")
    pw.add_argument("--extra", nargs=argparse.REMAINDER, help="Anything else to pass through")

    # NOVEL
    pn = sub.add_parser("novel", help="Run existing novel scraper script")
    pn.add_argument("--script", default="ScraperPocketHunting.py", help="Path to your novel script")
    pn.add_argument("--start-url", help="Start URL (passed if supported)")
    pn.add_argument("--out", help="Output path (passed if supported)")
    pn.add_argument("--extra", nargs=argparse.REMAINDER, help="Anything else to pass through")

    # BUNDLE
    pb = sub.add_parser("bundle", help="Bundle Markdown files into a single EPUB/MD")
    pb.add_argument("--inputs", required=True, help="Glob (e.g., 'out/*.md')")
    pb.add_argument("--epub", help="EPUB output path")
    pb.add_argument("--md", help="Merged Markdown output path")
    pb.add_argument("--title", default="Collected Works")
    pb.add_argument("--author", default="OnlineScrapers")

    return p.parse_args()

def cmd_wiki(args: argparse.Namespace) -> int:
    s = Path(args.script)
    passthrough: list[str] = []
    # Append commonly used flags only if provided; many original scripts are prompt-based.
    if args.base_url: passthrough += ["--base-url", args.base_url]
    if args.page:     passthrough += ["--page", args.page]
    if args.out:      passthrough += ["--out", args.out]
    if args.extra:    passthrough += args.extra
    return run_script(s, passthrough)

def cmd_novel(args: argparse.Namespace) -> int:
    s = Path(args.script)
    passthrough: list[str] = []
    if args.start_url: passthrough += ["--start-url", args.start_url]
    if args.out:       passthrough += ["--out", args.out]
    if args.extra:     passthrough += args.extra
    return run_script(s, passthrough)

def cmd_bundle(args: argparse.Namespace) -> int:
    paths = [Path(p) for p in glob.glob(args.inputs)]
    if not paths:
        print(f"[wrapper] No files matched: {args.inputs}", file=sys.stderr)
        return 2
    texts = read_texts(paths)
    merged_md = "\n\n".join(texts).strip()
    if args.md:
        Path(args.md).parent.mkdir(parents=True, exist_ok=True)
        Path(args.md).write_text(merged_md, encoding="utf-8")
        print(f"[wrapper] Wrote merged Markdown → {args.md}")
    if args.epub:
        paragraphs = [line for block in texts for line in block.splitlines()]
        write_epub(title=args.title, author=args.author, paragraphs=paragraphs, out_path=Path(args.epub))
        print(f"[wrapper] Wrote EPUB → {args.epub}")
    if not args.md and not args.epub:
        print("[wrapper] Nothing to write (pass --md and/or --epub).", file=sys.stderr)
        return 2
    return 0

def main() -> int:
    a = parse_args()
    if a.cmd == "wiki":   return cmd_wiki(a)
    if a.cmd == "novel":  return cmd_novel(a)
    if a.cmd == "bundle": return cmd_bundle(a)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
