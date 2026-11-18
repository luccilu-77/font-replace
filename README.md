# Font Image Text Replace 01

在不重新设计画面的前提下，只替换用户指定的普通文字字体，并保持原文案、位置、字号比例、颜色、旋转、描边、阴影、背景、主体和构图不变。文字型 Logo、品牌标识、二维码、水印以及用户未点名的文字默认保留，不进行替换；只有用户明确指定时才处理。

用户可以直接指定目标字体；未指定时，AI 会根据原文字的笔画粗细、字面宽窄、结构与重心、圆角或尖角、书写节奏及整体画面气质，从随包字体中选择字形相近的字体，也可以按主标题、副标题、正文和数字等文字角色组合使用。标准交付包括最终 PNG 预览，以及带 Photoshop 原生可编辑文字层的 PSD。精简包随附 21 款常用字魂字体，并提供 Photoshop 版本检测与确认式字体安装脚本。

## 效果示例

以下三组输入与输出图片由用户提供，用于展示不同题材中的字体替换效果。

### 示例 1：西藏旅行海报

输出字体：字魂白鸽天行体 + 字魂檀宋。

**输入**

![西藏旅行海报输入](assets/examples/example-01-tibet-input.jpg)

**输出**

![西藏旅行海报输出](assets/examples/example-01-tibet-output.png)

### 示例 2：免费接送班车时间表

输出字体：字魂公路体 + 字魂荧智。

**输入**

![班车时间表输入](assets/examples/example-02-shuttle-input.jpg)

**输出**

![班车时间表输出](assets/examples/example-02-shuttle-output.png)

### 示例 3：招聘海报

输出字体：字魂清润书体。

**输入**

![招聘海报输入](assets/examples/example-03-recruitment-input.png)

**输出**

![招聘海报输出](assets/examples/example-03-recruitment-output.png)

这些示例用于呈现字体应用前后的视觉差异，个别输出还包含轻微排版、日期格式或品牌信息调整，不作为“逐像素仅替换字体”的严格验证样本。正式任务仍以用户指定范围为准：默认保持原文案、位置、字号比例、颜色、字效和非目标内容不变，并经过旧字清理、Photoshop 原生文字层重建及字体回退验证。

示例中的字魂白鸽天行体、字魂檀宋、字魂清润书体和字魂公路体不在当前 21 款精简字体包内；复现这些效果时，需要用户另外提供字体文件。字魂荧智已包含在随包字体中。

## 能做什么

- 替换整张图或部分区域的中文、英文和数字字体。
- 保留未点名的文字、品牌 logo、二维码、水印、人物、商品和装饰。
- 用户未指定字体时，从随包字体中按原字形气质推荐合适字体。
- 使用 Image 2 / image-gen 清除目标旧文字及残影。
- 使用 Photoshop 创建独立、原生、可编辑的 `TEXT` 图层。
- 复刻原文字的 bbox、字号比例、颜色、旋转、字距、行距、描边、阴影和层级。
- 输出最终 PNG、可编辑 PSD 和字体验证 report。

该 Skill 不是海报重新设计工具。除非用户明确要求，否则不会修改文案、重排构图或替换品牌标识。

## 软件和环境

| 项目 | 要求与支持情况 |
| --- | --- |
| 操作系统 | Windows 10/11；macOS 提供独立检测、字体安装和 Photoshop 冒烟测试脚本 |
| Windows 脚本 | Windows PowerShell 5.1 或更高版本 |
| macOS 脚本 | 系统 Bash、`PlistBuddy`、`defaults` 和 `osascript` |
| Photoshop | 生成原生可编辑文字层 PSD 时必需 |
| Photoshop 版本 | 22.x 及以上走标准 JSX 流程；本包已在 Photoshop 25.5（PS 2024）检测通过 |
| 旧版 Photoshop | 可以尝试，但必须先运行 `photoshop-smoke-test.jsx` 验证原生文字层能力 |
| Python | Python 3，运行本地渲染及验证辅助脚本时需要 |
| Python 库 | `Pillow`，仅辅助脚本需要 |
| Image 2 / image-gen | 普通 JPG、PNG 等扁平图片清除旧文字时需要 |
| Mac 架构 | 检测方式兼容 Intel 与 Apple Silicon 应用包结构；仍需真实 Mac 完成一次端到端验证 |
| Linux | 可读取资产并生成临时 PNG，不支持 Photoshop 原生 PSD 自动化 |

### 没有安装 Photoshop

环境检测找不到 Photoshop 时，Skill 必须明确提醒：

