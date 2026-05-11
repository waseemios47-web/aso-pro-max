# Locale 策略与已知坑

> 通用 ASO 跨语言/跨市场知识。不含项目特定策略——具体 App 的市场定位、词分配等放 `{project_root}/.aso/context.md`。

## 跨 locale 集群定位策略（通用）

不同语言市场对同一功能的搜索习惯差异巨大，单一定位很难覆盖所有市场。常用做法是**分集群定位**：

- 把 locale 按文化/搜索习惯分 2-3 个集群（典型：西方 + 阿拉伯 vs 亚洲；或 EN-中心 vs 本地化）
- 每个集群在 Name/Subtitle 用对应核心定位词
- 同集群内部 keyword 池差异化（避免跨同语言 locale 重复）

具体哪个集群用什么词，取决于 App 实际功能 + 各市场用户搜索习惯，不能照搬模板——必须靠 iTunes Search API 在目标 storefront 实测 Top 5 竞品赛道。

## 跨索引 locale 矩阵

某些市场会同时索引多个 locale 的 Keywords，可以利用这点免费扩展关键词池。

| 主市场 | 主索引 locale | 跨索引 locale |
|--------|-------------|-------------|
| 美国 | en-US | es-MX, ar-SA, zh-Hans, zh-Hant, fr-CA, pt-BR + 更多（共约 10 个）|
| 英国 | en-GB | fr-FR (部分)|
| 法国 | fr-FR | en-GB (部分)|
| 加拿大 | en-CA | fr-CA |
| 沙特/UAE | ar-SA | en-US (部分)|

**实战**：在 ar-SA 等被美国跨索引的 locale 中，可以塞入 EN locale 装不下的英文高频词（如 retouch / edit / art / anime / makeup）。

**注意**：跨索引的英文词不要与主 EN locale 重复，否则浪费两边空间。

## 音译陷阱清单（必须删除的低价值词）

这些词是英文音译进非英语 locale 的，搜索量极低，不值得占字符预算：

| Locale | 应删除 | 替换为本地原生词 |
|--------|--------|--------------|
| ja | レトロ, ヴィンテージ, ロマンティック | AI写真, AI加工, ツーショット, 神社, 白無垢 |
| ko | 빈티지, 레트로, 로맨틱, 브라이덜, 리터칭 | 셀프웨딩, 인생네컷, AI사진, 보정, 스드메 |
| ar-SA | رومانسي (romantic), كلاسيك (classic), فنتج (vintage), ريترو (retro)| زواج, حناء, زفة, تعديل |
| th | วินเทจ (vintage), เรโทร (retro), โรแมนติก (romantic) | พรีเวดดิ้ง, แต่งรูป, ชุดไทย |
| tr | vintage, retro | nikah, kına, poz |
| es / pt / fr / de / it | vintage, retro | (各语言原生词，见各 locale 当前 keywords)|
| vi | vintage, retro | chỉnh sửa, đẹp, Hàn Quốc |

`aso_audit.py` 内置此清单，会自动 WARN。新增 locale 时注意更新脚本。

## 各语言 AI 词形参考（仅形态参考，非推荐清单）

2026 年 AI 关键词渗透率达 22%（Photo & Video 类最高）。**以下仅是各语言"AI"词如何拼写/组合的形态参考**，不代表这些词适合你 App——必须按候选词三层校验法（`stage5_audit_validate.md`）实测后再决定加不加。

| 语言 | AI 词形态例 | 形态注意 |
|------|--------|------|
| EN | ai photo editor / ai generator / ai portrait / ai art | 单词 `generator` / `avatar` 在 EN 已被游戏 IP/抽奖 app 占据，**赛道严重错位**，单字不可用，phrase 慎用 |
| JA | AI写真 / AI加工 / AI画像生成 | 复合词形式，不要用日韩混合的 `AI フォト` |
| KO | AI사진 / AI프로필 | 韩语 AI 常直接用英文 `AI` 前缀 |
| ZH | AI合成 / AI换脸 / AI修图 | 中文 AI 搜索极密集，但具体词的搜索量差异大 |
| AR | ذكاء اصطناعي | 阿拉伯语 AI 术语长，占预算多，慎用 |

**重要警告**：含 "AI" 的 keyword 经常和 name/subtitle 中的 "AI" 重复（黄金原则 #1），必须先确保 name/subtitle 已索引 "AI" 后再决定 keyword 是否需要 "AI"-前缀复合词。

## Face Swap 品类词（各语言）

Face Swap 品类爆发（Reface 1 亿+ 下载）。各语言"换脸/交换"词：

