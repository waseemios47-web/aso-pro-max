# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-05-11 — Real end-to-end clean run (afternoon)

### Added
- **Stage 6: Write plan + execute + verify** (`references/stage6_write_execute.md`)
  - Independent agent parses Stage 5 HTML → generates writeplan JSON
  - Main Claude only executes mechanically
  - Mandatory `aso_audit.py` re-run after writes (with ERROR-fix loop)
- **Golden Rule #7** "Real end-to-end requires real decontamination":
  - Archive `Marketing/ASO_*.md` before Stage 2
  - Temporarily `.bak` `memory/aso-strategy*.md`
  - Main Claude must NOT participate in Stage 2-6 decisions (use independent agents)
- **HTML output format** for Stages 2/3/4/5 (replaces markdown)
  - Browser-readable, structured with `<style>` blocks
  - Standard classes: `.verified` (iTunes実測通过), `.untested` (limited), `.danger` (错位)
- **Brand name per locale** field in `project_context_template.md`
  - Prevents Stage 4 from accidentally overwriting localized brand names (e.g. zh-Hans `微出片` not `WePics`)
- **Common Mistakes #12-14** documenting newly learned anti-patterns:
  - Not real-cleaning pollution
  - LLM inventing geo flavor words (boho/winter/maple — all iTunes-misaligned)
  - Cross-field conflict checks when merging draft ∪ live state

### Changed
- SKILL.md restructured to 6-stage flow (was 5)
- Stage 2 prompt now explicitly forbids reading `Marketing/ASO_*.md` and `.aso/*`
- Stage 3 emphasizes "honestly label untested" when iTunes 403/429
- Stage 5 explicitly recommends "draft ∪ live (union merge)" over wholesale replacement
- iTunes API rate-limit guidance: don't extrapolate or invent geo words; honestly mark `untested`

### Battle-tested against
- WePics 19-locale end-to-end clean run (2026-05-11 afternoon):
  - Stage 2: zero Marketing pollution verified
  - Stage 3: 4 parallel cluster agents → 19 locale HTMLs (iTunes 403s honestly marked)
  - Stage 4: 129KB HTML with EN/FR/ES/ZH 4-pool stem coordination
  - Stage 5: 805-line HTML decision report including "real-clean vs half-clean" diff
  - Stage 6: 17 locale writes + 2 zh-Hans/Hant follow-up = **0 ERROR on first audit**

## [0.1.0] - 2026-05-11

### Added — initial public release
- **5-stage end-to-end ASO workflow**:
  - Stage 1: Industry knowledge refresh (parallel agents, quarterly)
  - Stage 2: App feature analysis (Explore agent scans codebase)
  - Stage 3: Multi-locale market research (parallel agents per cluster)
  - Stage 4: Keyword drafting (based on Stage 2+3)
  - Stage 5: 3-layer validation (mechanical + competitive + functional)
- **Core script `aso_audit.py`** with 5 detector classes:
  - Character budget (Apple codepoint rules, CJK exemptions)
  - Cross-field same-root detection (NLTK Snowball stemmer, 16 languages)
  - CJK substring overlap detection (Apple CJK index heuristic)
  - Cross-same-language-locale duplication
  - Transliteration trap detection (per-locale built-in dictionary)
- **`itunes_search_check.py`** — public iTunes Search API competitor analysis
- **`google_signals.py`** — Google Trends + Suggest cross-platform signals (with rate-limit fallback)
- **`asa_auth.py`** — ASA OAuth ES256 JWT module (parked for future Apple Ads Platform API)
- **6 Golden Rules**, notably #6 "Category match ≠ Function match" derived from real-world miss
- **Project-data isolation**: skill stores zero project-specific data; each project keeps its own `.aso/` directory
- **Sample fixture** at `examples/sample_snapshot.json` for offline `--from-file` runs
- **Unit tests** at `tests/test_aso_audit.py` (22 tests covering all detectors)

### Known Limitations
- Apple Search Ads API v5 does not expose keyword popularity. See `references/asa_api_limitations.md` for full investigation.
- Google Trends (pytrends) frequently rate-limited; Google Suggest is the primary cross-platform signal.
- CJK substring detection is a heuristic; Apple's CJK tokenization is undocumented.

### Battle-tested against
- WePics (couple-photo compositor, iOS, 19 locales) — Stage 5 ran on 4 EN + 1 JA locale in 2026-05.
