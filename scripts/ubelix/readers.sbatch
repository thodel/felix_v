#!/bin/bash
# Felix V: read every Transkribus line with 7 HTR models (4 kraken, 3 TrOCR), 3 shards each = 21 array tasks.
# Resumable: finished pages are skipped, so a preempted or deadline-cut task is simply submitted again.
# UBELIX maintenance 16.11.2026 06:30-17:00 CET: submit with --deadline before it (see submit line in README).
#SBATCH --job-name=felixv-read
#SBATCH --account=gratis
#SBATCH --partition=gpu-invest
#SBATCH --qos=job_gpu_preemptable
#SBATCH --gres=gpu:rtx3090:1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=2:30:00
#SBATCH --array=0-20%12
#SBATCH --requeue
#SBATCH --output=/storage/homefs/%u/ubelix/logs/%x-%A_%a.out
set -u
R=/storage/research/wbkolleg_dh_1/Textrecognition_Training/datasets/felix-v
HF=/storage/research/wbkolleg_dh_1/Textrecognition_Training/hf_hub
SHARDS=3
# engine|model|name|sif|extra
READERS=(
  "kraken|$R/models/kraken-catmus_medieval.mlmodel|kraken-catmus_medieval|kraken-train|"
  "kraken|$R/models/kraken-tridis_v2.mlmodel|kraken-tridis_v2|kraken-train|"
  "kraken|$R/models/kraken-cremma_medieval.mlmodel|kraken-cremma_medieval|kraken-train|"
  "kraken|$R/models/kraken-medieval_latin_french_expanded.mlmodel|kraken-medieval_latin_french_expanded|kraken-train|"
  "trocr|dh-unibe/trocr-medieval-escriptmask|trocr-medieval-escriptmask|vlm-train|--mask"
  "trocr|medieval-data/trocr-medieval-base|trocr-catmus-base|vlm-train|"
  "trocr|medieval-data/trocr-medieval-cursiva|trocr-catmus-cursiva|vlm-train|"
)
i=${SLURM_ARRAY_TASK_ID}
IFS='|' read -r ENGINE MODEL NAME VENV EXTRA <<< "${READERS[$((i / SHARDS))]}"
SHARD=$((i % SHARDS))
echo "== $(hostname) task $i: $NAME shard $SHARD/$SHARDS"
apptainer exec --nv --bind /storage/research:/storage/research --env HF_HOME="$HF" --env HF_HUB_OFFLINE=1 \
  "$HOME/ubelix/$VENV.sif" "/opt/$VENV/bin/python" "$R/read_lines.py" --root "$R" --engine "$ENGINE" \
  --model "$MODEL" --name "$NAME" --shard "$SHARD" --shards "$SHARDS" $EXTRA
