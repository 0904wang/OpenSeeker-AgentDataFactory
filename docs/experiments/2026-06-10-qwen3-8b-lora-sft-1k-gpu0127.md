# 2026-06-10 Qwen3-8B LoRA SFT 1k, GPU 0/1/2/7

## Status

Completed. The first 4-GPU launch failed before training because `torchrun` resolved to the user-local executable. After forcing the approved conda environment's `bin` directory to the front of `PATH`, a 4-GPU smoke test passed and the 1k SFT pilot completed.

## Goal

Run a pilot Agent SFT experiment with LLaMAFactory on the 1,000-sample OpenSeeker AgentDataFactory SFT export, using Qwen3-8B with LoRA on 4 GPUs while skipping busy GPU3.

## Remote Context

- SSH entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote branch: `main`
- Remote commit observed before launch: `7b64c03`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Python/PyTorch: env Python with `torch 2.12.0+cu130`
- Model: `Qwen/Qwen3-8B`
- Model cache used offline: `/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B`
- Dataset name: `openseeker_sft_1k`
- Dataset dir: `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory`
- Training config: `/data/wzl/OpenSeeker-AgentDataFactory/repo/configs/llamafactory/qwen3_8b_lora_sft_1k.yaml`
- GPU selection: `CUDA_VISIBLE_DEVICES=0,1,2,7`
- Skipped GPUs: GPU3 and GPU4 were busy; GPU3 was explicitly skipped per user request.

## GPU Preflight

Before the successful retry:

```text
0, 3506, 32607
1, 3505, 32607
2, 3507, 32607
3, 25985, 32607
4, 26101, 32607
5, 3493, 32607
6, 3505, 32607
7, 18, 32607
```

During the successful run, GPUs 0, 1, 2, and 7 each used about 19.4 GiB for the Qwen3-8B LoRA training process, in addition to persistent small background allocations on GPUs 0/1/2.

## Failed First Launch

Initial session:

```text
openseeker-20260610-qwen3-8b-sft-1k-gpu0127
```

Initial log:

```text
/data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-1k-gpu0127.log
```

Failure excerpt:

```text
[INFO|2026-06-10 13:41:17] llamafactory.cli:143 >> Initializing 4 distributed tasks at: 127.0.0.1:34017
Traceback (most recent call last):
  File "/home/user/.local/bin/torchrun", line 3, in <module>
    from torch.distributed.run import main
ModuleNotFoundError: No module named 'torch'
subprocess.CalledProcessError: Command '['torchrun', ...]' returned non-zero exit status 1.
```

Root cause:

```text
LLaMAFactory invokes `torchrun` by command name for distributed training.
The activated shell still resolved `torchrun` to `/home/user/.local/bin/torchrun`.
With `PYTHONNOUSERSITE=1`, that user-local torchrun could not import torch.
Single-GPU smoke did not expose this because it does not spawn torchrun.
```

Fix:

```bash
export PATH=/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory/bin:$PATH
```

Path verification:

```text
CONDA_PREFIX=/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory/bin/python
2.12.0+cu130
/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory/bin/llamafactory-cli
/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory/bin/torchrun
```

## Distributed Smoke Test

Smoke log:

```text
/data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-smoke-offline-gpu0127.log
```

Command:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
export PATH=/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory/bin:$PATH
CUDA_VISIBLE_DEVICES=0,1,2,7 \
PYTHONNOUSERSITE=1 \
HF_HUB_OFFLINE=1 \
TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers \
llamafactory-cli train configs/llamafactory/qwen3_8b_lora_sft_smoke.yaml
```

Smoke result:

```text
world size: 4
Total train batch size: 4
Total optimization steps: 1
train_loss: 3.175175189971924
train_runtime: 1.4609s
train_samples_per_second: 2.738
train_steps_per_second: 0.685
```

## Successful Launch

tmux session:

```text
openseeker-20260610-qwen3-8b-sft-1k-gpu0127-retry1
```

Log:

```text
/data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-1k-gpu0127-retry1.log
```

Command:

```bash
tmux new-session -d -s openseeker-20260610-qwen3-8b-sft-1k-gpu0127-retry1 \
  "bash -lc 'cd /data/wzl/OpenSeeker-AgentDataFactory/repo && \
  source /home/user/anaconda3/etc/profile.d/conda.sh && \
  conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && \
  export PATH=/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory/bin:\$PATH && \
  CUDA_VISIBLE_DEVICES=0,1,2,7 \
  PYTHONNOUSERSITE=1 \
  HF_HUB_OFFLINE=1 \
  TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers \
  llamafactory-cli train configs/llamafactory/qwen3_8b_lora_sft_1k.yaml \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-1k-gpu0127-retry1.log'"
