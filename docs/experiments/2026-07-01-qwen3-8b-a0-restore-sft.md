# Qwen3-8B A0 Restore SFT

## Metadata

- Experiment name: qwen3-8b-a0-restore-sft
- Date: 2026-07-01
- Goal: Restore the deleted SFT-only A0 checkpoint for Stage A RFT/ReST-EM.
- Status: success
- Operator: Codex
- Remote host: `user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote git commit: `7b64c03` plus narrow-synced RFT tooling from local `0eaf540`
- Local branch: `codex/rft-rejection-sampling`
- Local commit: `0eaf540`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: `CUDA_VISIBLE_DEVICES=0,1,2,5`
- Number of GPUs: 4

## Commands

Preflight and smoke test:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m pytest
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli demo --count 3 --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/dry-run-rft-stage-a-20260701
```

Launch attempt:

```bash
tmux new-session -d -s openseeker-20260701-restore-a0-sft-gpu0125 "bash -lc 'bash /data/wzl/OpenSeeker-AgentDataFactory/repo/runs/launch_sft_mixed_v3_v4_v5blind_v6blindtoolchoice_2p4k_restore_a0_gpu0125.sh'"
```

The first tmux session was created but the nested Windows/SSH/tmux quoting left it at a shell prompt. The same approved launcher was then sent into that session:

```bash
tmux send-keys -t openseeker-20260701-restore-a0-sft-gpu0125 'bash /data/wzl/OpenSeeker-AgentDataFactory/repo/runs/launch_sft_mixed_v3_v4_v5blind_v6blindtoolchoice_2p4k_restore_a0_gpu0125.sh' C-m
```

Monitoring:

```bash
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader
tail -n 180 /data/wzl/OpenSeeker-AgentDataFactory/logs/20260701-restore-a0-qwen3-8b-sft-2p4k-gpu0125.log
ls -lah /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice-a0-restore-20260701
```

## Paths

- Log path: `/data/wzl/OpenSeeker-AgentDataFactory/logs/20260701-restore-a0-qwen3-8b-sft-2p4k-gpu0125.log`
- Results path: none for this restore-only training run
- Data path: `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice.jsonl`
- Checkpoint path: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice-a0-restore-20260701`
- Run path: `/data/wzl/OpenSeeker-AgentDataFactory/repo/runs/launch_sft_mixed_v3_v4_v5blind_v6blindtoolchoice_2p4k_restore_a0_gpu0125.sh`

## Raw Result Summary

Smoke test:

```text
68 passed in 10.83s
OpenSeeker AgentDataFactory demo complete: accepted=3 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run-rft-stage-a-20260701
```

Training setup:

```text
Num examples = 2,280
Num Epochs = 1
Instantaneous batch size per device = 1
Total train batch size (w. parallel, distributed & accumulation) = 32
Gradient Accumulation steps = 8
Total optimization steps = 72
Number of trainable parameters = 43,646,976
```

Training completion:

```text
Training completed. Do not forget to share your model on huggingface.co/models =)

{'train_runtime': 135.7892, 'train_samples_per_second': 16.791, 'train_steps_per_second': 0.53, 'train_loss': 0.37262238045029034, 'epoch': 1.0}

***** train metrics *****
  epoch                    =        1.0
  total_flos               = 20851319GF
  train_loss               =     0.3726
  train_runtime            = 0:02:15.78
  train_samples_per_second =     16.791
  train_steps_per_second   =       0.53
```

Checkpoint files:

```text
adapter_config.json
adapter_model.safetensors 167M
all_results.json
checkpoint-50/
checkpoint-72/
trainer_log.jsonl
trainer_state.json
training_loss.png
train_results.json
```

GPU after completion:

```text
0, 18 MiB, 32607 MiB
1, 18 MiB, 32607 MiB
2, 18 MiB, 32607 MiB
3, 18 MiB, 32607 MiB
4, 18 MiB, 32607 MiB
5, 18 MiB, 32607 MiB
6, 18 MiB, 32607 MiB
7, 18 MiB, 32607 MiB
```

## Metrics

| Metric | Value | Notes |
| --- | --- | --- |
| total train rows | 2,280 | 2.4k dataset with 5% validation split |
| optimization steps | 72 | 1 epoch |
| train_loss | 0.3726 | Matches previous A0 scale |
| train_runtime | 135.7892s | 4x RTX 5090 |
| train_samples_per_second | 16.791 | LLaMA-Factory report |
| train_steps_per_second | 0.53 | LLaMA-Factory report |
| checkpoint size | 182M top-level | LoRA adapter plus tokenizer and metadata |

## Failures / Warnings

- Initial tmux launch created the session but did not execute the launcher because nested quoting was swallowed. The approved launcher was then sent into the same session with `tmux send-keys`.
- Warnings observed: deprecated `TRANSFORMERS_CACHE`, NCCL device-id guessing, no eval plots. None were fatal.
- This run restores the checkpoint only. It has not yet re-run v6/v4/v5 evaluation after restoration.

## Analysis

The A0 checkpoint was successfully restored after checkpoint cleanup. The training loss and runtime are very close to the previous 2.4k mixed SFT run, so this is a suitable starting point for Stage A RFT/ReST-EM.

For the resume project, this keeps the experimental chain reproducible: the next RFT round can cite a concrete restored SFT-only baseline instead of relying on a deleted checkpoint.

## Next Steps

- Run a quick v6 heldout check if we want to re-confirm the restored A0 reaches the old `0.985` observation faithfulness.
- Start RFT round 1 candidate sampling from this checkpoint with `K=4`.
- Verifier-filter sampled trajectories and record pass rate plus trajectory diversity.
- Train one RFT SFT adapter only if the filtered set is non-trivial and diverse.
