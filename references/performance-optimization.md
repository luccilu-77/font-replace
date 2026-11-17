# 不降质加速规则

本文件只处理缓存、复用、返修范围和迭代停止条件。交付物与质量标准以 `SKILL.md` 和 [psd-output-guidelines.md](psd-output-guidelines.md) 为准。

## 总原则

只减少重复扫描、重复清理、重复启动和重复写模板，不省略当前任务所需的验证步骤。

## 字体名缓存

优先顺序：

1. 先查 `references/font-name-cache.md`。
2. 再查当前任务或历史输出中的 `*_report.json`。
3. 缓存没有命中，才调用 Photoshop 字体列表或新建测试文字层读取 `layer.textItem.font`。

缓存命中后仍要在最终 report 中验证 `actualFont`。如果 `actualFont` 变成 `AdobeHeiti`、`SimHei`、`MicrosoftYaHei` 或普通黑体，缓存视为失效，必须重新确认 PostScript name 或安装字体。

新确认的字体名要记录到任务 report；在维护 skill 时可补充进 `font-name-cache.md`。

## 复用清理底图

已通过视觉检查的 image 2 清理底图可以复用。以下情况不要重新跑 image 2：

- 字体名错误或回退。
- 字号、位置、颜色、描边、阴影需要微调。
- PSD 没有正确保存或 PNG 导出失败。
- 文案分层方式需要调整。

以下情况才重新跑 image 2：

- 清理区域仍有明显旧字灰影、残笔、污痕。
- 非目标内容被误删或变形。
- 用户明确要求重新用 image 2 清理。
- 新增了之前没有清理的目标文字区域。

重新清理时只描述失败区域，不要让 image 2 重绘整张图。

## Photoshop 常驻与模板化

尽量复用已打开的 Photoshop 实例，只执行新的 JSX 文件；不要每个小改动都反复启动应用。

每个任务的 JSX 应复用稳定函数：

- `colorFromHex`
- `boundsPx`
- `alignLayerToBox`
- `addTextLayer`
- `applyStroke` / `applyShadow` 等图层样式函数
- `addHiddenReference`
- `writeReport`
- PSD 保存与 PNG 导出函数

每次新任务只改：

- 输入/输出路径。
- 原图尺寸与清理底图尺寸。
- 字体配置。
- 文字 specs 列表。
- 少量必要的图层样式。

## 坐标与高清输出

先在原图尺寸上记录 bbox。若 image 2 输出为高清尺寸，按比例映射：

```javascript
var sx = cleanW / sourceW;
var sy = cleanH / sourceH;
function box(x, y, w, h) {
  return [x * sx, y * sy, w * sx, h * sy];
}
```

这样既能保持原图位置，又能利用 image 2 高清底图。不要在高清图上重新凭感觉找位置。

## 只重跑失败环节

- 字体回退：只修 font name/安装状态，重导 PSD/PNG。
- 文字偏移：只修 bbox、字号、tracking、leading 或旋转，重导 PSD/PNG。
- 清理残留：只重跑 image 2 清理残留区域，再重导 PSD/PNG。
- 预览不是成品：只修导出和最终回复，不重做底图。
- PSD 无可编辑文字层：修 Photoshop JSX 生成方式，不用 `ag-psd` 写最终 PSD。

## 文案位置修复上限

文案位置不正确时最多给两次机会：

1. 初版 Photoshop 导出是第 1 次机会。
2. 发现位置问题后，只允许做 1 次位置修复并重导，这是第 2 次机会。

如果第 2 次导出后位置仍明显不正确，停止继续微调，不再反复修改 bbox、字号或 tracking。交付当前 PSD 和 PNG，并说明 PSD 中文字层可编辑，后续交由人工在 Photoshop 中调整。

这个限制只针对“位置/视觉对齐微调”。字体回退、PSD 无文字层、文件未生成、清理底图明显脏等硬性质量问题不算位置微调，仍必须先修到可交付底线；但不能用这些修复作为借口无限调整位置。

## 返修后的最低验证集

返修完成后至少执行：

- 读取 report，检查每个目标层 `actualFont` 等于预期 font name。
- 用 `ag-psd` 读取 PSD，确认存在 text layer，内容正确。
- 打开最终 PNG 预览，检查清理残留、错位、遮挡和非目标内容。

只有当用户指出问题、画面很复杂、或字体/清理失败时，才扩大验证范围。
