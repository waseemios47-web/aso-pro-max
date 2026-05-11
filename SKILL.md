---
name: aso-pro-max
description: |
  App Store Optimization (ASO) 端到端 — 从抓最新 ASO 知识、分析 App 功能、多语言市场调研、起草候选词、到三层校验写入。
  触发场景：
  - 用户提到 ASO、应用商店优化、关键词策略、多语言扩展
  - 审计 / 检查 / 优化 App Store 的 name / subtitle / keywords / description
  - 新增 ASC locale、扩展市场、修复跨字段重复
  - 截图标题对齐 ASO 关键词（Apple 2025 截图索引算法）
  - 提到 asc CLI、ASC API、metadata pull/push、raw PATCH
  - 为新 App 从零做 ASO（端到端 5 阶段）
  即使用户没明说 "ASO"，凡涉及搜索可见性 / 关键词覆盖 / 多 locale 元数据，都用此 skill。
---

# ASO Pro Max — 端到端 5 阶段

## 工具集

```
~/.claude/skills/aso-pro-max/
├── SKILL.md                              # 本文件（导航 + 决策树）
├── .env / .env.example                   # ASA 凭据（保留备用）
├── scripts/
│   ├── aso_audit.py                      # Stage 5 主审计（字符预算/跨字段/跨 locale/CJK 子串/音译陷阱）
│   ├── itunes_search_check.py            # Stage 3+5 iTunes Search API 赛道验证
│   ├── google_signals.py                 # Stage 3+5 Google Trends + Suggest 补充信号
│   └── asa_auth.py                       # 备用：未来 Apple Ads Platform API
└── references/
    ├── stage1_industry_refresh.md        # Stage 1: 抓最新 ASO 知识（季度）
    ├── stage2_app_analysis.md            # Stage 2: 扫代码自动生成 {app}_context.md
    ├── stage3_locale_research.md         # Stage 3: 并行多 Agent 调研各 locale
    ├── stage4_keyword_drafting.md        # Stage 4: 基于 2+3 起草候选词
    ├── stage5_audit_validate.md          # Stage 5: 三层校验 + 写入 ASC
    ├── locale_strategy.md                # 通用：跨 locale 索引 / 音译陷阱 / 市场分级
    ├── asc_cli_recipes.md                # 通用：asc CLI + raw PATCH 坑
    ├── screenshot_keyword_audit.md       # 通用：截图标题对齐（任务 C）
    ├── asa_api_limitations.md            # ⚠️ ASA API 调研负面结论
    └── project_context_template.md       # 项目 context 空白模板（用户拷到自己项目里填）
```

## 5 阶段端到端流程

```
┌──────────────────────────────────────────────────────────────────┐
│ Stage 1: 抓 ASO 行业最新知识（季度跑 1 次）                       │
│   并行多 Agent 抓 Apple/AppTweak/Sensor Tower/论坛                │
│   → 更新 SKILL.md 黄金原则 / locale_strategy / asa_limitations    │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 2: 分析 App 真实功能（每个 App 1 次，重大改版后复跑）        │
│   Explore Agent 扫 README / CLAUDE.md / Models / Services         │
│   → 生成 {project_root}/.aso/context.md                              │
│   关键：明确"做什么 / 不做什么"，反推哪类词会功能错位（原则 #6）   │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 3: 多语言市场调研（每个 locale 首次 1 次）                   │
│   并行 4 集群 Agent 调研（EN 4 池 / CJK / 欧洲 / 新兴）            │
│   每个 Agent 用 itunes_search_check.py 验证赛道                   │
│   → Marketing/aso_locale_research/{LOCALE}.md 一份每 locale        │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 4: 起草候选词（每个 locale 写入前 1 次）                     │
│   基于 Stage 2 + Stage 3 起草 Name/Subtitle/Keywords              │
│   含跨字段预演 + 跨同语言 locale 协调                              │
│   → /tmp/{app}_drafts_{date}.json                                 │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 5: 三层校验 + 写入（每次改动必跑）                            │
│   Layer 1 机械: aso_audit.py（字符/跨字段/跨 locale/CJK 子串/音译）│
│   Layer 2 赛道: itunes_search_check.py（Top 5 竞品类型）           │
│   Layer 3 功能: 人脑（搜进来会失望吗？）+ ASC Analytics            │
│   → asc localizations update 写入                                  │
│   → 写入后必跑 audit verify（防引入新错）                          │
└──────────────────────────────────────────────────────────────────┘
```

## 决策树：用户来了我先跑哪个 Stage？

```
用户请求 / 触发场景 → 走哪个 Stage？

"看下/优化/审计 keywords"             → 直接 Stage 5
"为某 locale 起草新方案"                → Stage 4 → Stage 5
"新增 locale"                          → Stage 3 + 4 + 5
"接手新 App / App 上下文不熟"           → Stage 2 → 后续按需
"做一份新的全 locale 深度调研"          → Stage 3
"看看 ASO 最近有什么新动向"             → Stage 1
"截图标题与 keywords 对齐"              → 任务 C（screenshot_keyword_audit.md）
```

## 黄金原则（6 条，违反任何一条都意味着真金白银的浪费）

