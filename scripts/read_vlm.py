#!/usr/bin/env python3
"""Read a sample of register pages with a VLM through an OpenAI-compatible API.

Every Transkribus image is a microfilm opening (two pages). The script cuts it at
the gutter (from the PageXML text regions, falling back to the middle), scales
each half to --max-side and asks the model for a line-by-line transcription.

Output: data/readings/<run>/<model>/vol<V>_<page>_<L|R>.txt  (+ .json with usage)
The sample list is data/readings/sample.json (written by --make-sample).

GPUStack:  set -a; . ~/.gpustack.env; set +a   (GPUSTACK_API_KEY, GPUSTACK_BASE_URL)
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "data/export"
CACHE = ROOT / "data/cache/img"
PROMPT = ROOT / "prompts/felix_page_v1.md"


def gutter_x(page: dict) -> int:
    """x of the gap between left- and right-page text, from line boxes."""
    w = page["w"]
    xs = sorted((l["box"][0], l["box"][2]) for r in page["regions"] for l in r["lines"] if l.get("box"))
    best, best_gap = w // 2, 0
    lo, hi = int(w * 0.35), int(w * 0.65)
    covered = [0] * (hi - lo)
    for a, b in xs:
        for x in range(max(a, lo), min(b, hi)):
            covered[x - lo] += 1
    # widest run of zero coverage in the middle band
    run_start = None
    for i, c in enumerate(covered + [1]):
        if c == 0 and run_start is None:
            run_start = i
        elif c and run_start is not None:
            if i - run_start > best_gap:
                best_gap, best = i - run_start, lo + (run_start + i) // 2
            run_start = None
    return best


def image(page: dict) -> Image.Image:
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / f"{page['key']}.jpg"
    if not p.exists():
        with urllib.request.urlopen(f"https://files.transkribus.eu/Get?id={page['key']}&fileType=view", timeout=120) as r:
            p.write_bytes(r.read())
    return Image.open(p).convert("L")


def halves(page: dict, max_side: int, text_only: bool = False) -> dict[str, bytes]:
    img = image(page)
    sx = img.width / page["w"]
    g = int(gutter_x(page) * sx)
    out = {}
    boxes = [l["box"] for r in page["regions"] for l in r["lines"] if l.get("box")]
    for side, box in (("L", (0, 0, g, img.height)), ("R", (g, 0, img.width, img.height))):
        if text_only:
            mine = [b for b in boxes if ((b[0] + b[2]) / 2 * sx < g) == (side == "L")]
            if mine:
                m = int(60 * sx)
                box = (max(box[0], int(min(b[0] for b in mine) * sx) - m), max(0, int(min(b[1] for b in mine) * sx) - m),
                       min(box[2], int(max(b[2] for b in mine) * sx) + m), min(img.height, int(max(b[3] for b in mine) * sx) + m))
        h = img.crop(box)
        h.thumbnail((max_side, max_side))
        buf = io.BytesIO()
        h.save(buf, "JPEG", quality=88)
        out[side] = buf.getvalue()
    return out


def call(base: str, key: str, model: str, prompt: str, jpg: bytes, max_tokens: int, extra: dict) -> dict:
    body = {
        "model": model, "temperature": 0, "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(jpg).decode()}},
        ]}], **extra,
    }
    req = urllib.request.Request(base.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=900) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(30 * (attempt + 1))
                continue
            raise
    raise RuntimeError("unreachable")


def make_sample(n_per_vol: int, seed: int) -> list[dict]:
    rnd = random.Random(seed)
    sample = []
    for f in sorted(SITE.glob("vol*.json")):
        d = json.loads(f.read_text())
        # skip near-empty openings (covers, targets): need >= 30 lines
        cands = [p["n"] for p in d["pages"] if sum(len(r["lines"]) for r in p["regions"]) >= 30]
        for n in sorted(rnd.sample(cands, min(n_per_vol, len(cands)))):
            sample.append({"vol": d["vol"], "page": n})
    return sample


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--make-sample", type=int, metavar="N_PER_VOL")
    ap.add_argument("--run", default="sample-v1")
    ap.add_argument("--model", default="qwen3.8-27b")
    ap.add_argument("--max-side", type=int, default=2048)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--prompt", default="felix_page_v2.md")
    ap.add_argument("--text-crop", action="store_true", help="crop each half to its PageXML text block")
    ap.add_argument("--frequency-penalty", type=float, default=0.3)
    args = ap.parse_args()
    sample_file = ROOT / "data/readings/sample.json"
    if args.make_sample:
        sample_file.parent.mkdir(parents=True, exist_ok=True)
        s = make_sample(args.make_sample, 1440)
        sample_file.write_text(json.dumps(s, indent=1))
        print(f"{len(s)} openings -> {sample_file}")
        return 0
    base = os.environ.get("GPUSTACK_BASE_URL", "https://gpustack.unibe.ch/v1")
    key = os.environ["GPUSTACK_API_KEY"]
    extra = {"chat_template_kwargs": {"enable_thinking": False}} if args.model.startswith("qwen") else {}
    global PROMPT
    PROMPT = ROOT / "prompts" / args.prompt
    prompt = PROMPT.read_text()
    if args.frequency_penalty:
        extra["frequency_penalty"] = args.frequency_penalty
    out_dir = ROOT / "data/readings" / args.run / args.model
    out_dir.mkdir(parents=True, exist_ok=True)
    vols: dict[int, dict] = {}
    todo = json.loads(sample_file.read_text())[: args.limit]
    for item in todo:
        d = vols.setdefault(item["vol"], json.loads((SITE / f"vol{item['vol']}.json").read_text()))
        page = next(p for p in d["pages"] if p["n"] == item["page"])
        for side, jpg in halves(page, args.max_side, args.text_crop).items():
            stem = f"vol{item['vol']}_{item['page']:04d}_{side}"
            if (out_dir / f"{stem}.txt").exists():
                continue
            t0 = time.time()
            try:
                res = call(base, key, args.model, prompt, jpg, args.max_tokens, extra)
            except Exception as e:  # noqa: BLE001
                print(f"{stem}: ERROR {e}", flush=True)
                continue
            ch = res["choices"][0]
            text = ch["message"].get("content") or ""
            meta = {"finish": ch.get("finish_reason"), "usage": res.get("usage"), "seconds": round(time.time() - t0, 1),
                    "model": args.model, "max_side": args.max_side, "prompt": PROMPT.name, "text_crop": args.text_crop, "frequency_penalty": args.frequency_penalty}
            (out_dir / f"{stem}.json").write_text(json.dumps(meta))
            (out_dir / f"{stem}.txt").write_text(text)
            print(f"{stem}: {len(text)} chars, {meta['seconds']} s, finish={meta['finish']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
