# Stage 3: 多语言市场调研

> 为每个目标 locale 调研：本地搜索习惯、文化特定词、主要竞品、推荐主营销词。
> 这是 Stage 4 候选词起草的输入基础。

## 触发时机

- App 首次系统化做 ASO（一次性全 locale 调研）
- 扩展到新 locale 之前
- 重大算法/趋势变更后（Stage 1 后偶尔触发）

## 工作流

### Step 1: 准备输入

- 读 `{project_root}/.aso/context.html`（Stage 2 产出）
- 决定目标 locale 列表（参考 `locale_strategy.md` 通用市场分级）
- 决定集群分组（一般 3-4 个 locale 一组并行）

### Step 2: 并行启动多个 Agent

按市场文化集群分组，每组 1 个 Agent。典型分组：

```
集群 A: 英语 4 池 (en-US/GB/AU/CA)
集群 B: 东亚 CJK (ja, ko, zh-Hans, zh-Hant)
集群 C: 欧洲 (de-DE, fr-FR, fr-CA, es-ES, es-MX, it, pt-BR)
集群 D: 新兴市场 (ar-SA, tr, th, vi)
```

并行启动 4 个 Agent（在一个消息里发 4 个 tool_use）：

### Step 3: Agent prompt 模板

```
我要为 {APP_NAME} 在 {LOCALE_LIST} 市场做 ASO，需要调研每个 locale。

App 真实功能（必读）：
{粘贴 {project_root}/.aso/context.html 的"做的事/不做的事"节}

请并行/串行调研 {LOCALE_LIST} 每个 locale：

1. **本地搜索习惯**：该语言用户在 App Store 搜什么类型的词找类似功能 App？
2. **文化特定术语**：该市场独有的相关词（如日本「前撮り」、韩国「스드메」）
3. **主要竞品**：用 iTunes Search API 验证（`python3 itunes_search_check.py --country {CC} --keywords "..."`）。
   - 输入 5-10 个直觉候选词，看 Top 5 真实是什么 App
4. **推荐主营销词**：name/subtitle 候选 3-5 个 + 理由
5. **已知错位词警告**：按黄金原则 #6，列该 locale 上的功能错位词陷阱
6. **跨索引收益**：该 locale 是否被其他主市场跨索引？

输出格式严格按下方模板，每个 locale 一份。
```

### Step 4: 单 locale 调研输出模板（HTML 格式）

输出到 `{project_root}/.aso/locale/{LOCALE}.html`。参考 Stage 2 的 `context.html` 样式。

**iTunes 限流处理**（实战教训）：4 个并行 Agent 同时跑 iTunes 必触发 IP 限流（403/429）。限流时不要"凭直觉外推"或"LLM 编地域风情词"——上次 en-AU/CA 的 `boho/winter/maple` 全错位。老实在 HTML 中用 `class="untested"` 标记。

7 节结构（HTML 字段对应下方 markdown 说明）：

```markdown
# {App Name} - {LOCALE} 市场调研

> 集群: {A/B/C/D} | 调研日期: {YYYY-MM-DD}

## 1. 本地搜索习惯

[2-3 段]：用户主流搜什么类型的词找此类 App？年轻 vs 老年 / 文艺 vs 实用 差异。

## 2. 文化特定术语（必收录）

| 本地词 | 含义 | 搜索热度（iTunes 命中数）| 该 App 适用度 |
|---|---|---|---|
| 前撮り | 婚前拍摄 | 18/20 | ✅ 核心 |
| ナシ婚 | 不办婚礼直接登记 | 6/20 | ✅ 长尾 |

## 3. 主要竞品（iTunes Top 5 实测）

按候选词列出 Top 竞品：

### 词「{kw1}」
- Top 1: {App Name} ({bundle id}) ⭐{rating}
- Top 2: ...
- 赛道判定: 同功能/同大类不同功能/完全不同

### 词「{kw2}」
...

## 4. 推荐主营销词（写进 Name/Subtitle）

| 字段 | 候选 | 字符 | 理由 |
|---|---|---|---|
| Name #1 候选 | "..." | XX/30 | 含 {核心词}，目标搜索意图 {X} |
| Name #2 候选 | "..." | XX/30 | ... |
| Subtitle #1 候选 | "..." | XX/30 | 与 Name 不重叠 |

## 5. 已知错位词警告

按黄金原则 #6 在 {LOCALE} 上的特殊陷阱：

- `{词1}` → iTunes Top 是 {错位赛道}，App 实际功能不匹配 → ❌
- `{词2}` → 该词在该语言主要意思是 {其他} → ❌

## 6. 跨索引收益

[该 locale 是否被其他主市场跨索引？]
- 如 ar-SA 被美国跨索引 → 可塞英文高频词
- 如 fr-CA 被美国跨索引 → 可塞...

## 7. 推荐 Keywords 词族（25-30 词候选清单）

按价值分级，下一步 Stage 4 起草时挑选：

### 核心（直接对口，最高优先级）
- {kw1}, {kw2}, ...

### 长尾（半对口，待 Stage 5 验证）
- {kw1}, {kw2}, ...

### 跨索引候选（如适用）
- {kw1}, {kw2}, ...

### 已淘汰（不要加，原因列明）
- {kw1} — Top 是婚介赛道
- {kw2} — 巨头垄断
```

### Step 5: 汇总

把每个 locale 的调研存到项目内（**不进 skill**）：
- `Marketing/aso_locale_research/{LOCALE}.html`
- 或 `Marketing/ASO_Deep_Review_{YYYY-Q}.md`（合并所有 locale 一文）

### Step 6: 更新 skill 内 context

把每个 locale 调研的关键结论（核心词 + 错位词警告 + 跨索引）摘要回 `{project_root}/.aso/context.html` 的「locale 调研摘要」节，方便 Stage 4 起草和 Stage 5 校验时快速引用。

## 并行 vs 串行权衡

- **并行 4 集群**：~30-40 分钟（一次同时跑 4 个 Agent）
- **串行单 locale 跑完**：~10 分钟/locale × 13-19 locale = 2-3 小时

推荐并行——除非 Agent 调用预算紧张。

## 验证示例

如有项目内已存在的 ASO 深度调研报告（如 `Marketing/ASO_Deep_Review_*.md`），可作为 Stage 3 产出模板参考。
