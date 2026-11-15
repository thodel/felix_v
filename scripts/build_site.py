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


def clean_nulls(x):
    """The model sometimes writes the string "null"; make it a real null and drop empty objects."""
    if isinstance(x, str):
        return None if x.strip().lower() in {"null", "none", "", "n/a", "unknown"} else x
    if isinstance(x, list):
        return [y for y in (clean_nulls(v) for v in x) if y not in (None, {}, [])]
    if isinstance(x, dict):
        d = {k: clean_nulls(v) for k, v in x.items()}
        d = {k: v for k, v in d.items() if v not in (None, {}, [])}
        return d or None
    return x


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
        catmus_vol = {}  # page -> CATMuS text per site line (same order as the site's lines)
        n_cat = n_comb = 0
        for p in vol["pages"]:
            stem = f"{vol['docId']}_p{p['n']:04d}"
            cat_f, comb_f = ROOT / "data/catmus" / f"{stem}.json", ROOT / "data/combined" / f"{stem}.json"
            cat = [(l.get("text") or "").strip() for l in json.loads(cat_f.read_text())["lines"]] if cat_f.exists() else None
            n_all = sum(len(r["lines"]) for r in p["regions"])
            if cat is not None and len(cat) != n_all:
                cat = None  # line lists disagree: no alignment, no CATMuS for this page
            comb = {}
            if comb_f.exists() and cat is not None:
                comb = {l["i"]: l for l in json.loads(comb_f.read_text())["lines"]}
            regions, cat_lines, i = [], [], 0
            for r in p["regions"]:
                # only lines with text: the numbering then equals segment.py's line index + 1
                lines = []
                for l in r["lines"]:
                    t = l["text"].strip()
                    if t:
                        row = {"t": t, "b": l["box"]}
                        k = comb.get(i)
                        if k and k["text"] != t:
                            row["k"] = [k["text"], k["c"]]  # combined reading, only where it differs from CITlab
                            n_comb += 1
                        lines.append(row)
                        cat_lines.append(cat[i] if cat is not None else None)
                    i += 1
                if lines:
                    regions.append({"l": lines})
            pg = {"n": p["n"], "k": p["key"], "w": p["w"], "h": p["h"], "r": regions}
            if cat is not None:
                pg["cm"] = 1  # CATMuS and combined reading exist for this page
                catmus_vol[p["n"]] = cat_lines
                n_cat += 1
            pages.append(pg)
        (OUT / f"vol{v}.json").write_text(json.dumps({"vol": v, "docId": vol["docId"], "pages": pages},
                                                     ensure_ascii=False, separators=(",", ":")))
        (OUT / f"catmus{v}.json").write_text(json.dumps(catmus_vol, ensure_ascii=False, separators=(",", ":")))
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
        regs = []
        for c, e in zip(compact, ents):
            rf = ROOT / "data/regests" / f"{e['id']}.json"
            if not rf.exists():
                continue
            r = json.loads(rf.read_text())
            g = r.get("data")
            if not (r.get("ok") and g):
                continue
            g = clean_nulls(g)
            regs.append({"id": c["id"], "s": c["s"], "d": {k: c["d"].get(k) for k in ("iso", "check", "inherited", "place") if c["d"].get(k)},
                         "t": g.get("act_type") or "other", "a": g.get("act"),
                         "to": g.get("addressee"), "for": g.get("beneficiary"), "obj": g.get("object"),
                         "val": g.get("value"), "vac": g.get("vacancy"), "ex": g.get("executors") or [],
                         "pl": g.get("places") or [], "reg": e.get("reg"),
                         "de": g.get("regest_de"), "fr": g.get("regest_fr"), "la": g.get("regest_la"),
                         "conf": g.get("confidence"), "multi": bool(g.get("several_letters")),
                         "k": r.get("combined_share", 0)})
        (OUT / f"regests{v}.json").write_text(json.dumps(regs, ensure_ascii=False, separators=(",", ":")))
        isos = sorted(c["d"]["iso"] for c in compact if c["d"].get("iso") and c["d"].get("check") == "ok")
        n_lines = sum(len(r["l"]) for p in pages for r in p["r"])
        summary.append({
            "vol": v, "docId": vol["docId"], "title": vol["title"], "pages": len(pages), "lines": n_lines,
            "catmus_pages": n_cat, "combined_changed_lines": n_comb,
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
        # page readings (no line geometry) per opening, for the viewer's reading menu
        pr: dict = {}
        for h in json.loads(comp.read_text())["halves"]:
            for m, r in h["readers"].items():
                pr.setdefault(f"{h['vol']}:{h['page']}", {}).setdefault(m, {})[h["side"]] = r["text"]
        (OUT / "pagereadings.json").write_text(json.dumps(pr, ensure_ascii=False, separators=(",", ":")))
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
