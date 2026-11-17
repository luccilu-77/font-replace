#!/usr/bin/env python3
"""Read family, full, and PostScript names from OpenType/TrueType files."""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path


NAME_IDS = {1: "family", 2: "subfamily", 4: "full_name", 6: "postscript_name"}


def decode_name(platform_id: int, encoding_id: int, payload: bytes) -> str:
    if platform_id in (0, 3):
        return payload.decode("utf-16-be", errors="replace").strip("\x00")
    if platform_id == 1:
        return payload.decode("mac_roman", errors="replace").strip("\x00")
    return payload.decode("latin-1", errors="replace").strip("\x00")


def read_names(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    if len(data) < 12:
        raise ValueError("File is too small to be an OpenType/TrueType font")

    num_tables = struct.unpack_from(">H", data, 4)[0]
    name_offset = None
    name_length = None
    for index in range(num_tables):
        offset = 12 + index * 16
        tag, _, table_offset, table_length = struct.unpack_from(">4sIII", data, offset)
        if tag == b"name":
            name_offset = table_offset
            name_length = table_length
            break

    if name_offset is None or name_length is None:
        raise ValueError("Font has no name table")

    _, count, string_offset = struct.unpack_from(">HHH", data, name_offset)
    strings_base = name_offset + string_offset
    values: dict[str, list[dict[str, object]]] = {value: [] for value in NAME_IDS.values()}

    for index in range(count):
        record_offset = name_offset + 6 + index * 12
        platform_id, encoding_id, language_id, name_id, length, offset = struct.unpack_from(
            ">HHHHHH", data, record_offset
        )
        field = NAME_IDS.get(name_id)
        if field is None:
            continue
        start = strings_base + offset
        payload = data[start : start + length]
        text = decode_name(platform_id, encoding_id, payload)
        if not text:
            continue
        record = {
            "value": text,
            "platform_id": platform_id,
            "encoding_id": encoding_id,
            "language_id": language_id,
        }
        if record not in values[field]:
            values[field].append(record)

    preferred: dict[str, str | None] = {}
    for field, records in values.items():
        ordered = sorted(
            records,
            key=lambda item: (
                item["platform_id"] != 3,
                item["language_id"] not in (0x0804, 0x0409, 0),
            ),
        )
        preferred[field] = str(ordered[0]["value"]) if ordered else None

    return {"file": str(path), "preferred": preferred, "records": values}


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("fonts", nargs="+")
    args = parser.parse_args()
    results = [read_names(Path(value).resolve()) for value in args.fonts]
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
