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
- `bbox`：`[x, y, width, height]`，以原图像素坐标为准。
- `rotation`：角度，正数顺时针。
- `fill`：文字填充色。
- `stroke_layers`：从外到内或从底到上记录描边层。
- `shadow_layers`：阴影、偏移描边、立体投影。
- `opacity`：0 到 1。
- `z_index`：层级，数值越大越靠上。

## 推荐分析步骤

1. 先识别文案，不确定时向用户确认。
2. 估算文字包围盒和基线方向。
3. 拆解字效层级：底层投影、外描边、内描边、主填充。
4. 选择匹配字体后，先试排透明文字层。
5. 对比原图位置和视觉重量，微调 `bbox`、`rotation`、描边宽度和偏移。

## 样图文字分析示例

对“极速团战”游戏活动图：

- 文案：`极速团战`。
- 位置：底部黄色斜切 Banner 上方。
- 字效：白色填充、粗粉色描边、青蓝色偏移描边/投影、轻微右倾。
- 后续处理：用 image 2 清理目标文字，再用 Photoshop 原生可编辑 `TEXT` 图层按原 bbox 放回。
