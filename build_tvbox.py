#!/usr/bin/env python3
"""Build 影视仓 config from LibreTV API sources plus the pinned CSP catalogue."""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "sources.json"
CSP_SOURCE = BASE / "csp_sites.json"
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
    key = f"site_{index:03d}"
    if key in seen:
        raise SystemExit(f"重複站點 key：{key}")
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

csp_data = json.loads(CSP_SOURCE.read_text(encoding="utf-8"))
csp_sites = csp_data.get("sites")
if not isinstance(csp_sites, list) or len(csp_sites) != 143:
    raise SystemExit("csp_sites.json 應包含完整 143 個 CSP 站點，停止生成")
if not csp_data.get("spider"):
    raise SystemExit("csp_sites.json 缺少全域 spider，停止生成")

for item in csp_sites:
    key = item.get("key")
    api = item.get("api")
    if not key or key in seen or item.get("type") != 3 or not isinstance(api, str) or not api.startswith("csp_"):
        raise SystemExit(f"CSP 站點資料錯誤或 key 重複：{key}")
    seen.add(key)

all_sites = sites + csp_sites
output_data = {"spider": csp_data["spider"], "sites": all_sites}
tmp = OUTPUT.with_suffix(".json.tmp")
tmp.write_text(json.dumps(output_data, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
tmp.replace(OUTPUT)
print(f"已生成 {OUTPUT}：{len(sites)} 個 type:1 + {len(csp_sites)} 個 CSP，共 {len(all_sites)} 個站點")
