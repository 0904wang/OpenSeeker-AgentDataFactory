# Qwen3-8B LoRA SFT on canonical-v2 fixed 1k

Date: 2026-06-12

## Goal

Train a Qwen3-8B LoRA adapter on the canonical-v2 fixed OpenSeeker AgentDataFactory 1k SFT export, then use the adapter for the next heldout evaluation against canonical `wikidata_lookup[entity, P19]` and `wikidata_lookup[place, P17]` tool-call behavior.

## Remote Context

- Backend: SSH
- Entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote branch / commit observed before launch: `main` / `7b64c03`
- Environment: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Launcher synced from local path: `D:\resume\Data synthesis\runs\launch_sft_canonical_v2_fixed_1k_gpu0127.sh`
- Remote launcher path: `/data/wzl/OpenSeeker-AgentDataFactory/runs/launch_sft_canonical_v2_fixed_1k_gpu0127.sh`
- Note: this run used a narrow file sync for local dirty changes and configs, not a clean committed remote revision.

## Data

- Dataset name: `openseeker_sft_1k_canonical_v2_fixed`
- Dataset file: `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_1k_canonical_v2_fixed.jsonl`
- Source generation result: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate1k-fixed`
- SFT rows: 1000
- Train rows reported by LLaMAFactory: 950
- Validation split: 5%
- Training sample inspection confirmed canonical tool calls:
  - `Action: wikidata_lookup[Ada Lovelace, P19]`
  - `Action: wikidata_lookup[London, P17]`

## Training Config

- Config: `/data/wzl/OpenSeeker-AgentDataFactory/repo/configs/llamafactory/qwen3_8b_lora_sft_1k_canonical_v2_fixed.yaml`
- Base model: `/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218`
- Method: LoRA SFT
- LoRA rank / alpha / dropout: 16 / 32 / 0.05
- Trainable params: 43,646,976
- Total params: 8,234,382,336
- Trainable ratio: 0.5301%
- Epochs: 1
- Per-device batch size: 1
- Gradient accumulation: 8
- Distributed total batch size: 32
- Total optimization steps: 30
- GPUs: `CUDA_VISIBLE_DEVICES=0,1,2,7`

## Commands

Initial direct SSH launch attempts failed before creating a task:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 "<tmux launch command>"
```

Observed status after the first attempt:

```text
tmux list-sessions: empty
target log: no_log_yet
GPU 0/1/2/7 memory: unchanged
```

The second attempt used a stdin script but failed due to nested shell quoting:

```text
bash: line 10: syntax error: unexpected end of file
```

Final approved launcher approach:

```bash
scp -P 29509 "D:\resume\Data synthesis\runs\launch_sft_canonical_v2_fixed_1k_gpu0127.sh" \
  user@ssh-22.e6.luyouxia.net:/data/wzl/OpenSeeker-AgentDataFactory/runs/launch_sft_canonical_v2_fixed_1k_gpu0127.sh

ssh user@ssh-22.e6.luyouxia.net -p 29509 \
  "if tmux has-session -t openseeker-20260612-sft-canonical-v2-1k-gpu0127 2>/dev/null; then echo 'session already exists: openseeker-20260612-sft-canonical-v2-1k-gpu0127'; else tmux new-session -d -s openseeker-20260612-sft-canonical-v2-1k-gpu0127 'bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_sft_canonical_v2_fixed_1k_gpu0127.sh' && echo 'started: openseeker-20260612-sft-canonical-v2-1k-gpu0127'; fi"
```

Remote launcher content:

```bash
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

CUDA_VISIBLE_DEVICES=0,1,2,7 PYTHONNOUSERSITE=1 \
  llamafactory-cli train configs/llamafactory/qwen3_8b_lora_sft_1k_canonical_v2_fixed.yaml \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-1k-canonical-v2-fixed-gpu0127.log
```

## Outputs

- tmux session: `openseeker-20260612-sft-canonical-v2-1k-gpu0127`
- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-1k-canonical-v2-fixed-gpu0127.log`
- Checkpoint: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v2-fixed`
- Step checkpoint: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v2-fixed/checkpoint-30`
- Checkpoint size: 698M
- Main adapter file: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v2-fixed/adapter_model.safetensors`
- Metrics files:
  - `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v2-fixed/train_results.json`
  - `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v2-fixed/all_results.json`
  - `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v2-fixed/training_loss.png`

