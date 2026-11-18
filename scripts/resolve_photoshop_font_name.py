#!/usr/bin/env python3
"""Resolve and lock a bundled font against a Photoshop font inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_available(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8-sig")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return {part.strip() for line in text.splitlines() for part in line.split("\t") if part.strip()}

    values: set[str] = set()
    stack = [payload]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
        elif isinstance(item, str):
            values.add(item.strip())
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--font", required=True, help="Font id, display name, or bundled filename")
    parser.add_argument("--available-fonts", type=Path, required=True, help="Photoshop inventory as JSON or TSV")
    args = parser.parse_args()

    name_map = json.loads(args.map.read_text(encoding="utf-8"))
    entry = next(
        (
            item
            for item in name_map["entries"]
            if args.font in (item["id"], item["display_name"], item["file"])
        ),
        None,
    )
    if entry is None:
        print(json.dumps({"status": "unknown-font", "query": args.font}, ensure_ascii=False))
        return 2

    available = load_available(args.available_fonts)
    resolved = next((name for name in entry["photoshop_candidates"] if name in available), None)
    result = {
        "status": "locked" if resolved else "not-found",
        "id": entry["id"],
        "display_name": entry["display_name"],
        "resolved_photoshop_font_name": resolved,
        "candidates_checked": entry["photoshop_candidates"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if resolved else 3


if __name__ == "__main__":
    raise SystemExit(main())
