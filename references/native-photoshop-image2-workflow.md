# Image 2 清理与 Photoshop 重建流程

本文件用于普通栅格图的标准字体替换流程。PSD 的具体图层结构和保存验证要求见 [psd-output-guidelines.md](psd-output-guidelines.md)，文字字段和字效拆解见 [text-analysis-and-rendering.md](text-analysis-and-rendering.md)。

## 1. 确认输入和目标

记录：

- 原图路径、尺寸和色彩模式。
- 需要替换的文字块。
- 必须保留的文字、logo、二维码、水印和品牌标识。
- 用户指定字体；未指定时按原字形选择相似的字魂字体。
- Photoshop 是否可用。

只把用户明确指定的文字列入目标区域。位于画面顶部或底部的品牌文字也不能仅凭位置判断，需按 logo 或普通文案的实际角色区分。

## 2. 分析文字并确认字体

按 [text-analysis-and-rendering.md](text-analysis-and-rendering.md) 为每个文字块建立布局记录。bbox 使用原图像素坐标。

字体解析顺序：

1. 查 [font-name-cache.md](font-name-cache.md)。
2. 查当前任务或历史任务 report。
3. 缓存未命中或已失效时，用 Photoshop 测试文字层或字体 name table 确认。
4. 在最终 report 中复核 `actualFont`；缓存命中不能代替最终验证。

## 3. 使用 Image 2 清理目标文字

Image 2 只清理指定旧文字及其残影、描边、投影和碎片，不生成最终文字。提示词至少应表达：

```text
Remove only the specified target text and its remaining shadows, strokes, smudges, and fragments.
Preserve all non-target text, logos, watermarks, QR codes, subjects, products, decorations, background texture, composition, color, and lighting.
Do not add new text, pseudo-text, letters, numbers, logos, labels, symbols, or decorations.
```

多个区域应逐项描述位置和文案角色，避免把相邻的非目标文字一起清除。

## 4. 恢复尺寸并检查底图

1. 对比 Image 2 输出与原图尺寸。
2. 比例一致时缩放回原图尺寸；比例不一致时裁切或补边，并检查主体是否偏移。
3. 后续排版仍使用原图坐标；高清底图按比例映射 bbox。
4. 检查旧字残影、破碎笔画、下划线、主体边缘损伤及非目标内容误删。

底图未通过检查时，只针对失败区域重新清理。已通过检查的底图可以复用，具体复用条件见 [performance-optimization.md](performance-optimization.md)。

## 5. 在 Photoshop 中重建文字

按 [psd-output-guidelines.md](psd-output-guidelines.md) 执行：

1. 打开通过检查的清理底图。
2. 为每个目标文字块创建独立的原生 `TEXT` 图层。
3. 设置文案、真实 Photoshop font name、字号、颜色、字距、行距和旋转。
4. 读取文字层 bounds，并按目标 bbox 自动缩放和平移。
5. 使用图层样式或命名清楚的辅助效果层复刻描边、阴影和外发光。
6. 保存 PSD，导出当前可见效果 PNG，并写出字体 report。

## 6. 失败分流

- 清理残留或误删：只重跑对应区域的 Image 2 清理。
- 字体回退：修正字体安装或 font name，再重导 PSD、PNG 和 report。
- 文字位置或字效不准：修改布局数据或 Photoshop 参数，不重跑已经合格的底图。
- PSD 图层不可编辑：修正 Photoshop 生成方式，不用位图层或第三方 PSD 写入结果替代。
- 预览错误：只修正最终可见状态和 PNG 导出。

返修和停止条件见 [performance-optimization.md](performance-optimization.md)。

## 7. 最终交付

会话中展示最终替换后的 PNG，不把无字底图当成成品。交付说明列出实际字体名称、Photoshop font name、替换范围、保留范围、PSD 验证结果及文件路径。
