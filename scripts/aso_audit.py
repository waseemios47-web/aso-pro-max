#!/usr/bin/env python3
"""
ASO Audit — 一键审计 App Store Connect 元数据

功能：
  1. 拉取所有 locale 的 Name / Subtitle / Keywords（asc CLI 或本地 JSON）
  2. 字符预算计算（Apple 按 Unicode codepoint 数限制，CJK 1 字 = 1 codepoint）
  3. 跨字段同根词冲突（Name+Subtitle 与 Keywords 重复）
  4. 跨同语言 locale 词汇重复（en-US / en-GB / en-AU / en-CA 等）
  5. 输出 JSON 报告 + Markdown 摘要

用法：
  # 从 ASC API 拉
  python3 aso_audit.py --app-id <APP_ID> --version-id <VERSION_ID>

  # 从本地 JSON 跑（脱机审计或单元测试）
  python3 aso_audit.py --from-file metadata.json

  # 输出 markdown 报告
  python3 aso_audit.py --app-id <APP_ID> --version-id <VERSION_ID> --format markdown

本地 JSON 格式：
  {
    "app_info": {
      "en-US": {"name": "...", "subtitle": "..."},
      ...
    },
    "version": {
      "en-US": {"keywords": "a,b,c", "description": "..."},
      ...
    }
  }
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

LIMITS = {"name": 30, "subtitle": 30, "keywords": 100}

# locale → ASA storefront country code（用于 popularity 查询）
LOCALE_TO_STOREFRONT = {
    "en-US": "US", "en-GB": "GB", "en-AU": "AU", "en-CA": "CA",
    "ja": "JP", "ko": "KR",
    "zh-Hans": "CN", "zh-Hant": "TW",
    "ar-SA": "SA",
    "fr-FR": "FR", "fr-CA": "CA",
    "es-ES": "ES", "es-MX": "MX",
    "de-DE": "DE", "it": "IT",
    "tr": "TR", "pt-BR": "BR",
    "th": "TH", "vi": "VN",
}

# 同语言 locale 分组（用于跨 locale 去重）
SAME_LANGUAGE_GROUPS = {
    "en": ["en-US", "en-GB", "en-AU", "en-CA"],
    "fr": ["fr-FR", "fr-CA"],
    "es": ["es-ES", "es-MX"],
    "zh": ["zh-Hans", "zh-Hant"],
    "pt": ["pt-BR", "pt-PT"],
}

# 已知音译陷阱词（按 locale 标记应避免）
TRANSLITERATION_TRAPS = {
    "ja": ["レトロ", "ヴィンテージ", "ロマンティック"],
    "ko": ["빈티지", "레트로", "로맨틱", "브라이덜", "리터칭", "부케"],
    "ar-SA": ["رومانسي", "كلاسيك", "فنتج", "ريترو"],
    "th": ["วินเทจ", "เรโทร", "โรแมนติก"],
    "tr": ["vintage", "retro"],
    "es-ES": ["vintage", "retro"],
    "es-MX": ["vintage", "retro"],
    "fr-FR": ["vintage", "retro"],
    "fr-CA": ["vintage", "rétro"],
    "de-DE": ["vintage", "retro"],
    "it": ["vintage", "retro"],
    "pt-BR": ["vintage", "retro"],
    "vi": ["vintage", "retro"],
}


@dataclass
class LocaleMeta:
    locale: str
    name: str = ""
    subtitle: str = ""
    keywords: str = ""

    def kw_list(self) -> list[str]:
        return [k.strip() for k in self.keywords.split(",") if k.strip()]


@dataclass
class Finding:
    severity: str  # "error" | "warn" | "info"
    locale: str
    field: str
    msg: str


# ──────────────────────────────────────────────────────────────────────
# 数据加载
# ──────────────────────────────────────────────────────────────────────


def load_from_asc(app_id: str, version_id: str | None) -> dict[str, LocaleMeta]:
    metas: dict[str, LocaleMeta] = {}

    # app-info: name + subtitle
    cmd = ["asc", "localizations", "list", "--app", app_id, "--type", "app-info",
           "--output", "json", "--paginate"]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    for item in json.loads(res.stdout).get("data", []):
        attr = item.get("attributes", {})
        loc = attr.get("locale")
        if not loc:
            continue
        metas.setdefault(loc, LocaleMeta(locale=loc))
        metas[loc].name = attr.get("name") or ""
        metas[loc].subtitle = attr.get("subtitle") or ""

    # version: keywords
    if version_id:
        cmd = ["asc", "localizations", "list", "--version", version_id,
               "--output", "json", "--paginate"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        for item in json.loads(res.stdout).get("data", []):
            attr = item.get("attributes", {})
            loc = attr.get("locale")
            if not loc:
                continue
            metas.setdefault(loc, LocaleMeta(locale=loc))
            metas[loc].keywords = attr.get("keywords") or ""

    return metas


def load_from_file(path: str) -> dict[str, LocaleMeta]:
    with open(path) as f:
        data = json.load(f)
    metas: dict[str, LocaleMeta] = {}
    for loc, v in (data.get("app_info") or {}).items():
        metas.setdefault(loc, LocaleMeta(locale=loc))
        metas[loc].name = v.get("name", "")
        metas[loc].subtitle = v.get("subtitle", "")
    for loc, v in (data.get("version") or {}).items():
        metas.setdefault(loc, LocaleMeta(locale=loc))
        metas[loc].keywords = v.get("keywords", "")
    return metas


# ──────────────────────────────────────────────────────────────────────
# 词汇分析
# ──────────────────────────────────────────────────────────────────────


def char_count(s: str) -> int:
    """Apple 按 Unicode codepoint 数限制。"""
    return len(s)


_WORD_RE = re.compile(r"[\wÀ-ɏ֐-׿؀-ۿ぀-ヿ"
                      r"㐀-䶿一-鿿가-힯]+", re.UNICODE)


def tokenize(text: str, locale: str) -> list[str]:
    """按空格/标点切词。CJK + 泰语 + 阿拉伯按标点切（无空格分词器，整段当一个 token）。"""
    if locale.startswith(("zh", "ja", "ko", "th", "ar")):
        # 按各种分隔符（含 ASCII 空格和连字符）切，避免 name 整段当一个超长 token
        return [t.strip().lower()
                for t in re.split(r"[,，、\s\-—–·•\|\&]+", text)
                if t.strip()]
    return [w.lower() for w in _WORD_RE.findall(text)]


# Snowball stemmer 缓存（按 locale 语言初始化）
try:
    from nltk.stem.snowball import SnowballStemmer
    _SNOWBALL_AVAILABLE = True
except ImportError:
    _SNOWBALL_AVAILABLE = False

_LOCALE_TO_SNOWBALL = {
    "en": "english", "fr": "french", "de": "german", "es": "spanish",
    "it": "italian", "pt": "portuguese", "ar": "arabic",
    "nl": "dutch", "da": "danish", "sv": "swedish", "no": "norwegian",
    "fi": "finnish", "hu": "hungarian", "ro": "romanian", "ru": "russian",
}
_STEMMER_CACHE: dict[str, object] = {}


def _get_stemmer(locale: str):
    if not _SNOWBALL_AVAILABLE:
        return None
    lang_prefix = locale.split("-")[0].lower()
    snowball_name = _LOCALE_TO_SNOWBALL.get(lang_prefix)
    if not snowball_name:
        return None
    if snowball_name not in _STEMMER_CACHE:
        _STEMMER_CACHE[snowball_name] = SnowballStemmer(snowball_name)
    return _STEMMER_CACHE[snowball_name]


def stem(word: str, locale: str) -> str:
    """词干提取，捕捉 bride/bridal、photo/photograph、wed/wedding 等同根词。"""
    # CJK + 泰语：无形态变化，整词比对
    if locale.startswith(("zh", "ja", "ko", "th")):
        return word
    # 优先 Snowball（处理 EN/FR/DE/ES/IT/PT/AR/NL/DA/SV/NO/FI/HU/RO/RU 形态变化）
    stemmer = _get_stemmer(locale)
    if stemmer is not None:
        return stemmer.stem(word)
    # Fallback：5 字符截断（pip install nltk 失败时用）
    if len(word) <= 5:
        return word
    return word[:5]


# ──────────────────────────────────────────────────────────────────────
# 检测器
# ──────────────────────────────────────────────────────────────────────


def check_budget(meta: LocaleMeta) -> list[Finding]:
    out = []
    is_cjk = meta.locale.startswith(("zh", "ja", "ko"))
    for fld, limit in LIMITS.items():
        val = getattr(meta, fld)
        n = char_count(val)
        if n > limit:
            out.append(Finding("error", meta.locale, fld,
                               f"超限 {n}/{limit}：{val!r}"))
        elif n < limit * 0.85 and fld == "keywords":
            wasted = limit - n
            out.append(Finding("warn", meta.locale, fld,
                               f"未充分利用 {n}/{limit}（浪费 {wasted} 字符）"))
        elif fld == "name" and n < 15 and not is_cjk:
            # Name <15 是浪费机会，但 CJK 短 name（如 3-4 字符）密度高可豁免
            out.append(Finding("warn", meta.locale, fld,
                               f"过短 {n}/{limit}：{val!r}（非全球品牌建议 BrandName - Keyword 模式）"))
        elif fld == "subtitle" and n < 20 and not is_cjk:
            # Subtitle 推荐 ≥20，<20 浪费机会（与黄金原则 #2 对齐）
            out.append(Finding("warn", meta.locale, fld,
                               f"未充分利用 {n}/{limit}（浪费 {limit-n} 字符）"))
    return out


def check_cross_field_dup(meta: LocaleMeta) -> list[Finding]:
    """Name+Subtitle 与 Keywords 之间的同根词重复 = 浪费字符。

    CJK 语言额外做子串检测：keyword 是否包含或被包含于 name/subtitle 中的某 token。
    例如 ja keyword `フォトウェディング` 是 name `AIフォトウェディング前撮り` 的子串
    （Apple 的 CJK 索引算法可能把它视为重复）。
    """
    name_sub_words = tokenize(meta.name + " " + meta.subtitle, meta.locale)
    name_sub_stems = {stem(w, meta.locale) for w in name_sub_words}
    kw_tokens = tokenize(meta.keywords, meta.locale)

    out = []
    # Layer 1: stem 比对（所有 locale）
    dups = []
    for kw in kw_tokens:
        s = stem(kw, meta.locale)
        if s in name_sub_stems:
            dups.append(kw)
    if dups:
        out.append(Finding("error", meta.locale, "keywords",
                           f"与 Name/Subtitle 同根重复（浪费）：{dups}"))

    # Layer 2: CJK 子串检测（zh/ja/ko；阿拉伯/泰语 token 一般不会有子串重叠）
    if meta.locale.startswith(("zh", "ja", "ko")):
        # name+subtitle 的"长 token"（≥3 字符，避免误报短助词）
        ns_long_tokens = [w for w in name_sub_words if len(w) >= 3]
        substring_hits = []
        for kw in kw_tokens:
            if len(kw) < 2:
                continue
            for ns_tok in ns_long_tokens:
                if kw == ns_tok:
                    continue  # stem 检查已覆盖整词重复
                # keyword 是 name/subtitle token 的子串
                if kw in ns_tok or ns_tok in kw:
                    substring_hits.append(f"{kw}↔{ns_tok}")
                    break
        if substring_hits:
            out.append(Finding("warn", meta.locale, "keywords",
                               f"CJK 子串可能与 Name/Subtitle 重叠（Apple 索引行为黑盒，"
                               f"建议人工核查）：{substring_hits}"))

    return out


def check_translit_traps(meta: LocaleMeta) -> list[Finding]:
    traps = TRANSLITERATION_TRAPS.get(meta.locale, [])
    if not traps:
        return []
    text_lower = meta.keywords.lower()
    hits = [t for t in traps if t.lower() in text_lower]
    if hits:
        return [Finding("warn", meta.locale, "keywords",
                        f"音译陷阱词（建议替换为本地原生词）：{hits}")]
    return []


def check_same_language_dup(metas: dict[str, LocaleMeta]) -> list[Finding]:
    """同语言多 locale 之间的 keyword 重复 = 浪费第二个 100 char 池。"""
    out = []
    for lang, locales in SAME_LANGUAGE_GROUPS.items():
        present = [l for l in locales if l in metas]
        if len(present) < 2:
            continue
        # 收集每个 locale 的词干集合
        stem_sets = {l: {stem(w, l) for w in tokenize(metas[l].keywords, l)}
                     for l in present}
        # 两两比对
        for i, a in enumerate(present):
            for b in present[i + 1:]:
                inter = stem_sets[a] & stem_sets[b]
                if inter:
                    out.append(Finding("warn", a, "keywords",
                                       f"与 {b} 同根词重复（浪费跨 locale 池）：{sorted(inter)}"))
    return out


def check_keywords_format(meta: LocaleMeta) -> list[Finding]:
    """逗号后空格 = 浪费字符。"""
    if ", " in meta.keywords:
        n = meta.keywords.count(", ")
        return [Finding("warn", meta.locale, "keywords",
                        f"逗号后含空格 ×{n}（浪费 {n} 字符，应改为无空格）")]
    return []


# ──────────────────────────────────────────────────────────────────────
# 报告输出
# ──────────────────────────────────────────────────────────────────────


def run_all_checks(metas: dict[str, LocaleMeta]) -> list[Finding]:
    findings = []
    for meta in metas.values():
        findings += check_budget(meta)
        findings += check_cross_field_dup(meta)
        findings += check_translit_traps(meta)
        findings += check_keywords_format(meta)
    findings += check_same_language_dup(metas)
    return findings


# ──────────────────────────────────────────────────────────────────────
# Popularity 集成位（已停用）
# ──────────────────────────────────────────────────────────────────────
# 2026-05 调研结论：ASA API 在 v5 版本不公开 keyword popularity 端点，
# 此能力仅在 ASA 后台 UI 或 custom-reports 的 impression_share_report 中
# 暴露，而后者要求 campaign 真实投放过且 GET 端点自 2026-03-16 起 403。
# 详见 references/asa_api_limitations.md。
#
# 留 LOCALE_TO_STOREFRONT 表，未来接 AppTweak / Sensor Tower 等付费工具
# 或 Apple Ads Platform API（2026 夏推出）时可直接复用。


def format_table(metas: dict[str, LocaleMeta]) -> str:
    rows = ["| Locale | Name (n/30) | Subtitle (n/30) | Keywords (n/100) |",
            "|--------|-------------|-----------------|------------------|"]
    for loc in sorted(metas.keys()):
        m = metas[loc]
        rows.append(f"| {loc} | {char_count(m.name)}/30 | "
                    f"{char_count(m.subtitle)}/30 | "
                    f"{char_count(m.keywords)}/100 |")
    return "\n".join(rows)


def format_findings(findings: list[Finding], fmt: str = "markdown") -> str:
    if fmt == "json":
        return json.dumps([f.__dict__ for f in findings], ensure_ascii=False, indent=2)

    if not findings:
        return "✅ 无问题"

    by_sev = {"error": [], "warn": [], "info": []}
    for f in findings:
        by_sev[f.severity].append(f)

    lines = []
    for sev, label in [("error", "🔴 ERROR"), ("warn", "🟡 WARN"), ("info", "🔵 INFO")]:
        if not by_sev[sev]:
            continue
        lines.append(f"\n## {label} ({len(by_sev[sev])})")
        for f in by_sev[sev]:
            lines.append(f"- **{f.locale}** / `{f.field}` — {f.msg}")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────


def main():
    ap = argparse.ArgumentParser(description="ASO Audit")
    ap.add_argument("--app-id", help="ASC App ID (for app-info pull)")
    ap.add_argument("--version-id", help="ASC Version ID (for keywords pull)")
    ap.add_argument("--from-file", help="本地 JSON 快照（脱机审计用）")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    ap.add_argument("--out", help="输出文件路径（默认 stdout）")
    args = ap.parse_args()

    if args.from_file:
        metas = load_from_file(args.from_file)
    elif args.app_id:
        metas = load_from_asc(args.app_id, args.version_id)
    else:
        ap.error("必须指定 --from-file 或 --app-id")

    findings = run_all_checks(metas)
    popularity_scores = None  # 暂未接入数据源，见 references/asa_api_limitations.md

    if args.format == "json":
        report = json.dumps({
            "metas": {l: m.__dict__ for l, m in metas.items()},
            "findings": [f.__dict__ for f in findings],
            "popularity": popularity_scores,
        }, ensure_ascii=False, indent=2)
    else:
        report = "# ASO Audit Report\n\n## 字符预算\n\n"
        report += format_table(metas)
        report += "\n\n# Findings\n"
        report += format_findings(findings, "markdown")
        if popularity_scores:
            report += "\n\n## ASA Popularity 摘要\n"
            for loc in sorted(popularity_scores.keys()):
                kws = popularity_scores[loc]
                if not kws:
                    continue
                top = sorted(kws.items(), key=lambda x: -(x[1] or 0))[:5]
                report += f"\n**{loc}** Top 5: " + ", ".join(
                    f"`{k}`({p})" for k, p in top) + "\n"

    if args.out:
        with open(args.out, "w") as f:
            f.write(report)
        print(f"已写入 {args.out}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
