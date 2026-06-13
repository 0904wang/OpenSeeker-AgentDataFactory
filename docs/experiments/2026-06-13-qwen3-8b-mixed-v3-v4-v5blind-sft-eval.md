# Qwen3-8B Mixed v3/v4/v5blind SFT and Evaluation

## Goal

Train Qwen3-8B with a 2k mixed OpenSeeker AgentDataFactory SFT set and evaluate whether the adapter keeps canonical-v4 performance while improving blind-hard heldout robustness.

The mixed dataset was prepared as:

- 800 canonical-v3 rows
- 800 canonical-v4 rows
- 400 canonical-v5-blind-hard rows generated with `--start-index 200`

## Remote Context

- Date: 2026-06-13
- Remote entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote workspace: `/data/wzl/OpenSeeker-AgentDataFactory`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Local code commit before run: `992e312 Record mixed SFT data build smoke`
- Training session: `openseeker-20260613-sft-mixed-v3-v4-v5blind-2k-gpu0127`
- User approval: user explicitly approved breaking the project-local `4000 MiB` free-GPU threshold for this run

## Data Inputs

Mixed SFT data:

```text
/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_2k_mixed_v3_v4_v5blind.jsonl
```

Previous audit:

```text
total_rows 2000
source_counts {'v3': 800, 'v4': 800, 'v5blind': 400}
duplicate_ids 0
lookup_block_user_messages 800
arrow_in_v5_user_messages 0
missing_messages 0
bad_roles 0
v5 train/heldout id overlap 0
```

## SFT Launch

Command:

```bash
tmux new-session -d -s openseeker-20260613-sft-mixed-v3-v4-v5blind-2k-gpu0127 \
  "bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_sft_mixed_v3_v4_v5blind_2k_gpu0127.sh"
```

Launcher:

```text
/data/wzl/OpenSeeker-AgentDataFactory/runs/launch_sft_mixed_v3_v4_v5blind_2k_gpu0127.sh
```

Config:

```text
/data/wzl/OpenSeeker-AgentDataFactory/repo/configs/llamafactory/qwen3_8b_lora_sft_2k_mixed_v3_v4_v5blind.yaml
```

Key settings:

```text
model: Qwen3-8B local HF snapshot
dataset: openseeker_sft_2k_mixed_v3_v4_v5blind
max_samples: 2000
val_size: 0.05
LoRA rank: 16
LoRA alpha: 32
LoRA dropout: 0.05
per_device_train_batch_size: 1
gradient_accumulation_steps: 8
num_train_epochs: 1.0
bf16: true
CUDA_VISIBLE_DEVICES: 0,1,2,7
```

GPU preflight before launch:

```text
0, 4293 MiB, 32607 MiB, 0 %
1, 4293 MiB, 32607 MiB, 0 %
2, 4295 MiB, 32607 MiB, 0 %
7, 806 MiB, 32607 MiB, 0 %
```

The usual `4000 MiB` threshold was not met on 0/1/2. This run proceeded only because the user explicitly approved this one-time exception.

## SFT Result

Checkpoint:

```text
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2k-mixed-v3-v4-v5blind
```

Log:

```text
/data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-2k-mixed-v3-v4-v5blind-gpu0127.log
```

Trainer state:

```text
global_step 60
epoch 1.0
train_loss 0.4052645953527341
train_runtime 117.9302
```

Train results:

```json
{
  "epoch": 1.0,
  "total_flos": 1.6887064217780224e+16,
  "train_loss": 0.4052645953527341,
  "train_runtime": 117.9302,
  "train_samples_per_second": 16.111,
  "train_steps_per_second": 0.509
}
```

Checkpoint artifacts:

```text
adapter_model.safetensors: 167M
checkpoint dir size: 1.2G
checkpoint-50 and checkpoint-60 saved
training_loss.png saved
```

Training log loss points:

```text
step 5:  loss 3.1333
step 10: loss 1.1026
step 15: loss 0.4333
step 20: loss 0.1432
step 25: loss 0.0239
step 30: loss 0.0106
step 35: loss 0.0062
step 40: loss 0.0037
step 45: loss 0.0016
step 50: loss 0.0016
step 55: loss 0.0011
step 60: loss 0.0023
```

## Evaluation Commands

### v4 Heldout

```bash
tmux new-session -d -s openseeker-20260613-eval-mixed-v4heldout-gpu7 \
  "bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_mixed_v3_v4_v5blind_v4heldout_gpu7.sh"
```

Samples:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v4/samples.jsonl
```

Results:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-2k-mixed-v3-v4-v5blind-v4heldout200-gpu7
```

### v5 Blind-hard Heldout

