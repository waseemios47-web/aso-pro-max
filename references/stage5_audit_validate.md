# 任务 A 详细步骤：审计 + 优化某 locale 的 keywords

> 对应 SKILL.md「任务 A」。本文件详述每一步操作。

## 候选词三层校验（核心 — 每个新词必过）

```
Layer 1（机械）：aso_audit.py 自动
  - 字符预算 / 跨字段同根词（含 CJK 子串）/ 跨 locale 重复 / 音译陷阱 / 逗号格式

Layer 2（赛道）：itunes_search_check.py
  - 候选词在 App Store 该国家区返回的 Top 5 是不是同类 App

Layer 3（功能）：⚠️ 最容易遗漏，无脚本能替代
  - "用户搜这个词，点进这个 App 后会满意吗？"
  - 赛道对口（同 AI 大类）≠ 功能对口（你做合成对方做风格化）
  - 失望预测 = 错位词，宁可空 keywords 字段也不堆
```

## Step 1 — 跑 Layer 1（aso_audit.py）

```bash
# 在线模式：直接拉 ASC
python3 ~/.claude/skills/aso-pro-max/scripts/aso_audit.py \
  --app-id <APP_ID> --version-id <VERSION_ID> \
  --out /tmp/aso_report.md

# 脱机模式：从快照 JSON 跑（节省 API 调用，适合迭代调试）
python3 ~/.claude/skills/aso-pro-max/scripts/aso_audit.py \
  --from-file /tmp/snapshot.json --out /tmp/aso_report.md
```

脚本输出：
- 字符预算表（每 locale × 3 字段）
- 🔴 ERROR：跨字段同根词重复（Snowball stem 检测，捕捉 wedding/weddings、bride/bridal、photo/photograph 等）
- 🟡 WARN：keywords 未充分利用 / 跨 locale 同根重复 / 逗号后空格 / 音译陷阱命中 / **CJK 子串重叠**（如 ja `フォトウェディング` 与 name `AIフォトウェディング前撮り`）

## Step 2 — 跑 Layer 2（iTunes Search API）

对每个候选词跑 iTunes：

```bash
python3 ~/.claude/skills/aso-pro-max/scripts/itunes_search_check.py \
  --country jp \
  --keywords "候选词1,候选词2,候选词3" \
  --out /tmp/competition.md
```

读 Top 5 竞品名，分类：
- 同功能竞品 → ✅ 真对口
- 同大类不同功能 → 🟡 半对口（Layer 3 兜底）
- 完全不同领域 → ❌ 大类错位

可选加跑 Google Trends + Suggest（注意：Trends 大概率被限流，Suggest 通常稳定）：

```bash
python3 ~/.claude/skills/aso-pro-max/scripts/google_signals.py \
  --geo JP --hl ja-JP --keywords "..." --out /tmp/google.md
```

## Step 3 — 跑 Layer 3（人脑 + ASC Analytics）

每个 Layer 2 通过的词额外问：「**搜这个词的用户点进 App 后会满意吗？**」

参考已知错位陷阱（见 `locale_strategy.md`「功能错位词识别方法」节）。

数据复核：让用户去 ASC Analytics → Sources → App Store Search 看真实带量 Top 词，对照决策。

## Step 4 — 决定哪些 finding 不改

不是所有 ERROR/WARN 都要修：

- **跨 locale 已知刻意保留**：如某词在两个市场都是核心搜索词，宁可重复也不能舍
- **CJK 短 Name 豁免**：`微出片` 3 字符不需要补 BrandName 模式
- **Subtitle 短豁免**：CJK 语言 15/30 已能完整表达，硬塞反而破坏可读性
- **CJK 子串 WARN 是黑盒提醒**：Apple CJK 索引行为不明，可能浪费可能不浪费，看是否值得保留作"加权实验"

## Step 5 — 优化算法（Name + Subtitle + Keywords 重新分配）

### 字段分工

| 字段 | 字符 | 装什么 |
|------|------|--------|
| **Name** | 30 | Brand + #1 搜索词 |
| **Subtitle** | 30 | #2-#3 搜索词 + 价值主张（不重复 Name 任何词）|
| **Keywords** | 100 | 剩余所有搜索词，用逗号分隔，**逗号后不加空格** |

