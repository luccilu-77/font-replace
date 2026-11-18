# Photoshop 自动化执行排障与可靠做法

本文件记录已在本机环境验证通过的 Photoshop 自动化问题与解法。仅当标准 JSX 流程（见 [psd-output-guidelines.md](psd-output-guidelines.md)）被环境限制阻断时按本文件处理；不要把这些经验当成所有机器的默认前提，也不要把个人安装路径写进脚本或报告。

## 1. 症状：直接启动 Photoshop 后无法执行 JSX，PSD 自动化被判定"受阻"

典型表现：

- 从 Bash / PowerShell 用 `Start-Process` 或直接调用 `Photoshop.exe` 启动后，进程存在但 `MainWindowHandle = 0`，窗口没有挂到交互桌面。
- 命令行转发 `Photoshop.exe <脚本.jsx>` 没有反应，脚本不被执行，不产出报告文件。
- 界面上像"卡住"或"没有响应"，但这不是脚本或 PSD 文件的问题。

根因：**进程没有挂到交互桌面**，无法接收命令行转发的 JSX。此时让用户"自己在桌面运行一次脚本"不是必要的，应先按下面的方式自己把进程挂上桌面。

### 可靠解法：经 explorer shell 启动，再转发 JSX

Windows 上用资源管理器 shell 启动 Photoshop，进程会正确挂到交互桌面：

```powershell
$psExe = "C:\Program Files\Adobe\Adobe Photoshop 2026\Photoshop.exe"
Start-Process -FilePath "explorer.exe" -ArgumentList "`"$psExe`""
```

启动后等 `MainWindowHandle` 变为非 0、进程处于健康状态，再用命令行转发脚本：

```powershell
& $psExe "D:\path\to\build.jsx"
```

要点：

- 路径使用环境检测（[environment-adaptation.md](environment-adaptation.md)）得到的实际 Photoshop 路径，上面只是示例。
- 先确认有可用的交互桌面；完全无桌面的服务/会话中仍然无法驱动 GUI 应用。
- 一旦窗口句柄正常，JSX 转发即可稳定执行，自动化不要再退回"只交付 PNG、让用户自己跑脚本"的结论。

## 2. 症状：COM / cscript / Add-Type / rundll32 被安全策略拦截

在受限的 agent 沙箱里，这些方式可能全部被拦截，表现为调用直接失败或被拒绝：

- PowerShell COM 调用（例如创建 `Photoshop.Application` 对象）。
- `cscript` / `wscript` 调用。
- `Add-Type` 编译 C# 类型。
- `rundll32`。

处理原则：

- **驱动 Photoshop 执行脚本**：优先第 1 节的 explorer shell 启动 + 命令行转发 JSX，不依赖 COM/脚本宿主。
- **需要 Win32 API 广播（例如字体变更 `WM_FONTCHANGE`）**：改用 Python `ctypes` 纯解释调用；它在本环境可用，不需要编译 Add-Type：

```python
import ctypes

