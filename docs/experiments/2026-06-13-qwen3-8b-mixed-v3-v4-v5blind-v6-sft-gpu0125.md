# Qwen3-8B Mixed v3/v4/v5blind/v6 SFT on GPU0125

## Goal

Train Qwen3-8B with the 2.4k mixed OpenSeeker SFT dataset that adds 400 `canonical-v6-blind-tool-choice-hard` rows to the previous mixed v3/v4/v5blind recipe.

Target comparison after this run:

- preserve v4 and v5 blind-hard saturation
- improve v6 observation faithfulness over the previous mixed adapter baseline of `0.945`

## Remote Context

- Date: 2026-06-13
- Remote entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote workspace: `/data/wzl/OpenSeeker-AgentDataFactory`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Training session: `openseeker-20260613-sft-mixed-v6-2p4k-gpu0125`
- GPU selection: `CUDA_VISIBLE_DEVICES=0,1,2,5`
- Number of GPUs: 4

The user explicitly approved launching this 4-GPU SFT after the card switch. GPU7 was avoided because it had become busy.

## Data

Training data:

```text
/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice.jsonl
```

Recorded data build:

```text
docs/experiments/2026-06-13-qwen3-8b-mixed-v3-v4-v5blind-v6-data-smoke.md
```

Audit summary:

```text
total_rows 2400
existing_rows 2000
v6_rows 400
v6_train_heldout_overlap 0
duplicate_v6_ids 0
```

The existing 2k mix is the previous `800 v3 + 800 v4 + 400 v5blind` dataset. The 400 v6 rows were generated with `--start-index 200`, keeping them disjoint from the v6 heldout200 split.

## Preflight

Immediate preflight before launch:

```text
0, 3506 MiB, 32607 MiB, 0 %
1, 3505 MiB, 32607 MiB, 0 %
2, 3507 MiB, 32607 MiB, 0 %
3, 25985 MiB, 32607 MiB, 0 %
4, 26101 MiB, 32607 MiB, 0 %
5, 3493 MiB, 32607 MiB, 0 %
6, 3505 MiB, 32607 MiB, 0 %
7, 11805 MiB, 32607 MiB, 62 %
```

Selected GPUs `0,1,2,5` were all below the project-local `4000 MiB` free-GPU threshold. The target checkpoint and full SFT log did not exist before launch.

## Launch

Launcher:

```text
/data/wzl/OpenSeeker-AgentDataFactory/runs/launch_sft_mixed_v3_v4_v5blind_v6blindtoolchoice_2p4k_gpu0125.sh
```

Tmux command:

```bash
tmux new-session -d -s openseeker-20260613-sft-mixed-v6-2p4k-gpu0125 \
  "bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_sft_mixed_v3_v4_v5blind_v6blindtoolchoice_2p4k_gpu0125.sh"
```

Effective command:

```bash
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
```

## Config

Config:

```text
/data/wzl/OpenSeeker-AgentDataFactory/repo/configs/llamafactory/qwen3_8b_lora_sft_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice.yaml
```

Key settings:

```text
model: local Qwen3-8B snapshot
dataset: openseeker_sft_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice
max_samples: 2400
val_size: 0.05
effective train examples: 2280
LoRA rank: 16
LoRA alpha: 32
LoRA dropout: 0.05
per_device_train_batch_size: 1
gradient_accumulation_steps: 8
total_train_batch_size: 32
num_train_epochs: 1.0
total optimization steps: 72
bf16: true
```

## Result

Status: success.

Checkpoint:

```text
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice
```

Log:

```text
/data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice-gpu0125.log
```

Trainer result:

```json
{
  "epoch": 1.0,
  "total_flos": 2.238893403406336e+16,
  "train_loss": 0.3728570582332193,
  "train_runtime": 134.378,
  "train_samples_per_second": 16.967,
  "train_steps_per_second": 0.536
}
```

Trainer state:

```text
global_step 72
epoch 1.0
```

Checkpoint size:

```text
1.2G /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice
```

Key artifacts:

```text
adapter_model.safetensors 174655536
adapter_config.json 976
checkpoint-50
checkpoint-72
trainer_state.json
trainer_log.jsonl
train_results.json
training_loss.png
```

## Loss Trace

```text
step 5:  loss 3.3700
step 10: loss 1.2872
step 15: loss 0.4934
step 20: loss 0.1547
step 25: loss 0.0370
step 30: loss 0.0114
step 35: loss 0.0049
step 40: loss 0.0029
step 45: loss 0.0024
step 50: loss 0.0019
step 55: loss 0.0007
step 60: loss 0.0007
step 65: loss 0.0009
step 70: loss 0.0007
```

## Resource Notes

Peak selected-GPU memory observed shortly after launch:

```text
0: 22893 MiB
1: 22891 MiB
2: 22895 MiB
5: 22873 MiB
```

No OOM occurred. After training completed, GPUs returned to their pre-run baseline memory usage.

## Analysis

The run completed cleanly and is directly comparable to the previous 2k mixed v3/v4/v5blind SFT. Runtime and throughput are also close to the earlier mixed 2k run, with the expected slight increase from 60 to 72 optimization steps.

The loss again drops very quickly. That is consistent with this deterministic synthetic task family and should not be over-interpreted as broad agent generalization. The useful question is whether adding v6 blind tool-choice training improves the heldout v6 observation-faithfulness metric while preserving v4 and v5 answer/tool performance.

## Next Steps

1. Evaluate this adapter on v6 blind tool-choice heldout200.
2. Re-evaluate v4 and v5 blind-hard heldouts to check for regressions.
3. Record comparison against the previous mixed v3/v4/v5blind adapter:
   - previous v6 observation faithfulness: `0.945`
   - target: improve observation faithfulness without losing answer/tool correctness.
