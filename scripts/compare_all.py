#!/usr/bin/env python3
"""Reading test on the sample of page halves: every reader against every other.

Readers per page half (data/readings/sample.json, 50 openings = 100 halves):
  CITlab            Transkribus HTR, main-text lines of the half (data/export)
  vote              8-reader majority reading of the same lines (data/combined)
  <model>           page readings in data/readings/<run>/<model>/<stem>.txt (qwen3.8, Gemini …)

There is no ground truth. The matrix is pairwise disagreement (CER of one reading measured
against the other, normalised: lower case, u/v, i/j, no punctuation or diacritics), not accuracy.
What it can show: which readers agree with each other, and how often a reader comes back empty,
cut off or looping. If ground-truth files appear in data/readings/gt/<stem>.txt they are scored too.

Output: data/readings/compare_all.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from statistics import median

sys.path.insert(0, str(Path(__file__).resolve().parent))
from read_vlm import gutter_x  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXP = ROOT / "data/export"
RD = ROOT / "data/readings"
COMB = ROOT / "data/combined"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("j", "i").replace("v", "u").replace("y", "i").replace("ae", "e")
    s = re.sub(r"[^a-z0-9\s]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def lev(a: str, b: str) -> int:
    from rapidfuzz.distance import Levenshtein
    return Levenshtein.distance(a, b)


def cer(hyp: str, ref: str) -> float | None:
    r, h = norm(ref), norm(hyp)
    if not r:
        return None
    return round(lev(h, r) / len(r), 4)


def half_lines(page: dict, side: str, doc_id: int) -> tuple[str, str]:
    """(CITlab, vote) text of the main-text lines on one half of the opening."""
    g = gutter_x(page)
    comb_f = COMB / f"{doc_id}_p{page['n']:04d}.json"
    comb = {l["i"]: l["text"] for l in json.loads(comb_f.read_text())["lines"]} if comb_f.exists() else {}
    h, v, i = [], [], 0
    for r in page["regions"]:
        lines = [l for l in r["lines"]]
        txt = [l for l in lines if l["text"].strip()]
        avg = sum(len(l["text"]) for l in txt) / max(1, len(txt))
        marg = len(txt) <= 4 and avg < 28
        for l in lines:
            if not marg and l["text"].strip() and l.get("box") and ((l["box"][0] + l["box"][2]) / 2 < g) == (side == "L"):
                h.append(l["text"].strip())
                v.append(comb.get(i, l["text"]).strip())
            i += 1
    return "\n".join(h), ("\n".join(v) if comb else "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", default=["sample-v1", "gemini-v1"])
    args = ap.parse_args()
    sample = json.loads((RD / "sample.json").read_text())
    vols = {}
    halves = []
    for item in sample:
        d = vols.setdefault(item["vol"], json.loads((EXP / f"vol{item['vol']}.json").read_text()))
        page = next(p for p in d["pages"] if p["n"] == item["page"])
        for side in "LR":
            stem = f"vol{item['vol']}_{item['page']:04d}_{side}"
            cit, vote = half_lines(page, side, d["docId"])
            rd = {"CITlab": cit}
            if vote:
                rd["vote"] = vote
            meta = {}
            for run in args.runs:
                for mdir in sorted((RD / run).glob("*")) if (RD / run).exists() else []:
                    f = mdir / f"{stem}.txt"
                    if mdir.is_dir() and f.exists():
                        rd[mdir.name] = f.read_text()
                        mf = mdir / f"{stem}.json"
                        meta[mdir.name] = json.loads(mf.read_text()) if mf.exists() else {}
            gt_f = RD / "gt" / f"{stem}.txt"
            halves.append({"stem": stem, "vol": item["vol"], "page": item["page"], "side": side, "readers": rd,
                           "meta": meta, "gt": gt_f.read_text() if gt_f.exists() else None})
    names = sorted({n for h in halves for n in h["readers"]}, key=lambda n: (n not in ("CITlab", "vote"), n))
    # pairwise disagreement
    matrix = {}
    for a in names:
        for b in names:
            if a == b:
                continue
            vals = [cer(h["readers"][a], h["readers"][b]) for h in halves
                    if norm(h["readers"].get(a, "")) and norm(h["readers"].get(b, ""))]
            vals = [x for x in vals if x is not None]
            if vals:
                matrix.setdefault(a, {})[b] = {"median": round(median(vals), 3), "n": len(vals)}
    per = {}
    for n in names:
        have = [h for h in halves if n in h["readers"]]
        texts = [h["readers"][n] for h in have]
        empty = sum(1 for t in texts if not norm(t))
        loops = 0
        for t in texts:
            ls = [l.strip() for l in t.splitlines() if l.strip()]
            if ls and sum(1 for i, l in enumerate(ls) if l in ls[:i]) / len(ls) > 0.1:
                loops += 1
        mt = [h["meta"].get(n) or {} for h in have]
        cut = sum(1 for m in mt if m.get("finish") == "length" or m.get("truncated_by_model") or m.get("truncated"))
        secs = [m["seconds"] if "seconds" in m else m["timing_ms"] / 1000 for m in mt if "seconds" in m or m.get("timing_ms")]
        ratio = [len(norm(h["readers"][n])) / max(1, len(norm(h["readers"]["CITlab"]))) for h in have if norm(h["readers"]["CITlab"])]
        gt = [cer(h["readers"][n], h["gt"]) for h in have if h["gt"]]
        per[n] = {"halves": len(have), "empty": empty, "looping": loops, "cut_off": cut,
                  "median_len_vs_citlab": round(median(ratio), 2) if ratio else None,
                  "median_seconds": round(median(secs), 1) if secs else None,
                  **({"median_cer_vs_gt": round(median([g for g in gt if g is not None]), 3)} if gt else {})}
    out = {"note": "No ground truth: values are disagreement between readers, not accuracy.",
           "readers": names, "per_reader": per, "matrix": matrix,
           "halves": [{k: h[k] for k in ("stem", "vol", "page", "side", "readers")} for h in halves]}
    (RD / "compare_all.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    w = max(len(n) for n in names)
    print(" " * (w + 2) + "  ".join(f"{n[:10]:>10}" for n in names))
    for a in names:
        print(f"{a:<{w}}  " + "  ".join(f"{(matrix.get(a, {}).get(b, {}) or {}).get('median', ''):>10}" if a != b else f"{'—':>10}" for b in names))
    print()
    for n, p in per.items():
        print(n, p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
