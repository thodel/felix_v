#!/usr/bin/env python3
"""Regests for the segmented entries: structured fields + a regest in German, French and Latin.

qwen3.8 (GPUStack, text only, thinking off) reads one entry and returns JSON. The date and the
place of issue are NOT asked from the model: they come from the dating clause (llm_entries.py
--task date, computed in code) and are handed to the model as given facts. The registration
note (scribe) comes from the segmentation.

Text: the combined reading where it exists for a line (data/combined), else CITlab. The input
text is stored with the result; an entry is redone when its text or the prompt version changes.

Output: data/regests/<entry id>.json
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm_entries import call, date_fields  # noqa: E402
from segment import linear  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXP = ROOT / "data/export"
COMB = ROOT / "data/combined"
OUT = ROOT / "data/regests"
PROMPT_VERSION = "regest_v1"
MAX_CHARS = 14000

ACT_TYPES = ["provision", "collation", "expectative", "dispensation", "indulgence", "absolution", "confirmation",
             "appointment", "licence", "exemption", "commission", "union", "protection", "safe_conduct", "other"]

PROMPT = """You are an archivist writing calendar entries (regests) for the register of the antipope Felix V (1439-1449, formerly Duke Amadeus VIII of Savoy; residing at Basel, later Lausanne and Geneva).
Below is ONE register entry: a copied papal letter, read by handwriting recognition. The reading is noisy (confused letters, wrong words); read through the noise, but do not invent anything the text does not support. The entry may begin with the last lines of the previous letter; ignore those. If it clearly contains more than one letter, describe the one that ends with the dating clause (the last one) and set "several_letters": true.

Given facts (do not change them): date of issue {date}; place of issue {place}.

Return JSON only:
{{
 "act_type": one of {types},
 "act": short English label of the legal act, e.g. "provision of a canonry and prebend", "dispensation for illegitimacy", "commission to the official of Geneva to examine a case",
 "addressee": {{"name": "Latin nominative or null", "office": "e.g. abbas, officialis, decanus, episcopus", "institution": "e.g. monasterium sancti Mauricii Agaunensis", "diocese": "Latin adjective, e.g. Gebennensis"}},
 "beneficiary": {{"name": ..., "status": "e.g. clericus, presbyter, canonicus", "diocese": ...}} or null if the same as the addressee,
 "object": "benefice, office or matter, e.g. parochialis ecclesia de Furiaco Lugdunensis diocesis" or null,
 "value": "yearly value if stated, e.g. 24 libre turonenses parvorum" or null,
 "vacancy": "how the benefice fell vacant, e.g. per obitum Petri X" or null,
 "executors": ["…"],
 "other_persons": [{{"name": ..., "role": ...}}],
 "places": ["places and dioceses named, in Latin as normalised as the text allows"],
 "several_letters": false,
 "confidence": "high" | "medium" | "low",
 "regest_de": "German regest, 1-3 sentences, in the style of a printed calendar: Felix V. … (who, what, for whom, which benefice/matter, conditions). No date, it is shown separately. Names in their Latin form.",
 "regest_fr": "the same in French",
 "regest_la": "the same in Latin, in the abbreviated style of a papal register calendar (e.g. 'Guillelmo abbati mon. … providetur de …')"
}}
Use null where the text does not say. Write the three regests from the same facts; none may contain more than the others.

