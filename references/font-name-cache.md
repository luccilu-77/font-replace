# Photoshop 字体名缓存

本文件只记录已经验证过的字体名称映射，用于减少每次任务重复扫描 Photoshop 字体列表的时间。它不是字体推荐表；未指定字体时应优先比较笔画粗细、字面宽窄、结构重心、圆尖角、书写节奏和视觉密度。场景只作参考，不构成限制，同一画面可以按文字角色混用字体。

精简包随附字体的角色、文件名和授权提醒见 `assets/fonts/font-manifest.json`。机器可读的完整对照表位于 `assets/fonts/photoshop-font-name-map.json`，其中同时记录随包字体内部名称和不同安装版本的 Photoshop 候选名称。本文件只提供人工查阅入口，不能替代最终 report 验证。

使用规则：

- 先按用户给出的中文字体名或字体文件名查表。
- 不再假定每款字体只有一个 font name。按 `photoshop_candidates` 顺序与 Photoshop 实际字体列表匹配，并锁定第一个命中的名称。
- 将命中值写入任务布局或 report 的 `resolved_photoshop_font_name`，同一任务后续都使用该锁定值。
- 最终仍必须读取 report，确认 `actualFont` 等于 `resolved_photoshop_font_name`。
- 如果 Photoshop 回退到 `AdobeHeiti`、`SimHei`、`MicrosoftYaHei` 或普通黑体，本缓存不能作为交付依据。
- 新字体或新版本经 Photoshop 验证后，将别名加入 `scripts/build_font_name_map.py` 的 `KNOWN_ALIASES`，重新生成 JSON 对照表，并同步更新本页。

## 已验证映射

| 中文/文件名 | Photoshop font name / PostScript name | 备注 |
|---|---|---|
| 字魂荧智 W1 | `ZihunYingzhi_T-W1` | 字魂荧智系列 |
| 字魂荧智 W2 | `ZihunYingzhi_T-W2` | 字魂荧智系列 |
| 字魂荧智 W3 | `ZihunYingzhi_T-W3` | 常用于正文、小字 |
| 字魂荧智 W4 | `ZihunYingzhi_T-W4` | 字魂荧智系列 |
| 字魂荧智 W5 | `ZihunYingzhi_T-W5` | 常用于小标题 |
| 字魂荧智 W6 | `ZihunYingzhi_T-W6` | 常用于标题 |
| 字魂黑正体 | `zihunheizhengti` | 黑体类 |
| 字魂海马体字体 | `zihunhaimatiziti` | 海马体 |
| 字魂布丁体 | `zihun27hao-budingti-Regular` | 不要用显示名 `zihunbudingti` 直接写 JSX，曾回退到 AdobeHeiti |
| 字魂夏日诗歌体 | `zihunxiarishigeti` | 手写感、舒展 |
| 字魂招贴体 | `zihunzhaotieti` | 招贴类 |
| 字魂光子芯片体 | `zihunguangzixinpianti` | 科技/参数类 |
| 字魂百炼体 Heavy | `zihunbailianti-Heavy` | 标题重字重 |
| 字魂白润体 | `zihunbairunti` | 圆润正文/标题辅助，Photoshop 已验证 |
| 字魂正酷超级进化体 Heavy | `ZHZKCJJHT-Heavy` | Photoshop 使用缩写 PostScript 名 |
| 字魂正酷超级速度体 Heavy | `ZHZKCJSDT-Heavy` | Photoshop 使用缩写 PostScript 名 |
| 字魂方方先锋体 | `ZHFFXFT` | 方形骨架、现代几何 |
| 字魂正酷超级黑 | `zihun143-zhengkuchaojihei` | 超粗黑体、高冲击力 |
| 字魂龙吟手书 | `zihunlongyinshoushu` | 手书、飞白、力量感 |
| 字魂国潮手书 | `zihun43hao-guochaoshoushu`；`zihun43hao-guochaoshoushu-Regular` | 不同发行版本的 PostScript name 不同，必须以 Photoshop 实际列表锁定 |
| 字魂锐艺黑 | `zihun154hao-ruiyihei` | 英文/小字/标题辅助 |
| 字魂百变魔术体 | `zihunbaibianmoshuti` | 魔术体/趣味标题，Photoshop 已验证 |
| 字魂方悦黑 | `zihunfangyuehei` | 标题/产品名，Photoshop 已验证 |
| 字魂经典雅黑 | `zihun35hao-jingdianyahei-Regular` | 小字说明，Photoshop 使用 PostScript 名 |
| 字魂阅宋 | `zihunyuesong_T` | 宋体骨架、人文阅读感 |
