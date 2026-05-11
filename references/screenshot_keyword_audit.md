# Screenshot Keyword Audit Workflow

> Apple 2025 算法变更：截图标题文字被提取并作为关键词索引的一部分。截图既是转化资产，也是 ASO 资产。

## 目的

确保每个 locale 的截图标题文字与 Keywords 池**互补**——截图里的核心词应是 Keywords 字段里塞不下的、或值得重复加权的高价值词。

## 工作流

### 1. 列出每个 locale 的截图

截图路径项目内自定义。常见组织方式：

```
{project}/screenshots/{lang}/{device-size}/*.png
```

具体路径见各项目的 `{project_root}/.aso/context.md` 的「资源位置」节。

### 2. Claude 视觉读图（不要写 OCR 脚本）

直接用 `Read` 工具读 PNG，Claude 会"看"图片并提取标题文字。例如：

```
Read: Marketing/en-screenshots/output/65/01-hero-1284x2778.png
→ Claude 提取出："AI Couple Portraits in 30s"
```

### 3. 与 Keywords 池比对

对每个 locale 建立四象限：

| 截图里有 / Keywords 里有 | 截图里有 / Keywords 里**没** | 截图里**没** / Keywords 里有 |
|---|---|---|
| ✅ 双重加权（核心词，正确策略）| 🟢 免费多拿一个搜索词（截图独占）| ⚪ Keywords 独占（不强求截图也提）|

**审计目标**：
- **空白 1**：截图标题用了某词，但 Keywords 池没有 → 看是否值得加进 Keywords（双重加权）
- **空白 2**：Keywords 里的高价值词在截图里完全没体现 → 下次改截图时考虑加上
- **冲突**：截图标题与 Name/Subtitle 用了同样的词 → 某种程度上是浪费（同字段重复加权效益递减），但不是硬错

### 4. 报告格式

```markdown
## Screenshot Audit — en-US

**截图标题提取**（从 10 张图）：
- "AI Couple Portraits in 30s"
- "Wedding photos that look real"
- "Pose like the reference"
- ...

**Keywords 池**（en-US）：
face,dating,anniversary,romantic,studio,love,bridal,engagement,swap,merge,generator,avatar,ghibli

**比对结果**：
- ✅ 截图+Keywords 双重加权：couple, wedding, portrait
- 🟢 截图独占（已是免费加权词）：real, pose, reference
- 🟡 Keywords 独占但截图未提（可考虑下版改图）：generator, avatar, ghibli, swap
```

## 何时跑这个 workflow

1. **重大版本更换截图前** — 决定新截图标题文案时
2. **新增 locale 时** — 该 locale 的截图标题应有意识对齐 Keywords 缺口
3. **季度复审时** — 与 `aso_audit.py` 一起跑

## 项目状态记录建议

各项目截图标题对齐进度记到 `{project_root}/.aso/context.md` 的「待办」节。
