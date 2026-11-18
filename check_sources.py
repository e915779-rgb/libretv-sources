#!/usr/bin/env python3
"""Check availability of the MacCMS-style type:1 APIs without deleting sources."""
import concurrent.futures
import datetime
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "sources.json"
REPORT_JSON = BASE / "health-report.json"
REPORT_MD = BASE / "health-report.md"
TIMEOUT = 12
WORKERS = 12

def check(item):
    name = str(item.get("name") or "")
    api = str(item.get("url") or "").strip()
    parts = urllib.parse.urlsplit(api)
    query = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    if not any(k == "ac" for k, _ in query):
        query.append(("ac", "list"))
    url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, parts.path,
                                   urllib.parse.urlencode(query), parts.fragment))
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; LibreTV-SourceHealth/1.0)",
            "Accept": "application/json,text/plain,*/*",
            "Range": "bytes=0-65535",
        },
    )
    started = datetime.datetime.now(datetime.timezone.utc)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            status = response.status
            body = response.read(65536)
            content_type = response.headers.get("Content-Type", "")
        if status < 200 or status >= 300:
            return {"name": name, "url": api, "status": "http_error",
                    "http_status": status, "detail": f"HTTP {status}"}
        try:
            payload = json.loads(body.decode("utf-8-sig"))
        except Exception:
            return {"name": name, "url": api, "status": "invalid_response",
                    "http_status": status, "detail": "HTTP成功，但回應不是有效JSON"}
        if not isinstance(payload, (dict, list)) or not payload:
            return {"name": name, "url": api, "status": "invalid_response",
                    "http_status": status, "detail": "JSON回應為空或格式不符"}
        if isinstance(payload, dict):
            code = payload.get("code")
            if code in (-1, 0, 400, 401, 403, 404, 500):
                return {"name": name, "url": api, "status": "api_error",
                        "http_status": status, "detail": f"API回傳 code={code}"}
        elapsed = (datetime.datetime.now(datetime.timezone.utc) - started).total_seconds()
        return {"name": name, "url": api, "status": "ok",
                "http_status": status, "elapsed_seconds": round(elapsed, 2),
                "content_type": content_type}
    except urllib.error.HTTPError as exc:
        return {"name": name, "url": api, "status": "http_error",
                "http_status": exc.code, "detail": str(exc.reason)}
    except Exception as exc:
        return {"name": name, "url": api, "status": "unreachable",
                "detail": str(exc)[:240]}

data = json.loads(SOURCE.read_text(encoding="utf-8"))
items = data.get("sources", [])
if not isinstance(items, list) or not items:
    raise SystemExit("sources.json 無有效來源，停止檢測")

with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
    results = list(pool.map(check, items))

ok = sum(x["status"] == "ok" for x in results)
failed = len(results) - ok
report = {
    "checked_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "total": len(results),
    "available": ok,
    "unavailable_or_unverified": failed,
    "results": results,
}
REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

lines = [
    "# LibreTV API 可用性檢測",
    "",
    f"- 檢測時間（UTC）：{report['checked_at_utc']}",
    f"- 總數：{len(results)}",
    f"- 回應正常：{ok}",
    f"- 異常或未能確認：{failed}",
    "",
    "| 狀態 | 來源 | HTTP | 耗時 | 說明 |",
    "|---|---|---:|---:|---|",
]
for x in results:
    state = "正常" if x["status"] == "ok" else "異常/待確認"
    elapsed = f"{x.get('elapsed_seconds', '-')}"
    detail = x.get("detail", "")
    lines.append(f"| {state} | {x['name']} | {x.get('http_status', '-')} | {elapsed} | {detail} |")
REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

summary = "\n".join(lines)
github_summary = os.environ.get("GITHUB_STEP_SUMMARY")
if github_summary:
    with open(github_summary, "a", encoding="utf-8") as f:
        f.write(summary + "\n")

print(f"API檢測完成：共 {len(results)} 個，正常 {ok} 個，異常/待確認 {failed} 個")
