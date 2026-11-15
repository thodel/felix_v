#!/usr/bin/env python3
"""qwen3.8 (GPUStack, text only, thinking off) on the segmented entries.

  --task date   read each dating clause into fields; ISO date + pontificate check are computed in code
  --task ner    extract persons, places, institutions, dates from an entry (test: --sample N)

Results: data/llm/<task>/<entry id>.json  (resumable; one file per entry)
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from segment import check, to_iso  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "data/export"
MODEL = "qwen3.8-27b"
PROMPT_VERSION = {"date": "date_v2", "ner": "ner_v1"}

DATE_PROMPT = """Below is a dating clause from a 15th-century papal register of Felix V (1439-1449), as read by handwriting recognition. The recognition is noisy: letters are confused (c/t, u/n, s/f), words are split or joined. Read it as a Latin dating clause and return JSON only:

{"place": Latin place name as written, normalised (e.g. "Basilee", "Lausanne", "Gebennis", "Thononii", "Ripaille") or null,
 "day_number": the ordinal before the reckoning as a number (pridie = 2, no ordinal = 1) or null,
 "reckoning": "kalendas" | "nonas" | "idus" | "day_of_month" | null,
 "month": month the reckoning refers to, 1-12, or null,
 "year": year AD as written after "anno a nativitate domini" (e.g. millesimo quadringentesimo quadragesimo secundo = 1442) or null,
 "pontificate_year": number after "pontificatus nostri anno" or null,
 "ut_supra": true if the clause says "Datum ut supra",
 "confidence": "high" | "medium" | "low"}

How to read the noisy recognition:
- The dating clause is "Datum <place> <ordinal> <kalendas|nonas|idus> <month genitive> anno a nativitate domini millesimo quadringentesimo <year words> pontificatus nostri anno <ordinal>".
- "kl." (kalendas) is often misread as: bal, ball, ballis, bli, bls, ll, lai, libs, libus, kls, kl, habilis, Rl, l. "id." (idus) as: ious, iodus, idrm, dus, ida, sous, so. "non." (nonas) as: non, nos, noi, nonn.
- An ordinal followed by one of these and a month is kalendas/nonas/idus, NOT a day of the month. Use "day_of_month" only if the text has no such word at all.
- Ordinals are often damaged: cercio/certio/tercio = 3, cruinto/guinto/quito/suinto = 5, dexto/sexto = 6, oetavo/octano = 8, decino/decimo = 10, "pridie" = 2.
- The year words after "quadringentesimo": quadragesimo = 1440, quadragesimo primo = 1441 (also "pmo", "p̄mo", "pimo", "pumo"), secundo = 1442, tercio = 1443, quarto = 1444, quinto = 1445, sexto = 1446, septimo = 1447, octavo = 1448, nono = 1449. Read the word that follows "quadragesimo" carefully; joined words are common ("quadragesimosecundo").
- The pontificate year is the ordinal after "pontificatus nostri anno" (or "suscepti a nobis apostolatus officii anno"); "pmo/p̄mo/pumo/premo" = primo.

Do not compute a calendar date. Clause:
"""

NER_PROMPT = """Below is one entry from a papal register of Felix V (1439-1449), a Latin letter read by handwriting recognition (noisy: letters confused, words split or joined). Extract the named entities. Return JSON only:

{"persons": [{"name": as written, "normalised": Latin nominative form, "role": e.g. "addressee", "petitioner", "beneficiary", "deceased predecessor", "executor", "scribe", "other", "office": office or title if stated, "diocese": if stated}],
 "places": [{"name": as written, "normalised": Latin or modern name, "type": "city" | "diocese" | "parish" | "region" | "other"}],
 "institutions": [{"name": as written, "normalised": e.g. "ecclesia sancti Petri Gebennensis", "type": "church" | "monastery" | "chapel" | "chapter" | "hospital" | "university" | "other", "place": if stated}],
 "dates": [{"text": as written, "iso": "YYYY-MM-DD" or "YYYY-MM" or "YYYY" if you are sure, else null}],
 "summary": "one-sentence English summary of the act (e.g. provision of a canonry, dispensation, indulgence)"}

