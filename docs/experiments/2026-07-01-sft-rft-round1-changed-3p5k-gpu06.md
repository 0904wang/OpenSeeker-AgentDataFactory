# RFT Round 1 Changed-only SFT

## Metadata

- Experiment name: sft-rft-round1-changed-3p5k-gpu06
- Date: 2026-07-01
- Goal: Continue SFT from the restored A0 checkpoint using the original 2.4k mixed data plus 1,095 verifier-passing RFT trajectories that differ from the gold trace.
- Status: success
- Operator: Codex
- Remote host: `user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Local branch: `codex/rft-rejection-sampling`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: `CUDA_VISIBLE_DEVICES=0,6`
- Number of GPUs: 2

## Commands

Launcher:

```bash
/data/wzl/OpenSeeker-AgentDataFactory/repo/runs/launch_sft_rft_round1_changed_3p5k_gpu06.sh
```

Effective launch:

```bash
tmux new-session -d -s openseeker-20260701-sft-rftchanged-3p5k-gpu06 \
  "bash /data/wzl/OpenSeeker-AgentDataFactory/repo/runs/launch_sft_rft_round1_changed_3p5k_gpu06.sh"
```

Training command:

```bash
CUDA_VISIBLE_DEVICES=0,6 PYTHONNOUSERSITE=1 llamafactory-cli train \
  configs/llamafactory/qwen3_8b_lora_sft_3p5k_mixed_v3_v4_v5blind_v6_rftchanged_round1.yaml \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/20260701-sft-rft-round1-changed-3p5k-gpu06.log
```

Monitoring:

```bash
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader
tail -n 160 /data/wzl/OpenSeeker-AgentDataFactory/logs/20260701-sft-rft-round1-changed-3p5k-gpu06.log
ls -lah /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-3p5k-mixed-v3-v4-v5blind-v6-rftchanged-round1-20260701
```

## Paths

- Training data: `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_3p5k_mixed_v3_v4_v5blind_v6_rftchanged.jsonl`
- Base model: `/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218`
- Starting adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice-a0-restore-20260701`
- Output checkpoint: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-3p5k-mixed-v3-v4-v5blind-v6-rftchanged-round1-20260701`
- Log path: `/data/wzl/OpenSeeker-AgentDataFactory/logs/20260701-sft-rft-round1-changed-3p5k-gpu06.log`
- Run path: `/data/wzl/OpenSeeker-AgentDataFactory/repo/runs/launch_sft_rft_round1_changed_3p5k_gpu06.sh`

## Raw Result Summary

Setup:

```text
Loading dataset openseeker_sft_3p5k_mixed_v3_v4_v5blind_v6_rftchanged.jsonl...
Loaded adapter(s): /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice-a0-restore-20260701
trainable params: 43,646,976 || all params: 8,234,382,336 || trainable%: 0.5301
```

Training setup:

```text
Num examples = 3,320
Num Epochs = 1
Instantaneous batch size per device = 1
Total train batch size (w. parallel, distributed & accumulation) = 16
Gradient Accumulation steps = 8
Total optimization steps = 208
Number of trainable parameters = 43,646,976
```

Training completion:

```text
Training completed. Do not forget to share your model on huggingface.co/models =)

{'train_runtime': 388.6431, 'train_samples_per_second': 8.543, 'train_steps_per_second': 0.535, 'train_loss': 0.005898799997969315, 'epoch': 1.0}

***** train metrics *****
  epoch                    =        1.0
  total_flos               = 30341535GF
  train_loss               =     0.0059
  train_runtime            = 0:06:28.64
  train_samples_per_second =      8.543
  train_steps_per_second   =      0.535
```

Checkpoint files:

```text
adapter_config.json
adapter_model.safetensors 167M
all_results.json
checkpoint-200/
checkpoint-208/
trainer_log.jsonl
trainer_state.json
training_loss.png
train_results.json
```

GPU after completion:

```text
0, 18 MiB, 32607 MiB
1, 18 MiB, 32607 MiB
2, 31610 MiB, 32607 MiB
3, 31650 MiB, 32607 MiB
4, 31610 MiB, 32607 MiB
5, 31610 MiB, 32607 MiB
6, 18 MiB, 32607 MiB
7, 18 MiB, 32607 MiB
```

## Metrics

| Metric | Value | Notes |
| --- | --- | --- |
| source data rows | 3,495 | 2,400 base + 1,095 changed RFT |
| train examples | 3,320 | after 5% validation split |
| optimization steps | 208 | 1 epoch, 2 GPUs |
| train_loss | 0.0059 | continued from A0 |
| train_runtime | 388.6431s | 2x RTX 5090 |
| train_samples_per_second | 8.543 | LLaMA-Factory report |
| train_steps_per_second | 0.535 | LLaMA-Factory report |
| checkpoint size | 182M top-level | LoRA adapter plus tokenizer and metadata |

## Failures / Warnings

- GPU2-5 were occupied by an unrelated OpenR1 session, so this run used GPUs `0,6` instead of 4 GPUs.
- The low training loss is expected because this is a continuation from A0 and many rows remain close to the original SFT distribution. Heldout evaluation is required before claiming improvement.
- Warnings observed: deprecated `TRANSFORMERS_CACHE`, no eval loss/accuracy plots. None were fatal.

## Analysis

The changed-only RFT SFT run completed cleanly. It is now ready for the real comparison:

```text
SFT-only A0: v6 observation faithfulness 0.985, failures 3/200
SFT + RFT Round 1 changed-only: TBD
```

This is the right next checkpoint to evaluate because it avoids the naive all-accepted RFT dataset, where 8,334 of 9,429 accepted samples were exact copies of the gold trajectory.

## Next Steps

- Evaluate this adapter on v6 blind tool-choice heldout200 first.
- If v6 improves or remains stable, run v4/v5 regression.
- If v6 regresses, inspect whether changed RFT samples overfit noisy-context rewrites.