> 未检测到 Adobe Photoshop。原生可编辑文字层 PSD 暂时无法完成。请通过 Adobe Creative Cloud 安装 Photoshop，首次启动完成初始化后重新运行环境检测。Windows 自定义路径使用 `-PhotoshopPath` 或 `PHOTOSHOP_EXE`；Mac 使用 `--photoshop-path` 或 `PHOTOSHOP_APP`。

此时可以先输出清理底图、布局 JSON、透明文字层或临时 PNG，但这些文件不能冒充已经完成的可编辑 PSD。Skill 不会自动下载 Photoshop，也不提供非官方安装包。

## 安装 Skill

1. 解压 ZIP。
2. 将整个 `font-image-text-replace-01` 文件夹放入 Codex Skills 目录：

```text
C:\Users\<用户名>\.codex\skills\font-image-text-replace-01
```

macOS：

```text
~/.codex/skills/font-image-text-replace-01
```

3. 重新打开 Codex，或刷新可用 Skills。
4. 确认 Skill 可通过 `$font-image-text-replace-01` 调用。

也可以把 Skill 放在项目工作区中使用，但全局 Skills 目录更适合跨项目调用。

## 首次环境检测

Windows：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\detect-environment.ps1 -AsJson
```

macOS：

```bash
bash scripts/detect-environment-macos.sh --json
```

检测内容包括：

- 操作系统、版本、架构和脚本运行环境。
- Photoshop 是否存在。
- Photoshop 实际安装路径、文件版本和主版本号。
- 多版本 Photoshop 的候选列表和最终选择。
- 21 个随包字体文件是否完整。

自定义 Photoshop 路径：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\detect-environment.ps1 `
  -PhotoshopPath "D:\Adobe\Photoshop\Photoshop.exe" -AsJson
```

也可以设置：

```powershell
$env:PHOTOSHOP_EXE = "D:\Adobe\Photoshop\Photoshop.exe"
```

Mac 自定义路径：

```bash
bash scripts/detect-environment-macos.sh --json \
  --photoshop-path "/Applications/Adobe Photoshop 2025/Adobe Photoshop 2025.app"
```

也可以设置 `PHOTOSHOP_APP`。

## 安装随包字体

字体安装会修改操作系统字体目录，不能静默执行。Skill 会先询问：

> 确认已拥有这些字体的合法使用授权，并允许安装全部 21 款到当前用户吗？

只有用户明确同意后才能继续。系统级安装还必须明确指定并具备管理员权限。

Windows 预览与当前用户安装：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\install-bundled-fonts.ps1 -WhatIf
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\install-bundled-fonts.ps1 `
  -ConfirmAuthorizedUse -CurrentUser
