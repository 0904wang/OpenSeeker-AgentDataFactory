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

SAMPLES=/data/wzl/OpenSeeker-AgentDataFactory/data/rft/openseeker_agent_samples_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice.jsonl
MODEL=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218
ADAPTER=/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice-a0-restore-20260701
OUT=/data/wzl/OpenSeeker-AgentDataFactory/results/rft-round1-a0-k4-t1p0-20260701

mkdir -p "${OUT}"

CUDA_VISIBLE_DEVICES=0 PYTHONNOUSERSITE=1 python -m openseeker_factory.cli sample-rft-candidates \
  --samples "${SAMPLES}" \
  --out-dir "${OUT}" \
  --model-label qwen3-8b-a0-restore-rft-round1-k4-t1p0 \
  --model-name-or-path "${MODEL}" \
  --adapter-path "${ADAPTER}" \
  --num-return-sequences 4 \
  --temperature 1.0 \
  --top-p 0.98 \
  --batch-size 1 \
  --max-new-tokens 160 \
  --local-files-only \
  --disable-thinking \
  --seed 20260701 \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/rft-round1-a0-k4-t1p0-20260701-sample.log

PYTHONNOUSERSITE=1 python -m openseeker_factory.cli rft-filter \
  --samples "${SAMPLES}" \
  --prediction-file "${OUT}/candidate_predictions.jsonl" \
  --out-dir "${OUT}" \
  --model-label qwen3-8b-a0-restore-rft-round1-k4-t1p0 \
  --iteration 1 \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/rft-round1-a0-k4-t1p0-20260701-filter.log

cat "${OUT}/rft_summary.json"
