#!/usr/bin/env python3
"""Build the machine-readable Photoshop font-name map from bundled TTF files."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path


KNOWN_ALIASES = {
    "zihun-guochaoshoushu": ["zihun43hao-guochaoshoushu-Regular"],
    "zihun-zhengkuchaojihei": [
        "zihun143hao-zhengkuchaojihei-Heavy",
        "zihun143hao-zhengkuchaojihei-Regular",
    ],
}


def read_name_table(path: Path) -> dict[str, list[str]]:
    data = path.read_bytes()
    num_tables = struct.unpack_from(">H", data, 4)[0]
    tables: dict[str, tuple[int, int]] = {}
    for index in range(num_tables):
        base = 12 + index * 16
        tag = data[base : base + 4].decode("ascii")
        _, offset, length = struct.unpack_from(">III", data, base + 4)
        tables[tag] = (offset, length)
    if "name" not in tables:
        raise ValueError(f"{path.name}: missing OpenType name table")

    offset, _ = tables["name"]
    _, count, string_offset = struct.unpack_from(">HHH", data, offset)
    result = {"family": [], "subfamily": [], "full_name": [], "postscript_name": []}
    id_to_key = {1: "family", 2: "subfamily", 4: "full_name", 6: "postscript_name"}
    for index in range(count):
        record = struct.unpack_from(">HHHHHH", data, offset + 6 + index * 12)
        platform_id, _, _, name_id, length, relative_offset = record
        if name_id not in id_to_key or platform_id not in (0, 3):
            continue
        raw = data[
            offset + string_offset + relative_offset :
            offset + string_offset + relative_offset + length
        ]
        value = raw.decode("utf-16-be", errors="replace").strip("\x00 ")
        bucket = result[id_to_key[name_id]]
        if value and value not in bucket:
            bucket.append(value)
    return result


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--font-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    entries = []
    for font in manifest["fonts"]:
        internal = read_name_table(args.font_dir / font["file"])
        candidates = unique(
            [font.get("photoshop_font_name", "")]
            + internal["postscript_name"]
            + KNOWN_ALIASES.get(font["id"], [])
        )
        entries.append(
            {
                "id": font["id"],
                "display_name": font["display_name"],
                "file": font["file"],
                "bundled_internal_names": internal,
                "photoshop_candidates": candidates,
                "lock_rule": "Use the first candidate that appears in Photoshop and confirm actualFont equals it.",
            }
        )

    payload = {
        "schema_version": 1,
        "purpose": "Resolve version-dependent Photoshop/PostScript font names before creating text layers.",
        "entries": entries,
    }
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} font entries to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