```

- 默认安装到 `%LOCALAPPDATA%\Microsoft\Windows\Fonts` 并写 HKCU，不需要管理员权限。
- 只有用户明确要求系统级安装时才添加 `-SystemWide`；该模式写入 `C:\Windows\Fonts` 和 HKLM，需要管理员权限。
- 没有 `-ConfirmAuthorizedUse` 时脚本拒绝实际安装；`-Force` 强制覆盖。
- 只有"文件存在**且**注册表项存在"才算已安装，脚本会补齐只拷文件却没注册的字体。
- 需要预览安装清单时使用 `-WhatIf`。
- 安装结果输出 `scope`、`installed`、`already_installed`、`failed` 等字段；安装后重启 Photoshop，并以测试文字层的 `actualFont` 验证没有回退。

macOS 预览与安装：

```bash
bash scripts/install-bundled-fonts-macos.sh --dry-run
bash scripts/install-bundled-fonts-macos.sh --confirm-authorized-use
```

- 安装到 `~/Library/Fonts`，不需要管理员权限；没有 `--confirm-authorized-use` 时拒绝实际安装，同名字体默认跳过，`--force` 强制覆盖。
- 需要预览安装清单时使用 `--dry-run`。
- 安装后退出并重新打开 Photoshop，再验证字体实际名称。

受限环境中写入真实字体目录可能仍需环境放行；沙箱映射目录不算安装成功。若字体在 Photoshop 中仍回退到默认黑体，核验注册表与字体列表，做法见 `references/photoshop-automation-troubleshooting.md`。

## 使用方法

向 Codex 上传图片，然后说明：

1. 哪些文字需要替换。
2. 使用哪款字体；也可以要求 Skill 推荐合适的随包字体。
3. 哪些文字、logo、水印或区域必须保留。
4. 是否需要修改文案。默认只换字体，不改原文案。

示例请求：

```text
使用 $font-image-text-replace-01 处理这张图片。
把主标题替换为字魂百炼体 Heavy，底部说明使用字魂经典雅黑。
保持文案、位置、颜色、字号比例和字效不变，顶部品牌 logo 不处理。
输出最终 PNG 和带原生可编辑文字层的 PSD。
```

未指定字体时：

```text
使用 $font-image-text-replace-01，只替换图片里的活动标题字体。
请从随包字体中选择与原字形最接近的字体，保留其他内容。
```

## 处理流程

1. 检测运行环境和 Photoshop 版本。
2. 识别目标文字与必须保留的内容。
3. 记录文字 bbox、颜色、旋转、字距、行距和字效层级。
4. 通过 `assets/fonts/photoshop-font-name-map.json` 确认字体文件、版本别名与 Photoshop PostScript/font name，并锁定实际命中名称。
5. 使用 Image 2 / image-gen 清理指定旧文字。
6. 将清理底图恢复到原画布尺寸。
7. 在 Photoshop 中创建原生 `TEXT` 图层并对齐原 bbox。
8. 导出 PSD、最终 PNG 和字体 report。
9. 检查残影、错字、位置、遮挡、字体回退和 PSD 可编辑性。

## 输出内容

标准输出：

| 文件 | 内容 |
| --- | --- |
| `*_native_text_preview.png` | 最终替换字体后的完整成品预览 |
| `*_native_text.psd` | 包含清理底图和 Photoshop 原生可编辑文字层的 PSD |
| `*_native_text_report.json` | 文字内容、目标字体、Photoshop 实际字体和验证结果 |

根据任务需要还可能输出：

- Image 2 清理后的无目标文字底图。
- 原图、清理底图和成品的对照图。
- 文字布局 JSON。
- 透明文字层 PNG。
- Photoshop 兼容性测试结果。

清理底图和透明文字层属于辅助文件，不能替代最终 PNG 与可编辑 PSD。

## 随包字体

完整机器可读清单位于 `assets/fonts/font-manifest.json`。

字体名称锁定表位于 `assets/fonts/photoshop-font-name-map.json`。它记录每款随包字体的内部 family、full name、PostScript name，以及不同发行版本可能出现的 Photoshop 候选名称。需要重新扫描随包字体时运行：

```bash
python scripts/build_font_name_map.py \
  --manifest assets/fonts/font-manifest.json \
  --font-dir assets/fonts \
  --out assets/fonts/photoshop-font-name-map.json
```

拿到 Photoshop 字体清单后，可按字体 ID、中文名或文件名锁定实际名称：

```bash
python scripts/resolve_photoshop_font_name.py \
  --map assets/fonts/photoshop-font-name-map.json \
  --font 字魂国潮手书 \
  --available-fonts photoshop-font-inventory.tsv
```

输出中的 `resolved_photoshop_font_name` 必须写入任务布局或字体 report，并在最终 PSD 中通过 `actualFont` 再次确认。

字体替换优先匹配原字的字形，而不是按行业或场景硬套：比较笔画粗细、字面宽窄、结构与重心、圆角/尖角、书写节奏和视觉密度。同一张图可按主标题、副标题、正文、数字等角色混用多款字体。

下表只是便于快速查找的字形参考分组，不是使用限制：

| 字形参考 | 随包字体 |
| --- | --- |
| 清晰、中性、适合信息文字 | 字魂荧智 W3、字魂荧智 W6、字魂经典雅黑、字魂方悦黑、字魂锐艺黑 |
| 方正、粗重、高冲击力 | 字魂黑正体、字魂百炼体 Heavy、字魂正酷超级黑、字魂正酷超级进化体 Heavy |
| 几何、切角、速度与现代感 | 字魂光子芯片体、字魂正酷超级速度体 Heavy、字魂方方先锋体 |
| 圆润、柔和或趣味造型 | 字魂白润体、字魂布丁体、字魂百变魔术体、字魂招贴体 |
| 手写、书写节奏与个性 | 字魂海马体、字魂夏日诗歌体、字魂龙吟手书、字魂国潮手书 |
| 宋体骨架与人文阅读感 | 字魂阅宋 |

用户指定的字体不在随包清单中时，可以使用系统中已安装的字体或用户另外提供的字体文件，但仍需确认 Photoshop 实际 font name。同一字体不同版本可能存在 `-Regular` 等差异，随包字体的已知别名见 `assets/fonts/photoshop-font-name-map.json`。

## Photoshop 专业图层结构

- 一个语义文字块默认只建立一个原生文字层，不把 OCR 逐字结果直接做成一字一层。
- 文字图层直接用文案命名，例如文案“寻找”的图层名就是 `寻找`。
- 图层名默认最长 20 个字符，超长用 `…` 截断；同名层追加 `-02`、`-03`。
- 连续竖排中文使用一个竖排文本框；多列竖排按列拆分，不按字符拆分。
- 只有字符需要独立颜色、旋转、路径排列、主体遮挡或不同字效时才允许拆层，并记录拆分原因。
- 主标题、副标题、正文、装饰文字和效果层按角色分组；简单海报不创建无意义的空组或单层嵌套组。

布局整理命令：

```bash
python scripts/prepare_photoshop_layers.py \
  --layout layout.json \
  --out layout.photoshop.json \
  --audit-out layer-audit.json
