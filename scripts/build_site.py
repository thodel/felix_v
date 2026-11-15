#!/usr/bin/env python3
"""Build docs/data/ for the GitHub Pages site from data/export, data/llm and data/readings.

  docs/data/summary.json      volumes with page/line/entry counts and date range
  docs/data/vol<N>.json       pages: key, size, regions with lines (text, box) — the HTR first reading
  docs/data/entries<N>.json   entries without text: span, clause, date (LLM reading, rule check)
  docs/data/register.json     entity register from the NER test (if present)
  docs/data/readings.json     reading comparison sample (if present)
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm_entries import date_fields  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXP = ROOT / "data/export"
OUT = ROOT / "docs/data"


def entry_date(e: dict) -> dict:
    f = ROOT / "data/llm/date" / f"{e['id']}.json"
    if f.exists():
        r = json.loads(f.read_text())
        if r.get("ok") and r.get("data") and r.get("input") == e["clause"]:
            return date_fields(r["data"])
    return {}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    summary = []
    all_entries = {}
    for vf in sorted(EXP.glob("vol*.json"), key=lambda p: int(re.sub(r"\D", "", p.stem))):
        vol = json.loads(vf.read_text())
        v = vol["vol"]
        pages = []
        for p in vol["pages"]:
            regions = []
            for r in p["regions"]:
                # only lines with text: the numbering then equals segment.py's line index + 1
                lines = [{"t": l["text"].strip(), "b": l["box"]} for l in r["lines"] if l["text"].strip()]
                if lines:
                    regions.append({"l": lines})
            pages.append({"n": p["n"], "k": p["key"], "w": p["w"], "h": p["h"], "r": regions})
        (OUT / f"vol{v}.json").write_text(json.dumps({"vol": v, "docId": vol["docId"], "pages": pages},
                                                     ensure_ascii=False, separators=(",", ":")))
        ents = json.loads((EXP / f"entries_vol{v}.json").read_text())
        compact = []
        prev = None
        for e in ents:
            d = entry_date(e)
            if d.get("ut_supra") and prev:
                d = {**prev, "ut_supra": True, "inherited": True}
            if d.get("iso"):
                prev = {k: val for k, val in d.items() if k not in ("ut_supra", "inherited")}
            first = e["text"].split("\n", 1)[0]
            compact.append({"id": e["id"], "s": [e["start"]["page"], e["start"]["line"]], "e": [e["end"]["page"], e["end"]["line"]],
                            "n": e["lines"], "inc": first[:90], "cl": e["clause"], "d": d,
                            "m": [m["text"] for m in e["marg"]][:6]})
            all_entries[e["id"]] = compact[-1]
        (OUT / f"entries{v}.json").write_text(json.dumps(compact, ensure_ascii=False, separators=(",", ":")))
        isos = sorted(c["d"]["iso"] for c in compact if c["d"].get("iso") and c["d"].get("check") == "ok")
        n_lines = sum(len(r["l"]) for p in pages for r in p["r"])
        summary.append({
            "vol": v, "docId": vol["docId"], "title": vol["title"], "pages": len(pages), "lines": n_lines,
            "thumb": max(pages[len(pages) // 4: len(pages) // 2] or pages, key=lambda p: sum(len(r["l"]) for r in p["r"]))["k"], "entries": len(compact),
            "dated": sum(1 for c in compact if c["d"].get("iso")),
            "checked": sum(1 for c in compact if c["d"].get("check") == "ok"),
            "from": isos[len(isos) // 20] if isos else None, "to": isos[-1 - len(isos) // 20] if isos else None,
        })
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1))

    # register from the NER test
    ner_dir = ROOT / "data/llm/ner"
    if ner_dir.exists():
        reg = {"persons": defaultdict(list), "places": defaultdict(list), "institutions": defaultdict(list)}
        tested, summaries = [], {}
        mentions = {k: 0 for k in reg}
        not_verbatim = {k: 0 for k in reg}
        role_other, secs = 0, []
        for f in sorted(ner_dir.glob("*.json")):
            r = json.loads(f.read_text())
            if not (r.get("ok") and r.get("data")):
                continue
            tested.append(r["id"])
            summaries[r["id"]] = r["data"].get("summary")
            secs.append(r.get("seconds") or 0)
            src = (r.get("input") or "").lower()
            for kind in reg:
                for ent in r["data"].get(kind) or []:
                    mentions[kind] += 1
                    written = (ent.get("name") or "").strip().lower()
                    if written and written not in src:
                        not_verbatim[kind] += 1
                    if kind == "persons" and ent.get("role") == "other":
                        role_other += 1
                    key = (ent.get("normalised") or ent.get("name") or "").strip()
                    if not key:
                        continue
                    reg[kind][key].append({"entry": r["id"], "as": ent.get("name"),
                                           **{k: ent.get(k) for k in ("role", "office", "diocese", "type", "place") if ent.get(k)}})
        stats = {"tested": len(tested), "mentions": mentions, "not_verbatim": not_verbatim, "role_other": role_other,
                 "median_seconds": round(sorted(secs)[len(secs) // 2]) if secs else None}
        out = {"tested": tested, "summaries": summaries, "stats": stats,
               **{k: sorted(({"name": n, "refs": refs} for n, refs in v.items()), key=lambda x: x["name"].lower())
                  for k, v in reg.items()}}
        (OUT / "register.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))

    comp = ROOT / "data/readings/compare.json"
    if comp.exists():
        (OUT / "readings.json").write_text(comp.read_text())
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
