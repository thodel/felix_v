#!/usr/bin/env python3
"""Combined reading from up to 8 line readings (ROVER-style word vote), no language model.

Readers per Transkribus line (aligned by line id, so exactly the same line):
  H      CITlab HTR from Transkribus (data/export)
  …      every folder in data/lines/<reader>/<docId>_p<NNNN>.json (UBELIX: kraken, TrOCR)

Per line:
  1. Every reading is tokenised; tokens are compared on a key (lower case, u/v, i/j, no diacritics
     or abbreviation signs).
  2. The skeleton is the reading with the highest summed similarity to all others (medoid).
  3. Every other reading is aligned to the skeleton word by word (difflib on keys); at each skeleton
     position the readers vote for a key (a reader that has no word there votes for "nothing").
  4. Votes are weighted by the reader's weight = its mean similarity to the other readers over the
     whole volume (a reader that reads this hand badly counts less, computed, not set by hand).
  5. The winning key is written in the surface form of the best-ranked EXPANDING reader that has it
     (H, kraken TRIDIS, kraken Latin/French expanded), else of any reader; «nothing» wins only with a
     clear majority (> 60 % of the weight), so words are dropped only when most readers lack them.
  6. Per word the vote share is kept; per line the mean share is the line's agreement.

Output: data/combined/<docId>_p<NNNN>.json
  {"version", "readers": [...], "lines": [{"i", "text", "agree", "low": [[start,end],…]}]}
  low = words whose winning share is < 0.5 (shown as uncertain in the viewer).
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXP = ROOT / "data/export"
LINES = ROOT / "data/lines"
OUT = ROOT / "data/combined"
VERSION = "combine_multi_v2"
# surface-form preference: readers that expand abbreviations first
EXPANDING = ["H", "kraken-tridis_v2", "kraken-medieval_latin_french_expanded"]


def key(tok: str) -> str:
    s = unicodedata.normalize("NFKD", tok)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("j", "i").replace("v", "u").replace("y", "i")
    return re.sub(r"[^a-z]", "", s)


def toks(text: str) -> list[str]:
    return [t for t in (text or "").split() if key(t)]


def sim(a: list[str], b: list[str]) -> float:
    ka, kb = " ".join(key(t) for t in a), " ".join(key(t) for t in b)
    if not ka or not kb:
        return 0.0
    return difflib.SequenceMatcher(None, ka, kb, autojunk=False).ratio()


def readers_for_page(vol: dict, page: dict, names: list[str]) -> dict:
    """reader -> {line id: text}"""
    out = {"H": {l["id"]: l["text"] for r in page["regions"] for l in r["lines"]}}
    stem = f"{vol['docId']}_p{page['n']:04d}"
    for n in names:
        f = LINES / n / f"{stem}.json"
        if f.exists():
            out[n] = {l["id"]: l.get("text") or "" for l in json.loads(f.read_text())["lines"]}
    return out


def combine_line(readings: dict[str, list[str]], weight: dict[str, float]) -> dict:
    names = [n for n, t in readings.items() if t]
    if not names:
        return {"text": "", "agree": 0.0, "low": []}
    if len(names) == 1:
        return {"text": " ".join(readings[names[0]]), "agree": 0.0, "low": []}
    # medoid as skeleton
    score = {n: sum(sim(readings[n], readings[m]) * weight.get(m, 1) for m in names if m != n) for n in names}
    piv = max(names, key=lambda n: score[n])
    P = readings[piv]
    pk = [key(t) for t in P]
    votes = [defaultdict(float) for _ in P]          # position -> key -> weight
    gaps = defaultdict(lambda: defaultdict(float))   # gap before position i -> key sequence -> weight
    gap_forms = defaultdict(dict)                    # (gap, key sequence) -> surface (first expanding reader wins)
    forms = [defaultdict(dict) for _ in P]           # position -> key -> reader -> surface
    total = sum(weight.get(n, 1) for n in names)
    for n in names:
        w = weight.get(n, 1)
        R = readings[n]
        if n == piv:
            for i, t in enumerate(P):
                votes[i][pk[i]] += w
                forms[i][pk[i]][n] = t
            continue
        rk = [key(t) for t in R]
        voted = set()

        def gap_vote(at, j1, j2):
            ks = tuple(rk[j1:j2])
            gaps[at][ks] += w
            cur = gap_forms[(at, ks)]
            if not cur or (n in EXPANDING and cur.get("rank", 99) > EXPANDING.index(n)):
                gap_forms[(at, ks)] = {"text": R[j1:j2], "rank": EXPANDING.index(n) if n in EXPANDING else 99}
        for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, pk, rk, autojunk=False).get_opcodes():
            if op == "equal" or (op == "replace" and i2 - i1 == j2 - j1):
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    votes[i][rk[j]] += w
                    forms[i][rk[j]][n] = R[j]
                    voted.add(i)
            elif op == "replace":  # unequal block: the reader's words, joined, against the skeleton's
                joined = "".join(rk[j1:j2])
                for i in range(i1, i2):
                    if pk[i] and pk[i] in joined:
                        votes[i][pk[i]] += w
                        voted.add(i)
                if j2 - j1 > i2 - i1:  # more words than the skeleton has here: the surplus is an insertion
                    gap_vote(i1, j1, j1 + (j2 - j1) - (i2 - i1))
            elif op == "insert":
                gap_vote(i1, j1, j2)
        for i in range(len(P)):
            if i not in voted:
                votes[i][""] += w  # this reader has nothing here
    out, low, pos, shares = [], [], 0, []

    def put(surf, share):
        nonlocal pos
        if out:
            pos += 1
        if share < 0.5:
            low.append([pos, pos + len(surf)])
        out.append(surf)
        pos += len(surf)

    for i in range(len(P) + 1):
        if gaps.get(i):  # words the skeleton lacks but most readers have
            ks, gw = max(gaps[i].items(), key=lambda kv: kv[1])
            if gw / total > 0.5:
                for tkn in gap_forms[(i, ks)]["text"]:
                    put(tkn, gw / total)
                    shares.append(gw / total)
        if i == len(P):
            break
        ranked = sorted(votes[i].items(), key=lambda kv: -kv[1])
        best_k, best_w = ranked[0]
        if best_k == "" and best_w / total <= 0.6:
            best_k, best_w = next(((k, v) for k, v in ranked if k), (pk[i], 0))
        if best_k == "":
            continue
        cand = forms[i].get(best_k, {})
        surf = next((cand[r] for r in EXPANDING if r in cand), None) or (next(iter(cand.values())) if cand else P[i])
        share = best_w / total
        shares.append(share)
        put(surf, share)
    return {"text": " ".join(out), "agree": round(sum(shares) / len(shares), 3) if shares else 0.0, "low": low,
            "pivot": piv}


def reader_weights(vol: dict, names: list[str], sample_pages: int = 40) -> dict:
    """Mean similarity of each reader to the others on a sample of pages of this volume."""
    acc, cnt = defaultdict(float), defaultdict(int)
    pages = vol["pages"][:: max(1, len(vol["pages"]) // sample_pages)]
    for p in pages:
        rd = readers_for_page(vol, p, names)
        for lid in rd["H"]:
            have = {n: toks(rd[n].get(lid, "")) for n in rd}
            have = {n: t for n, t in have.items() if t}
            if len(have) < 3:
                continue
            for n in have:
                acc[n] += sum(sim(have[n], have[m]) for m in have if m != n) / (len(have) - 1)
                cnt[n] += 1
    w = {n: acc[n] / cnt[n] for n in cnt}
    # a reader far below the others (reads this hand badly) gets little say
    return {n: round(max(0.05, v) ** 2, 3) for n, v in w.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vols", type=int, nargs="*")
    ap.add_argument("--pages", help="vol:page,…")
    ap.add_argument("--min-readers", type=int, default=5, help="pages with fewer readers are left alone")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    names = sorted(p.name for p in LINES.iterdir() if p.is_dir()) if LINES.exists() else []
    want = {tuple(map(int, x.split(":"))) for x in args.pages.split(",")} if args.pages else None
    report = {}
    for f in sorted(EXP.glob("vol*.json"), key=lambda p: int(re.sub(r"\D", "", p.stem))):
        vol = json.loads(f.read_text())
        if args.vols and vol["vol"] not in args.vols:
            continue
        weight = reader_weights(vol, names)
        weight.setdefault("H", 1.0)
        done = 0
        for p in vol["pages"]:
            if want and (vol["vol"], p["n"]) not in want:
                continue
            rd = readers_for_page(vol, p, names)
            if len(rd) < args.min_readers:
                continue
            lines, i = [], 0
            for r in p["regions"]:
                for l in r["lines"]:
                    readings = {n: toks(rd[n].get(l["id"], "")) for n in rd}
                    if l["text"].strip():
                        c = combine_line(readings, weight)
                        lines.append({"i": i, **c})
                    i += 1
            (OUT / f"{vol['docId']}_p{p['n']:04d}.json").write_text(json.dumps(
                {"version": VERSION, "readers": sorted(rd), "weights": {n: weight.get(n) for n in rd}, "lines": lines},
                ensure_ascii=False))
            done += 1
        report[vol["vol"]] = {"pages": done, "weights": weight}
        print(f"vol {vol['vol']}: {done} pages, weights {weight}", flush=True)
    (ROOT / "data/combine_report.json").write_text(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
