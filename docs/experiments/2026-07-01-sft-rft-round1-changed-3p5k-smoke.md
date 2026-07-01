# RFT Round 1 Changed-only SFT Data Smoke

## Metadata

- Experiment name: sft-rft-round1-changed-3p5k-smoke
- Date: 2026-07-01
- Goal: Build the changed-only RFT SFT mix and verify LLaMA-Factory can load it while continuing from the restored A0 adapter.
- Status: success
- Operator: Codex
- Remote host: `user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Local branch: `codex/rft-rejection-sampling`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: `CUDA_VISIBLE_DEVICES=0`
- Number of GPUs: 1

## Commands

Data build:

```bash
base=/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice.jsonl
rft=/data/wzl/OpenSeeker-AgentDataFactory/data/rft/rft_round1_changed_sft_conversations.jsonl
out=/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_3p5k_mixed_v3_v4_v5blind_v6_rftchanged.jsonl
```

Smoke command:

```bash
CUDA_VISIBLE_DEVICES=0 PYTHONNOUSERSITE=1 llamafactory-cli train \
  configs/llamafactory/qwen3_8b_lora_sft_3p5k_mixed_v3_v4_v5blind_v6_rftchanged_round1_smoke.yaml \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/20260701-sft-rft-round1-changed-3p5k-smoke-gpu0.log
```

## Paths

- Dataset: `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_3p5k_mixed_v3_v4_v5blind_v6_rftchanged.jsonl`
- Dataset registry: `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/dataset_info.json`
- Smoke config: `/data/wzl/OpenSeeker-AgentDataFactory/repo/configs/llamafactory/qwen3_8b_lora_sft_3p5k_mixed_v3_v4_v5blind_v6_rftchanged_round1_smoke.yaml`
- Smoke log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/20260701-sft-rft-round1-changed-3p5k-smoke-gpu0.log`
- Smoke checkpoint: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/smoke-qwen3-8b-openseeker-sft-3p5k-rftchanged-round1-20260701`

## Raw Result Summary

Data build:

```text
combined_rows 3495
base_rows 2400
rft_changed_rows 1095
registry_has_entry True
```

Smoke load:

```text
Loading dataset openseeker_sft_3p5k_mixed_v3_v4_v5blind_v6_rftchanged.jsonl...
Generating train split: 3495 examples
Converting format of dataset: 100%|██████████| 8/8
Running tokenizer on dataset: 100%|██████████| 8/8
Loaded adapter(s): /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice-a0-restore-20260701
trainable params: 43,646,976 || all params: 8,234,382,336 || trainable%: 0.5301
Total optimization steps = 1
```

Smoke completion:

```text
{'loss': 0.0011, 'grad_norm': 0.1023457944393158, 'learning_rate': 5e-05, 'epoch': 0.12}
{'train_runtime': 1.5909, 'train_samples_per_second': 0.629, 'train_steps_per_second': 0.629, 'train_loss': 0.001121288863942027, 'epoch': 0.12}
```

## Metrics

| Metric | Value | Notes |
| --- | --- | --- |
| base rows | 2,400 | restored A0 mixed SFT data |
| changed RFT rows | 1,095 | accepted and changed from gold |
| combined rows | 3,495 | next SFT data |
| smoke max_samples | 8 | registry/load smoke |
| smoke max_steps | 1 | continuation smoke |
| smoke train_loss | 0.0011 | not a quality metric |

## Failures / Warnings

- Smoke created a small adapter checkpoint. It is not the final RFT model.
- The real run should avoid busy GPUs because OpenR1 is currently using GPU1-5.

## Analysis

The data and continuation path are ready. The clean training candidate is `original 2.4k + changed-only RFT 1,095`, not all 9,429 accepted RFT rows.

This preserves the strong A0 baseline and adds only verifier-approved trajectories that differ from the original gold trace.

## Next Steps

- Launch 2-GPU RFT SFT on GPUs `0,6` if they remain free.
- Evaluate on v6 heldout first, then v4/v5 regression.
