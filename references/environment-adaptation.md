# 运行环境与 Photoshop 适配

本 Skill 不假定 Photoshop 2024，也不把 Photoshop 路径写死。先识别操作系统，再使用对应检测、字体安装和 Photoshop 启动方式。

## 平台入口

### Windows

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts\detect-environment.ps1 -AsJson
```

发现顺序：

1. `-PhotoshopPath`。
2. 环境变量 `PHOTOSHOP_EXE`。
3. Windows `Photoshop.exe` App Paths 注册表项。
4. Adobe 常见安装目录。

### macOS

```bash
bash scripts/detect-environment-macos.sh --json
```

发现顺序：

1. `--photoshop-path` 指定的 `.app`。
2. 环境变量 `PHOTOSHOP_APP`。
3. `/Applications/Adobe Photoshop*.app`。
4. `~/Applications/Adobe Photoshop*.app`。

Mac 检测器从应用包的 `Info.plist` 读取版本、Bundle ID 和真实可执行文件路径，同时兼容 Intel 与 Apple Silicon 路径结构。

显式路径优先；没有显式路径时选择检测到的最高版本。正式自动化必须使用检测结果，不能继续引用开发电脑上的固定路径。

## Photoshop 版本策略

- 能识别版本且主版本不低于 22：使用标准 JSX 路线。
- 更早版本或版本号无法识别：先运行 Photoshop 冒烟测试。
- 多版本共存：默认选择最高版本；用户指定版本时使用平台对应的路径参数。
- 不使用只在单一 Photoshop 版本存在、且没有能力检测或回退方案的 API。

Windows 可直接执行 `photoshop-smoke-test.jsx`。Mac 使用：

```bash
bash scripts/run-photoshop-smoke-test-macos.sh
```

自定义 Mac Photoshop 路径：

```bash
bash scripts/run-photoshop-smoke-test-macos.sh \
  --photoshop-path "/Applications/Adobe Photoshop 2025/Adobe Photoshop 2025.app"
```

macOS 首次控制 Photoshop 时可能弹出自动化权限请求。用户应在“系统设置 > 隐私与安全性 > 自动化”中允许当前终端或 Codex 控制 Photoshop。

## 未安装 Photoshop

检测结果为 `photoshop.found = false` 时：

1. 告诉用户原生可编辑文字层 PSD 暂时无法完成。
2. 提示通过 Adobe Creative Cloud 安装 Photoshop，并至少启动一次完成初始化。
3. Windows 自定义位置使用 `-PhotoshopPath` 或 `PHOTOSHOP_EXE`。
4. macOS 自定义位置使用 `--photoshop-path` 或 `PHOTOSHOP_APP`。
5. 可以先输出清理底图、布局 JSON、透明文字层或临时 PNG，但不能声称 PSD 交付完成。

不要自动下载 Photoshop，不提供非官方安装包，不用位图文字 PSD 冒充完成结果。

## 字体环境

随包字体位于 `assets/fonts/`，清单见 `assets/fonts/font-manifest.json`。

- 本地渲染脚本可以直接读取字体文件。
- Photoshop 通常需要操作系统已安装字体才能稳定识别 PostScript name。
- 安装字体会修改当前用户字体目录，因此必须先获得用户明确同意。
- 安装或更新字体后，关闭并重新启动 Photoshop，再做字体测试。
- 最终必须读取 Photoshop report，确认 `actualFont` 没有回退。

## 确认式一键安装

仅当任务需要随包字体、且 Photoshop 尚未识别这些字体时，向用户询问：

> 确认已拥有这些字体的合法使用授权，并允许安装全部 21 款到当前用户吗？

普通字体替换请求、上传图片或选择字体，不等于安装授权。只有用户明确回答同意后，才能执行系统修改。

### Windows 安装

预览：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts\install-bundled-fonts.ps1 -WhatIf
```

安装：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File scripts\install-bundled-fonts.ps1 -ConfirmAuthorizedUse
```

- 安装到当前用户 `%LOCALAPPDATA%\Microsoft\Windows\Fonts`。
- 写入当前用户字体注册信息，不要求管理员权限。
- 已登记字体默认跳过，覆盖安装必须得到用户明确要求并添加 `-Force`。
- 安装成功后广播 Windows 字体变更，但仍需重启 Photoshop。

### macOS 安装

预览：

```bash
bash scripts/install-bundled-fonts-macos.sh --dry-run
```

安装：

```bash
bash scripts/install-bundled-fonts-macos.sh --confirm-authorized-use
```

- 安装到当前用户 `~/Library/Fonts`，不要求管理员权限。
- 同名字体默认跳过；覆盖安装必须得到用户明确要求并添加 `--force`。
- 不自动删除 macOS 字体缓存，不调用 `sudo`。
- 安装后退出并重新打开 Photoshop，再验证字体实际名称。

## 执行与验证规则

- Windows 安装器缺少 `-ConfirmAuthorizedUse` 时拒绝安装。
- macOS 安装器缺少 `--confirm-authorized-use` 时拒绝安装。
- 安装命令在 Codex 沙箱或受限环境运行时，需要用户批准对真实用户字体目录的写入；沙箱映射目录不算安装成功。
- Windows 检查安装结果 JSON 中的 `installed`、`already_installed` 和 `failed`。
- macOS 检查 `SUMMARY` 中的 `installed`、`skipped` 和 `failed`。
- Photoshop 重启后创建测试文字层，确认 `actualFont` 与 `font-manifest.json` 一致。

## 支持边界

- Windows：PowerShell 5.1 及以上，已在 Photoshop 25.5 环境验证检测脚本。
- macOS：使用系统 Bash、`PlistBuddy`、`defaults` 和 `osascript`；脚本兼容 Bash 3.2 语法。
- Mac 脚本已完成静态语法检查，但仍应在真实 Intel 或 Apple Silicon Mac 上完成一次安装和 Photoshop 自动化验证。
- Linux：可以读取字体资产和生成临时 PNG，但不支持 Photoshop 原生 PSD 自动化。