### 步骤

1. 先确定 Name 的 #1 关键词（市场定位决定，参考 `{project_root}/.aso/context.md`）
2. Subtitle 选 2-3 个不同根的核心词
3. Keywords 列出 12-25 个候选词，按价值排序
4. **从 Keywords 中删除所有与 Name+Subtitle 同根的词**（脚本自动检测）
5. 删除 Layer 2/3 错位的词
6. 用空出的字符塞高价值长尾词，目标 90-100/100

### 跨字段同根词识别（参考）

EN/FR/ES/IT/DE/PT 等罗曼语系词形变化丰富，脚本用 Snowball stemmer 自动捕获：

| 同根词组 | 语言 |
|---------|-----|
| photo / photograph / Photos | EN |
| bride / bridal / brides | EN |
| wed / wedding / weddings | EN |
| novio / novios / novia | ES |
| sposo / sposa / sposi | IT |
| Hochzeit / Hochzeits | DE |
| mariée / marié | FR |

CJK / 泰语：脚本用整词 + 子串双重检测。

## Step 6 — 同语言多 locale 差异化

EN 4 locale (US/GB/AU/CA)、FR 2 locale (FR/CA)、ES 2 locale (ES/MX) 各自独立 100 字符池。脚本会自动检测同语言 locale 间的词干重复并 WARN。

**通用分配思路**（具体词需 iTunes 验证）：

- 主市场 locale（en-US/fr-FR/es-ES）→ 装核心高价值对口词
- 次市场 locale（en-GB/AU/CA / fr-CA / es-MX）→ 装地域文化词 + 互补长尾词

具体某 App 在某 locale 装什么，必须按候选词三层校验法逐一验证，不要照搬其他 App 的分配。

## Step 7 — 落地写入

详见 `asc_cli_recipes.md`：
- 单行字段（name/subtitle/keywords）：`asc localizations update --version <VID> --locale <L> --keywords "..."`
- 多行字段（description/whatsNew）：必须 raw PATCH（CLI 直传会破坏换行）

## Step 8 — 写入后立刻复跑 aso_audit.py（**不能跳，最容易踩坑**）

写入操作不会自动检测新引入的问题。每次改完必须立刻：

```bash
# 复跑全 locale audit（确保新改没引入重复）
python3 ~/.claude/skills/aso-pro-max/scripts/aso_audit.py \
  --app-id <APP_ID> --version-id <VID>
```

**典型新错引入场景**（实战教训）：
- 加 `wedding planner` 到 keywords，但 subtitle 已含 wedding → 新引入跨字段重复
- 给 en-US 加 `bridesmaid`，给 en-GB 加 `brides` → 新引入跨同语言 locale 重复（stem 都是 `bride`）
- 给 ja keyword 加 phrase，与 name 中复合词部分重叠 → 新引入 CJK 子串重复

如果 audit 报新 ERROR/WARN 而不是已有的，说明本次写入引入了问题，立刻修。

---

## 关联任务

- 任务 B（扩展新 locale）：见下方
- 任务 C（截图标题审计）：见 `screenshot_keyword_audit.md`

---

## 任务 B：扩展新 locale 详细步骤

### 市场分级

通用 iOS 市场分级见 `locale_strategy.md`「通用市场分级」节。

### 新 locale 创建清单

1. **App Info**（name + subtitle）：
   ```bash
   asc localizations update --app <APP_ID> --type app-info --locale <LOCALE> \
     --name "..." --subtitle "..."
   ```

2. **Version**（keywords + description）：
   ```bash
   asc localizations create --version <VERSION_ID> --locale <LOCALE> \
     --keywords "..." --description "..."
   ```

3. **Screenshots**（iPhone 6.5" + iPad 13"）— 见项目内截图工具

4. **whatsNew**（多行字段，必须 raw PATCH）— 见 `asc_cli_recipes.md`

### 同语言变体处理

- `fr-CA` 创建后用 `fr-FR` 截图（不要 fallback 到英文）
- `es-MX` 同理用 `es-ES` 截图
- `pt-PT` 用 `pt-BR` 截图
- `zh-Hant` 与 `zh-Hans` 各有独立截图（不互通）
