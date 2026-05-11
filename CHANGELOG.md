# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

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