Entry:
"""


def combined_lookup(vol: dict) -> dict:
    """line id -> combined text, for pages where the combined reading exists."""
    out = {}
    for p in vol["pages"]:
        f = COMB / f"{vol['docId']}_p{p['n']:04d}.json"
        if not f.exists():
            continue
        by_i = {l["i"]: l["text"] for l in json.loads(f.read_text())["lines"]}
        i = 0
        for r in p["regions"]:
            for l in r["lines"]:
                if i in by_i:
                    out[l["id"]] = by_i[i]
                i += 1
    return out


def entry_texts(vol: dict, entries: list[dict]) -> dict:
    """entry id -> (text, share of lines from the combined reading), main text lines only."""
    comb = combined_lookup(vol)
    rows = list(linear(vol))
    pos = {(r[0], r[1]): n for n, r in enumerate(rows)}
    out = {}
    for e in entries:
        a, b = pos.get((e["start"]["page"], e["start"]["line"])), pos.get((e["end"]["page"], e["end"]["line"]))
        if a is None or b is None:
            out[e["id"]] = (e["text"], 0.0)
            continue
        main = [r for r in rows[a:b + 1] if r[2] == "main"]
        lines = [comb.get(r[4], r[3]) for r in main]
        share = sum(1 for r in main if r[4] in comb) / max(1, len(main))
        out[e["id"]] = ("\n".join(lines), round(share, 2))
    return out


def regest_one(e: dict, text: str, d: dict) -> dict:
    date = d.get("iso") or "unknown"
    if d.get("check") == "mismatch":
        date += " (uncertain)"
    prompt = PROMPT.format(date=date, place=d.get("place") or "unknown", types=json.dumps(ACT_TYPES))
    body = text if len(text) <= MAX_CHARS else text[:MAX_CHARS // 3] + "\n[…]\n" + text[-2 * MAX_CHARS // 3:]
    data, meta = call_json(prompt + body)
    return {"id": e["id"], "prompt": PROMPT_VERSION, "input": text, "date_given": date, "data": data, **meta}


def call_json(prompt: str):
    res = call(prompt, 3072)
    return res.get("data"), {k: res.get(k) for k in ("ok", "finish", "seconds", "error")}


def entry_date(e: dict) -> dict:
    f = ROOT / "data/llm/date" / f"{e['id']}.json"
    if e.get("clause") and f.exists():
        r = json.loads(f.read_text())
        if r.get("ok") and r.get("data") and r.get("input") == e["clause"]:
            return date_fields(r["data"])
    return {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vols", type=int, nargs="*")
    ap.add_argument("--sample", type=int)
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = []
    for f in sorted(EXP.glob("vol*.json"), key=lambda p: int(re.sub(r"\D", "", p.stem))):
        vol = json.loads(f.read_text())
        if args.vols and vol["vol"] not in args.vols:
            continue
        ents = json.loads((EXP / f"entries_vol{vol['vol']}.json").read_text())
        texts = entry_texts(vol, ents)
        prev = None
        for e in ents:
            d = entry_date(e)
            if d.get("ut_supra") and prev:
                d = {**prev, "inherited": True}
            if d.get("iso"):
                prev = d
            text, share = texts[e["id"]]
            if len(text.strip()) < 80:
                continue  # covers, fragments
            jobs.append((e, text, d, share))
    if args.ids:
        jobs = [j for j in jobs if j[0]["id"] in set(args.ids)]
    if args.sample:
        jobs = random.Random(1449).sample(jobs, min(args.sample, len(jobs)))

    def done(j):
        f = OUT / f"{j[0]['id']}.json"
        if not f.exists():
            return False
        r = json.loads(f.read_text())
        return r.get("ok") and r.get("data") and r.get("prompt") == PROMPT_VERSION and r.get("input") == j[1]

    todo = [j for j in jobs if not done(j)]
    print(f"{len(todo)} of {len(jobs)} entries to do", flush=True)

    def work(j):
        e, text, d, share = j
        r = regest_one(e, text, d)
        r["combined_share"] = share
        tmp = OUT / f"{e['id']}.tmp"
        tmp.write_text(json.dumps(r, ensure_ascii=False))
        tmp.replace(OUT / f"{e['id']}.json")
        return e["id"], r.get("ok"), r.get("seconds")

    with cf.ThreadPoolExecutor(args.workers) as ex:
        for i, (eid, ok, s) in enumerate(ex.map(work, todo), 1):
            if i % 25 == 0 or not ok or i <= 3:
                print(i, eid, ok, s, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
