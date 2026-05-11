# aso-pro-max

**End-to-end App Store Optimization toolkit.** Audit, research, draft, and validate ASO metadata across 19+ locales using free public APIs — no AppTweak/Sensor Tower subscription required.

Built as a [Claude Code](https://claude.com/claude-code) skill, also usable as standalone Python scripts.

> 中文用户：本工具方法论与文档均为中文撰写，README 提供英文入口供国际用户参考。详细使用见 `SKILL.md` 与 `references/`。

## Why this exists

ASO tools cost €99-499/month. Independent developers can't justify that. This toolkit fills the gap with three insights:

1. **Mechanical detection is free** — character budgets, cross-field stem overlaps, CJK substring leaks, transliteration traps. The script `aso_audit.py` catches all of these automatically.
2. **Free competitive signals exist** — iTunes Search API (public, no key) returns top-5 competitors per keyword per storefront. Google Suggest reveals autocomplete demand. ASC Analytics shows your real traffic-driving search terms.
3. **The hidden trap is "category match ≠ function match"** — your `ghibli` keyword may land on ChatGPT's territory (AI stylization), but if your app does couple compositing, users searching `ghibli` will bounce. We codify this as Golden Rule #6.

## Features

- **Audit** — character budget, cross-field same-root detection (Snowball stemmer for EN/FR/DE/ES/IT/PT/AR + 16 other languages), CJK substring overlap detection, cross-locale duplication, transliteration trap lookup
- **Research** — iTunes Search API competitor analysis, Google Trends + Suggest signals
- **End-to-end 5-stage workflow** — industry refresh → app analysis → locale research → keyword drafting → validation + write
- **6 battle-tested golden rules** including the often-missed "category match ≠ function match"
- **Multi-locale aware** — handles same-language locale pools (en-US/GB/AU/CA, fr-FR/CA, es-ES/MX) with cross-locale stem checks

## Quick start

```bash
# 1. Clone (or symlink) into Claude Code skills dir
git clone <repo> ~/.claude/skills/aso-pro-max

# 2. Install Python deps (requires Python ≥ 3.10)
pip install -r ~/.claude/skills/aso-pro-max/requirements.txt

# 3. Install asc CLI (for ASC API access)
brew install rudrankriyam/tap/asc
asc auth init

# 4. (Optional) Set up ASA OAuth for future Apple Ads Platform API
mkdir -p ~/.config/aso-pro-max/.secrets
cp ~/.claude/skills/aso-pro-max/.env.example ~/.config/aso-pro-max/.env
# Edit ~/.config/aso-pro-max/.env with your ASA credentials
# Generate private key:
openssl ecparam -genkey -name prime256v1 -noout -out ~/.config/aso-pro-max/.secrets/asa_private_key.pem
openssl ec -in ~/.config/aso-pro-max/.secrets/asa_private_key.pem -pubout
```

## Usage as standalone scripts

```bash
# Audit your current ASC metadata
python scripts/aso_audit.py --app-id <YOUR_APP_ID> --version-id <VID>

# Or use a snapshot JSON (offline mode)
python scripts/aso_audit.py --from-file examples/sample_snapshot.json

# Validate keyword candidates against iTunes Search
python scripts/itunes_search_check.py --country jp \
  --keywords "wedding photo,couple portraits,ai bride"

# Cross-platform demand signals (Google Trends + Suggest)
python scripts/google_signals.py --geo JP --hl ja-JP \
  --keywords "wedding photo,couple portraits"
```

## Usage as Claude Code skill

Once installed at `~/.claude/skills/aso-pro-max/`, just ask Claude:

> "Audit my app's ASO" / "Optimize en-US keywords" / "Extend to ja locale"

The skill auto-triggers on ASO-related prompts. See `SKILL.md` for the full workflow.

## Project data layout convention

**This skill stores no project-specific data.** Each project using the skill keeps its own `.aso/` directory at its repo root:

```
{your_project}/.aso/
├── context.md              # Stage 2 output (App functions/boundaries)
├── locale/{LL}.md          # Stage 3 output (per-locale market research)
├── drafts/{date}.json      # Stage 4 output (keyword draft candidates)
└── reports/audit_{date}.md # Stage 5 audit run archives
```

This keeps the skill portable across projects without data pollution.

## 5-Stage end-to-end workflow

```
Stage 1: Industry knowledge refresh (quarterly, parallel agents)
   ↓
Stage 2: App feature analysis (one-time per app, Explore agent scans codebase)
   ↓
Stage 3: Multi-locale market research (parallel agents per cluster)
   ↓
Stage 4: Keyword drafting (based on Stage 2+3 outputs)
   ↓
Stage 5: 3-layer validation + write (mechanical + competitive + functional)
```

See `references/stage{1..5}_*.md` for each stage's detailed workflow.

## Golden rules

1. **Name + Subtitle + Keywords share one index pool** — never repeat any word (or root) across fields
2. **Character budget = money** — fill it: Name ≥15, Subtitle ≥20, Keywords 95-100
3. **Same-language locales have independent 100-char pools** — en-US/GB/AU/CA must use different words
4. **Transliteration traps** — `vintage` / `retro` / `romantic` have near-zero search volume in non-English locales
5. **Screenshot captions are indexed (Apple 2025+)** — caption text becomes search-discoverable keywords
6. **Category match ≠ function match** — a keyword can land on competitors in your category but in a completely different feature space. Ask: "would users searching this be disappointed by my app?" If yes, skip the keyword.

## Known limitations

- **No popularity data** — Apple Search Ads API (v5) doesn't expose keyword popularity. See `references/asa_api_limitations.md` for the full investigation. AppTweak/Sensor Tower paid APIs are the alternative; we recommend manual ASA backend UI lookup as a free fallback.
- **Google Trends rate-limited** — `pytrends` is unofficial; expect 429s. Google Suggest endpoint is stable and used as the primary cross-platform signal instead.
- **CJK substring detection is heuristic** — Apple's CJK index tokenization is a black box; the script flags potential overlaps as WARN, requires human judgment.

## Contributing

Issues and PRs welcome. The toolkit was developed against a real iOS app (couple photo compositor) with 19 locales; some assumptions reflect that — if your app type breaks an assumption (e.g., a single-portrait app on which `headshot` is genuinely on-function), please open an issue and we'll generalize.

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgments

- [`rudrankriyam/tap/asc`](https://github.com/rudrankriyam/asc) — App Store Connect CLI
- [`phiture/searchads_api`](https://github.com/phiture/searchads_api) — ASA v5 endpoint inventory reference
- Apple Developer Forum [thread/820073](https://developer.apple.com/forums/thread/820073) — ASA custom-reports GET 403 incident reference
