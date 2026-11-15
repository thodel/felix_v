#!/bin/bash
# Fetch the reader models onto the research storage (run on the UBELIX login node; compute nodes need no internet).
set -u
R=/storage/research/wbkolleg_dh_1/Textrecognition_Training/datasets/felix-v
mkdir -p "$R/models"
# kraken models: name zenodo-record-id
while read -r name rec; do
  [ -n "$(ls "$R/models/$name".* 2>/dev/null)" ] && { echo "have $name"; continue; }
  url=$(curl -sf "https://zenodo.org/api/records/$rec" | python3 -c '
import json,sys
fs=json.load(sys.stdin)["files"]
fs=[f for f in fs if f["key"].endswith((".mlmodel",".safetensors"))]
print(fs[0]["links"]["self"] + " " + fs[0]["key"]) if fs else print("")')
  set -- $url
  [ -z "${1:-}" ] && { echo "NO MODEL FILE in record $rec ($name)"; continue; }
  ext=${2##*.}
  curl -sfL -o "$R/models/$name.$ext" "$1" && echo "got $name.$ext ($2)"
done <<'LIST'
kraken-catmus_medieval 15030337
kraken-tridis_v2 13862096
kraken-cremma_medieval 7631619
kraken-medieval_latin_french_expanded 7516057
LIST
# TrOCR models into the shared HF cache
export HF_HOME=/storage/research/wbkolleg_dh_1/Textrecognition_Training/hf_hub
apptainer exec --bind /storage/research:/storage/research --env HF_HOME="$HF_HOME" "$HOME/ubelix/vlm-train.sif" \
  /opt/vlm-train/bin/python -c '
from huggingface_hub import snapshot_download
for r in ["dh-unibe/trocr-medieval-escriptmask", "medieval-data/trocr-medieval-base", "medieval-data/trocr-medieval-cursiva"]:
    print(r, snapshot_download(r))'
ls -la "$R/models"