## Raw Metrics

```json
{
  "epoch": 1.0,
  "total_flos": 5277892774723584.0,
  "train_loss": 0.9167700429757436,
  "train_runtime": 57.317,
  "train_samples_per_second": 16.574,
  "train_steps_per_second": 0.523
}
```

Selected training log excerpts:

```text
Num examples = 950
Num Epochs = 1
Instantaneous batch size per device = 1
Total train batch size (w. parallel, distributed & accumulation) = 32
Gradient Accumulation steps = 8
Total optimization steps = 30
Number of trainable parameters = 43,646,976
```

```text
{'loss': 3.4445, 'grad_norm': 4.024735927581787, 'learning_rate': 9.738265855914013e-05, 'epoch': 0.17}
{'loss': 1.2659, 'grad_norm': 1.2298921346664429, 'learning_rate': 8.236931423909138e-05, 'epoch': 0.34}
{'loss': 0.4852, 'grad_norm': 0.8106163144111633, 'learning_rate': 5.808909982763825e-05, 'epoch': 0.5}
{'loss': 0.1812, 'grad_norm': 0.51581209897995, 'learning_rate': 3.149309223300428e-05, 'epoch': 0.67}
{'loss': 0.0759, 'grad_norm': 0.588141679763794, 'learning_rate': 1.0195346714717813e-05, 'epoch': 0.84}
{'loss': 0.048, 'grad_norm': 0.47582313418388367, 'learning_rate': 2.9310214228202013e-07, 'epoch': 1.0}
```

Final log:

```text
Training completed.
train_loss = 0.9168
train_runtime = 0:00:57.31
train_samples_per_second = 16.574
train_steps_per_second = 0.523
Figure saved at: /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v2-fixed/training_loss.png
```

## Status

Completed successfully. The tmux session exited after training, GPUs were released, and the final checkpoint directory contains adapter weights, tokenizer files, trainer state, metrics JSON, and a loss plot.

## Analysis

This run fixes the previous cleaned-1k SFT weakness where heldout evaluation had perfect final-answer metrics but only 0.65 tool-call success because the model often emitted natural property names instead of canonical `P19/P17` calls. The canonical-v2 fixed dataset directly labels the desired tool-call syntax in the supervised target, so the key next metric is not train loss but heldout tool-call success and canonical action coverage.

The run is intentionally small: 1k generated samples over the current 180-row seed bank. The rapid loss drop suggests the format is easy to learn and may be partly memorized. A heldout evaluation against unseen or at least non-training prompts is required before using this as a resume result.

The launcher-script pattern is better than deeply nested SSH command strings for future runs. It is reproducible, auditable, and keeps all writes under `/data/wzl/OpenSeeker-AgentDataFactory/runs`.

## Warnings and Risks

- Remote repo commit `7b64c03` does not fully represent the local dirty working tree used to generate and configure this run. Before publishing or scaling, commit and push the code/config/data-prep changes.
- No eval metric was produced during training; LLaMAFactory logged warnings that `eval_loss` and `eval_accuracy` were not available to plot.
- Dataset diversity is limited by the current seed bank. Scaling to 5k-20k should expand entities, relation paths, noisy contexts, and harder trajectory variants rather than only increasing repeated paraphrases.

## Next Steps

1. Run heldout200 evaluation with the new adapter:
   - adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v2-fixed`
   - compare against previous cleaned-1k adapter and base model
   - primary metrics: final answer correctness, canonical tool-call coverage, tool-call success, trajectory validity.
2. If tool-call success improves materially, record resume-ready comparison: cleaned-1k vs canonical-v2 fixed 1k.
3. If heldout tool-call success remains weak, inspect generated outputs and adjust SFT target formatting or decoding/evaluator normalization before scaling data.
4. After evaluation, prepare a committed GitHub snapshot so remote experiments can be reproduced from branch + commit rather than narrow synced files.
