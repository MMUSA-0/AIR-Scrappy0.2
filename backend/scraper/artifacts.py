from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional

ARTIFACT_DIR = Path(os.getenv("ARTIFACT_DIR", "/tmp/artifacts")).resolve()
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def _ts() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def safe_slug(url: str) -> str:
    keep = [c if c.isalnum() else "-" for c in (url or "")]
    return ("".join(keep)).strip("-")[:120]


def save_html(html: str, url: str, tag: str = "error") -> Path:
    name = f"{_ts()}_{tag}_{safe_slug(url)}.html"
    path = ARTIFACT_DIR / name
    path.write_text(html or "", encoding="utf-8")
    return path


async def save_screenshot(page, url: str, tag: str = "error") -> Optional[Path]:
    try:
        name = f"{_ts()}_{tag}_{safe_slug(url)}.png"
        path = ARTIFACT_DIR / name
        await page.screenshot(path=path)
        return path
    except Exception:
        return None
