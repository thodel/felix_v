#!/usr/bin/env python3
"""Compare page-half readings of the sample against the Transkribus HTR (CITlab) reading.

There is NO ground truth yet. The numbers are disagreement with CITlab, not accuracy:
a reader that is better than CITlab also disagrees with it. What the script can say
without ground truth is listed per reader:
  - cer_vs_htr       character error rate of the reader measured against CITlab (normalised text)
  - truncated        finish_reason == length (ran out of tokens: loops or runaway)
  - loop_lines       share of output lines that repeat an earlier line verbatim
  - len_ratio        output characters / CITlab characters (skipped text < 1, invented text > 1)

--export-crops writes the exact crops read (data/readings/crops/<stem>.jpg) so that
other readers (Gemini, Argon) can be run on identical input.

Ground truth: data/readings/gt/<stem>.txt, if present, is scored as well (cer_vs_gt).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from read_vlm import gutter_x, halves  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
EXP = ROOT / "data/export"
RD = ROOT / "data/readings"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("j", "i").replace("v", "u").replace("ae", "e").replace("y", "i")
    s = re.sub(r"[^a-z0-9\s]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def lev(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def cer(hyp: str, ref: str) -> float | None:
    r = norm(ref)
    return round(lev(norm(hyp), r) / len(r), 4) if r else None


def htr_half(page: dict, side: str) -> str:
    g = gutter_x(page)
    out = []
    for r in page["regions"]:
        lines = [l for l in r["lines"] if l["text"].strip() and l.get("box")]
        avg = sum(len(l["text"]) for l in lines) / max(1, len(lines))
        if len(lines) <= 4 and avg < 28:  # marginal notes: the VLM prompt leaves them out
            continue
        for l in lines:
            if ((l["box"][0] + l["box"][2]) / 2 < g) == (side == "L"):
                out.append(l["text"])
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="sample-v1")
    ap.add_argument("--export-crops", action="store_true")
    args = ap.parse_args()
    sample = json.loads((RD / "sample.json").read_text())
    vols = {}
    rows = []
    run_dir = RD / args.run
    readers = sorted(p.name for p in run_dir.iterdir() if p.is_dir()) if run_dir.exists() else []
    for item in sample:
        d = vols.setdefault(item["vol"], json.loads((EXP / f"vol{item['vol']}.json").read_text()))
        page = next(p for p in d["pages"] if p["n"] == item["page"])
        if args.export_crops:
            (RD / "crops").mkdir(parents=True, exist_ok=True)
            for side, jpg in halves(page, 3072, True).items():
                (RD / "crops" / f"vol{item['vol']}_{item['page']:04d}_{side}.jpg").write_bytes(jpg)
        for side in "LR":
            stem = f"vol{item['vol']}_{item['page']:04d}_{side}"
            ref = htr_half(page, side)
            gt_f = RD / "gt" / f"{stem}.txt"
            gt = gt_f.read_text() if gt_f.exists() else None
            row = {"stem": stem, "vol": item["vol"], "page": item["page"], "side": side, "htr_chars": len(norm(ref)),
                   "htr": ref, "readers": {}}
            if gt:
                row["htr_cer_vs_gt"] = cer(ref, gt)
            for m in readers:
                f = run_dir / m / f"{stem}.txt"
                if not f.exists():
                    continue
                text = f.read_text()
                meta = json.loads((run_dir / m / f"{stem}.json").read_text())
                ls = [l.strip() for l in text.splitlines() if l.strip()]
                rep = sum(1 for i, l in enumerate(ls) if l in ls[:i]) / max(1, len(ls))
                row["readers"][m] = {
                    "cer_vs_htr": cer(text, ref), "truncated": meta.get("finish") == "length",
                    "loop_lines": round(rep, 3), "len_ratio": round(len(norm(text)) / max(1, len(norm(ref))), 2),
                    "seconds": meta.get("seconds"), "text": text,
                    **({"cer_vs_gt": cer(text, gt)} if gt else {}),
                }
            rows.append(row)
    agg = {}
    for m in readers:
        rs = [r["readers"][m] for r in rows if m in r["readers"]]
        if not rs:
            continue
        c = sorted(x["cer_vs_htr"] for x in rs if x["cer_vs_htr"] is not None)
        agg[m] = {"halves": len(rs), "median_cer_vs_htr": c[len(c) // 2] if c else None,
                  "truncated": sum(x["truncated"] for x in rs), "with_loops": sum(x["loop_lines"] > 0.1 for x in rs),
                  "median_len_ratio": sorted(x["len_ratio"] for x in rs)[len(rs) // 2],
                  "median_seconds": sorted(x["seconds"] or 0 for x in rs)[len(rs) // 2]}
    out = {"run": args.run, "note": "No ground truth: cer_vs_htr is disagreement with the CITlab reading, not accuracy.",
           "aggregate": agg, "halves": rows}
    (RD / "compare.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print(json.dumps(agg, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
