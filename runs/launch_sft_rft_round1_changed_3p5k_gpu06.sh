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

CUDA_VISIBLE_DEVICES=0,6 PYTHONNOUSERSITE=1 \
  llamafactory-cli train configs/llamafactory/qwen3_8b_lora_sft_3p5k_mixed_v3_v4_v5blind_v6_rftchanged_round1.yaml \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/20260701-sft-rft-round1-changed-3p5k-gpu06.log
