---
name: aso-pro-max
description: |
  App Store Optimization (ASO) 专家级工具 — 审计、优化和扩展 App Store 元数据以最大化搜索可见性和下载转化率。
  Use this skill whenever the user mentions any of the following:
  - ASO, App Store Optimization, 应用商店优化
  - Review/audit app store metadata, keywords, title, subtitle
  - Optimize keywords, expand to new markets/languages
  - "review my ASO", "optimize keywords", "add new language to ASC"
  - "check my app store listing", "improve search ranking"
  - Multi-language/locale expansion strategy
  - Keyword analysis, keyword deduplication, keyword coverage
  Even if the user doesn't explicitly say "ASO", use this skill for any task involving optimizing App Store search visibility, keyword strategy, or multi-locale metadata expansion.
---

# ASO Pro Max — App Store Optimization Expert

## Overview

This skill turns Claude into a professional ASO (App Store Optimization) consultant. It covers the complete lifecycle: auditing existing metadata, optimizing Name/Subtitle/Keywords for maximum search coverage, expanding to new locales for market reach, and ensuring zero wasted character budget.

**Prerequisites**: The `appstore-connect` skill must be available for API calls. Ensure `ASC_ISSUER_ID`, `ASC_KEY_ID`, and `ASC_PRIVATE_KEY_PATH` are configured.

## Core ASO Principles

### 1. Apple's Search Index = Name + Subtitle + Keywords (Combined Pool)

Apple's algorithm indexes **all three fields together** as a unified pool. A word appearing in ANY of the three fields is indexed. Therefore:

> **NEVER repeat a word across Name, Subtitle, and Keywords. Every repetition wastes precious characters.**

### 2. Field Weight Hierarchy

| Field | Weight | Limit | Purpose |
|-------|--------|-------|---------|
| **Name** | Highest | 30 chars | Brand + #1 keyword |
| **Subtitle** | High | 30 chars | #2 keyword + value prop |
| **Keywords** | Medium | 100 chars | All remaining search terms |

### 3. Character Budget = Money

Every unused character is a missed search opportunity. Target:
- Name: Use 20-30 chars (include core keyword)
- Subtitle: Use 20-30 chars (different keywords from Name)
- Keywords: Use 95-100 chars (fill it up!)

### 4. Locale Multiplication Strategy

Each App Store locale gets its own independent 100-char keyword field. By adding locales (even without translating the app UI), you multiply your keyword coverage:

| Strategy | Keyword Capacity |
|----------|:----:|
| en-US only | 100 chars |
| + en-GB, en-AU, en-CA | 400 chars |
| + de, fr, es, it, etc. | 1,500+ chars |

**Key insight**: Users in these markets see localized metadata in search results. The app UI falls back to English — but they can FIND the app in their language.

## Workflow 1: Audit Existing ASO Metadata

### Step 1: Pull current state

```bash
ASC="node /path/to/asc-api.js"

# Get app info localizations (name, subtitle)
$ASC get-app-info-localizations <appInfoId>

# Get version localizations (keywords, description)
$ASC get-localizations <versionId>
```

### Step 2: Build audit table

For each locale, extract and display:

```
Locale   | Name (len/30) | Subtitle (len/30) | Keywords (len/100)
---------|---------------|-------------------|-------------------
en-US    | MyApp (5/30) | AI Photo Edit... (28) | photo,edit... (91)
```

### Step 3: Check for these issues

**Issue 1: Keyword field underutilized**
- Any locale with keywords < 90/100 chars is wasting search potential
- Target: 95-100 chars for every locale

**Issue 2: Cross-field duplication**
- Extract all words from Name + Subtitle
- Check if any of those words appear in Keywords
- Every duplicate = wasted keyword chars

**Issue 3: Name field too short**
- Name under 15 chars for a non-famous brand = wasted opportunity
- Pattern: `BrandName - Core Keyword` (e.g., "MyApp - AI Photo Editor")

**Issue 4: Subtitle duplicates Name**
- If Name and Subtitle share >50% of words, the subtitle is wasted
- Subtitle should introduce DIFFERENT keywords

### Step 4: Report format

Present findings as:

```markdown
## ASO Audit Report

### Problem Summary
| Issue | Affected Locales | Impact |
|-------|-----------------|--------|
| Keywords underutilized | ko(44/100), zh-Hant(46/100) | 56+ chars wasted per locale |
| Cross-field duplication | ja, ko, vi | 3-5 wasted keyword slots |
| Name too short | en-US(6/30), zh-Hans(3/30) | Missing high-weight keywords |

### Optimization Proposals
(Show before/after for each field with change rationale)
```

## Workflow 2: Optimize Name + Subtitle + Keywords

### Optimization Algorithm

For each locale:

1. **Name optimization**: If Name < 20 chars and brand is not globally famous:
   ```
   "{Brand} - {#1 Search Term in this language}"
   ```
   Example: `MyBrand - AI Photos` (7 → 20 chars)

