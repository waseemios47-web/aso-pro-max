# ASO Pro Max — Claude Code Skill for App Store Optimization

[English](#english) | [中文](#中文)

---

<a id="english"></a>
## English

A professional-grade [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill that turns Claude into an ASO (App Store Optimization) expert. It covers the complete lifecycle: auditing existing metadata, optimizing Name/Subtitle/Keywords for maximum search coverage, expanding to new locales, and ensuring zero wasted character budget.

### What It Does

- **Audit** existing App Store metadata across all locales — find underutilized keywords, cross-field duplication, and wasted characters
- **Optimize** Name, Subtitle, and Keywords using Apple's indexing rules (combined pool deduplication)
- **Expand** to new locales for multiplied keyword coverage (even without translating the app UI)
- **Batch operations** for adding 10+ locales efficiently via App Store Connect API
- **Verify** all changes with automated completeness checks

### Key Principles

1. **Apple indexes Name + Subtitle + Keywords as ONE pool** — never repeat words across fields
2. **Every unused character = missed search opportunity** — target 95-100/100 chars for Keywords
3. **Locale multiplication** — 4 English locales = 4 × 100 chars = 400 keyword chars
4. **Same-language locales get DIFFERENT keywords** — en-US, en-GB, en-AU, en-CA each with unique terms

### Installation

Copy the `SKILL.md` file to your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills/aso-pro-max
cp SKILL.md ~/.claude/skills/aso-pro-max/SKILL.md
```

### Prerequisites

This skill works best with an App Store Connect API integration skill for automated metadata operations. Without it, you can still use the ASO knowledge for manual optimization.

### Usage

Once installed, Claude Code will automatically activate this skill when you mention:

- "Review my ASO" / "Audit my app store metadata"
- "Optimize keywords" / "Improve search ranking"
- "Add new language to App Store Connect"
- "Expand to new markets"
- Any task involving App Store search visibility or keyword strategy

#### Example Prompts

```
Review my App Store metadata and suggest ASO improvements.

Optimize my keywords for en-US — I'm only using 44 out of 100 characters.

Add German (de-DE), French (fr-FR), and Spanish (es-ES) to my App Store listing.

I have en-US keywords set up. Add en-GB, en-AU, en-CA with different keywords to maximize coverage.
```

### Workflows

| # | Workflow | Description |
|---|---------|-------------|
| 1 | **Audit** | Pull all locales, build char-count table, identify 4 issue types |
| 2 | **Optimize** | Deduplicate across fields, fill keyword budget, per-language strategies |
| 3 | **Expand** | Market prioritization framework, per-locale creation checklist |
| 4 | **Batch Ops** | Python scripts for adding 10+ locales at once |
| 5 | **Verify** | Post-optimization completeness checks |

### Common Mistakes This Skill Prevents

1. Repeating keywords across Name/Subtitle/Keywords (Apple indexes them together)
2. Keywords field half-empty (leaving search potential on the table)
3. Same keywords in fr-FR and fr-CA (wasting the second keyword pool)
4. Spaces after commas in Keywords (`bride, groom` wastes 1 char each)
5. Missing Terms of Service & Privacy Policy in descriptions
6. Not verifying after API changes (silent truncation)

---

<a id="中文"></a>
## 中文

一个专业级 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 技能，让 Claude 变身 ASO（App Store 搜索优化）专家。覆盖完整生命周期：审计现有元数据、优化名称/副标题/关键词以最大化搜索覆盖、扩展多语言市场、确保零字符浪费。

### 功能

- **审计** 所有语言的 App Store 元数据 — 发现关键词浪费、跨字段重复、字符预算未用满
- **优化** 名称、副标题和关键词，遵循 Apple 索引规则（联合池去重）
- **扩展** 新语言区域以成倍增加关键词容量（无需翻译 App 界面）
- **批量操作** 通过 App Store Connect API 高效添加 10+ 语言
- **验证** 自动化完整性检查，确保所有改动生效

### 核心原则

1. **Apple 将名称 + 副标题 + 关键词作为一个联合池索引** — 绝不跨字段重复用词
2. **每个未用字符 = 错过一次搜索机会** — 关键词字段目标 95-100/100 字符
3. **语言区域乘数效应** — 4 个英语区域 = 4 × 100 字符 = 400 字符关键词容量
4. **相同语言的不同区域用不同关键词** — en-US、en-GB、en-AU、en-CA 各放独立词组

### 安装

将 `SKILL.md` 复制到 Claude Code 技能目录：

```bash
mkdir -p ~/.claude/skills/aso-pro-max
cp SKILL.md ~/.claude/skills/aso-pro-max/SKILL.md
```

### 前置条件

配合 App Store Connect API 集成技能使用效果最佳，可以自动化执行元数据操作。没有它也可以使用 ASO 知识进行手动优化。

### 使用方法

安装后，当你提到以下内容时 Claude Code 会自动激活此技能：

- "审查我的 ASO" / "审计 App Store 元数据"
- "优化关键词" / "提高搜索排名"
- "添加新语言到 App Store Connect"
- "扩展到新市场"
- 任何涉及 App Store 搜索可见性或关键词策略的任务

#### 示例提示

```
审查我的 App Store 元数据，给出 ASO 优化建议。

优化 en-US 的关键词 — 我只用了 100 个字符中的 44 个。

给我的 App Store 添加德语（de-DE）、法语（fr-FR）和西班牙语（es-ES）。

我已经设置了 en-US 关键词，添加 en-GB、en-AU、en-CA 并使用不同关键词以最大化覆盖。
```

### 工作流程

| # | 工作流 | 说明 |
|---|--------|------|
| 1 | **审计** | 拉取所有语言，构建字符计数表，识别 4 类问题 |
| 2 | **优化** | 跨字段去重，填满关键词预算，按语言制定策略 |
| 3 | **扩展** | 市场优先级框架，逐语言创建清单 |
| 4 | **批量操作** | Python 脚本一次添加 10+ 语言 |
| 5 | **验证** | 优化后完整性检查 |

### 本技能帮你避免的常见错误

1. 名称/副标题/关键词之间重复用词（Apple 将它们作为整体索引）
2. 关键词字段半空（浪费一半搜索潜力）
3. fr-FR 和 fr-CA 使用相同关键词（浪费了第二个关键词池）
4. 关键词逗号后加空格（`bride, groom` 每个多浪费 1 个字符）
5. 描述中缺少服务条款和隐私政策链接
6. API 修改后不验证（可能被静默截断）

---

## Related Projects / 相关项目

- **[appstore-connect](https://github.com/AfeiFun/appstore-connect)** — A Claude Code skill for managing App Store Connect via API (metadata, screenshots, versions). Pair with this skill for end-to-end automated ASO workflows.
- **[appstore-connect](https://github.com/AfeiFun/appstore-connect)** — 通过 API 管理 App Store Connect 的 Claude Code 技能（元数据、截图、版本管理）。与本技能搭配使用，实现端到端自动化 ASO 工作流。

## License

MIT License — see [LICENSE](LICENSE).
