#!/usr/bin/env python3
"""Validate basic text replacement outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops


REQUIRED_FIELDS = {
    "text",
    "bbox",
    "rotation",
    "fill",
    "stroke_layers",
    "shadow_layers",
    "opacity",
    "z_index",
}


def validate_layout(path: Path) -> list[str]:
    errors: list[str] = []
    data = json.loads(path.read_text(encoding="utf-8"))
    texts = data.get("texts", data if isinstance(data, list) else None)
    if not isinstance(texts, list) or not texts:
        return ["layout must contain a non-empty texts list"]
    layer_names: list[str] = []
    for idx, item in enumerate(texts):
        missing = REQUIRED_FIELDS - set(item)
        if missing:
            errors.append(f"text[{idx}] missing fields: {', '.join(sorted(missing))}")
        bbox = item.get("bbox")
        if not isinstance(bbox, list) or len(bbox) != 4:
            errors.append(f"text[{idx}] bbox must be [x, y, width, height]")
        elif bbox[2] <= 0 or bbox[3] <= 0:
            errors.append(f"text[{idx}] bbox width/height must be positive")
        orientation = item.get("orientation")
        if orientation is not None and orientation not in {"horizontal", "vertical"}:
            errors.append(f"text[{idx}] orientation must be horizontal or vertical")
        layer_name = item.get("layer_name")
        if layer_name is not None:
            layer_name = str(layer_name)
            layer_names.append(layer_name)
            if not layer_name.strip():
                errors.append(f"text[{idx}] layer_name must not be empty")
            if len(layer_name) > 20:
                errors.append(f"text[{idx}] layer_name exceeds 20 characters: {layer_name}")
    duplicates = sorted({name for name in layer_names if layer_names.count(name) > 1})
    if duplicates:
        errors.append(f"duplicate layer_name values: {', '.join(duplicates)}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", help="Original source image path.")
    parser.add_argument("--background", required=True, help="Cleaned background image path.")
    parser.add_argument("--final", required=True, help="Final replacement PNG path.")
    parser.add_argument("--text-layer", help="Transparent text layer path.")
    parser.add_argument("--layout", required=True, help="Layout JSON path.")
    args = parser.parse_args()

    errors = validate_layout(Path(args.layout))

    background = Image.open(args.background).convert("RGBA")
    final = Image.open(args.final).convert("RGBA")
    if background.size != final.size:
        errors.append(f"background and final sizes differ: {background.size} vs {final.size}")

    if args.original:
        original = Image.open(args.original)
        if original.size != final.size:
            errors.append(f"original and final sizes differ: {original.size} vs {final.size}")

    if args.text_layer:
        text_layer = Image.open(args.text_layer).convert("RGBA")
        if text_layer.size != final.size:
            errors.append(f"text layer and final sizes differ: {text_layer.size} vs {final.size}")
        alpha = text_layer.getchannel("A")
        if not alpha.getbbox():
            errors.append("text layer has no visible pixels")

    diff = ImageChops.difference(background.convert("RGB"), final.convert("RGB"))
    if not diff.getbbox():
        errors.append("final image is identical to background; no replacement text appears")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    print("OK: text replacement output passed basic validation")


if __name__ == "__main__":
    main()