```

## Training Configuration

Effective training settings from the log:

```text
Num examples = 950
Num Epochs = 1
Instantaneous batch size per device = 1
Total train batch size = 32
Gradient Accumulation steps = 8
Total optimization steps = 30
LoRA rank = 16
LoRA alpha = 32
Trainable params = 43,646,976
All params = 8,234,382,336
Trainable percent = 0.5301
```

The data split reserved 5 percent as validation via `val_size: 0.05`, but this config did not produce `eval_loss` or `eval_accuracy` in the saved plots.

## Raw Result Summary

Final metrics:

```json
{
  "epoch": 1.0,
  "total_flos": 6604947541983232.0,
  "train_loss": 0.8497752030690511,
  "train_runtime": 56.8517,
  "train_samples_per_second": 16.71,
  "train_steps_per_second": 0.528
}
```

Trainer log:

```text
step 5/30:  loss=2.2688, lr=9.738265855914013e-05, epoch=0.17
step 10/30: loss=0.9318, lr=8.236931423909138e-05, epoch=0.34
step 15/30: loss=0.5730, lr=5.808909982763825e-05, epoch=0.50
step 20/30: loss=0.4673, lr=3.149309223300428e-05, epoch=0.67
step 25/30: loss=0.4469, lr=1.0195346714717813e-05, epoch=0.84
step 30/30: loss=0.4110, lr=2.9310214228202013e-07, epoch=1.00
```

## Artifacts

Checkpoint root:

```text
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k
```

Important files:

```text
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k/adapter_model.safetensors
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k/adapter_config.json
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k/train_results.json
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k/all_results.json
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k/trainer_log.jsonl
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k/training_loss.png
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k/checkpoint-30/adapter_model.safetensors
```

Final adapter size:

```text
174,655,536 bytes
```

## Warnings And Notes

- `TRANSFORMERS_CACHE` is deprecated in Transformers v5; this run used it intentionally to force reuse of the existing complete model cache and avoid duplicate downloads.
- PEFT warned that it could not find a config file in `Qwen/Qwen3-8B` and assumed the vocabulary was not modified. The adapter and tokenizer files were still saved.
- LLaMAFactory did not plot `eval_loss` or `eval_accuracy`; this was a training pilot, not a full evaluation.
- The loss curve drops quickly on only 950 train examples. This confirms the training loop works, but it is not evidence of task generalization by itself.

## Analysis

This run proves the remote environment can train Qwen3-8B LoRA with CUDA 13.0 PyTorch packages inside the approved project-local conda environment. It also validates the 4-GPU path after fixing the `torchrun` resolution issue.

The 1k dataset is small and has repeated seed structure, so the low final training loss should be treated as a pipeline sanity signal rather than a model-quality result. The next meaningful project claim requires evaluation against held-out multi-hop/tool-use questions and a base-model comparison.

The PATH issue should be encoded into future launch commands or a small project-local launcher script. Otherwise any distributed LLaMAFactory job can silently pick up `/home/user/.local/bin/torchrun` again.

## Next Steps

- Add a reusable remote launch script or README note that prepends the approved conda env to `PATH` before any distributed LLaMAFactory run.
- Run inference/evaluation for base Qwen3-8B vs this LoRA adapter on a held-out OpenSeeker eval split.
- Report answer EM/F1, tool-call success rate, trajectory validity, and hallucination rate rather than only train loss.
- If the adapter improves the held-out metrics, scale data from 1k to 5k with stronger seed diversity before another SFT.