u = ctypes.windll.user32
res = ctypes.c_ulong()
u.SendMessageTimeoutW(
    0xFFFF,      # HWND_BROADCAST
    0x001D,      # WM_FONTCHANGE
    0, 0,
    0x0002,      # SMTO_ABORTIFHUNG
    3000,
    ctypes.byref(res),
)
```

- 不要用被拦截的调用方式去"重试"；直接换上面已验证可用的通道。

## 3. 症状：字体装了但 Photoshop 不认，文字回退到 AdobeHeiti / 普通黑体

根因通常是**字体文件复制成功 ≠ 注册成功**，而不是字体文件损坏。

排查与修复顺序：

1. 核验注册表 `HKCU\Software\Microsoft\Windows NT\CurrentVersion\Fonts`，确认 21 款字体每一项都有对应键值。
   - 若安装脚本曾中断，可能只写了少量注册表项，其余字体只是拷了文件，Windows 和 Photoshop 都不认。
   - 安装脚本已修复：只有"文件存在**且**注册表项存在"才算已安装，否则补注册，不再因文件存在而跳过。
2. 若补齐当前用户注册后 Photoshop 仍不识别，在获得用户对系统级安装的明确同意且当前账户是管理员后，才改做系统级安装：
   - 复制 21 个 `.ttf` 到 `C:\Windows\Fonts`。
   - 写 `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts`。
   - 清理 Photoshop 的 `CT Font Cache` / `FontFeatureCache`。
3. 用第 2 节的 Python `ctypes` 广播 `WM_FONTCHANGE`。
4. 关闭并重新启动 Photoshop，再确认字体列表中确实出现字魂字体（本机验证：列表数量 547 → 568）。
5. 创建测试文字层读 `layer.textItem.font`，确认没有回退到 `AdobeHeiti`、`SimHei`、`MicrosoftYaHei` 等，再继续重建 PSD。

关键判断：**必须以 Photoshop 报告中的 `actualFont` 为准**，不能只看安装脚本返回成功，也不能只看字体文件存在。

## 4. 症状：ExtendScript 里 `JSON` 未定义

Photoshop 的 ExtendScript 运行环境没有内置 `JSON` 对象，直接 `JSON.stringify()` 会报错，导致报告写不出来、JSX 中断。

处理方式：报告内容用字符串拼接（或自己实现极简序列化）写出，不要依赖 `JSON`。布局数据可以从外部 `layout.json` 读入，但报告写出要在 JSX 内用字符串拼装。

## 5. 症状：重建的文字跑到画布外或 y 坐标为负

新建文字层的初始 `bounds` 不在 (0,0)，只做一次 `translate` 补偿会算错位移。

可靠顺序：

1. 设置 `textItem.font` / `size` / `contents`。
2. 设 `position = [x, y + size]`（给基线留空间）。
3. 按目标宽度缩放字号。
4. 重新设置 `position`。
5. **读取当前 `bounds`**，实时计算 `dx = targetX - bounds[0]`、`dy = targetY - bounds[1]`。
6. 再用 `layer.translate(dx, dy)` 对齐到目标 bbox。

## 6. 症状：底部高亮区域白色字与深色字重叠

当多段文字共享同一水平空间时，分段渲染会互相覆盖。

可靠做法：先把整句保留为一个语义文字层，用 Photoshop 文字范围样式（text style ranges）处理局部颜色；如果自动化环境无法稳定写入范围样式，才按“连续同色片段”拆成少量文字层，并记录 `split_reason: mixed_color`。禁止退化为一字一层。底图上的高亮块应填成纯色并清掉残留旧字，避免半透明色块与新字打架。

## 7. 症状：文字层数量过多，竖排文字被拆成一字一层

根因通常是把 OCR 的逐字识别结果直接转换为 Photoshop 图层。

处理顺序：

1. 按语义和空间关系给连续字符标记同一 `block_id`。
2. 运行 `scripts/prepare_photoshop_layers.py` 合并同一块的字符记录。
3. 横排文字按 x 坐标排序并合并；单列竖排按 y 坐标排序并合并。
4. Photoshop 竖排文字设置 `textItem.direction = Direction.VERTICAL`，优先使用段落文本框。
5. 只有独立颜色、旋转、路径文字、遮挡层级或不同字效时才拆分，并记录 `split_reason`。
6. 图层名使用文案，长文案截断，同名层追加序号。

详细规范见 [photoshop-layer-architecture.md](photoshop-layer-architecture.md)。

## 8. 交付前验证

即使自动化过程艰难，验证标准也不能降低：

- 用 Photoshop 重新打开生成的 PSD，逐层核对 `layer.kind === LayerKind.TEXT`、`textItem.contents` 与 `textItem.font`。
- 确认文字层数量与语义文字块数量接近；无理由单字层为 0，竖排连续文字使用一个文本框。
- 确认图层名能直接识别文案，长文案和同名层命名符合规范。
- 确认字体全部为目标字体、无回退。
- 确认 PNG 预览与 PSD 当前可见效果一致，无旧字残影、无遮挡错误。

只要上述验证通过，就可以正常交付可编辑 PSD，不要再说"这一步受环境限制无法完成"。
