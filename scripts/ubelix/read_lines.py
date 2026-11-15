#!/usr/bin/env python3
"""Read every Transkribus line of the Felix V registers with one HTR model (UBELIX, inside a container).

  --engine kraken --model <file.mlmodel|.safetensors>   kraken recognition on the PageXML baselines/polygons
  --engine trocr  --model <hf repo>                       TrOCR on line crops (bbox; --mask whites out the
                                                          area outside the line polygon)

Input  (ROOT = the dataset dir): manifest.json, pagexml/<stem>.xml, images/<stem>.jpg (full size)
Output: ROOT/readings/<name>/<stem>.json = {"model", "lines": [{"id", "text", "conf"}]}
Pages are split across array tasks with --shard i --shards n; finished pages are skipped (resumable).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw

NS = {"p": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15"}
Image.MAX_IMAGE_PIXELS = None


def pts(s: str) -> list[tuple[int, int]]:
    out = []
    for tok in (s or "").split():
        if "," in tok:
            x, y = tok.split(",", 1)
            out.append((int(float(x)), int(float(y))))
    return out


def page_lines(xml_path: Path) -> list[dict]:
    root = ET.parse(xml_path).getroot()
    lines = []
    for tl in root.iter(f"{{{NS['p']}}}TextLine"):
        c, b = tl.find("p:Coords", NS), tl.find("p:Baseline", NS)
        poly = pts(c.get("points")) if c is not None else []
        base = pts(b.get("points")) if b is not None else []
        if len(poly) >= 3:
            lines.append({"id": tl.get("id"), "poly": poly, "base": base})
    return lines


# ----------------------------------------------------------------------------------------- kraken
class KrakenReader:
    def __init__(self, model: str, device: str):
        from kraken.lib import models
        self.net = models.load_any(model, device=device)

    def read(self, im: Image.Image, lines: list[dict]) -> list[dict]:
        from kraken import rpred
        from kraken.containers import BaselineLine, Segmentation
        usable = [l for l in lines if len(l["base"]) >= 2]
        seg = Segmentation(type="baselines", imagename="page", text_direction="horizontal-lr", script_detection=False,
                           lines=[BaselineLine(id=l["id"], baseline=l["base"], boundary=l["poly"]) for l in usable],
                           regions={}, line_orders=[])
        out = {}
        for rec in rpred.rpred(self.net, im, seg):
            conf = sum(rec.confidences) / len(rec.confidences) if rec.confidences else None
            out[rec.id] = {"id": rec.id, "text": rec.prediction, "conf": round(conf, 3) if conf is not None else None}
        return [out.get(l["id"], {"id": l["id"], "text": "", "conf": None}) for l in lines]


# ------------------------------------------------------------------------------------------ TrOCR
class TrocrReader:
    def __init__(self, model: str, device: str, mask: bool, batch: int):
        import torch
        from transformers import TrOCRProcessor, VisionEncoderDecoderModel
        self.torch = torch
        self.proc = TrOCRProcessor.from_pretrained(model)
        self.model = VisionEncoderDecoderModel.from_pretrained(model).to(device).eval()
        if device.startswith("cuda"):
            self.model = self.model.half()
        self.device, self.mask, self.batch = device, mask, batch

    def crop(self, im: Image.Image, poly) -> Image.Image:
        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
        box = (max(0, min(xs)), max(0, min(ys)), min(im.width, max(xs)), min(im.height, max(ys)))
        c = im.crop(box).convert("RGB")
        if self.mask:
            m = Image.new("L", c.size, 0)
            ImageDraw.Draw(m).polygon([(x - box[0], y - box[1]) for x, y in poly], fill=255)
            white = Image.new("RGB", c.size, (255, 255, 255))
            c = Image.composite(c, white, m)
        return c

    def read(self, im: Image.Image, lines: list[dict]) -> list[dict]:
        out = []
        for k in range(0, len(lines), self.batch):
            chunk = lines[k:k + self.batch]
            crops = [self.crop(im, l["poly"]) for l in chunk]
            pv = self.proc(images=crops, return_tensors="pt").pixel_values.to(self.device)
            if self.device.startswith("cuda"):
                pv = pv.half()
            with self.torch.no_grad():
                gen = self.model.generate(pv, max_new_tokens=160, num_beams=1, output_scores=True,
                                          return_dict_in_generate=True)
            texts = self.proc.batch_decode(gen.sequences, skip_special_tokens=True)
            # mean token probability as a rough confidence
            scores = self.model.compute_transition_scores(gen.sequences, gen.scores, normalize_logits=True)
            for l, t, sc in zip(chunk, texts, scores):
                valid = sc[sc > -1e4]
                conf = float(valid.exp().mean()) if len(valid) else None
                out.append({"id": l["id"], "text": t.strip(), "conf": round(conf, 3) if conf is not None else None})
        return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--engine", choices=["kraken", "trocr"], required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--name", required=True, help="output folder name, e.g. kraken-tridis_v2")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--stems", nargs="*")
    ap.add_argument("--mask", action="store_true")
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--device", default="cuda:0")
    args = ap.parse_args()

    man = json.loads((args.root / "manifest.json").read_text())
    stems = [m["stem"] for m in man]
    if args.stems:
        stems = [s for s in stems if s in set(args.stems)]
    stems = stems[args.shard::args.shards][: args.limit]
    out = args.root / "readings" / args.name
    out.mkdir(parents=True, exist_ok=True)
    todo = [s for s in stems if not (out / f"{s}.json").exists()]
    print(f"{args.name}: {len(todo)} of {len(stems)} pages to read (shard {args.shard}/{args.shards})", flush=True)
    if not todo:
        return 0
    reader = (KrakenReader(args.model, args.device) if args.engine == "kraken"
              else TrocrReader(args.model, args.device, args.mask, args.batch))
    t0 = time.time()
    for i, s in enumerate(todo, 1):
        img_f = args.root / "images" / f"{s}.jpg"
        if not img_f.exists():
            print(f"{s}: no image", flush=True)
            continue
        lines = page_lines(args.root / "pagexml" / f"{s}.xml")
        im = Image.open(img_f)
        im.load()
        try:
            res = reader.read(im, lines)
        except Exception as e:  # noqa: BLE001 — one bad page must not end the shard
            print(f"{s}: ERROR {type(e).__name__}: {e}", flush=True)
            continue
        tmp = out / f"{s}.tmp"
        tmp.write_text(json.dumps({"model": args.model, "engine": args.engine, "mask": args.mask, "lines": res},
                                  ensure_ascii=False))
        tmp.replace(out / f"{s}.json")
        if i % 20 == 0 or i <= 2:
            print(f"{i}/{len(todo)} {s}: {len(res)} lines, {(time.time() - t0) / i:.1f} s/page", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
