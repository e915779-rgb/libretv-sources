import json
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(__file__).resolve().parent
INPUT = "https://mylazily.github.io/ziyuanzhan/data/online.json"
OUTPUT = BASE / "sources.json"

req = urllib.request.Request(
    INPUT,
    headers={"User-Agent": "Mozilla/5.0 LibreTV-Updater"}
)

with urllib.request.urlopen(req, timeout=30) as r:
    data = json.load(r)

if not isinstance(data.get("data"), list):
    raise RuntimeError("上游 JSON 格式錯誤")

sources = []
seen = set()
adult_words = ["成人", "色情", "伦理片", "福利", "情色"]

for item in data["data"]:
    name = str(item.get("name") or "").strip()
    api = str(item.get("api") or "").strip()
    link = str(item.get("link") or "").strip()

    if item.get("status") != "ok" or not name or not api:
        continue

    parsed = urlparse(api)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        continue

    api = api.rstrip("/")
    if api in seen:
        continue
    seen.add(api)

    tags = " ".join(item.get("tags", []))
    adult = (
        "新极品" in name
        or any(word in name + tags for word in adult_words)
    )

    source = {
        "name": name,
        "url": api,
        "isAdult": adult
    }

    if link:
        source["detail"] = link.rstrip("/")

    sources.append(source)

sources = sources[:57]

if len(sources) < 10:
    raise RuntimeError(
        f"來源數量異常：{len(sources)}，保留舊文件"
    )

result = {
    "name": "GitHub自動更新影视点播源",
    "version": 2,
    "sources": sources
}

tmp = OUTPUT.with_suffix(".json.tmp")
tmp.write_text(
    json.dumps(result, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
tmp.replace(OUTPUT)

print("上游數量:", data.get("total"))
print("生成數量:", len(sources))
print("成人來源:", sum(s["isAdult"] for s in sources))
print("輸出:", OUTPUT)
