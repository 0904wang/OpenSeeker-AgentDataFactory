# 2026-06-11 Qwen3-8B LoRA SFT on Cleaned 1k, GPU 0/1/2/7

## Metadata

- Experiment name: `qwen3-8b-openseeker-sft-1k-cleaned-gpu0127`
- Date: 2026-06-11
- Goal: Run a 4-GPU LLaMAFactory LoRA SFT pass on the repaired and cleaned 1k OpenSeeker AgentDataFactory SFT dataset.
- Status: success
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Branch: `main`
- Commit: `7b64c03755802c1c203b48ae5360aca0cb20e456`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Model: Qwen3-8B local snapshot at `/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218`
- Training framework: LLaMAFactory 0.9.3
- GPU selection: `CUDA_VISIBLE_DEVICES=0,1,2,7`
- Number of GPUs: 4

## Commands

Preflight:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 '
  nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader &&
  tmux list-sessions 2>/dev/null || true &&
  ! tmux has-session -t openseeker-20260611-sft-cleaned1k-gpu0127 2>/dev/null
'
```

Observed GPU preflight:

```text
0, 3506 MiB, 32607 MiB
1, 3505 MiB, 32607 MiB
2, 3507 MiB, 32607 MiB
3, 25985 MiB, 32607 MiB
4, 26101 MiB, 32607 MiB
5, 3493 MiB, 32607 MiB
6, 3505 MiB, 32607 MiB
7, 18 MiB, 32607 MiB
```

Dry run:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
export HF_HOME=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface
export TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export PATH=/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory/bin:$PATH
CUDA_VISIBLE_DEVICES=0,1,2,7 PYTHONNOUSERSITE=1 \
  llamafactory-cli train configs/llamafactory/qwen3_8b_lora_sft_1k_cleaned_smoke.yaml \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-1k-cleaned-smoke-4gpu0127.log
```

Dry run result:

```text
world size: 4
Total train batch size: 4
Total optimization steps: 1
train_loss: 3.306814193725586
train_runtime: 1.4583s
train_samples_per_second: 2.743
train_steps_per_second: 0.686
```

Launch:

```bash
tmux new-session -d -s openseeker-20260611-sft-cleaned1k-gpu0127 \
  "bash -lc 'cd /data/wzl/OpenSeeker-AgentDataFactory/repo && \
  source /home/user/anaconda3/etc/profile.d/conda.sh && \
  conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && \
  export HF_HOME=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface && \
  export TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers && \
  export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 && \
  export PATH=/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory/bin:\$PATH && \
  CUDA_VISIBLE_DEVICES=0,1,2,7 PYTHONNOUSERSITE=1 \
  llamafactory-cli train configs/llamafactory/qwen3_8b_lora_sft_1k_cleaned.yaml \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-1k-cleaned-gpu0127.log'"
```

Monitoring:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 '
  nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader &&
  tmux list-sessions 2>/dev/null || true &&
  tail -n 120 /data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-1k-cleaned-gpu0127.log &&
  find /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-cleaned -maxdepth 2 -type f | sort | head -80
'
```

## Paths

- Log path: `/data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-1k-cleaned-gpu0127.log`
- Data path: `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_1k_cleaned.jsonl`
- Dataset info: `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/dataset_info.json`
- Training config: `/data/wzl/OpenSeeker-AgentDataFactory/repo/configs/llamafactory/qwen3_8b_lora_sft_1k_cleaned.yaml`
- Checkpoint path: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-cleaned`
- Intermediate checkpoint: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-cleaned/checkpoint-30`
- Smoke checkpoint: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-cleaned-smoke`
- Local record: `D:\resume\Data synthesis\docs\experiments\2026-06-11-qwen3-8b-cleaned1k-sft-4gpu0127.md`

## Training Configuration

Effective settings from the log:

```text
Num examples = 950
Num Epochs = 1
Instantaneous batch size per device = 1
Total train batch size = 32
Gradient Accumulation steps = 8
Total optimization steps = 30
LoRA rank = 16
LoRA alpha = 32
LoRA dropout = 0.05
Trainable params = 43,646,976
All params = 8,234,382,336
Trainable percent = 0.5301
```