```bash
tmux new-session -d -s openseeker-20260613-eval-mixed-v5blindhard-gpu7 \
  "bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_mixed_v3_v4_v5blind_v5blindhard_gpu7.sh"
```

Samples:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v5-blind-hard/samples.jsonl
```

Results:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-2k-mixed-v3-v4-v5blind-v5blindhard-heldout200-gpu7
```

Both evaluations used GPU7 with:

```text
limit: 200
batch_size: 2
max_new_tokens: 160
disable_thinking: true
local_files_only: true
```

## Evaluation Results

### v4 Heldout200

Overall:

```text
total 200
exact_match_rate 1.0
canonical_match_rate 1.0
answer_f1_avg 1.0
gold_answer_mention_rate 1.0
final_answer_rate 1.0
tool_call_success_rate 1.0
tool_call_coverage_avg 1.0
observation_faithfulness_rate 1.0
observation_coverage_avg 1.0
trajectory_valid_rate 1.0
hallucination_rate 0.0
correct_rate 1.0
```

By task type:

```text
multi_hop_qa: 67/67, all reported rates 1.0, hallucination 0.0
noisy_context_retrieval_qa: 66/66, all reported rates 1.0, hallucination 0.0
tool_use_qa: 67/67, all reported rates 1.0, hallucination 0.0
```

Prediction rows:

```text
200 /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-2k-mixed-v3-v4-v5blind-v4heldout200-gpu7/qwen3-8b-lora-sft-2k-mixed-v3-v4-v5blind-v4heldout200_predictions.jsonl
```

### v5 Blind-hard Heldout200

Overall:

```text
total 200
exact_match_rate 1.0
canonical_match_rate 1.0
answer_f1_avg 1.0
gold_answer_mention_rate 1.0
final_answer_rate 1.0
tool_call_success_rate 1.0
tool_call_coverage_avg 1.0
observation_faithfulness_rate 1.0
observation_coverage_avg 1.0
trajectory_valid_rate 1.0
hallucination_rate 0.0
correct_rate 1.0
```

By task type:

```text
multi_hop_qa: 67/67, all reported rates 1.0, hallucination 0.0
noisy_context_retrieval_qa: 66/66, all reported rates 1.0, hallucination 0.0
tool_use_qa: 67/67, all reported rates 1.0, hallucination 0.0
```

Prediction rows:

```text
200 /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-2k-mixed-v3-v4-v5blind-v5blindhard-heldout200-gpu7/qwen3-8b-lora-sft-2k-mixed-v3-v4-v5blind-v5blindhard-heldout200_predictions.jsonl
```

## Comparison With Prior Runs

Best previous v4 heldout:

```text
canonical-v4 SFT: exact/canonical/tool/obs/correct = 1.0
```

Best previous v5 blind-hard:

```text
canonical-v3 SFT:
exact 0.930
canonical 1.000
tool_success 1.000
observation_faithfulness 0.930
hallucination 0.000
correct 0.930
```

Mixed 2k SFT:

```text
v4 heldout: exact/canonical/tool/obs/correct = 1.0, hallucination = 0.0
v5 blind-hard: exact/canonical/tool/obs/correct = 1.0, hallucination = 0.0
```

This mixed run improves the v5 blind-hard result over the previous canonical-v3 adapter while preserving v4 saturation.

## Analysis

The mixed data objective worked on the current deterministic heldout suite. The 800/800/400 composition appears to keep the canonical-v4 tool-observation contract and adds enough blind-hard examples to remove the answer and observation-faithfulness failures seen in prior v5 blind-hard evaluation.

The training loss falls extremely quickly after step 15. That is expected for this compact deterministic synthetic task family, but it also means the present heldout suite may no longer be hard enough to distinguish stronger data strategies. The 1.0/1.0 results should be reported as a project milestone, not as evidence that the broader agent problem is solved.

The one-time GPU threshold exception did not cause OOM. Peak selected-GPU memory observed during SFT was about:

```text
GPU0: 23666 MiB
GPU1: 23666 MiB
GPU2: 23664 MiB
GPU7: 20179 MiB
```

## Next Steps

1. Create a harder heldout split that randomizes phrasing and withholds ReAct trajectory scaffolding, not just lookup observations.
2. Add a mixed-data ablation table for resume/README:
   - base Qwen3-8B
   - canonical-v3 SFT
   - canonical-v4 SFT
   - mixed v3/v4/v5blind SFT
3. Consider reducing template leakage in evaluation by requiring the model to choose tool schema and intermediate relation without the exact P19/P17 instruction pattern.
4. Record this result in README as the first successful closed-loop run: data build -> LoRA SFT -> v4/v5 heldout evaluation.
