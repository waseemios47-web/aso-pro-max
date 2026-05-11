---
name: aso-pro-max
description: |
  App Store Optimization (ASO) 端到端 — 从抓最新 ASO 知识、分析 App 功能、多语言市场调研、起草候选词、三层校验到写入 ASC 全链路。
  触发场景：
  - 用户提到 ASO、应用商店优化、关键词策略、多语言扩展
  - 审计 / 检查 / 优化 App Store 的 name / subtitle / keywords / description
  - 新增 ASC locale、扩展市场、修复跨字段重复
  - 截图标题对齐 ASO 关键词（Apple 2025 截图索引算法）
  - 提到 asc CLI、ASC API、metadata pull/push、raw PATCH
  - 为新 App 从零做 ASO（端到端 6 阶段）
  即使用户没明说 "ASO"，凡涉及搜索可见性 / 关键词覆盖 / 多 locale 元数据，都用此 skill。
---

# ASO Pro Max — 端到端 6 阶段

## 工具集

```
~/.claude/skills/aso-pro-max/
├── SKILL.md                              # 本文件（导航 + 决策树）
├── .env / .env.example                   # ASA 凭据（保留备用）
├── scripts/
│   ├── aso_audit.py                      # Stage 5 主审计（字符/跨字段/跨 locale/CJK 子串/音译陷阱）
│   ├── itunes_search_check.py            # Stage 3+5 iTunes Search API 赛道验证
│   ├── google_signals.py                 # Stage 3+5 Google Trends + Suggest 补充信号
│   ├── asa_auth.py                       # 备用：未来 Apple Ads Platform API
│   └── preflight_check.sh                # 开源/同步前安全自检
└── references/
    ├── stage1_industry_refresh.md        # Stage 1: 抓最新 ASO 知识（季度）
    ├── stage2_app_analysis.md            # Stage 2: 扫代码生成 context.html
    ├── stage3_locale_research.md         # Stage 3: 并行多 Agent 调研各 locale
    ├── stage4_keyword_drafting.md        # Stage 4: 基于 2+3 起草候选词
    ├── stage5_audit_validate.md          # Stage 5: 三层校验 + 决策报告
    ├── stage6_write_execute.md           # Stage 6: 写入计划 + 执行 + verify
    ├── locale_strategy.md                # 通用：跨 locale 索引 / 音译陷阱 / 市场分级
    ├── asc_cli_recipes.md                # 通用：asc CLI + raw PATCH 坑
    ├── screenshot_keyword_audit.md       # 通用：截图标题对齐
    ├── asa_api_limitations.md            # ⚠️ ASA API 调研负面结论
    └── project_context_template.md       # 项目 context 空白模板
```

## 6 阶段端到端流程

```
┌──────────────────────────────────────────────────────────────────┐
│ Stage 1: 抓 ASO 行业最新知识（季度跑 1 次）                       │
│   并行多 Agent 抓 Apple/AppTweak/Sensor Tower/论坛                │
│   → 更新 SKILL.md 黄金原则 / locale_strategy / asa_limitations    │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 2: 分析 App 真实功能（每个 App 1 次）                        │
│   Explore Agent 扫 README / CLAUDE.md / Models / Services         │
│   → {project}/.aso/context.html（HTML 格式，含依据 + 错位词族）    │
│   ⚠️ 严禁读 Marketing/ASO_*.md 等历史 ASO 报告（污染源）          │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 3: 多语言市场调研（每个 locale 首次 1 次）                   │
│   并行 4 集群 Agent（EN 4 / CJK / 欧洲 / 新兴）                    │
│   每集群跑 itunes_search_check.py 验证赛道                        │
│   → {project}/.aso/locale/{LL}.html × 19                          │
│   ⚠️ iTunes 限流时诚实标 "untested"，不要凭直觉外推                │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 4: 起草候选词（每 locale 写入前 1 次）                       │
│   独立 Agent 基于 Stage 2+3 起草 Name/Subtitle/Keywords            │
│   ⚠️ 主 Claude 不参与判断、不参考现网（避免 LLM 风格漂移）         │
│   → {project}/.aso/drafts/{date}_draft.html                       │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 5: 三层校验 + 对比决策（每次写入前必做）                     │
│   Layer 1 机械: aso_audit.py                                      │
│   Layer 2 赛道: itunes_search_check.py                            │
│   Layer 3 功能: 人脑 + ASC Analytics                              │
│   + 对比现网（草案 vs ASC 当前状态）                              │
│   → {project}/.aso/reports/stage5_final.html                      │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│ Stage 6: 写入计划 + 执行 + verify（每次改动必做）                  │
│   独立 Agent 读 Stage 5 决策 → 生成写入计划 JSON                  │
│   主 Claude 机械执行 asc localizations update                     │
│   写入后立刻复跑 aso_audit.py（必跑，不能跳！）                   │
│   如有 ERROR 立即修复（实战教训：第一次写入常因保留 v2.1 Name      │
│   引入跨字段 ERROR）                                              │
│   → {project}/.aso/reports/audit_postwrite.md                     │
└──────────────────────────────────────────────────────────────────┘
```

## 决策树：用户来了我先跑哪个 Stage？

