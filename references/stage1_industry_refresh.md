# Stage 1: ASO 行业知识刷新

> 定期抓最新 ASO 算法/趋势/工具变化，更新 skill 的黄金原则、locale_strategy.md、asa_api_limitations.md 等通用知识。

## 触发时机

- **季度跑一次**（ASO 算法不经常变，但年度有 1-2 次重大更新）
- 用户明确要求"看看 ASO 最近有什么新动向"
- 发现脚本/工作流明显失灵时（兜底排查）

## 工作流

### Step 1: 启动并行调研 Agent

按主题分 3-4 个 Agent 并行跑，每个负责一类信息源：

```
Agent A: Apple 官方更新
  - Apple Developer documentation - App Store search / ASO
  - WWDC ASO 相关 session
  - App Store Connect 帮助文档变更
  - ASA / Apple Ads Platform API 文档

Agent B: 第三方 ASO 工具厂商博客
  - AppTweak blog (apptweak.com/blog)
  - AppFollow blog
  - Sensor Tower 报告
  - data.ai 季度报告
  - Mobile Action insights

Agent C: 独立 ASO 顾问 + 论坛
  - ASO Stack newsletter
  - r/AppStoreOptimization
  - Apple Developer Forums 搜索热点

Agent D: AI / 算法变更追踪
  - Apple AI 产品发布对搜索的影响
  - 截图算法变更
  - 跨索引规则变化
```

### Step 2: 每个 Agent 的 prompt 模板

```
抓取 [信息源] 2025-12 至今的 ASO 相关内容。
重点查：
1. Apple App Store 搜索算法是否有变更（截图索引、字段权重等）
2. 新增/废弃的 ASC 字段或 API 端点
3. 新热门关键词类型（如 2024 的 AI、2025 的截图标题、2026 的 ?）
4. 各 locale 新文化词或衰退词
5. ASA / Apple Ads Platform API 状态

输出格式：
- 时间 | 来源 | 变更内容 | 对本 skill 的影响
- 最多 200 字总结
```

### Step 3: 汇总产出

把 Agent 结果归类合并到：

| 影响目标 | 行动 |
|---|---|
| 黄金原则需更新 | 改 `SKILL.md` 黄金原则节 |
| Locale 知识变更 | 改 `locale_strategy.md` |
| API 变更 | 改 `asa_api_limitations.md` |
| 新工具可接入 | 评估加新 script |
| 算法变更影响检测逻辑 | 改 `aso_audit.py` 检测器 |

### Step 4: 保留调研报告

汇总报告存到项目内：`Marketing/aso_industry_refresh_{YYYY-Q}.md`（不进 skill）

skill 内只更新通用规则。

## 已知历史更新（参考时间线）

- **2024-Q4**：Apple Search Ads Connect → "Apple Ads"（含 Search + Display 等）品牌升级
- **2025-?**：截图标题文字开始被索引为关键词（黄金原则 #5）
- **2025-?**：AI 关键词渗透率达 22%（Photo & Video 类最高）
- **2026-03**：ASA Custom Reports GET 端点开始返回 403（Apple 迁 Insights API）
- **2026 夏（计划）**：Apple Ads Platform API 上线，v5 计划 2027-01-26 日落

## 何时不需要跑 Stage 1

- 处理日常 keyword 优化任务（直接 Stage 5）
- 单 locale 词调整（直接 Stage 5）
- 字符预算/重复检测（直接 Stage 5）
- 截图标题对齐（任务 C）
