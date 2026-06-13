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

CUDA_VISIBLE_DEVICES=0,1,2,5 PYTHONNOUSERSITE=1 \
  llamafactory-cli train configs/llamafactory/qwen3_8b_lora_sft_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice.yaml \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice-gpu0125.log
