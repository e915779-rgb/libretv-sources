#!/usr/bin/env python3
"""Convert LibreTV sources.json into a TVBox/影视仓 sites configuration."""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "sources.json"
OUTPUT = BASE / "tvbox.json"

data = json.loads(SOURCE.read_text(encoding="utf-8"))
sources = data.get("sources")
if not isinstance(sources, list) or len(sources) < 10:
    raise SystemExit("sources.json 格式錯誤或來源數量異常，停止生成")

sites = []
seen = set()
for index, item in enumerate(sources, 1):
    name = str(item.get("name") or "").strip()
    api = str(item.get("url") or "").strip()
    if not name or not re.match(r"^https?://", api, re.I):
        continue
    slug = re.sub(r"[^\\w\\u4e00-\\u9fff]+", "", name, flags=re.UNICODE)[:12] or "source"
    key = f"src_{index:02d}_{slug}"
    if key in seen:
        key = f"{key}_{index}"
    seen.add(key)
    display_name = ("【成人】" if item.get("isAdult") is True else "") + name
    sites.append({
        "key": key,
        "name": display_name,
        "type": 1,
        "api": api,
        "searchable": 1,
        "quickSearch": 1,
        "filterable": 1
    })

if len(sites) < 10:
    raise SystemExit(f"有效來源數量異常：{len(sites)}，停止覆蓋")

tmp = OUTPUT.with_suffix(".json.tmp")
tmp.write_text(json.dumps({"sites": sites}, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
tmp.replace(OUTPUT)
print(f"已生成 {OUTPUT}，共 {len(sites)} 個站點；成人標記 {sum(1 for x in sites if x['name'].startswith('【成人】'))} 個")
