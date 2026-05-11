# Stage 6: 写入计划 + 执行 + Verify

> 把 Stage 5 决策报告（HTML）解析成机械执行的写入计划，逐 locale 调 `asc localizations update` 写入 ASC，写入后立即跑 audit verify 兜底。

## 触发时机

- Stage 5 决策报告已出（`{project_root}/.aso/reports/stage5_final.html`）
- 用户授权写入 ASC（必须明确授权，不擅自执行）

## 黄金原则 #7 应用

**主 Claude 只做机械执行**，不参与"该写哪些 / 改哪些字段"的判断。决策来自 Stage 5 报告 + 独立 Agent 的写入计划。

## 工作流

### Step 1: 独立 Agent 解析 Stage 5 报告 → 生成写入计划 JSON

启动 1 个 general-purpose Agent，让它读 `stage5_final.html` + 现网 ASC 状态，输出写入计划：

```bash
# Agent 输出到:
{project_root}/.aso/drafts/{date}_writeplan.json
```

JSON schema：
```json
{
  "version_id": "ASC version id",
  "app_id": "ASC App ID",
  "generated_at": "YYYY-MM-DD",
  "source_report": "{project_root}/.aso/reports/stage5_final.html",
  "skip_locales": ["zh-Hans", "zh-Hant", ...],
  "skip_rationale": {"zh-Hans": "用户决定不动", ...},
  "writes": [
    {
      "locale": "en-US",
      "name": null,                    // null 表示不改这个字段
      "subtitle": "新 subtitle 文本",
      "keywords": "kw1,kw2,...",
      "char_check": {"name": "X/30", "subtitle": "X/30", "keywords": "X/100"},
      "rationale": "Stage 5 决策 + 修复了什么 ERROR + 合并自哪",
      "source": "草案 ∪ 现网（并集合并）",
      "audit_self_check": "✅ Snowball stem 比对零跨字段同根"
    }
  ]
}
```

### Step 2: Agent 自检（必做）

写入计划生成时 Agent 必须自检：
1. 拉一次 ASC 现网真实状态作为"并集合并"的基准
2. 每个 locale 的 name + subtitle + keywords 跑 Snowball stem 自检（CJK 整词+子串双重）
3. 字符预算检查（30/30/100）
4. 修复 Stage 5 报告中所有 ERROR
5. 标注每个 locale 的"采纳来源"：纯草案 / 草案 ∪ 现网 / 保留现网

### Step 3: 主 Claude 机械执行写入

```python
import json, subprocess

with open("{project_root}/.aso/drafts/{date}_writeplan.json") as f:
    plan = json.load(f)

VID = plan["version_id"]
APP_ID = plan["app_id"]

for w in plan["writes"]:
    loc = w["locale"]
    name = w.get("name")
    sub = w.get("subtitle")
    kw = w.get("keywords")

    # app-info update（name 或 subtitle 任一非 null 就要跑）
    if name is not None or sub is not None:
        cmd = ["asc", "localizations", "update", "--app", APP_ID,
               "--type", "app-info", "--locale", loc]
        if name is not None:
            cmd += ["--name", name]
        if sub is not None:
            cmd += ["--subtitle", sub]
        subprocess.run(cmd, check=True)

    # version update（keywords）
    if kw is not None:
        cmd = ["asc", "localizations", "update", "--version", VID,
               "--locale", loc, "--keywords", kw]
        subprocess.run(cmd, check=True)
```

### Step 4: 写入后立刻跑 audit verify（不能跳！）

```bash
python3 ~/.claude/skills/aso-pro-max/scripts/aso_audit.py \
  --app-id <APP_ID> --version-id <VID> \
  --out {project_root}/.aso/reports/audit_postwrite.md
```

### Step 5: 如有 ERROR 立即修复

**实战教训**：第一次端到端测试中，写入后立刻发现 5 个新 ERROR：
- `fr-CA` keyword `AI couple` 与 v2.1 现网保留的 Name `Couple IA` 跨字段冲突
- `vi` keyword `đám cưới` 与 Name `Ảnh Cưới` 冲突
- `ko` keyword `얼굴 합성` 与 Name `합성` 冲突
- `en-GB` keyword `bridal` 与新写入 Subtitle `Bridal Shoot` 冲突
- `es-ES` keyword `retrato` 与 Name `Retratos` 冲突

**根因**：Stage 4 草案与"保留 v2.1 Name"做"并集合并"时漏检了跨字段冲突。Stage 6 Step 2 的 Agent 自检如果包含**真实拉一次现网状态**+ **逐 locale Snowball stem 比对**，能避免这类错误。

**修复方法**：
1. 用 `asc localizations list` 查冲突 locale 现状
2. 删 keyword 中的冲突词，或调整 Subtitle 让 keyword 词不重叠
3. 复跑 audit verify 确认零 ERROR

### Step 6: 二次 audit verify 直到全绿

Step 5 修复后必须**再跑一次** audit，直到 `🔴 ERROR (0)`。

剩余 WARN 可分类容忍：
- 字符未充分利用（设计接受）
- 跨同语言 locale 同根（设计接受，二选一）
- CJK 子串重叠（黑盒提醒，作加权实验保留）

## 实战 checklist

```
□ Stage 5 报告 HTML 存在
□ 用户授权写入
□ 启 Agent 生成 writeplan.json
□ Agent 自检：现网拉取 + Snowball stem + 字符预算 + ERROR 修复 + 简繁字形差异
□ 主 Claude 机械跑 asc localizations update
□ 写入后立刻跑 aso_audit.py（**必跑**）
□ 有 ERROR 立即修
□ 二次 audit 确认 ERROR=0
□ 把 audit_postwrite.md 归档到 .aso/reports/
```

## 何时不需要 Stage 6

- 单字段微调（直接 asc 命令 + 单一 audit）
- 仅看不改（Stage 5 报告读完用户决定不动）
- 重做 Stage 3 调研（这不涉及写入）

## 与 Stage 5 的交接

Stage 5 输出 `stage5_final.html`（决策报告）→ Stage 6 Agent 把决策落实成 JSON → 主 Claude 执行写入 → audit verify。

如果 Stage 5 没有给某 locale 具体的字段值（如只标 "✅ 升级" 但不附文本），Stage 6 Agent 要从 Stage 4 草案 + Stage 5 报告综合提取。