The config reserved 5 percent via `val_size: 0.05`, but this run did not emit `eval_loss` or `eval_accuracy`; it should be treated as a training loop and adapter artifact experiment, not a completed model-quality evaluation.

## Raw Result Summary

Final `train_results.json`:

```json
{
  "epoch": 1.0,
  "total_flos": 6575351794761728.0,
  "train_loss": 0.8588244040807088,
  "train_runtime": 57.6342,
  "train_samples_per_second": 16.483,
  "train_steps_per_second": 0.521
}
```

Trainer log excerpts:

```text
step 5/30:  loss=2.2726, lr=9.738265855914013e-05, epoch=0.17
step 10/30: loss=0.9664, lr=8.236931423909138e-05, epoch=0.34
step 15/30: loss=0.5948, lr=5.808909982763825e-05, epoch=0.50
step 20/30: loss=0.4633, lr=3.149309223300428e-05, epoch=0.67
step 25/30: loss=0.4465, lr=1.0195346714717813e-05, epoch=0.84
step 30/30: loss=0.4093, lr=2.9310214228202013e-07, epoch=1.00
```

Checkpoint summary:

```text
Checkpoint root size: 698M
Final adapter: /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-cleaned/adapter_model.safetensors
Training loss plot: /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-cleaned/training_loss.png
```

## Metrics

| Metric | Value | Notes |
| --- | ---: | --- |
| train examples | 950 | 5 percent held out by config |
| global steps | 30 | From trainer log |
| epochs | 1.0 | Full configured epoch completed |
| train loss | 0.8588244040807088 | Final train result |
| train runtime | 57.6342 s | 4-GPU DDP |
| train samples/s | 16.483 | Effective throughput |
| train steps/s | 0.521 | Effective throughput |
| checkpoint size | 698M | Adapter plus checkpoint-30 optimizer state |
| GPUs | 0,1,2,7 | GPU3/4 were busy and skipped |

## Failures / Warnings

- The first launch attempt hit an SSH connection timeout before returning a remote result. A guarded retry was used: if the tmux session already existed, it would not start a duplicate run. The guarded retry launched successfully.
- Transformers warned that `TRANSFORMERS_CACHE` is deprecated. It was intentionally set to reuse the complete local model cache and keep the run offline.
- LLaMAFactory warned that no `eval_loss` or `eval_accuracy` was available to plot. The next step must run a separate held-out evaluation.
- A post-run diagnostic one-liner for parsing `trainer_state.json` had quoting issues over SSH. This did not affect training; final metrics were read from `train_results.json` and the raw training log.

## Analysis

This run validates that the cleaned 1k SFT dataset can be trained end to end with Qwen3-8B LoRA on the shared remote server using four GPUs and the approved project-local CUDA 13.0 environment. Compared with the previous 1k SFT pass, this run uses the repaired dataset where the automatic audit reported zero entity-mismatch rows and zero synthetic-round leakage rows.

The final train loss and fast convergence are useful as a pipeline sanity signal, but they are not enough to claim model improvement. The dataset is still small and template-heavy, so the meaningful evidence must come from a held-out evaluation against base Qwen3-8B and, ideally, the earlier non-cleaned adapter.

For the resume project, the important engineering claim is now stronger: the data factory can generate, audit, repair, export, and train an Agent SFT adapter in a reproducible remote workflow. The next claim should be about task metrics: answer accuracy, evidence/tool-call correctness, trajectory validity, and hallucination rate.

## Next Steps

- Run held-out evaluation for base Qwen3-8B vs `qwen3-8b-openseeker-sft-1k-cleaned`.
- Compare the cleaned adapter against the previous non-cleaned 1k adapter to see whether the repair pass changes answer/tool behavior.
- If held-out metrics improve, scale cleaned generation beyond 1k before the next SFT.
- Add the final evaluation table to the README and resume material only after the held-out evaluation completes.
