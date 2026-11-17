# PSD 输出规则

PSD 是本 skill 的固定交付物，不是可选模式。交付标准是：Photoshop 打开后能直接看到替换后的文字，并且每段替换文字都是可用文字工具编辑内容的 Photoshop 原生 `TEXT` 图层。

## 能力检查

先按 [environment-adaptation.md](environment-adaptation.md) 运行 `scripts/detect-environment.ps1`。后续自动化必须使用检测结果中的 Photoshop 路径和版本，不得写死 Photoshop 2024 或某台电脑的安装目录。

如果检测到旧版本或无法识别版本，先执行 `scripts/photoshop-smoke-test.jsx`，确认能创建原生文字层并读取字体名。多版本共存或自定义路径的处理也以环境适配文档为准。

如果 Photoshop 不可用，不要声称已经生成真实可编辑文字层 PSD。明确提示用户通过 Adobe Creative Cloud 安装 Photoshop 并完成首次启动，然后重新检测。可以先交付 PNG、清理底图、布局 JSON 或透明文字层作为临时辅助文件，但必须说明最终 PSD 原生文字层受阻，不能把临时文件当成完成交付。

## 字体检查

必须检查目标字体是否被 Photoshop 识别。

字体有多个名字：

- 文件名。
- 中文字体名。
- Photoshop `textItem.font` 需要的 PostScript/font name。

不能只凭字体文件名猜测 Photoshop font name。创建测试文字层后读取 `layer.textItem.font` 是最可靠的确认方式之一。

如果 Photoshop 实际使用的字体不是目标字体，尤其回退到 `AdobeHeiti`、`SimHei`、`MicrosoftYaHei`、普通黑体等，必须先修正字体安装或 font name，不能交付。

## 固定 PSD 目标

最低图层结构：

1. `00-clean-background`：image 2 / image-gen 清理后的底图。
2. `10-editable-*`：每个目标文字块一个 Photoshop 原生文字层。
3. `11-text-effects-*`：可选效果层或图层样式。
4. `90-original-reference`：可选隐藏参考层，用于人工对照。

`10-editable-*` 必须是 Photoshop 原生文字层。描边、阴影、外发光应优先使用图层样式；若需要少量辅助位图效果，必须命名为 `optional-effect-raster`，并保留可编辑文字层作为主体。

## 最终 PSD 写入方式

最终 PSD 必须由 Photoshop 原生脚本或 Photoshop 自动化保存。

不要使用 `ag-psd` 作为最终 PSD 写入方案来承诺 Photoshop 可编辑文字层。`ag-psd` 可以用于读取、诊断和验证，但它写入的 text layer 数据可能在 Photoshop 中不可见、不可正常编辑或无法正确渲染。

推荐流程：

1. 打开清理底图。
2. 创建每个 `LayerKind.TEXT` 文字层。
3. 设置 `textItem.contents`、`textItem.font`、`textItem.size`、`textItem.color`。
4. 读取文字层 bounds。
5. 自动缩放/平移到目标 bbox。
6. 保存 PSD。
7. 导出 PNG 预览。
8. 写出 report JSON。

## 验证要求

交付前验证：

- PSD 尺寸等于原图尺寸。
- Photoshop 打开后文字直接可见。
- 图层面板中每个目标文字层显示为文字层。
- 隐藏任意 `10-editable-*` 层时，对应文字消失。
- report 中 `actualFont` 等于目标字体。
- PNG 预览与 PSD 当前可见效果一致。

## 禁止

- 不得只放一张整图并称为已拆层 PSD。
- 不得在 PSD 中只放整张文字预览图冒充可编辑文字层。
- 不得把不可编辑位图文字说成可编辑文字层。
- 不得把文字转成矢量轮廓后声称可直接编辑文字内容。
- 不得让背景层盖住主体。
- 不得让装饰层压住文字。
- 不得把阴影层放到文字填充上方造成脏边。
- 不得用位图文字层替代原生文字层。
