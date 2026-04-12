from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import MigrationReport


def write_report(report: MigrationReport, path: Path, dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(report), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
