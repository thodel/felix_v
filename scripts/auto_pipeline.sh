#!/bin/bash
# Felix V: unattended chain after the UBELIX reader run.
#   wait for the UBELIX readers (resubmit after the maintenance if pages are missing)
#   -> copy readings -> 8-reader combination -> regests v2 with entities (GPUStack)
#   -> entity linking (corpus, kf, SSRQ, HLS, Wikidata) -> site build -> commit + push
# Start:  nohup caffeinate -dimsu scripts/auto_pipeline.sh >> data/auto/pipeline.log 2>&1 &
# Needs: VPN (UBELIX, GPUStack), ~/.gpustack.env, ~/.claude.json (MCP endpoints).
set -u
cd "$(dirname "$0")/.."
REPO=$PWD
PY=$REPO/.venv/bin/python
R=/storage/research/wbkolleg_dh_1/Textrecognition_Training/datasets/felix-v
JOB=${FELIX_JOB:-22282879}
READERS="kraken-catmus_medieval kraken-tridis_v2 kraken-cremma_medieval kraken-medieval_latin_french_expanded trocr-medieval-escriptmask trocr-catmus-base trocr-catmus-cursiva"
PAGES=2699
STATE=$REPO/data/auto
mkdir -p "$STATE"
log() { echo "$(date '+%Y-%m-%d %H:%M:%S %Z') $*"; echo "$*" > "$STATE/status.txt"; }
ub() { ssh -o ConnectTimeout=30 -o BatchMode=yes ubelix "$@" 2>/dev/null | grep -v "quantum\|store now\|upgraded"; }
fail() { log "FAILED: $*"; exit 1; }

log "start; waiting for UBELIX job $JOB"
resubmits=0
while true; do
  running=$(ub "squeue -h -j $JOB 2>/dev/null | wc -l" | tail -1)
  if [ -z "$running" ]; then log "UBELIX not reachable (VPN?), retry in 10 min"; sleep 600; continue; fi
  if [ "$running" != "0" ]; then sleep 600; continue; fi
  counts=$(ub "cd $R/readings && for r in $READERS; do echo \$r \$(ls \$r 2>/dev/null | grep -c '\.json\$'); done")
  missing=$(echo "$counts" | awk -v n=$PAGES '$2 < n {print $1}' | tr '\n' ' ')
  log "job $JOB finished; pages per reader: $(echo $counts | tr '\n' ' ')"
  [ -z "$missing" ] && break
  if [ $resubmits -ge 2 ]; then log "still missing after $resubmits resubmits: $missing; going on with what is there"; break; fi
  # UBELIX maintenance 16.11.2026 06:30-17:00 CET: anything resubmitted starts after it
  out=$(ub "cd $R && sbatch --begin=2026-11-16T17:30:00 readers.sbatch")
  newjob=$(echo "$out" | grep -o 'Submitted batch job [0-9]*' | grep -o '[0-9]*$')
  [ -z "$newjob" ] && fail "resubmit failed: $out"
  resubmits=$((resubmits + 1)); JOB=$newjob
  log "missing pages for: $missing; resubmitted as job $JOB (starts after the maintenance)"
done

log "copying readings from UBELIX"
mkdir -p data/lines
for r in $READERS; do
  rsync -a --exclude '*.tmp' "ubelix:$R/readings/$r/" "data/lines/$r/" 2>/dev/null || fail "rsync $r"
done
log "readings here: $(for r in $READERS; do printf '%s=%s ' $r $(ls data/lines/$r 2>/dev/null | wc -l | tr -d ' '); done)"

while pgrep -f "scripts/regest.py" >/dev/null; do log "waiting for the running regest pass"; sleep 300; done

log "8-reader combination"
"$PY" scripts/combine_multi.py > "$STATE/combine.log" 2>&1 || fail "combine_multi (see data/auto/combine.log)"
tail -8 "$STATE/combine.log"

log "regests v2 with entities (GPUStack, several hours)"
set -a; . "$HOME/.gpustack.env"; set +a
for attempt in 1 2 3; do
  "$PY" scripts/regest.py --workers 3 > "$STATE/regest.log" 2>&1 && break
  log "regest pass $attempt ended with an error; retrying in 10 min"; sleep 600
done
left=$("$PY" -c 'import json,glob; fs=glob.glob("data/regests/*.json"); v2=sum(1 for f in fs if json.load(open(f)).get("prompt")=="regest_v2"); print(f"{v2} of {len(fs)} regests on regest_v2")')
log "regests done: $left"

log "entity linking"
"$PY" scripts/nel.py > "$STATE/nel.log" 2>&1 || fail "nel (see data/auto/nel.log)"
tail -30 "$STATE/nel.log"

log "site build"
"$PY" scripts/build_site.py > "$STATE/build.log" 2>&1 || fail "build_site (see data/auto/build.log)"

log "commit and push"
git add docs data/regests data/nel/entities.json data/nel/report.json data/combine_report.json data/llm/date 2>/dev/null
git commit -q -m "Automatic update: 8 line readings combined, regests v2 with entities, entity linking

Run by scripts/auto_pipeline.sh after UBELIX job(s) for the readers finished.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" || log "nothing to commit"
for attempt in 1 2 3; do git push -q && break; sleep 120; done || fail "git push"
log "DONE: pushed $(git log --oneline -1)"
