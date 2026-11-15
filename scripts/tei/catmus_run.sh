#!/usr/bin/env bash
# CATMuS Medieval (kraken) on the Transkribus lines of every Felix V page, via the ATR gateway.
# Runs on tei as dh. Chunks of 50 pages; after each chunk only the line readings are kept
# (out/<doc>_p<page>.json) and the page images are deleted: / has little room.
set -u
PY=/home/dh/agentic_historian/.venv/bin/python3
PIPE=/home/dh/agentic_historian/agentic_historian/ruemlang/pipeline.py
VT=/home/dh/agentic_historian/agentic_historian/data/vlm_test
BASE=$HOME/felix-v-catmus
OUT=$BASE/out
mkdir -p "$OUT"
LOG=$BASE/status.log
# docId:pages, in volume order 1..8
DOCS="249230:316 249232:315 249233:315 249354:338 249355:340 249356:340 249357:349 249231:386"
CHUNK=50
for dp in $DOCS; do
  doc=${dp%%:*}; n=${dp##*:}
  for ((a=1; a<=n; a+=CHUNK)); do
    b=$((a+CHUNK-1)); ((b>n)) && b=$n
    have=$(ls "$OUT" | grep -c "^${doc}_p" || true)
    done_chunk=1
    for ((p=a; p<=b; p++)); do [ -f "$OUT/${doc}_p$(printf %04d $p).json" ] || { done_chunk=0; break; }; done
    ((done_chunk)) && continue
    free=$(df --output=avail -BG / | tail -1 | tr -dc 0-9)
    if (( free < 3 )); then echo "$(date -Is) STOP: only ${free}G free on /" >> "$LOG"; exit 1; fi
    run="felix-v-catmus-${doc}-${a}"
    echo "$(date -Is) doc $doc pages $a-$b start (${have} done, ${free}G free)" >> "$LOG"
    "$PY" "$PIPE" eval --out "$VT/$run" --collection 53095 --doc "$doc" --on-page-lines --pages "$a-$b" \
      --extra-model kraken-catmus_medieval --primary D --line-model none --trocr-model none --page-model none --no-llm \
      > "$BASE/$run.log" 2>&1
    rc=$?
    "$PY" - "$VT/$run/eval/pages" "$OUT" <<'PYEOF'
import json, pathlib, sys
src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
for d in sorted(src.glob("doc*_p*")):
    f = d / "rec_kraken-catmus_medieval.json"
    if not f.exists():
        continue
    r = json.loads(f.read_text())
    lines = [{"order": l.get("order"), "text": l.get("text"), "conf": round(l.get("confidence") or 0, 3),
              "bbox": [round(v) for v in (l.get("bbox") or [])]} for l in r.get("lines") or []]
    doc, page = d.name.split("_p")
    (out / f"{doc[3:]}_p{page}.json").write_text(json.dumps(
        {"model": r.get("model"), "scale": r.get("scale_to_original"), "lines_given": r.get("lines_given"),
         "segmented_by": r.get("segmented_by"), "lines": lines}, ensure_ascii=False))
PYEOF
    find "$VT/$run" -name 'image*.jpg' -delete
    echo "$(date -Is) doc $doc pages $a-$b rc=$rc, $(ls "$OUT" | grep -c "^${doc}_p") pages of $doc done" >> "$LOG"
  done
done
echo "$(date -Is) ALL DONE: $(ls "$OUT" | wc -l) pages" >> "$LOG"
