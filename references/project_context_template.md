# {App Name} 项目特定上下文（模板）

> 本文件是 **模板**。每个用 skill 的项目应在**项目自己的目录**下维护一份具体内容，路径约定：
> `{project_root}/.aso/context.md`
>
> 此模板**不要直接填**——拷贝到项目目录后再填。skill 内的本模板永远保持空白/示例状态，避免不同项目数据互相污染。

## 基础信息

- **App Name**:
- **App ID** (ASC):
- **Bundle ID**:
- **类型**: iOS / Android / 跨平台
- **覆盖 locale**:
- **brand_name_per_locale**:  ← 关键字段，防 Stage 4 误改品牌名
  - en-US: "..."
  - zh-Hans: "..."（如本地化品牌名「微出片」而非英文名）
  - zh-Hant: "..."
  - ja: "..."
  - ...

## App 真实功能（决定 keyword 选词）

### 做的事
- 核心功能 1
- 核心功能 2

### 不做的事（明确边界）
按黄金原则 #6（赛道对口 ≠ 功能对口）反推：
- 不做 X（避免相关 keyword）
- 不做 Y

## 商业模型

- **付费模式**:
- **定价**:
- **目标用户**:

## 资源位置

- **截图**: `{project}/{path}`
- **本地化**: `{project}/{path}`
- **市场调研报告**: `{project}/{path}`

## 当前 ASO 状态

- **现网 PREPARE_FOR_SUBMISSION version_id**:
- **最近一次大改时间**:
- **现网 keywords 分布**（按 locale 列字符使用率）:

## 推荐能用的核心词类型

按黄金原则 #6 + 该 App 实际功能反推：

1. **核心功能词族**:
2. **场景/品类词**:
3. **半对口可补充**:

## 应避免的功能错位词族

按"用户搜进来会失望吗？"标准，已识别错位词族：

- 词族 1（原因）
- 词族 2（原因）

## 待办与已知未完成

- TODO 1
- TODO 2

## 历史调研引用

- `.aso/locale/{LL}.md` × N — Stage 3 各 locale 调研
- `.aso/drafts/{date}.json` × N — Stage 4 历次草案
- `.aso/reports/audit_{date}.md` × N — Stage 5 历次 audit 归档

---

> 用户 memory 中可能有跨会话 ASO 决策历史（如 `aso-strategy.md`）—— Claude 自动加载，无需在此引用路径。
