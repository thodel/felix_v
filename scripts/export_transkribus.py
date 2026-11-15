#!/usr/bin/env python3
"""Export the Felix V bullarium (Transkribus collection 53095) to static JSON.

Per volume: data/raw/vol<N>/fulldoc.json (manifest without user names) and
data/raw/vol<N>/pagexml/<page>.xml (latest transcript), plus
data/export/vol<N>.json with per page: image key, size, status, lines (text + box).

Images are NOT copied: the site loads them from Transkribus by image key.

Env: TRANSKRIBUS_USER, TRANSKRIBUS_PASSWORD (read from a .env given with --env).
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

REST = "https://transkribus.eu/TrpServer/rest"
OIDC = "https://account.readcoop.eu/auth/realms/readcoop/protocol/openid-connect/token"
COL = 53095
NS = {"p": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}
ROOT = Path(__file__).resolve().parent.parent


def load_env(path: Path) -> None:
    for line in path.read_text().splitlines():
        m = re.match(r"\s*([A-Z_]+)\s*=\s*(.*)\s*$", line)
        if m and m.group(1) not in os.environ:
            os.environ[m.group(1)] = m.group(2).strip().strip('"').strip("'")


class TK:
    def __init__(self) -> None:
        self.login()

    def login(self) -> None:
        data = urllib.parse.urlencode({
            "grant_type": "password", "client_id": os.environ.get("TRANSKRIBUS_OIDC_CLIENT_ID", "transkribus-api-client"),
            "username": os.environ["TRANSKRIBUS_USER"], "password": os.environ["TRANSKRIBUS_PASSWORD"],
        }).encode()
        with urllib.request.urlopen(urllib.request.Request(OIDC, data=data, method="POST"), timeout=60) as r:
            self.token = json.loads(r.read())["access_token"]

    def get(self, url: str) -> bytes:
        for attempt in range(3):
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self.token}"})
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    return r.read()
            except urllib.error.HTTPError as e:
                if e.code == 401 and attempt < 2:
                    self.login()
                    continue
                raise
            except (urllib.error.URLError, TimeoutError):
                if attempt == 2:
                    raise
        raise RuntimeError(url)


def strip_users(obj):
    """Drop user names/e-mails from the manifest before it is stored in the repo."""
    if isinstance(obj, dict):
        return {k: strip_users(v) for k, v in obj.items()
                if k not in {"userName", "uploader", "userId", "uploaderId", "creator", "email"}}
    if isinstance(obj, list):
        return [strip_users(v) for v in obj]
    return obj


def parse_pagexml(xml: bytes) -> dict:
    root = ET.fromstring(xml)
    page = root.find("p:Page", NS)
    out = {"regions": []}
    if page is None:
        return out
    for reg in page.iter(f"{{{NS['p']}}}TextRegion"):
        lines = []
        for tl in reg.findall("p:TextLine", NS):
            coords = tl.find("p:Coords", NS)
            pts = [tuple(map(int, p.split(","))) for p in (coords.get("points", "") if coords is not None else "").split() if "," in p]
            box = [min(x for x, _ in pts), min(y for _, y in pts), max(x for x, _ in pts), max(y for _, y in pts)] if pts else None
            ue = tl.find("p:TextEquiv/p:Unicode", NS)
            lines.append({"id": tl.get("id"), "box": box, "text": (ue.text or "") if ue is not None else ""})
        rc = reg.find("p:Coords", NS)
        out["regions"].append({"id": reg.get("id"), "type": reg.get("type") or "", "custom": reg.get("custom", ""),
                               "coords": rc.get("points", "") if rc is not None else "", "lines": lines})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", type=Path, default=Path.home() / "Repos/reformation/.env")
    ap.add_argument("--only", type=int, nargs="*", help="volume numbers")
    args = ap.parse_args()
    load_env(args.env)
    tk = TK()
    docs = json.loads(tk.get(f"{REST}/collections/{COL}/list"))
    vols = {}
    for d in docs:
        m = re.search(r"Vol_(\d+)", d["title"])
        if m:
            vols[int(m.group(1))] = d["docId"]
    summary = []
    for vol, doc_id in sorted(vols.items()):
        if args.only and vol not in args.only:
            continue
        raw = ROOT / "data/raw" / f"vol{vol}"
        (raw / "pagexml").mkdir(parents=True, exist_ok=True)
        full = json.loads(tk.get(f"{REST}/collections/{COL}/{doc_id}/fulldoc"))
        (raw / "fulldoc.json").write_text(json.dumps(strip_users(full), ensure_ascii=False, indent=1))
        pages = full["pageList"]["pages"]

        def fetch(p):
            ts = max(p["tsList"]["transcripts"], key=lambda t: int(t.get("timestamp") or 0))
            target = raw / "pagexml" / f"{p['pageNr']:04d}.xml"
            if not target.exists():
                target.write_bytes(tk.get(ts["url"]))
            parsed = parse_pagexml(target.read_bytes())
            return {"n": p["pageNr"], "key": p["key"], "file": p.get("imgFileName"), "w": p["width"], "h": p["height"],
                    "status": ts.get("status"), "tool": ts.get("toolName") or "", **parsed}

        with cf.ThreadPoolExecutor(8) as ex:
            out_pages = sorted(ex.map(fetch, pages), key=lambda x: x["n"])
        site = ROOT / "data/export"
        site.mkdir(parents=True, exist_ok=True)
        meta = {"vol": vol, "docId": doc_id, "title": full["md"]["title"], "pages": out_pages}
        (site / f"vol{vol}.json").write_text(json.dumps(meta, ensure_ascii=False, separators=(",", ":")))
        nlines = sum(len(r["lines"]) for p in out_pages for r in p["regions"])
        summary.append({"vol": vol, "docId": doc_id, "pages": len(out_pages), "lines": nlines,
                        "status": sorted({p["status"] for p in out_pages}), "tools": sorted({p["tool"] for p in out_pages})})
        print(json.dumps(summary[-1], ensure_ascii=False), flush=True)
    (ROOT / "data/export_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