- EN: swap, merge, morph, blend
- ES: intercambio, troca (PT)
- DE: Tausch
- IT: scambio
- FR: échange
- JA: 合成写真 / 顔交換（少用）
- KO: 합성사진
- ZH: 合成 / 换脸

## 通用市场分级（订阅类 App，按 iOS 渗透 + 消费力）

iOS App Store locale 不需要也不应该全做。订阅类垂直 App 的常用分级：

| 梯队 | 市场 | iOS 渗透率 | 决策 |
|------|------|-----------|------|
| S | 美国、日本 | 50-57% | ✅ 必做 |
| A | 韩国、沙特/UAE、台湾 | 30-45% | ✅ 必做 |
| B | DE/FR/GB/IT/ES/AU/CA | 28-55% | ✅ 通常做 |
| C | 越南、泰国、土耳其 | 28-34% | 🟡 看产品文化匹配 |
| D | 巴西、墨西哥（iOS<22%）| 17-22% | 🟡 跨索引收益为主 |
| ❌ | 印尼（id）、印度（hi）、马来（ms）| <15% | ❌ 跳过 |

具体某 App 是否做某 locale，要结合订阅价格、产品文化适配（如婚纱 App 在伊斯兰市场需注意内容）综合判断。

## 「功能错位词」识别方法

每个 App 类型有自己的错位词陷阱。**没有放之四海而皆准的清单**——同一个词在不同 App 上可能完全相反（`bridal` 在伴娘服 App 上对口，在双人合成 App 上错位）。

**通用识别方法**：

1. 跑 `itunes_search_check.py --country <CC> --keywords "..."` 看候选词的 Top 5
2. 列 Top 5 实际是什么类型的 App（修图 / 风格化 / 婚介 / 游戏 / 工具…）
3. 对比你 App 的实际功能：
   - **同功能** → ✅ 完美对口
   - **同大类不同功能** → ❌ 功能错位（最危险，看着像对其实不对）
   - **完全不同领域** → ❌ 大类错位

**典型错位词陷阱（按 App 类型分类，仅供参考，不是绝对清单）**：

| 错位词族 | 真实意图 | 哪类 App 应该躲开 |
|---|---|---|
| ghibli / cartoon me / anime me / toon | 单人 AI 风格化 | 多人合成、修图、生产力 |
| retouch / glow up / beautify / airbrush | 单人美颜修图 | 合成、相册、风格化 |
| headshot / portrait maker | 单人职业头像 | 合影、合成、广告头像之外的 |
| renew / restore old photo | 老照片修复 | 合成、新拍 |
| collage / gallery / frame / stitch | 拼贴/相册管理 | AI 合成、单图编辑 |
| bridal / bridesmaid / gown / tuxedo | 礼服购物 | 拍照类、合成类 |
| dating / married / soulmate / fiancé | 婚介找对象 | 给已确认伴侣的 App |
| love / romantic（单字）| 浪漫小说 / widget | 工具类 App |

**为什么功能错位词比纯空白更糟**：用户搜进来 → 发现你 App 做的不是他要的 → 秒跳出 → 转化率极低 → Apple 算法看到低转化率 → **降权**（不仅这个词没用，整体排名都被拉下来）。

宁可空 keywords 字段也不堆功能错位词。

## 通用「品类巨头垄断词」清单

下列词在 EN 是被巨头吞噬的，搜进去用户全去了大平台，垂直 App 拿不到曝光：

| 词 | 巨头 | 垄断证据（iTunes Top） |
|---|---|---|
| face | Facebook + FaceApp | 7800万 总评分 |
| dating | Hinge + Bumble | 880万 |
| generator | Spin The Wheel | 333万（赛道转抽奖）|
| avatar | Avatar World + Avatar Realms | 406万（游戏 IP）|
| ring | Ring - Always Home | 智能家居 |
| wed | Web Video Cast | 浏览器 |
| duo | Duo Mobile | 双因素认证 |
| fiance | Yahoo Finance | 金融 |
| ghibli | ChatGPT | AI 风格化（且巨头流量）|

垂直 App 不要碰这些大词——抢不到曝光，反而占字符。

## 不被 ASC 支持的 locale

```
en-IN, en-SG, en-PH, en-ZA   — Apple 不支持这些英语变体
```

## Apple 完整 locale 清单（高价值）

```
en-US, en-GB, en-AU, en-CA  — 英语 4 池
zh-Hans, zh-Hant            — 中文 2 池
ja, ko                      — 日韩
de-DE                       — 德语
fr-FR, fr-CA                — 法语 2 池
es-ES, es-MX                — 西语 2 池
it                          — 意大利语
ar-SA                       — 阿拉伯语
pt-BR                       — 巴西葡语
th                          — 泰语
tr                          — 土耳其语
vi                          — 越南语
```
