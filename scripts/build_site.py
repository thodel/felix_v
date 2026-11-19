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
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm_entries import date_fields  # noqa: E402
from incipit import fix_line  # noqa: E402

START = re.compile(r"^\W*(Felix\s+e|ep(iscop)?(us|s|ũs)?\.?\s+(etc|ꝫc|servus))", re.I)

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
        # line readers: UBELIX readers in data/lines/<reader>/ (by line id); the old gateway CATMuS
        # run (data/catmus, by line index) only where UBELIX has no CATMuS for the page
        reader_names = sorted(p.name for p in (ROOT / "data/lines").iterdir() if p.is_dir()) if (ROOT / "data/lines").exists() else []
        per_reader = {n: {} for n in reader_names}
        n_comb = 0
        for p in vol["pages"]:
            stem = f"{vol['docId']}_p{p['n']:04d}"
            ids = [l["id"] for r in p["regions"] for l in r["lines"]]
            got = {}
            for n in reader_names:
                f = ROOT / "data/lines" / n / f"{stem}.json"
                if f.exists():
                    got[n] = {l["id"]: (l.get("text") or "").strip() for l in json.loads(f.read_text())["lines"]}
            if "kraken-catmus_medieval" not in got:
                cf = ROOT / "data/catmus" / f"{stem}.json"
                if cf.exists():
                    cl = [(l.get("text") or "").strip() for l in json.loads(cf.read_text())["lines"]]
                    if len(cl) == len(ids):
                        got["kraken-catmus_medieval"] = dict(zip(ids, cl))
                        per_reader.setdefault("kraken-catmus_medieval", {})
            comb_f = ROOT / "data/combined" / f"{stem}.json"
            comb, comb_multi = {}, False
            if comb_f.exists():
                cj = json.loads(comb_f.read_text())
                comb_multi = str(cj.get("version", "")).startswith("combine_multi")
                comb = {l["i"]: l for l in cj["lines"]}
            regions, i = [], 0
            texts = {n: [] for n in got}
            for r in p["regions"]:
                # only lines with text: the numbering then equals segment.py's line index + 1
                lines = []
                for l in r["lines"]:
                    t = l["text"].strip()
                    if t:
                        row = {"t": t, "b": l["box"]}
                        k = comb.get(i)
                        if not k:  # no combined reading yet: the joint reading is CITlab, with the incipit restored
                            ft, _, fixed = fix_line(t, [])
                            if fixed:
                                k = {"text": ft, "c": [], "low": []}
                        else:
                            ft, sp, fixed = fix_line(k["text"], k.get("low") if comb_multi else k.get("c", []))
                            if fixed:
                                k = {**k, "text": ft, ("low" if comb_multi else "c"): sp}
                        if k and k["text"] != t:
                            # combined reading, only where it differs from CITlab:
                            # [text, spans, 1] spans = uncertain words (multi-reader vote)
                            # [text, spans]    spans = words taken from CATMuS (two-reader rule)
                            row["k"] = [k["text"], k["low"], 1] if comb_multi else [k["text"], k.get("c", [])]
                            n_comb += 1
                        lines.append(row)
                        for n in got:
                            texts[n].append(got[n].get(l["id"], ""))
                    i += 1
                if lines:
                    regions.append({"l": lines})
            pg = {"n": p["n"], "k": p["key"], "w": p["w"], "h": p["h"], "r": regions}
            if got:
                pg["rd"] = sorted(got)
            if comb:
                pg["cm"] = 2 if comb_multi else 1
            for n in got:
                per_reader[n][p["n"]] = texts[n]
            pages.append(pg)
        (OUT / f"vol{v}.json").write_text(json.dumps({"vol": v, "docId": vol["docId"], "pages": pages},
                                                     ensure_ascii=False, separators=(",", ":")))
        for n, data in per_reader.items():
            if data:
                (OUT / f"read-{n}-{v}.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
        old = OUT / f"catmus{v}.json"
        if old.exists():
            old.unlink()
        n_cat = sum(1 for pg in pages if pg.get("rd"))
        page_by_n = {pg["n"]: pg for pg in pages}
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
            # preview: image key of the start page and the box around the entry's first lines there
            sp = page_by_n.get(e["start"]["page"])
            if sp:
                flat = []  # (line, is_marginal) in site order; marginal regions as in the viewer
                for r in sp["r"]:
                    avg = sum(len(l["t"]) for l in r["l"]) / max(1, len(r["l"]))
                    flat += [(l, len(r["l"]) <= 4 and avg < 28) for l in r["l"]]
                first_l = e["start"]["line"]
                last_l = e["end"]["line"] if e["end"]["page"] == e["start"]["page"] else len(flat) - 1
                main = [l for l, marg in flat[first_l:last_l + 1] if not marg and l.get("b")]
                boxes = [l["b"] for l in main[:8]]
                if boxes:
                    compact[-1]["pk"] = sp["k"]
                    compact[-1]["bx"] = [min(b[0] for b in boxes), min(b[1] for b in boxes),
                                         max(b[2] for b in boxes), max(b[3] for b in boxes)]
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
        # first image with a real entry: a line of the joint reading opens with «Felix ep…» or, where the
        # whole word «Felix» is lost, with «episcopus etc.» (checked by hand on all eight volumes, 19.11.2026)
        start = next((p["n"] for p in pages if any(START.match((l["k"][0] if l.get("k") else l["t"]) or "")
                                                   for r in p["r"] for l in r["l"])), 1)
        summary.append({
            "vol": v, "start": start, "docId": vol["docId"], "title": vol["title"], "pages": len(pages), "lines": n_lines,
            "reader_pages": n_cat, "combined_changed_lines": n_comb,
            "readers": {n: len(d) for n, d in per_reader.items() if d},
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

    # linked entities (scripts/nel.py) for the register page
    ent_f = ROOT / "data/nel/entities.json"
    if ent_f.exists():
        starts = {}
        for v_ in range(1, 9):
            ef = OUT / f"entries{v_}.json"
            if ef.exists():
                for e in json.loads(ef.read_text()):
                    starts[e["id"]] = [v_] + e["s"]
        out = []
        for c in json.loads(ent_f.read_text()):
            ms = c["mentions"]
            names = Counter((m.get("name") or m.get("as_written") or "").strip() for m in ms)
            label = c["mentions"][0].get("seat") or names.most_common(1)[0][0]
            def top(field):
                return [x for x, _ in Counter(m.get(field) for m in ms if m.get(field)).most_common(3)]
            out.append({"id": c["id"], "kind": c["kind"], "label": label, "grade": c["grade"],
                        "forms": sorted({m.get("as_written") for m in ms if m.get("as_written")})[:12],
                        "roles": top("role"), "offices": top("office"), "dioc": top("diocese"), "types": top("type"),
                        "links": [{k: l.get(k) for k in ("source", "id", "label", "grade", "url", "dates", "desc") if l.get(k)} for l in c["links"]],
                        **({"coord": c["coord"]} if c.get("coord") else {}),
                        "entries": sorted({m["entry"] for m in ms}),
                        "at": {m["entry"]: starts.get(m["entry"]) for m in ms}})
        out.sort(key=lambda x: (-len(x["entries"]), x["label"].lower()))
        (OUT / "entities.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")))
        rep = ROOT / "data/nel/report.json"
        if rep.exists():
            (OUT / "nel_report.json").write_text(rep.read_text())

    comp = ROOT / "data/readings/compare_all.json"  # scripts/compare_all.py: CITlab, vote, qwen3.8, Gemini …
    if comp.exists():
        from compare_all import cer
        ca = json.loads(comp.read_text())
        models = [n for n in ca["readers"] if n not in ("CITlab", "vote")]
        agg = {n: {"halves": ca["per_reader"][n]["halves"],
                   "median_cer_vs_htr": (ca["matrix"].get(n, {}).get("CITlab") or {}).get("median"),
                   "empty": ca["per_reader"][n]["empty"], "truncated": ca["per_reader"][n]["cut_off"],
                   "with_loops": ca["per_reader"][n]["looping"],
                   "median_len_ratio": ca["per_reader"][n]["median_len_vs_citlab"],
                   "median_seconds": ca["per_reader"][n]["median_seconds"]} for n in models}
        halves = [{"vol": h["vol"], "page": h["page"], "side": h["side"], "htr": h["readers"]["CITlab"],
                   "readers": {n: {"text": h["readers"][n], "cer_vs_htr": cer(h["readers"][n], h["readers"]["CITlab"])}
                               for n in ["vote"] + models if h["readers"].get(n, "").strip()}} for h in ca["halves"]]
        (OUT / "readings.json").write_text(json.dumps(
            {"note": ca["note"], "aggregate": agg, "readers": ca["readers"], "matrix": ca["matrix"], "halves": halves},
            ensure_ascii=False, separators=(",", ":")))
        # page readings (no line geometry) per opening, for the viewer's reading menu; empty answers left out
        pr: dict = {}
        for h in ca["halves"]:
            for m in models:
                if h["readers"].get(m, "").strip():
                    pr.setdefault(f"{h['vol']}:{h['page']}", {}).setdefault(m, {})[h["side"]] = h["readers"][m]
        (OUT / "pagereadings.json").write_text(json.dumps(pr, ensure_ascii=False, separators=(",", ":")))
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
