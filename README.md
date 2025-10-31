# OnlineScrapers

[![Tests](https://github.com/MrRai20/OnlineScrapers/actions/workflows/tests.yml/badge.svg)](https://github.com/MrRai20/OnlineScrapers/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python 3.10–3.11](https://img.shields.io/badge/python-3.10–3.11-blue.svg)

Lightweight scrapers with a **unified CLI wrapper**. Keep your existing scripts **unchanged**; run them via `merge_cli.py`, and (optionally) bundle Markdown into **EPUB**.
Work in Progress
---

## Quick Start

    # (optional) create & activate a virtual environment
    python -m venv .venv
    # macOS/Linux
    source .venv/bin/activate
    # Windows PowerShell
    # .\.venv\Scripts\Activate.ps1

    # install dependencies
    pip install -U pip
    pip install -r requirements.txt

---

## Usage (Unified CLI)

> The wrapper **shells out** to your existing scripts and forwards flags if they support them.  
> If a script is interactive, the wrapper just launches it normally.

**Run existing Wiki scraper**

    python merge_cli.py wiki ^
      --script FandomScraper.py ^
      --base-url https://starwars.fandom.com ^
      --page "The Force" ^
      --out out/The_Force.md

*(On macOS/Linux replace `^` line-breaks with `\`.)*

**Run existing Novel scraper**

    python merge_cli.py novel ^
      --script ScraperPocketHunting.py ^
      --start-url https://example.com/novel/chapter-1 ^
      --out out/Novel.md

**Bundle multiple Markdown files (MD + EPUB)**

    python merge_cli.py bundle ^
      --inputs "out/*.md" ^
      --md out/Collected.md ^
      --epub out/Collected.epub ^
      --title "Collected Works" ^
      --author "OnlineScrapers"

---

## Tests

Deterministic tests (no internet). Runs the wrapper and checks `bundle` output.

    pip install pytest
    pytest -q



---

## Security & Ethics

- **Respect robots.txt & Terms of Service.** Only scrape where permitted; content may be copyrighted.  
- **Be polite:** use a descriptive User-Agent and small delays; avoid aggressive parallelism.  
- **No secrets in repo:** never commit API keys/tokens; prefer environment variables.  
- **Local I/O:** outputs are Markdown/EPUB files; no databases/services required by default.

---

## Troubleshooting

- Run commands from the **repo root**: `python merge_cli.py ...`  
- **Windows:** if `python` isn’t found, use `py -3`.  
- Ensure `out/` is writable; the wrapper creates it when needed.  
- Interactive scripts remain interactive; the wrapper doesn’t change that.

---

## Project Structure (example)

    FandomScraper.py
    ScraperPocketHunting.py
    merge_cli.py
    requirements.txt
    tests/
      test_quick.py
      test_merge_cli.py
    .github/workflows/
      tests.yml
    out/                 # generated

---

## License

MIT — see `LICENSE`.