1. **Name + Subtitle + Keywords 是统一索引池** — 跨字段绝不重复任何词（含同根词）
2. **字符预算 = 钱** — Name 用满 ≥15（CJK 可豁免）、Subtitle 用满 ≥20、Keywords 用满 95-100
3. **同语言多 locale 各自独立 100 字符** — en-US/GB/AU/CA 用 4 套不同词，绝不重复
4. **音译陷阱**：vintage / retro / romantic 在非英语 locale 搜索量极低，删了换本地原生词
5. **截图标题 2025 年起被索引** — 截图既是转化资产也是 ASO 资产，标题要承接核心搜索词
6. **「赛道对口」≠「功能对口」** — iTunes Top 竞品在同一大类（如 AI 图像处理）不代表 App 真能服务该搜索意图。每个候选词必须问：**搜这个词的用户点进这个 App 后会失望吗？** 失望→转化率低→Apple 算法降权。宁可空 keywords 字段也不堆功能错位词。

## 任务对应入口

| 用户请求 | 任务 | 入口 reference |
|---|---|---|
| 审计现有 / 优化 keywords | 任务 A | `stage5_audit_validate.md` |
| 扩展新 locale | 任务 B | `stage3` + `stage4` + `stage5` |
| 截图标题 ASO 对齐 | 任务 C | `screenshot_keyword_audit.md` |
| 深度多语言调研 | 任务 D | `stage3_locale_research.md` |
| 接手新 App | 任务 E | `stage2_app_analysis.md` |
| ASO 季度行业刷新 | 任务 F | `stage1_industry_refresh.md` |

## 字段限制速查

| 字段 | 限制 | 用什么装 |
|------|------|---------|
| Name | 30 codepoints | Brand + #1 关键词 |
| Subtitle | 30 codepoints | #2-#3 关键词 + 价值主张 |
| Keywords | 100 codepoints | 剩余所有词，逗号分隔（**不加空格**）|
| Promotional Text | 170 codepoints | 营销文案（不被索引）|
| Description | 4000 codepoints | SEO 长文，前 3 行最重要 |

## 项目数据 vs Skill 数据（重要架构约定）

**skill 不存储任何项目数据**。所有 App 特定的 context、调研、草案、audit 归档都放在**项目自己的目录**下：

```
{project_root}/.aso/
├── context.md              # Stage 2 产出（App 功能分析）
├── locale/{LL}.md          # Stage 3 产出（每 locale 一份调研）
├── drafts/{date}.json      # Stage 4 产出（候选词草案）
└── reports/audit_{date}.md # Stage 5 audit 历史归档
```

skill 内只放空白模板 `references/project_context_template.md`——用户首次为某 App 跑 Stage 2 时，把模板拷到 `{project}/.aso/context.md` 然后由 Agent 填充。

**好处**：
- skill 干净可分发（任何项目通用）
- 项目数据跟项目走（用户自己版本化 / .gitignore）
- skill 升级不影响项目数据
- 多 App 互不污染

## 安装 / 卸载 / 健康检查

```bash
# 安装（首次）
git clone <repo> ~/.claude/skills/aso-pro-max     # 或 symlink 本地开发
pip3 install -r ~/.claude/skills/aso-pro-max/requirements.txt
brew install rudrankriyam/tap/asc                  # asc CLI（ASC API 访问）
asc auth init                                      # 多账号用 asc auth switch --name <profile>

# 健康检查
python3 ~/.claude/skills/aso-pro-max/scripts/aso_audit.py \
  --from-file ~/.claude/skills/aso-pro-max/examples/sample_snapshot.json
# 应输出 2 个 ERROR + 3 个 WARN（教学示例）

# 可选：ASA OAuth（未来 Apple Ads Platform API 准备）
mkdir -p ~/.config/aso-pro-max/.secrets
cp ~/.claude/skills/aso-pro-max/.env.example ~/.config/aso-pro-max/.env
# 编辑 ~/.config/aso-pro-max/.env 填凭据
openssl ecparam -genkey -name prime256v1 -noout \
  -out ~/.config/aso-pro-max/.secrets/asa_private_key.pem
python3 ~/.claude/skills/aso-pro-max/scripts/asa_auth.py   # 应显示 ✅ 认证成功

# 卸载
rm -rf ~/.claude/skills/aso-pro-max
rm -rf ~/.config/aso-pro-max     # 凭据存储位置
```

Python 要求：**≥ 3.10**（脚本使用 PEP 604/585 类型语法）。

## 常见错误

1. 跨字段重复（Name/Subtitle/Keywords 共词）
2. Keywords 字段未填满
3. 同语言 locale 用相同 keywords
4. 音译词填充非英语 locale
5. description 多行字段直接 CLI 传参（必须 raw PATCH）
6. 逗号后加空格（每次浪费 1 字符）
7. 改完不复查（必须复跑 aso_audit.py verify）
8. **功能错位词**（黄金原则 #6）— iTunes Top 赛道对了不代表 App 能服务该意图
9. **用大热单字赌曝光** — face / dating / generator / avatar / ring / wed / duo 在 EN 都被巨头垄断
10. **跳过 Stage 2 直接起草** — 不清楚 App 真实功能 → Stage 3 调研偏 → Stage 4 起草必错
11. **同语言 locale 不协调起草** — 后期一定碰跨 locale 同根冲突（实战教训）
