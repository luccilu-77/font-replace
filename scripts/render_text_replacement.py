#!/usr/bin/env python3
"""Render replacement text from a layout JSON onto a cleaned background image."""

from __future__ import annotations

import argparse
import json
import math
import shutil
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def parse_color(value: str | None, opacity: float = 1.0) -> tuple[int, int, int, int]:
    if not value:
        return (255, 255, 255, round(255 * opacity))
    value = value.strip()
    if value.startswith("#"):
        value = value[1:]
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if len(value) == 6:
        r, g, b = int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)
        return (r, g, b, round(255 * opacity))
    if len(value) == 8:
        r, g, b, a = (
            int(value[0:2], 16),
            int(value[2:4], 16),
            int(value[4:6], 16),
            int(value[6:8], 16),
        )
        return (r, g, b, round(a * opacity))
    raise ValueError(f"Unsupported color: {value!r}")


def copy_font_to_ascii_path(font_path: Path, tmp_dir: Path) -> Path:
    suffix = font_path.suffix or ".ttf"
    target = tmp_dir / f"font{suffix}"
    shutil.copy2(font_path, target)
    return target


def text_bbox(font: ImageFont.FreeTypeFont, text: str, stroke_width: int = 0) -> tuple[int, int, int, int]:
    probe = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    draw = ImageDraw.Draw(probe)
    return draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)


def fit_font(font_path: Path, text: str, box_w: int, box_h: int, max_stroke: int) -> ImageFont.FreeTypeFont:
    low, high = 8, max(16, box_h * 3)
    best = ImageFont.truetype(str(font_path), low)
    for _ in range(18):
        mid = (low + high) // 2
        font = ImageFont.truetype(str(font_path), mid)
        x0, y0, x1, y1 = text_bbox(font, text, max_stroke)
        tw, th = x1 - x0, y1 - y0
        if tw <= box_w and th <= box_h:
            best = font
            low = mid + 1
        else:
            high = mid - 1
    return best


def render_text_item(size: tuple[int, int], font_path: Path, item: dict[str, Any]) -> Image.Image:
    text = str(item["text"])
    x, y, w, h = [round(v) for v in item["bbox"]]
    rotation = float(item.get("rotation", 0))
    opacity = float(item.get("opacity", 1))
    stroke_layers = item.get("stroke_layers") or []
    shadow_layers = item.get("shadow_layers") or []
    max_stroke = max([round(float(s.get("width", 0))) for s in stroke_layers] + [0])

    font_size = item.get("font_size")
    if font_size:
        font = ImageFont.truetype(str(font_path), round(float(font_size)))
    else:
        font = fit_font(font_path, text, w, h, max_stroke)

    pad = max(64, max_stroke * 4 + 48)
    canvas_w = max(1, w + pad * 2)
    canvas_h = max(1, h + pad * 2)
    text_layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)

    bx0, by0, bx1, by1 = text_bbox(font, text, max_stroke)
    tx = pad + (w - (bx1 - bx0)) / 2 - bx0
    ty = pad + (h - (by1 - by0)) / 2 - by0

    for shadow in shadow_layers:
        offset = shadow.get("offset", [0, 0])
        sx, sy = float(offset[0]), float(offset[1])
        blur = float(shadow.get("blur", 0))
        shadow_opacity = opacity * float(shadow.get("opacity", 1))
        shadow_color = parse_color(shadow.get("color", "#000000"), shadow_opacity)
        shadow_img = Image.new("RGBA", text_layer.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        shadow_draw.text((tx + sx, ty + sy), text, font=font, fill=shadow_color, stroke_width=max_stroke, stroke_fill=shadow_color)
        if blur > 0:
            shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(blur))
        text_layer = Image.alpha_composite(text_layer, shadow_img)
        draw = ImageDraw.Draw(text_layer)

    for stroke in stroke_layers:
        offset = stroke.get("offset", [0, 0])
        sw = round(float(stroke.get("width", 0)))
        color = parse_color(stroke.get("color", "#000000"), opacity * float(stroke.get("opacity", 1)))
        draw.text((tx + float(offset[0]), ty + float(offset[1])), text, font=font, fill=color, stroke_width=sw, stroke_fill=color)

    fill = parse_color(item.get("fill", "#ffffff"), opacity)
    draw.text((tx, ty), text, font=font, fill=fill)

    if abs(rotation) > 0.01:
        text_layer = text_layer.rotate(-rotation, resample=Image.Resampling.BICUBIC, expand=True)

    positioned = Image.new("RGBA", size, (0, 0, 0, 0))
    px = round(x + w / 2 - text_layer.width / 2)
    py = round(y + h / 2 - text_layer.height / 2)
    positioned.alpha_composite(text_layer, (px, py))
    return positioned


def load_layout(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    texts = data.get("texts", data if isinstance(data, list) else None)
    if not isinstance(texts, list):
        raise ValueError("Layout JSON must be a list or an object with a 'texts' list.")
    for item in texts:
        for field in ("text", "bbox", "fill", "stroke_layers", "shadow_layers", "opacity", "z_index"):
            if field not in item:
                raise ValueError(f"Missing required field {field!r} in text item: {item}")
        if len(item["bbox"]) != 4:
            raise ValueError(f"bbox must be [x, y, width, height]: {item}")
    return sorted(texts, key=lambda t: float(t.get("z_index", 0)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--background", required=True, help="Cleaned background image path.")
    parser.add_argument("--font", required=True, help="Local font path.")
    parser.add_argument("--layout", required=True, help="Text layout JSON path.")
    parser.add_argument("--out", required=True, help="Final PNG output path.")
    parser.add_argument("--text-layer-out", help="Optional transparent text layer PNG output path.")
    parser.add_argument("--layout-out", help="Optional normalized layout JSON output path.")
    args = parser.parse_args()

    background_path = Path(args.background)
    font_path = Path(args.font)
    layout_path = Path(args.layout)
    out_path = Path(args.out)

    base = Image.open(background_path).convert("RGBA")
    text_accum = Image.new("RGBA", base.size, (0, 0, 0, 0))
    texts = load_layout(layout_path)

    with tempfile.TemporaryDirectory(prefix="font-replace-") as tmp:
        safe_font = copy_font_to_ascii_path(font_path, Path(tmp))
        for item in texts:
            text_accum = Image.alpha_composite(text_accum, render_text_item(base.size, safe_font, item))

    final = Image.alpha_composite(base, text_accum)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(out_path)

    if args.text_layer_out:
        text_layer_path = Path(args.text_layer_out)
        text_layer_path.parent.mkdir(parents=True, exist_ok=True)
        text_accum.save(text_layer_path)

    if args.layout_out:
        layout_out = Path(args.layout_out)
        layout_out.parent.mkdir(parents=True, exist_ok=True)
        layout_out.write_text(json.dumps({"texts": texts}, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
