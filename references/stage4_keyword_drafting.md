# Stage 4: 候选词起草

> 基于 Stage 2 App 功能 + Stage 3 Locale 调研，为每个 locale 起草 Name/Subtitle/Keywords 候选。
> 产出物直接送进 Stage 5 校验。

## 触发时机

- Stage 3 完成后，每个目标 locale 跑一次
- 中途想加入新 locale 时（单 locale 跑）
- 重做某 locale 全面优化时（如 ja v2.1 的重新分配）

## 工作流

### Step 1: 收集输入

| 来源 | 内容 |
|---|---|
| `{project_root}/.aso/context.md` | 做的事 / 不做的事 / 推荐核心词类型 |
| `Marketing/aso_locale_research/{LOCALE}.md` | 该 locale 文化词 / 主营销词 / 错位警告 |
| 现网 ASC 数据（如已存在） | 当前 name/subtitle/keywords 作起点 |
| `locale_strategy.md` | 同语言 locale 差异化分配原则 |

### Step 2: 起草 Name + Subtitle

按 locale 起草，每字段 2-3 个候选，注明字符数：

```markdown
## {LOCALE} — Name & Subtitle 草案

### Name 候选 (限 30 codepoints)

| # | 候选 | 字符 | 主索引词 | 理由 |
|---|---|---|---|---|
| 1 | "{Brand} - {Keyword 1}" | XX/30 | Keyword 1 | 引用 Stage 3 推荐 #1 |
| 2 | "{Brand} · {Keyword 1} {Keyword 2}" | XX/30 | Keyword 1, 2 | 双关键词更密 |
| 3 | ... | ... | ... | ... |

**推荐**: #X，理由 ...

### Subtitle 候选 (限 30 codepoints)

| # | 候选 | 字符 | 主索引词 | 理由 |
|---|---|---|---|---|
| 1 | "..." | XX/30 | Keyword 3 | 与 Name 不重叠，承接价值主张 |
| 2 | ... | ... | ... | ... |

**推荐**: #X
```

### Step 3: 起草 Keywords 列表

从 Stage 3 推荐词族中按价值分级选词。**目标 90-100/100，20-25 词**。

```markdown
## {LOCALE} — Keywords 草案

### 选词清单（按价值排序）

| 词 | 字符（含逗号）| Layer 1 预检 | Layer 2 赛道 | Layer 3 功能 | 决定 |
|---|---|---|---|---|---|
| {kw1} | X | ✓ 不与 Name/Subtitle 重 | ✓ Top 同类 | ✓ 用户搜进不失望 | 加入 |
| {kw2} | X | ⚠️ 与 Name "{token}" 同根 | - | - | 砍掉 |
| ... | ... | ... | ... | ... | ... |

### 最终选词字符串

```
{kw1},{kw2},{kw3},...
```
长度: XX/100, N 词

### 砍掉清单（带原因）

- `{词}` — 与 Name 中 `{token}` 同根（Layer 1 失败）
- `{词}` — iTunes Top 是 {错位赛道}（Layer 2 失败）
- `{词}` — 用户搜进会失望（Layer 3 失败，黄金原则 #6）
```

### Step 4: 跨字段预演检查

起草完后，自己先过一遍 Layer 1（无需跑脚本）：

```
预演检查清单:
□ Keywords 每个词与 Name+Subtitle 中的每个 token 都不同根（含 stem）
□ Keywords 总字符 ≤ 100
□ Name 字符 ≤ 30
□ Subtitle 字符 ≤ 30
□ Keywords 间没有同根词
□ Keywords 没有逗号后空格
□ CJK locale: 没有 keyword 是 Name/Subtitle 长 token 的子串
```

预演通过才进入 Stage 5 正式校验。

### Step 5: 跨同语言 locale 协调

如果在批量起草多个同语言 locale（如 en-US/GB/AU/CA），需要全局视角：

```markdown
## 同语言 locale 协调表（en 集群示例）

| 词 | en-US | en-GB | en-AU | en-CA | 跨 locale 同根？|
|---|---|---|---|---|---|
| engagement | ✓ | | | | 唯一 |
| bridesmaid | ✓（含 bride stem）| | | | 与 en-GB "brides" 同根冲突 ❌ |
| brides | | ✓ | | | 与 en-US "bridesmaid" 同根冲突 ❌ |
| ... | ... | ... | ... | ... | ... |
```

发现冲突 → 必须二选一 → 把另一个 locale 改成不同根的词。

### Step 6: 输出格式

最终产出 JSON / Markdown：

```json
{
  "app": "<App Name>",
  "version": "<v2.1>",
  "drafts": {
    "en-US": {
      "name": "<Brand - Keyword>",
      "subtitle": "<value prop with #2-#3 keywords>",
      "keywords": "kw1,kw2,...",
      "char_counts": {"name": 28, "subtitle": 29, "keywords": 95}
    },
    "en-GB": { },
    "ja": { }
  },
  "metadata": {
    "drafted_at": "YYYY-MM-DD",
    "stage3_research_ref": "{project_root}/.aso/locale/",
    "stage2_features_ref": "{project_root}/.aso/context.md"
  }
}
```

存到 `{project_root}/.aso/drafts/{date}.json`，送进 Stage 5 校验。

## 起草 Anti-pattern

❌ **直接复制 Stage 3 推荐词全塞 Keywords** — 会超字符 + 跨字段重复
❌ **追求 100/100 硬塞低对口词** — 90-95/100 + 全对口比 100/100 含错位词强
❌ **同语言 locale 用相似词** — 浪费 4 个独立池
❌ **Keyword 含 Name/Subtitle 已索引词** — 跨字段重复浪费
❌ **跨 locale 不协调直接起草** — 后期一定碰跨 locale 同根冲突

## 起草 Best Practice

✅ Name 装 #1 高价值核心词（最高权重字段）
✅ Subtitle 装 #2-#3 核心词 + 价值主张（不重 Name）
✅ Keywords 装剩余对口长尾词（按 Stage 3 推荐分级挑选）
✅ 同语言 locale 词全部 unique（事先过协调表）
✅ 起草完先自检 Layer 1 预演，再进 Stage 5

## 与 Stage 5 的交接

Stage 4 输出的 JSON / Markdown 草案 → 跑 Stage 5 三层校验 → 通过的写入 ASC。

如果 Stage 5 报错（如 stage 4 自检漏了某项），回 Stage 4 改草案再跑。
