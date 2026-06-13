#!/usr/bin/env bash
set -euo pipefail

cd /data/wzl/OpenSeeker-AgentDataFactory/repo

source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory

export HF_HOME=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface
export TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export PATH=/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory/bin:$PATH

CUDA_VISIBLE_DEVICES=7 PYTHONNOUSERSITE=1 python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v6-blind-tool-choice-hard/samples.jsonl \
  --model-label qwen3-8b-lora-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v6blindtoolchoice-heldout200 \
  --model-name-or-path /data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218 \
  --adapter-path /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice \
  --limit 200 \
  --batch-size 2 \
  --max-new-tokens 160 \
  --device cuda \
  --local-files-only \
  --disable-thinking \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v6blindtoolchoice-heldout200-gpu7 \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v6blindtoolchoice-heldout200-gpu7.log