2. **Subtitle optimization**: Remove any words already in the optimized Name. Replace with new high-value keywords:
   ```
   Before: "AI Photo Editor App" (repeats "AI Photo" from Name)
   After:  "One-tap portraits & filters" (all new words)
   ```

3. **Keyword optimization**:
   - List all words already indexed from Name + Subtitle
   - Remove ALL of them from Keywords
   - Fill freed space with new search terms
   - Prioritize: high-search-volume terms > niche terms > synonyms

### Keyword Selection Strategy by Language

**Latin-alphabet languages** (en, fr, es, de, it, pt, tr, vi):
- Apple splits keywords by commas AND may split by spaces
- Single words are more flexible: "bride" matches "bride", "bridal" needs separate entry
- Use singular form (Apple matches plural automatically)

**CJK languages** (zh, ja, ko):
- Chinese: Characters are dense, each char carries meaning. Pack more terms.
- Japanese: Mix of kanji + katakana. Include both forms of loan words.
- Korean: Compound words common. 웨딩사진 = 웨딩 + 사진, both indexed.

**Arabic/Thai**:
- Longer character sequences per word, budget runs out faster
- Focus on the most essential 12-15 terms

### Same-Language Locale Trick

For languages with multiple locales (en, fr, es), use DIFFERENT keywords per locale to maximize total coverage:

```
en-US keywords: marriage,bride,groom,bridal,engagement,face,swap,...     (100/100)
en-GB keywords: photograph,picture,ceremony,honeymoon,edit,filter,...    (100/100)
en-AU keywords: pic,image,proposal,enhance,blend,collage,gallery,...    (97/100)
en-CA keywords: portrait,editor,beauty,selfie,pose,celebration,...      (97/100)
                                                              Total: ~400 chars, 62 unique words
```

This gives 4x keyword coverage with zero additional effort.

Same for:
- `fr-FR` + `fr-CA`: Different keyword sets
- `es-ES` + `es-MX`: Different keyword sets

## Workflow 3: Expand to New Locales

### Market Prioritization Framework

Score each market on 3 axes:

| Factor | Weight | How to assess |
|--------|--------|---------------|
| **iOS purchasing power** | 40% | GDP per capita × iOS market share |
| **Product-market fit** | 35% | Does this culture have demand for your app's core feature? |
| **Competition density** | 25% | How many competing apps have this locale? |

### Tier List Example (Adjust per product)

| Tier | Markets | Rationale |
|------|---------|-----------|
| **Tier 1** | de-DE, fr-FR, es-ES, it, ar-SA | High spending + iOS dominant |
| **Tier 2** | th, pt-BR, tr | Strong culture fit + growing iOS |
| **Tier 3** | fr-CA, es-MX | Extra keyword pool (low effort) |
| **Skip** | id, ms, hi | Low iOS adoption + low spending at $5-10/mo price point |

### Per-Locale Creation Checklist

For each new locale, create:

1. **App Info Localization** (name + subtitle):
   ```bash
   $ASC create-app-info-localization <appInfoId> <locale> \
     --name="..." --subtitle="..."
   ```

2. **Version Localization** (description + keywords):
   ```bash
   # This is auto-created when app-info localization is created.
   # Find its ID:
   $ASC get-localizations <versionId>

   # Update with description + keywords via raw PATCH:
   $ASC raw PATCH /v1/appStoreVersionLocalizations/<locId> @body.json
   ```

3. **Screenshot Sets** (iPhone + iPad):
   ```bash
   # Create sets
   $ASC create-screenshot-set <locId> APP_IPHONE_65
   $ASC create-screenshot-set <locId> APP_IPAD_PRO_3GEN_129

   # Upload (can reuse English screenshots for non-primary markets)
   $ASC upload-screenshot <setId> /path/to/screenshot.png
   ```

### Description Template

Every locale's description should follow this structure:

```
{AppName} — {One-line value prop}

{2-sentence hook: what the app does + why it's effortless}

【Features/Fonctionnalités/Funktionen/...】
・Feature 1: {specific detail}
・Feature 2: {specific detail}
・...

【Who is it for?】
・Use case 1
・Use case 2
・...

【Subscription】
・Free: {free tier info}
・Manage/cancel: Settings → Apple ID → Subscriptions

{Localized "Terms of Service & Privacy Policy"}
- https://www.apple.com/legal/internet-services/itunes/dev/stdeula/
- {Your privacy policy URL}
```

**CRITICAL**: The Terms of Service & Privacy Policy section must appear at the end of EVERY locale's description. Missing it can cause App Review rejection.

## Workflow 4: Batch Operations

### Add 10+ locales efficiently

Use Python for batch operations instead of bash loops (avoids shell parsing issues with Unicode):

