# Stage 2: App 功能自动分析

> 扫 App 代码库自动生成 `{project_root}/.aso/context.html`，是 Stage 3-5 的输入基础。

## 触发时机

- **首次为某 App 做 ASO**（一次性）
- App 核心功能大改后（增删合集、改变定位、推出新付费模式等）
- 接手他人的项目 / 上下文不熟时

## 工作流

### Step 1: 收集项目元信息

需要的输入：
- 项目根路径（如 `~/Code/MyApp`）
- 项目类型（iOS / Android / 跨平台）
- 主要语言（Swift / Kotlin / JS 等）

### Step 2: 用 Explore Agent 扫描

启动 1 个 Agent (subagent_type=Explore)。**必须在 prompt 中明确禁读历史 ASO 报告**（黄金原则 #7）：

⚠️ **严禁读** `{project_root}/Marketing/ASO_*.md`、`Marketing/WePics_Market_Research_*.md`、`{project_root}/.aso/` 任何文件。否则 Agent 会引用历史结论，污染"从零分析"前提。

如果项目内已有 ASO 历史报告，**在跑 Stage 2 前先把它们移到 `.archive/`**：
```bash
mkdir -p {project_root}/Marketing/.archive/
mv {project_root}/Marketing/ASO_*.md {project_root}/Marketing/.archive/
mv {project_root}/Marketing/*Market_Research*.md {project_root}/Marketing/.archive/
```

```
prompt 模板：

我要为 {APP_NAME} 做 ASO，需要先理解 App 实际功能边界（避免 keyword 功能错位）。
请扫这个项目 {ROOT_PATH}，提取以下信息：

1. **核心功能**：用户主要能做什么？（看 README / CLAUDE.md / 主入口 / Models 目录）
2. **不做的事**：明显的边界（如"只做双人合成，不做单人风格化"）
3. **目标用户**：付费用户画像 / 订阅模式 / 定价
4. **关键资产位置**：截图 / 营销文案 / locale 文件路径
5. **当前 ASO 状态**：是否有 ASC App ID / Bundle ID / 当前版本号

输出格式严格按下方模板填写，不要凭空补充信息。不确定的字段标 "?待用户补充"。
```

### Step 3: Agent 输出模板（HTML 格式）

输出到 `{project_root}/.aso/context.html`。HTML 结构示例：

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{App Name} — ASO Context</title>
  <style>
    body { font-family: -apple-system, sans-serif; max-width: 1000px; margin: 2em auto; padding: 0 1em; line-height: 1.6; }
    h1, h2 { border-bottom: 1px solid #ddd; padding-bottom: .3em; }
    table { border-collapse: collapse; width: 100%; margin: 1em 0; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background: #f5f5f5; }
    .source { color: #888; font-size: .85em; font-style: italic; }
    .warn { color: #c00; }
    .ok { color: #060; }
    code { background: #f0f0f0; padding: 2px 4px; border-radius: 3px; }
  </style>
</head>
<body>
  <h1>{App Name} 项目特定上下文</h1>
  <p class="source">Generated: {date} | Source: code + docs（Marketing/.md 被禁读）</p>

  <h2>基础信息</h2>
  <table>...App ID / Bundle ID / 类型 / 覆盖 locale / brand_name_per_locale...</table>

  <h2>做的事（依据代码反推）</h2>
  <ul>... 每条带 <span class="source">依据: {file}</span> ...</ul>

  <h2>不做的事（明确边界）</h2>
  <ul>...</ul>

  <h2>商业模型</h2>
  ...

  <h2>资源位置</h2>
  <table>...</table>

  <h2>推荐核心词类型（按真实功能反推）</h2>
  ...

  <h2>应避免的功能错位词族</h2>
  <table>... 词族 + 错位赛道 + 风险等级 ...</table>

  <h2>?待用户补充字段</h2>
  ...
</body>
</html>
```

**关键字段**：
- `brand_name_per_locale` — 各 locale 的品牌名（如 zh-Hans/Hant 用「微出片」而非英文名）。这字段防 Stage 4 误改品牌名（实战教训）
- 每个结论必须带"依据"（哪个文件哪行）
- 不确定的字段标 `?待用户补充`

### Step 4: 用户审核

Agent 输出后，**让用户检查 "做的事 / 不做的事 / 推荐核心词" 几节**——这部分必须用户确认对，否则 Stage 3-5 全错。

不确定的字段（?待用户补充）必须填完。

### Step 5: 落地

保存为 `{project_root}/.aso/context.html`。

### Step 6: 当 App 功能变更后

重新跑 Stage 2 → 覆盖 `{project_root}/.aso/context.html`。Stage 3 调研可能需要相应更新。

## 自动分析的边界（人脑兜底）

Agent **能识别**：
- README/CLAUDE.md 明文写的功能
- 代码目录结构暗示的功能（Services/GenerationService → 生成功能）
- 截图目录暗示的营销资产

Agent **不能识别**（必须用户补充）：
- 战略定位（"我们想往哪走"）
- 隐含的不做事项（代码里没明说）
- 未来 1-2 个版本的产品路线

## 验证示例

已验证：Explore Agent 跑过中等规模 iOS 项目（含 README + CLAUDE.md + Swift 代码）能自动生成约 ~80% 完整度的 context（基础信息、做的事、不做的事、错位词族），剩 20% 是用户战略层（如双轨定位、未来路线）。
