#!/usr/bin/env python3
"""Normalize layout JSON for clean, editable Photoshop text layers."""

from __future__ import annotations

import argparse
import copy
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


STYLE_KEYS = (
    "font_id",
    "font",
    "photoshop_font_name",
    "font_size",
    "fill",
    "stroke_layers",
    "shadow_layers",
    "opacity",
    "rotation",
    "orientation",
    "role",
    "layer_group",
)

ROLE_GROUPS = {
    "主标题": "10-主标题",
    "副标题": "20-副标题",
    "正文": "30-正文与说明",
    "说明": "30-正文与说明",
    "装饰文字": "40-装饰文字",
}


def load_texts(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    texts = data.get("texts", data if isinstance(data, list) else None)
    if not isinstance(texts, list):
        raise ValueError("Layout must be a list or an object containing a texts list")
    return [copy.deepcopy(item) for item in texts]


def clean_layer_name(text: str, max_length: int) -> str:
    name = re.sub(r"[\x00-\x1f\x7f]+", " ", str(text))
    name = re.sub(r"\s+", " ", name).strip()
    name = name or "文本"
    if len(name) > max_length:
        name = name[: max(1, max_length - 1)].rstrip() + "…"
    return name


def unique_layer_name(base: str, seen: dict[str, int], max_length: int) -> str:
    seen[base] += 1
    index = seen[base]
    if index == 1:
        return base
    suffix = f"-{index:02d}"
    stem = base[: max(1, max_length - len(suffix))].rstrip("… ")
    return stem + suffix


def bbox_union(items: list[dict[str, Any]]) -> list[float]:
    boxes = [item["bbox"] for item in items]
    x0 = min(float(box[0]) for box in boxes)
    y0 = min(float(box[1]) for box in boxes)
    x1 = max(float(box[0]) + float(box[2]) for box in boxes)
    y1 = max(float(box[1]) + float(box[3]) for box in boxes)
    return [x0, y0, x1 - x0, y1 - y0]


def same_style(items: list[dict[str, Any]]) -> bool:
    first = items[0]
    for item in items[1:]:
        for key in STYLE_KEYS:
            if item.get(key) != first.get(key):
                return False
    return True


def merge_block(items: list[dict[str, Any]]) -> dict[str, Any]:
    if len(items) == 1:
        result = items[0]
        result["source_item_count"] = 1
        return result
    if not same_style(items):
        raise ValueError(f"block_id={items[0].get('block_id')!r} contains incompatible styles")
    orientation = items[0].get("orientation", "horizontal")
    if orientation == "vertical":
        ordered = sorted(items, key=lambda item: (float(item["bbox"][1]), float(item["bbox"][0])))
    else:
        ordered = sorted(items, key=lambda item: (float(item["bbox"][0]), float(item["bbox"][1])))
    result = ordered[0]
    joiner = str(result.get("joiner", ""))
    result["text"] = joiner.join(str(item.get("text", "")) for item in ordered)
    result["bbox"] = bbox_union(ordered)
    result["source_item_count"] = len(ordered)
    result.pop("char_index", None)
    return result


def prepare(texts: list[dict[str, Any]], max_name_length: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    standalone: list[dict[str, Any]] = []
    for item in texts:
        if "text" not in item or "bbox" not in item:
            raise ValueError(f"Each item needs text and bbox: {item}")
        item.setdefault("orientation", "horizontal")
        if item["orientation"] not in ("horizontal", "vertical"):
            raise ValueError(f"Unsupported orientation: {item['orientation']!r}")
        block_id = item.get("block_id")
        if block_id:
            grouped[str(block_id)].append(item)
        else:
            standalone.append(item)

    merged = [merge_block(items) for items in grouped.values()] + standalone
    merged.sort(key=lambda item: float(item.get("z_index", 0)))

    seen: dict[str, int] = defaultdict(int)
    single_char_without_reason: list[str] = []
    for item in merged:
        base = clean_layer_name(str(item.get("text", "")), max_name_length)
        item["layer_name"] = unique_layer_name(base, seen, max_name_length)
        role = str(item.get("role", "正文"))
        item.setdefault("layer_group", ROLE_GROUPS.get(role, "30-正文与说明"))
        if len(str(item.get("text", "")).strip()) == 1 and not item.get("split_reason"):
            single_char_without_reason.append(item["layer_name"])

    audit = {
        "schema_version": 1,
        "input_item_count": len(texts),
        "output_text_layer_count": len(merged),
        "merged_item_count": len(texts) - len(merged),
        "vertical_text_layer_count": sum(item.get("orientation") == "vertical" for item in merged),
        "single_character_layers_without_split_reason": single_char_without_reason,
        "layer_names": [item["layer_name"] for item in merged],
    }
    return merged, audit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--layout", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--audit-out")
    parser.add_argument("--max-name-length", type=int, default=20)
    args = parser.parse_args()

    if args.max_name_length < 4:
        raise SystemExit("--max-name-length must be at least 4")
    texts = load_texts(Path(args.layout))
    prepared, audit = prepare(texts, args.max_name_length)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"texts": prepared}, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.audit_out:
        audit_out = Path(args.audit_out)
        audit_out.parent.mkdir(parents=True, exist_ok=True)
        audit_out.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False))


if __name__ == "__main__":
    main()