```
用户请求 / 触发场景 → 走哪个 Stage？

"看下/优化/审计 keywords"             → Stage 5（含 Step 8 verify）
"为某 locale 起草新方案"                → Stage 4 → 5 → 6
"新增 locale"                          → Stage 3 + 4 + 5 + 6
"接手新 App / App 上下文不熟"           → Stage 2 → 后续按需
"做一份新的全 locale 深度调研"          → Stage 3
"看看 ASO 最近有什么新动向"             → Stage 1
"截图标题与 keywords 对齐"              → 任务 C（screenshot_keyword_audit.md）
"端到端从零做"                         → Stage 2 → 3 → 4 → 5 → 6
```

## 黄金原则（7 条，违反任何一条都意味着真金白银的浪费）

1. **Name + Subtitle + Keywords 是统一索引池** — 跨字段绝不重复任何词（含同根词）
2. **字符预算 = 钱** — Name 用满 ≥15（CJK 可豁免）、Subtitle 用满 ≥20、Keywords 用满 95-100
3. **同语言多 locale 各自独立 100 字符** — en-US/GB/AU/CA 用 4 套不同词，绝不重复
4. **音译陷阱**：vintage / retro / romantic 在非英语 locale 搜索量极低
5. **截图标题 2025 年起被索引** — 截图既是转化资产也是 ASO 资产
6. **「赛道对口」≠「功能对口」** — iTunes Top 竞品在同一大类不代表 App 真能服务该搜索意图。失望→转化率低→Apple 算法降权。宁可空 keywords 字段也不堆功能错位词
7. **"端到端" 必须真清污染** — 主 Claude 自己的会话记忆是最大污染源。Stage 2-6 全程用独立 Agent 决策，主 Claude 仅做机械执行 + 数据传递；同时归档 `Marketing/ASO_*.md`、临时屏蔽 `memory/aso-strategy*.md` 才算真端到端

## 任务对应入口

| 用户请求 | 任务 | 入口 reference |
|---|---|---|
| 审计现有 / 优化 keywords | 任务 A | `stage5_audit_validate.md` + `stage6_write_execute.md` |
| 扩展新 locale | 任务 B | `stage3` + `stage4` + `stage5` + `stage6` |
| 截图标题 ASO 对齐 | 任务 C | `screenshot_keyword_audit.md` |
| 深度多语言调研 | 任务 D | `stage3_locale_research.md` |
| 接手新 App | 任务 E | `stage2_app_analysis.md` |
| ASO 季度行业刷新 | 任务 F | `stage1_industry_refresh.md` |
| 端到端从零跑 | 任务 G | Stage 2-6 全套 |

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
├── context.html                 # Stage 2 产出（HTML）
├── locale/{LL}.html             # Stage 3 产出（每 locale 一份 HTML）
├── drafts/{date}_draft.html     # Stage 4 产出（HTML）
├── drafts/{date}_writeplan.json # Stage 6 写入计划（JSON）
└── reports/
    ├── stage5_final.html        # Stage 5 决策报告（HTML）
    └── audit_*.md               # 每次 audit 归档
```

新项目从零跑 Stage 2 时，Agent 自动按 `project_context_template.md` 生成 `context.html`。

## 安装 / 卸载 / 健康检查

```bash
# 安装
git clone https://github.com/AfeiFun/aso-pro-max ~/.claude/skills/aso-pro-max
pip3 install -r ~/.claude/skills/aso-pro-max/requirements.txt
brew install rudrankriyam/tap/asc
asc auth init

# 健康检查
python3 ~/.claude/skills/aso-pro-max/scripts/aso_audit.py \
  --from-file ~/.claude/skills/aso-pro-max/examples/sample_snapshot.json
# 应输出 2 ERROR + 3 WARN（教学示例）

# 开源/同步前安全自检
bash ~/.claude/skills/aso-pro-max/scripts/preflight_check.sh

# 可选：ASA OAuth 准备（未来 Apple Ads Platform API）
mkdir -p ~/.config/aso-pro-max/.secrets
cp ~/.claude/skills/aso-pro-max/.env.example ~/.config/aso-pro-max/.env
openssl ecparam -genkey -name prime256v1 -noout \
  -out ~/.config/aso-pro-max/.secrets/asa_private_key.pem
```

Python 要求：**≥ 3.10**。

## 常见错误

1. 跨字段重复（Name/Subtitle/Keywords 共词）
2. Keywords 字段未填满
3. 同语言 locale 用相同 keywords
4. 音译词填充非英语 locale
5. description 多行字段直接 CLI 传参（必须 raw PATCH）
6. 逗号后加空格（每次浪费 1 字符）
7. 改完不复查（**必须复跑 aso_audit.py verify** — Stage 6 Step 8）
8. **功能错位词**（黄金原则 #6）— iTunes Top 赛道对了不代表 App 能服务该意图
9. **用大热单字赌曝光** — face / dating / generator / avatar / ring / wed / duo 在 EN 都被巨头垄断
10. **跳过 Stage 2 直接起草** — 不清楚 App 真实功能 → Stage 3 调研偏 → Stage 4 起草必错
11. **同语言 locale 不协调起草** — 后期一定碰跨 locale 同根冲突（实战教训）
12. **"端到端" 没真清污染**（黄金原则 #7）— Marketing 历史报告 + memory + 主 Claude 自己脑子里的旧经验都是污染源
13. **LLM 编"地域风情词"** — 上一次实战中 en-AU/CA 用 `boho/winter/cottage/maple` 等 iTunes 实测全错位。Stage 4 起草时若该词在 Stage 3 标 `untested`，必须 Stage 5 实测后再决定
14. **保留现网字段但写入新 keywords 时漏检跨字段冲突** — 实战教训：Stage 4 草案与现网 v2.1 字段做"并集合并"时，必须用 Snowball stem 全量自检