Only entities that are named in the text. No guessing beyond the text. Entry:
"""


def call(prompt: str, max_tokens: int = 2048) -> dict:
    base = os.environ.get("GPUSTACK_BASE_URL", "https://gpustack.unibe.ch/v1")
    body = {"model": MODEL, "temperature": 0, "max_tokens": max_tokens,
            "chat_template_kwargs": {"enable_thinking": False},
            "response_format": {"type": "json_object"},
            "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request(base.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {os.environ['GPUSTACK_API_KEY']}",
                                          "Content-Type": "application/json"})
    for attempt in range(5):
        try:
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=600) as r:
                res = json.loads(r.read())
            text = res["choices"][0]["message"].get("content") or ""
            m = re.search(r"\{.*\}", text, re.S)
            return {"ok": True, "data": json.loads(m.group(0)) if m else None, "raw": None if m else text,
                    "finish": res["choices"][0].get("finish_reason"), "seconds": round(time.time() - t0, 1)}
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            if attempt == 4:
                return {"ok": False, "error": str(e)}
            time.sleep(20 * (attempt + 1))
        except json.JSONDecodeError as e:
            return {"ok": False, "error": f"json: {e}", "raw": text}
    return {"ok": False}


RECK = {"kalendas": "kal", "nonas": "non", "idus": "id"}


def date_fields(d: dict) -> dict:
    """LLM fields -> the same structure segment.py uses, plus ISO and pontificate check computed here."""
    r = d.get("reckoning")
    out = {"place": d.get("place"), "year": d.get("year"), "month": d.get("month"), "pont": d.get("pontificate_year"),
           "day_ord": d.get("day_number"), "reckoning": RECK.get(r) if r in RECK else None,
           "ut_supra": bool(d.get("ut_supra")), "confidence": d.get("confidence"), "source": MODEL}
    if r == "day_of_month" and out["year"] and out["month"] and out["day_ord"]:
        out["iso"] = f"{out['year']}-{int(out['month']):02d}-{int(out['day_ord']):02d}"
    else:
        try:
            out["iso"] = to_iso({**out, "year": int(out["year"]) if out["year"] else None,
                                 "month": int(out["month"]) if out["month"] else None,
                                 "day_ord": int(out["day_ord"]) if out["day_ord"] else None})
        except (TypeError, ValueError):
            out["iso"] = None
    try:
        out["check"] = check({**out, "pont": int(out["pont"]) if out["pont"] else None})
    except (TypeError, ValueError):
        out["check"] = None
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=["date", "ner"], required=True)
    ap.add_argument("--sample", type=int, help="random entries (seeded) instead of all")
    ap.add_argument("--vols", type=int, nargs="*")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--ids", type=Path, help="JSON list of entry ids to (re)run")
    ap.add_argument("--out", help="output subdirectory instead of the task name")
    args = ap.parse_args()
    entries = []
    for f in sorted(SITE.glob("entries_vol*.json")):
        es = json.loads(f.read_text())
        if args.vols and es and es[0]["vol"] not in args.vols:
            continue
        entries += es
    if args.task == "date":
        entries = [e for e in entries if e.get("clause")]
    else:
        entries = [e for e in entries if 6 <= e["lines"] <= 120]
    if args.ids:
        want = set(json.loads(args.ids.read_text()))
        entries = [e for e in entries if e["id"] in want]
    if args.sample:
        entries = random.Random(1440).sample(entries, min(args.sample, len(entries)))
    out = ROOT / "data/llm" / (args.out or args.task)
    out.mkdir(parents=True, exist_ok=True)
    def inp(e):
        return e["clause"] if args.task == "date" else e["text"]

    def done(e):
        f = out / f"{e['id']}.json"
        if not f.exists():
            return False
        r = json.loads(f.read_text())
        return r.get("ok") and r.get("input") == inp(e) and r.get("prompt") == PROMPT_VERSION[args.task]

    todo = [e for e in entries if not done(e)]
    print(f"{len(todo)} of {len(entries)} to do", flush=True)

    def work(e):
        if args.task == "date":
            res = call(DATE_PROMPT + e["clause"], 512)
        else:
            res = call(NER_PROMPT + e["text"], 4096)
        res["id"] = e["id"]
        res["input"] = inp(e)
        res["prompt"] = PROMPT_VERSION[args.task]
        (out / f"{e['id']}.json").write_text(json.dumps(res, ensure_ascii=False))
        return e["id"], res.get("ok"), res.get("seconds")

    with cf.ThreadPoolExecutor(args.workers) as ex:
        for i, (eid, ok, s) in enumerate(ex.map(work, todo), 1):
            if i % 25 == 0 or not ok:
                print(i, eid, ok, s, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
