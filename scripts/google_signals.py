"""
Google Trends + Google Suggest — 候选关键词的跨平台信号

完全免费、无需 API key。
两类信号合并：
  1. Google Trends（pytrends 库）：候选词的相对搜索热度（0-100 标准化分）
  2. Google Suggest：autocomplete 是否补全（命中=高频）

⚠️ 实测注意（2026-05）：
  - **Google Trends（pytrends）大概率被 429 限流**——Google 已识别 pytrends UA
    实战跑 ja 时 Trends 全失败，仅 Suggest 工作。
    如果你需要 Trends 数据，建议手动登录 trends.google.com 看（UI 不限流）。
  - Google Suggest 端点稳定，10 个候选词补全数量是判断词热度的可靠信号。
  - Google 数据 ≠ App Store 数据，但同语言市场两者通常正相关。
  - 日本市场用 geo='JP'，hl='ja-JP'

用法：
  python3 google_signals.py --geo JP --hl ja-JP \
    --keywords "結婚,入籍,婚活,着物,大人婚"

  python3 google_signals.py --geo JP \
    --keywords "結婚,入籍,婚活,着物,大人婚" --baseline "iPhone"
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from urllib.parse import quote

import requests

# Google Suggest 端点（公开、无 key）
SUGGEST_URL = "https://suggestqueries.google.com/complete/search"


def google_suggest(query: str, hl: str = "ja", gl: str = "jp") -> list[str]:
    """查 Google Suggest 的 autocomplete。"""
    params = f"?client=firefox&q={quote(query)}&hl={hl}&gl={gl}"
    try:
        r = requests.get(SUGGEST_URL + params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return data[1] if len(data) > 1 else []
    except Exception as e:
        return [f"(error: {e})"]


def google_trends(keywords: list[str], geo: str = "JP",
                  timeframe: str = "today 12-m") -> dict:
    """用 pytrends 查相对搜索热度。每次最多 5 词同框对比。"""
    from pytrends.request import TrendReq

    out = {}
    pytrends = TrendReq(hl="ja-JP", tz=540)  # 540 = Japan UTC+9

    # pytrends 单次最多 5 词。分批
    for i in range(0, len(keywords), 5):
        batch = keywords[i:i + 5]
        try:
            pytrends.build_payload(batch, geo=geo, timeframe=timeframe)
            df = pytrends.interest_over_time()
            if df.empty:
                for kw in batch:
                    out[kw] = {"avg_trend": None, "max_trend": None,
                               "note": "Trends 无数据（搜索量过低）"}
                continue
            for kw in batch:
                if kw not in df.columns:
                    out[kw] = {"avg_trend": None, "max_trend": None,
                               "note": "未在 Trends 响应中"}
                    continue
                col = df[kw]
                out[kw] = {
                    "avg_trend": round(float(col.mean()), 1),
                    "max_trend": int(col.max()),
                    "note": "相对热度 0-100，仅限本批次内对比",
                }
        except Exception as e:
            for kw in batch:
                out[kw] = {"avg_trend": None, "error": str(e)[:200]}
        time.sleep(2)  # 防 429
    return out


def analyze(keywords: list[str], geo: str, hl: str) -> list[dict]:
    # Trends 大概率失败（pytrends 限流或未装），失败时仅退化 Suggest
    print(f"🔍 查 Google Trends ({geo}/{hl})...", file=sys.stderr)
    try:
        trends = google_trends(keywords, geo=geo)
    except ImportError:
        print(f"⚠️  pytrends 未安装，跳过 Trends（仅用 Suggest）", file=sys.stderr)
        trends = {kw: {"avg_trend": None, "note": "pytrends 未安装"} for kw in keywords}
    except Exception as e:
        print(f"⚠️  Trends 整体失败（{e}），跳过，仅用 Suggest", file=sys.stderr)
        trends = {kw: {"avg_trend": None, "note": f"Trends 失败: {str(e)[:80]}"} for kw in keywords}

    rows = []
    for kw in keywords:
        print(f"🔍 查 Suggest: {kw}", file=sys.stderr)
        suggestions = google_suggest(kw, hl=hl.split("-")[0], gl=geo.lower())
        rows.append({
            "keyword": kw,
            "trends": trends.get(kw, {}),
            "suggest_top5": suggestions[:5],
            "suggest_count": len(suggestions),
        })
        time.sleep(0.5)
    return rows


def format_markdown(rows: list[dict]) -> str:
    out = ["# Google Signals — Trends + Suggest 报告\n",
           "## Trends 相对热度（同批次内 0-100 标准化）\n",
           "| Keyword | Avg Trend | Max Trend | 备注 |",
           "|---|---|---|---|"]
    for r in rows:
        t = r["trends"]
        avg = t.get("avg_trend") if t.get("avg_trend") is not None else "—"
        mx = t.get("max_trend") if t.get("max_trend") is not None else "—"
        note = t.get("note") or t.get("error") or ""
        out.append(f"| `{r['keyword']}` | {avg} | {mx} | {note[:60]} |")

    out.append("\n## Google Suggest 命中（autocomplete 越多越说明该词在 Google 上是真高频）\n")
    for r in rows:
        out.append(f"### `{r['keyword']}` (suggest 总数: {r['suggest_count']})")
        if r["suggest_top5"]:
            for s in r["suggest_top5"]:
                out.append(f"- {s}")
        else:
            out.append("- (无 autocomplete → 极低频或 Google 不认)")
        out.append("")

    out.append("\n## 解读建议\n")
    out.append("- **Avg Trend 高（30+）+ Suggest 多（5+）**：跨平台真高频，闭眼放进 keywords")
    out.append("- **Avg Trend 低（<10）+ Suggest 少（<3）**：低频或纯 App Store 现象，可能要砍")
    out.append("- **Trends 高 + Suggest 少**：可能是 Google 信号噪音（如新闻热点）")
    out.append("- **Trends 低 + Suggest 多**：可能是日常生活词（不一定通过 Google 搜）")
    out.append("- 与 ASC Analytics + iTunes Search API 数据交叉验证")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geo", default="JP", help="Google Trends 地区码：JP/US/KR/...")
    ap.add_argument("--hl", default="ja-JP", help="语言：ja-JP/en-US/...")
    ap.add_argument("--keywords", required=True)
    ap.add_argument("--out")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = ap.parse_args()

    kws = [k.strip() for k in args.keywords.split(",") if k.strip()]
    rows = analyze(kws, args.geo, args.hl)

    if args.format == "json":
        text = json.dumps(rows, ensure_ascii=False, indent=2)
    else:
        text = format_markdown(rows)

    if args.out:
        open(args.out, "w").write(text)
        print(f"已写入 {args.out}", file=sys.stderr)
    else:
        print(text)


if __name__ == "__main__":
    main()
