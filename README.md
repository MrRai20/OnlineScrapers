# OnlineScrapers

[![CI](https://github.com/MrRai20/OnlineScrapers/actions/workflows/ci.yml/badge.svg)](https://github.com/MrRai20/OnlineScrapers/actions/workflows/ci.yml)
[![Tests](https://github.com/MrRai20/OnlineScrapers/actions/workflows/tests.yml/badge.svg)](https://github.com/MrRai20/OnlineScrapers/actions/workflows/tests.yml)
[![Release](https://img.shields.io/github/v/release/MrRai20/OnlineScrapers?display_name=tag&sort=semver)](https://github.com/MrRai20/OnlineScrapers/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python 3.10–3.11](https://img.shields.io/badge/python-3.10–3.11-blue.svg)

**Lightweight scrapers with a unified CLI wrapper.**  
Keep your existing scripts **unchanged**; run them via `merge_cli.py`, and (optionally) bundle Markdown outputs into **EPUB**.

---

## Features
- Unified CLI wrapper (`merge_cli.py`) for both **wiki** and **novel** scrapers (no code changes inside your scripts).
- Optional **bundle** command to merge multiple Markdown files and produce a minimal **EPUB**.
- Tests ready (no network): dummy scripts + end-to-end wrapper checks.
- CI-ready (Ruff + Pytest matrix) with green, recruiter-friendly badges.

---

## Quick Start

```bash
# (optional) create & activate a virtual environment
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# . .\.venv\Scripts\Activate.ps1

# install runtime deps
pip install -U pip
pip install -r requirements.txt
