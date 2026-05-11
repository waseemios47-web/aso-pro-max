# ASC CLI 实战配方与已知坑

## 前置

```bash
brew install rudrankriyam/tap/asc
asc auth init   # 配置 API key
```

## 常用查询

### 列出当前账号下所有 App

```bash
asc apps list --output json --paginate \
  | python3 -c "import json,sys; d=json.load(sys.stdin); [print(a['id'], a['attributes']['bundleId']) for a in d['data']]"
```

### 拉取所有 locale 的 app-info（name + subtitle）

```bash
asc localizations list --app <APP_ID> --type app-info --output json --paginate
```

### 拉取所有 locale 的 version localization（keywords + description）

```bash
asc localizations list --version <VERSION_ID> --output json --paginate
```

### 单 locale 详情

```bash
asc localizations list --version <VERSION_ID> --locale "ja,ko" --output table
```

## 写入操作

### 单行字段（name / subtitle / keywords）— 直接 CLI

```bash
# Name + Subtitle 在 app-info 下
asc localizations update --app <APP_ID> --type app-info --locale <L> \
  --name "<name 内容>" --subtitle "<subtitle 内容>"

# Keywords 在 version 下
asc localizations update --version <VERSION_ID> --locale <L> \
  --keywords "kw1,kw2,kw3,..."
```

### 多行字段（description / whatsNew）— **必须 raw PATCH**

⚠️ **已知坑**：`--whatsNew='line1\nline2'` 通过 shell 传参会破坏换行，API 返回 200 但内容为空。

**正确做法**：写 JSON 到临时文件，用 `asc raw PATCH`：

```python
import json, subprocess
loc_id = "<localization-id>"
note = """v1.5 更新内容：
- 新增 12 个亚洲风格模板
- 修复 iPad 截图错位问题"""

body = {
    "data": {
        "type": "appStoreVersionLocalizations",
        "id": loc_id,
        "attributes": {"whatsNew": note}
    }
}
with open(f"/tmp/wn_{loc_id}.json", "w") as f:
    json.dump(body, f, ensure_ascii=False)

subprocess.run([
    "asc", "raw", "PATCH",
    f"/v1/appStoreVersionLocalizations/{loc_id}",
    f"@/tmp/wn_{loc_id}.json"
])
```

## 截图上传

```bash
LOC_ID=$(asc localizations list --version <VERSION_ID> --locale ja --output json \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['data'][0]['id'])")

asc screenshots upload --version-localization "$LOC_ID" \
  --path "Marketing/ja-screenshots-gen/output/65" \
  --device-type "APP_IPHONE_65"

asc screenshots upload --version-localization "$LOC_ID" \
  --path "Marketing/ipad_output/ja" \
  --device-type "APP_IPAD_PRO_3GEN_129"
```

**已知坑**：失败状态（FAILED）的截图会阻塞提交审核（"仍有截屏上传中"），必须用 raw DELETE 删除后才能重新上传。

## 批量元数据 pull/push

```bash
# 拉到本地
asc metadata pull --app <APP_ID> --version "1.5.0" --dir ./metadata

# 编辑各 locale 的 name.txt / subtitle.txt / keywords.txt / description.txt

# 推回
asc metadata push --app <APP_ID> --version "1.5.0" --dir ./metadata

# 验证
asc metadata validate --dir ./metadata
```

⚠️ **实战中较少用**：multi-line 字段（description）经过文件中转后可能仍有换行问题。复杂改动还是用 raw PATCH 更稳。

## 资源 ID 速查模板

各项目的常用 ID 记到对应 `{project_root}/.aso/context.md`，包括：

```
App ID:                <由 asc apps list 查到>
LIVE appInfo ID:       <从 asc localizations list --app <APP> --type app-info 提取>
PENDING appInfo ID:    <同上>
当前 PREPARE_FOR_SUBMISSION version_id: <由 asc versions list --app <APP> 查到>
```

> ⚠️ ID 会随版本生命周期变化：提交新版本后原 PENDING 变 LIVE、新 PENDING 重新生成。改动前必须用 `asc apps list` 和 `asc versions list --app <APP>` 重新确认。
> 各项目的 ID 速查记录在 `{project_root}/.aso/context.md`。