```

完整规则见 `references/photoshop-layer-architecture.md`。

## Photoshop 版本适配

- 优先使用用户通过 `-PhotoshopPath` 指定的版本，其次使用 `PHOTOSHOP_EXE`、注册表和 Adobe 安装目录。
- macOS 优先使用 `--photoshop-path`，其次使用 `PHOTOSHOP_APP`、`/Applications` 和 `~/Applications`。
- 多版本共存时默认选择检测到的最高版本。
- 版本低于 22 或版本无法识别时，先运行：

```text
scripts/photoshop-smoke-test.jsx
```

该脚本会测试是否能创建原生文字层、读取字体名，并将结果写入系统临时目录。

Mac 使用包装脚本启动测试并等待结果：

```bash
bash scripts/run-photoshop-smoke-test-macos.sh
```

首次执行时，macOS 可能要求授予终端或 Codex 控制 Photoshop 的“自动化”权限。

## 常见问题

### Photoshop 找不到随包字体

核验字体是否已注册（Windows 检查 `C:\Windows\Fonts` 与 HKLM/HKCU 注册表，Mac 检查 `~/Library/Fonts`）。关闭并重新启动 Photoshop，再创建测试文字层读取 `layer.textItem.font`。若字体文件存在但 Photoshop 仍不认，按 `references/photoshop-automation-troubleshooting.md` 第 3 节补齐系统级注册。

### PSD 中的文字变成普通黑体

说明 Photoshop font name 不正确或字体发生回退。不要交付，先修正 PostScript name 或字体安装状态。

### 清理后还有旧字灰影

只针对残影区域重新运行 Image 2 清理，不要重新生成整张画面。

### 只有 PNG，没有可编辑 PSD

检查 Photoshop 是否安装并通过环境检测。没有 Photoshop 时，PNG 只能作为临时输出。

### Photoshop 存在但脚本不执行

如果 Photoshop 进程 `MainWindowHandle = 0`、转发的 JSX 不执行，不要判定"受环境限制无法完成"，也不要把脚本交给用户自己运行。用 `explorer.exe` 启动 Photoshop 使窗口挂到交互桌面，再命令行转发 JSX：

```powershell
Start-Process -FilePath "explorer.exe" -ArgumentList "`"$psExe`""
& $psExe "$jsxPath"
```

受限环境中 COM / cscript / Add-Type / rundll32 可能被拦截，可改用 explorer 启动转发和 Python `ctypes` 广播字体变更。详见 `references/photoshop-automation-troubleshooting.md`。

### Photoshop 安装在自定义目录

Windows 使用 `-PhotoshopPath` 或 `PHOTOSHOP_EXE`；Mac 使用 `--photoshop-path` 或 `PHOTOSHOP_APP`。不要修改 Skill 写死个人路径。

## 文件结构

```text
font-image-text-replace-01/
|-- SKILL.md
|-- README.md
|-- agents/
|-- assets/
|   |-- examples/
|   `-- fonts/
|       |-- font-manifest.json
|       |-- photoshop-font-name-map.json
|       `-- 21 font files
|-- references/
|   |-- photoshop-layer-architecture.md
|   |-- photoshop-automation-troubleshooting.md
|   `-- ...
`-- scripts/
    |-- detect-environment.ps1
    |-- detect-environment-macos.sh
    |-- install-bundled-fonts.ps1
    |-- install-bundled-fonts-macos.sh
    |-- run-photoshop-smoke-test-macos.sh
    |-- photoshop-smoke-test.jsx
    |-- build_font_name_map.py
    |-- resolve_photoshop_font_name.py
    |-- prepare_photoshop_layers.py
    |-- render_text_replacement.py
    `-- validate_text_replacement.py
```

## 授权说明

随包字体版权归字魂所有。公开仓库仅用于 Skill 的安装、测试与演示，不等同于向第三方授予无条件商用许可；实际使用范围以字魂正式授权协议为准。安装脚本在执行真实安装前会要求确认字体来源与安装范围。