```python
import subprocess, json

ASC = ["node", "/path/to/asc-api.js"]
LOCALES = {
    "de-DE": {"name": "...", "subtitle": "...", "keywords": "...", "description": "..."},
    "fr-FR": {"name": "...", ...},
    # ...
}

# Step 1: Create app info localizations
for locale, meta in LOCALES.items():
    subprocess.run(ASC + [
        "create-app-info-localization", APP_INFO_ID, locale,
        f"--name={meta['name']}", f"--subtitle={meta['subtitle']}"
    ])

# Step 2: Find auto-created version localization IDs
result = subprocess.run(ASC + ["get-localizations", VERSION_ID], capture_output=True, text=True)
loc_ids = {
    loc["attributes"]["locale"]: loc["id"]
    for loc in json.loads(result.stdout)["data"]
}

# Step 3: Update descriptions + keywords via raw PATCH
for locale, meta in LOCALES.items():
    body = {
        "data": {
            "type": "appStoreVersionLocalizations",
            "id": loc_ids[locale],
            "attributes": {
                "description": meta["description"],
                "keywords": meta["keywords"],
                "supportUrl": "https://your-site.com"
            }
        }
    }
    json.dump(body, open(f"/tmp/{locale}.json", "w"), ensure_ascii=False)
    subprocess.run(ASC + ["raw", "PATCH",
        f"/v1/appStoreVersionLocalizations/{loc_ids[locale]}",
        f"@/tmp/{locale}.json"])

# Step 4: Create screenshot sets + upload
for locale, loc_id in loc_ids.items():
    for display_type in ["APP_IPHONE_65", "APP_IPAD_PRO_3GEN_129"]:
        r = subprocess.run(ASC + ["create-screenshot-set", loc_id, display_type],
                          capture_output=True, text=True)
        set_id = json.loads(r.stdout)["data"]["id"]
        for f in screenshot_files:
            subprocess.run(ASC + ["upload-screenshot", set_id, f])
```

## Workflow 5: Verification

### Post-optimization checklist

After all changes, run a full audit to verify:

```python
# Pull all locales and verify completeness
for locale in all_locales:
    assert len(name) <= 30
    assert len(subtitle) <= 30
    assert len(keywords) <= 100
    assert len(keywords) >= 90  # Should be nearly full
    assert len(description) > 500  # Meaningful description
    assert "privacy" in description.lower() or "隐私" in description  # ToS present
    assert screenshot_count >= 10  # iPhone + iPad
```

Display as a summary table:
```
Locale   │ Name(len) │ Sub(len) │ KW(len) │ Desc │ Screenshots
─────────┼───────────┼──────────┼─────────┼──────┼────────────
en-US    │ ✅ 26/30  │ ✅ 27/30 │ ✅100   │ 1401 │ ✅ 10
de-DE    │ ✅ 26/30  │ ✅ 27/30 │ ✅ 96   │ 1268 │ ✅ 10
...
```

## Common Mistakes to Avoid

1. **Repeating keywords across Name/Subtitle/Keywords** — #1 most common mistake. Apple indexes them together.

2. **Keywords field half-empty** — If you're at 44/100 chars, you're leaving half your search potential on the table.

3. **Same keywords in fr-FR and fr-CA** — You get two separate 100-char pools. Use different words in each!

4. **Adding low-spending locales** — Indonesia (id), India (hi) at $8/month subscription = almost zero conversion. Prioritize de-DE, ar-SA, fr-FR.

5. **Forgetting ToS/Privacy Policy in description** — Must appear in EVERY locale. App Review will flag this.

6. **Using spaces after commas in Keywords** — `bride, groom` wastes 1 char vs `bride,groom`. Multiply by 15 terms = 15 chars wasted.

7. **Not verifying after changes** — Always pull metadata back from ASC and verify. API calls can silently truncate or fail.

## Quick Reference: Apple Locale Codes

### High-value locales (prioritize these)
```
en-US, en-GB, en-AU, en-CA    — English (4 keyword pools!)
zh-Hans                         — Simplified Chinese (China)
zh-Hant                         — Traditional Chinese (Taiwan/HK)
ja                              — Japanese
ko                              — Korean
de-DE                           — German
fr-FR, fr-CA                   — French (2 pools)
es-ES, es-MX                  — Spanish (2 pools)
it                              — Italian
ar-SA                           — Arabic (Saudi/UAE/Gulf)
pt-BR                           — Portuguese (Brazil)
th                              — Thai
tr                              — Turkish
vi                              — Vietnamese
```

### Lower priority (evaluate per product)
```
id        — Indonesian (low iOS spending)
ms        — Malay (small market)
hi        — Hindi (low iOS adoption)
ru        — Russian
nl        — Dutch
sv        — Swedish
da        — Danish
no        — Norwegian
fi        — Finnish
pl        — Polish
uk        — Ukrainian
el        — Greek
he        — Hebrew
ro        — Romanian
hu        — Hungarian
cs        — Czech
sk        — Slovak
```

### NOT valid ASC locales (will error)
```
en-IN, en-SG, en-PH, en-ZA   — Apple doesn't support these English variants
```
