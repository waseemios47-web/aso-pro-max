# Stage 2: App 功能自动分析

> 扫 App 代码库自动生成 `{project_root}/.aso/context.md`，是 Stage 3-5 的输入基础。

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

启动 1 个 Agent (subagent_type=Explore)：

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

### Step 3: Agent 输出模板

```markdown
# {App Name} 项目特定上下文

## 基础信息
- **App ID**: [从 README 或 CLAUDE.md 提取，找不到则 ?待补充]
- **Bundle ID**: [扫 Xcode 项目或 Manifest 提取]
- **类型**: [iOS/Android/跨平台]
- **覆盖 locale**: [扫 Localizable.xcstrings 或 strings 文件统计]

## App 真实功能（决定 keyword 选词）

### 做的事
- [从 README 主功能列表提取]
- [从 Services/ 目录提取核心 service]
- [从 Views/ 目录提取主要界面行为]

### 不做的事（明确边界）
基于上面"做的事"反推：
- [若 App 是双人合成 → 明确不做单人风格化/AI 修图]
- [若 App 是工具类 → 明确不做内容消费]
- [其他明显边界]

## 商业模型
- **付费模式**: [从订阅 SDK 集成、IAP 代码提取]
- **定价**: [从 RevenueCat / 产品代码或截图]
- **目标用户**: [从市场定位文档/营销文案推断]

## 资源位置
- **截图**: [扫 Marketing/ 目录]
- **本地化**: [Localizable.xcstrings / strings.xml 等]
- **市场调研**: [如有 Marketing/*.md 调研报告]

## 当前 ASO 状态（如已存在）
- **现有 locale**: [枚举 xcstrings 中所有 lang]
- **历史 ASO 调研**: [Marketing/ASO_*.md]
- **最近一次大改时间**: [扫 git log 中 ASO 相关 commit]

## 推荐能用的核心词类型（基于功能反推）

按黄金原则 #6（赛道对口 ≠ 功能对口），列出此 App **真正能服务**的搜索意图类型：

1. **核心功能词族**: [列 2-3 类]
2. **场景/品类词**: [列 2-3 类]
3. **半对口可补充**: [列 1-2 类]

**应避免的功能错位词族**（用户搜进来会失望）：
- [列 3-5 类]

## 待办与已知未完成

[扫 TODO / FIXME 注释 + Marketing/ 内的 P3 标记]
```

### Step 4: 用户审核

Agent 输出后，**让用户检查 "做的事 / 不做的事 / 推荐核心词" 几节**——这部分必须用户确认对，否则 Stage 3-5 全错。

不确定的字段（?待用户补充）必须填完。

### Step 5: 落地

保存为 `references/{project_root}/.aso/context.md`。

### Step 6: 当 App 功能变更后

重新跑 Stage 2 → 覆盖 `{project_root}/.aso/context.md`。Stage 3 调研可能需要相应更新。

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
