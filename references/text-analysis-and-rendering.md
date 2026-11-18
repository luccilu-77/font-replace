# 文本分析与本地渲染

## 必须保留

- 文案内容不变。
- 文字块位置不变。
- 字号比例不变。
- 旋转、倾斜、行距和字距尽量复刻。
- 填充、描边、阴影、外发光、偏移描边和透明度尽量复刻。

## 布局 JSON

`scripts/render_text_replacement.py` 接受以下结构：

```json
{
  "texts": [
    {
      "text": "极速团战",
      "block_id": "main-title",
      "role": "主标题",
      "orientation": "horizontal",
      "bbox": [280, 700, 350, 95],
      "rotation": -3,
      "fill": "#ffffff",
      "stroke_layers": [
        {"color": "#ff4ca6", "width": 12, "offset": [0, 0]},
        {"color": "#28c7ff", "width": 8, "offset": [-5, 9]}
      ],
      "shadow_layers": [
        {"color": "#1c72d8", "offset": [-8, 12], "blur": 0, "opacity": 0.8}
      ],
      "opacity": 1,
      "z_index": 10
    }
  ]
}
```

字段说明：

- `text`：原文案。
- `block_id`：语义文字块标识。OCR 逐字结果属于同一横排或竖排文本框时使用同一 `block_id`。
- `role`：主标题、副标题、正文、说明或装饰文字，用于 Photoshop 分组。
- `orientation`：`horizontal` 或 `vertical`。竖排文字使用一个竖排文本框，不按单字拆层。
- `bbox`：`[x, y, width, height]`，以原图像素坐标为准。
- `rotation`：角度，正数顺时针。
- `fill`：文字填充色。
- `stroke_layers`：从外到内或从底到上记录描边层。
- `shadow_layers`：阴影、偏移描边、立体投影。
- `opacity`：0 到 1。
- `z_index`：层级，数值越大越靠上。
- `layer_name`：Photoshop 图层名，由文案生成；长文案截断，同名层追加序号。
- `layer_group`：Photoshop 图层组，例如 `10-主标题`。
- `split_reason`：只有确实需要按字符或片段拆分时填写原因。

布局记录完成后运行：

```bash
python scripts/prepare_photoshop_layers.py --layout layout.json --out layout.ps.json --audit-out layer-audit.json
```

该步骤会按 `block_id` 合并逐字记录、处理竖排文本、生成唯一图层名并统计文字层数量。

## 推荐分析步骤

1. 先识别文案，不确定时向用户确认。
2. 估算文字包围盒、基线方向和横排/竖排方向；先确定语义块，再记录字符。
3. 拆解字效层级：底层投影、外描边、内描边、主填充。
4. 选择匹配字体后，先试排透明文字层。
5. 对比原图位置和视觉重量，微调 `bbox`、`rotation`、描边宽度和偏移。
6. 检查是否存在连续单字层；能用一个文本框完成时必须合并。

## 样图文字分析示例

对“极速团战”游戏活动图：

- 文案：`极速团战`。
- 位置：底部黄色斜切 Banner 上方。
- 字效：白色填充、粗粉色描边、青蓝色偏移描边/投影、轻微右倾。
- 后续处理：用 image 2 清理目标文字，再用 Photoshop 原生可编辑 `TEXT` 图层按原 bbox 放回。
