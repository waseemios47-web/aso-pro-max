"""
iTunes Search API — 候选关键词的 App Store 竞争度检测

公开免费、无需鉴权。
对每个候选词查 App Store {country} 区返回的应用列表，输出：
  - 命中数（少 = 蓝海，多 = 红海）
  - Top N 应用名 / bundle / rating（看主要竞品）
  - 平均评分 / 总评分数（高 = 该品类已被认知）

用法：
  python3 itunes_search_check.py --country jp \
    --keywords "結婚,入籍,婚活,着物,大人婚,変身,フォト婚,ナシ婚"

  python3 itunes_search_check.py --country jp \
    --keywords-file ja_candidates.txt --out /tmp/ja_competition.md
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from urllib.parse import urlencode

import requests

API = "https://itunes.apple.com/search"


def search(term: str, country: str, limit: int = 20) -> dict:
    params = {"term": term, "country": country, "media": "software",
              "entity": "software", "limit": limit}
    r = requests.get(f"{API}?{urlencode(params)}", timeout=20)
    r.raise_for_status()
    return r.json()


def analyze(term: str, country: str) -> dict:
    data = search(term, country)
    results = data.get("results", [])
    n = len(results)
    out = {
        "keyword": term,
        "country": country,
        "result_count": n,
        "top_apps": [],
    }
    if not results:
        return out

    ratings = [r.get("averageUserRatingForCurrentVersion") or r.get("averageUserRating") or 0
               for r in results]
    rating_counts = [r.get("userRatingCountForCurrentVersion") or r.get("userRatingCount") or 0
                     for r in results]

    out["avg_rating"] = round(sum(ratings) / max(len(ratings), 1), 2)
    out["total_ratings"] = sum(rating_counts)

    for r in results[:5]:
        out["top_apps"].append({
            "name": r.get("trackName"),
            "bundleId": r.get("bundleId"),
            "rating": r.get("averageUserRating"),
            "rating_count": r.get("userRatingCount"),
        })
    return out


def format_markdown(rows: list[dict]) -> str:
    out = ["# iTunes Search API — 竞争度报告\n",
           "| Keyword | 命中数 | 平均评分 | 总评分数 | Top 1 竞品 | Top 2 |",
           "|---|---|---|---|---|---|"]
    for r in rows:
        top = r.get("top_apps", [])
        t1 = (top[0]["name"][:25] + "…") if len(top) > 0 and top[0].get("name") and len(top[0]["name"]) > 25 else (top[0].get("name") if top else "")
        t2 = (top[1]["name"][:25] + "…") if len(top) > 1 and top[1].get("name") and len(top[1]["name"]) > 25 else (top[1].get("name", "") if len(top) > 1 else "")
        out.append(f"| `{r['keyword']}` | {r['result_count']} | "
                   f"{r.get('avg_rating', '-')} | {r.get('total_ratings', '-')} | "
                   f"{t1} | {t2} |")

    out.append("\n## 解读建议")
    out.append("- **命中数 0-3**：超蓝海，可能是低搜索量也可能是真空白。配合其他信号判断")
    out.append("- **命中数 4-10**：竞争适中，值得放进 keywords 池")
    out.append("- **命中数 15-20**：红海，已饱和。除非词本身搜索量极大，否则不值得抢")
    out.append("- **总评分数 < 1k**：该品类受众小")
    out.append("- **总评分数 > 100k**：该词触达大量用户，但你需要在 Top 5 才有曝光")

    out.append("\n## 各 keyword 的 Top 5 竞品详情\n")
    for r in rows:
        if not r.get("top_apps"):
            continue
        out.append(f"### `{r['keyword']}` ({r['result_count']} 个结果)")
        for app in r["top_apps"]:
            rc = app.get("rating_count") or 0
            out.append(f"- **{app['name']}** "
                       f"(`{app['bundleId']}`) "
                       f"⭐{app.get('rating', '-')} ({rc:,} 评分)")
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True, help="国家码：jp/us/kr/...")
    ap.add_argument("--keywords", help="逗号分隔候选词")
    ap.add_argument("--keywords-file", help="一行一个候选词的文件")
    ap.add_argument("--out", help="markdown 输出路径")
    ap.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = ap.parse_args()

    if args.keywords:
        kws = [k.strip() for k in args.keywords.split(",") if k.strip()]
    elif args.keywords_file:
        kws = [l.strip() for l in open(args.keywords_file) if l.strip()]
    else:
        ap.error("--keywords 或 --keywords-file 二选一")

    rows = []
    for kw in kws:
        try:
            rows.append(analyze(kw, args.country))
            time.sleep(0.5)  # 节流，iTunes Search API 有速率限制
        except Exception as e:
            print(f"⚠️  {kw}: {e}", file=sys.stderr)
            rows.append({"keyword": kw, "country": args.country,
                         "result_count": -1, "error": str(e)})

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
