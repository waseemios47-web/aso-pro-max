# Apple Search Ads API 限制（2026-05 调研）

> 本文档记录 ASA API **不能做什么**，避免下次有人再花时间走弯路。
>
> 调研依据：
> - 实测端点（自建 PAUSED campaign + 多端点探测，详见下表）
> - [Apple Developer Forum thread/820073](https://developer.apple.com/forums/thread/820073)（custom-reports GET 自 2026-03-16 起 403）
> - [phiture/searchads_api](https://github.com/phiture/searchads_api) 库的端点清单参考

## 核心结论

**ASA API（v5）不公开「全局关键词 popularity」端点。** 这不是配置问题，是 Apple 设计选择。

## 调研路径与证据

| 端点 | 状态 | 证据 |
|------|------|------|
| `POST /api/v5/recommendations` | 503（路径不存在） | 路由表外 |
| `POST /api/v5/keyword-recommendations` | 503 | 路由表外 |
| `POST /api/v5/keyword-search-volumes` | 503 | 路由表外 |
| `POST /api/v5/keywords/search-popularity` | 404（路径合法但资源不存在）| 已废弃或从未存在 |
| `POST /api/v4/.../recommendations` | 410 INVALID_API_VERSION | v4 已废弃 |
| `POST /api/v5/custom-reports`（impression_share_report） | 200 创建成功 | 可写 |
| `GET /api/v5/custom-reports/{id}` | **403 since 2026-03-16** | Apple Developer Forum [thread/820073](https://developer.apple.com/forums/thread/820073) — Apple 正在迁到 Insights API |

## 唯一能拿 popularity 的路径（不可行）

ASA API 的关键词搜索热度（searchPopularity 字段）藏在
**Custom Reports → impression-share-report** 中。要拿到这份报告需要：

1. 账号下有 campaign + adgroup（**OK，可建 PAUSED 不花钱**）
2. campaign 必须 **真实投放过**，有 impression 数据
3. POST 创建 custom-report → 拿 report_id（OK）
4. GET 拿结果 → **403 自 2026-03-16 起，Apple 在迁 Insights API**

即使没有 #4 的 403 bug，第 #2 条「真实投放过」就排除了无广告预算的 ASO 工具场景。

## 替代方案

| 方案 | 成本 | 提供的数据 |
|------|------|----------|
| AppTweak API | €99/月起 | popularity score + 难度 + 排名追踪 |
| Sensor Tower API | $$$ | 类似 + 竞品深度数据 |
| data.ai (App Annie) | $$$ | 类似 |
| AppFollow API | €69/月起 | popularity + ASO 工具 |
| Apple Ads Platform API（2026 夏推出） | 免费？未知 | v5 后继，能力未知 |
| **手工查 ASA 后台 UI** | 免费 | popularity 可见但需手动逐词查 |

## 已保留的资产

- ✅ `scripts/asa_auth.py` — JWT + token 缓存模块。未来接 Apple Ads Platform API 或其他需 ES256 OAuth 的端点时可直接复用
- ✅ `.env.example` 模板 — 用户按需在自己机器上拷贝为 `.env` 填凭据（凭据不存 skill）
- ✅ `aso_audit.py` 中保留 `LOCALE_TO_STOREFRONT` 映射，接其他 popularity 数据源时直接用

## 已删除（不再使用）

- ❌ `scripts/asa_keywords.py` — keyword recommendations / popularity stub（端点不存在）
- ❌ `scripts/asa_bid.py` — bid recommendations stub（同上）
- ❌ `references/asa_api_recipes.md` — 旧版接入指南，已被本文件取代

## 时间线参考

- **2027-01-26**：ASA API v5 日落
- **2026 夏**：新 "Apple Ads Platform API" 上线（继任者）
- 上线后再评估是否值得接入
