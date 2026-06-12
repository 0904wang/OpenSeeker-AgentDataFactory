# Qwen3-8B Canonical-v3 1k SFT on 4 GPUs

## Goal

Train a Qwen3-8B LoRA adapter on the canonical-v3 observation-grounded OpenSeeker SFT dataset, then use the resulting checkpoint for the next heldout evaluation against prior canonical-v2 fixed training.

## Remote Context

- Date: 2026-06-12
- Remote entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote workspace: `/data/wzl/OpenSeeker-AgentDataFactory`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Local config commit: `80e8125 Add canonical v3 SFT configs`
- Smoke record commit: `897e0c7 Record canonical v3 SFT smoke`
- Remote sync mode: narrow config sync, because the remote experiment workspace had pre-existing dirty changes and `git pull --ff-only` was not safe.

## Inputs

- Dataset: `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_1k_canonical_v3.jsonl`
- Dataset rows: 1000
- Dataset registry: `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/dataset_info.json`
- Config: `/data/wzl/OpenSeeker-AgentDataFactory/repo/configs/llamafactory/qwen3_8b_lora_sft_1k_canonical_v3.yaml`
- Base model: `/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218`
- GPUs: `CUDA_VISIBLE_DEVICES=0,1,2,7`
- tmux session: `openseeker-20260612-sft-canonical-v3-1k-gpu0127`

## Preflight

GPU memory before launch:

```text
0, 3506 MiB, 32607 MiB
1, 3505 MiB, 32607 MiB
2, 3507 MiB, 32607 MiB
3, 25985 MiB, 32607 MiB
4, 26101 MiB, 32607 MiB
5, 3493 MiB, 32607 MiB
6, 3505 MiB, 32607 MiB
7, 931 MiB, 32607 MiB
```

Checkpoint path was clear before launch:

```text
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v3
```

Smoke prerequisite:

- `tests/test_pipeline.py`: 22 passed
- single-GPU smoke SFT completed on GPU7

## Launch Command

```bash
tmux new-session -d -s openseeker-20260612-sft-canonical-v3-1k-gpu0127 "bash -lc 'cd /data/wzl/OpenSeeker-AgentDataFactory/repo && source /home/user/anaconda3/etc/profile.d/conda.sh && conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && export HF_HOME=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface && export TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers && export HF_HUB_OFFLINE=1 && export TRANSFORMERS_OFFLINE=1 && export PATH=/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory/bin:$PATH && CUDA_VISIBLE_DEVICES=0,1,2,7 PYTHONNOUSERSITE=1 llamafactory-cli train configs/llamafactory/qwen3_8b_lora_sft_1k_canonical_v3.yaml 2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-1k-canonical-v3-gpu0127.log'"
```

## Outputs

- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-1k-canonical-v3-gpu0127.log`
- Final checkpoint: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v3`
- Step checkpoint: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v3/checkpoint-30`
- Adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v3/adapter_model.safetensors`
- Training curve: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v3/training_loss.png`
- Checkpoint disk usage: `698M`

## Training Configuration

- Model: Qwen3-8B
- Fine-tuning type: LoRA
- LoRA rank: 16
- LoRA alpha: 32
- LoRA dropout: 0.05
- LoRA target: all linear modules
- Trainable parameters: 43,646,976
- Trainable ratio: 0.5301%
- Dataset split after validation holdout: 950 train examples
- Validation size: 0.05
- Per-device train batch size: 1
- Gradient accumulation steps: 8
- Effective train batch size: 32
- Epochs: 1
- Optimization steps: 30
- Learning rate: `1.0e-4`
- Scheduler: cosine
- Precision: bf16

## Metrics

Final train results:

```json
{
  "epoch": 1.0,
  "total_flos": 6493872507060224.0,
  "train_loss": 0.9266009499629339,
  "train_runtime": 56.634,
  "train_samples_per_second": 16.774,
  "train_steps_per_second": 0.53
}
```

Loss trace:

```text
step 5:  loss=3.3639, lr=9.7383e-05
step 10: loss=1.2802, lr=8.2369e-05
step 15: loss=0.5307, lr=5.8089e-05
step 20: loss=0.2128, lr=3.1493e-05
step 25: loss=0.1057, lr=1.0195e-05
step 30: loss=0.0664, lr=2.9310e-07
```

Runtime notes:

- Run completed normally and the tmux session exited.
- GPU memory returned to idle levels after completion.
- No eval loss was plotted because this SFT config only reported training metrics in LLaMAFactory output.

## Interpretation

The run successfully trains a canonical-v3 observation-grounded adapter with the same broad setup as the prior canonical-v2 fixed 1k SFT, making it suitable for a direct heldout comparison. The training loss curve drops quickly, which is expected for the deterministic canonical data; it does not by itself prove better heldout behavior. The real test is whether the new adapter improves observation faithfulness and tool-call success on the canonical-v3 clean heldout set without regressing final answer accuracy.

## Next Step

Evaluate this checkpoint on `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v3-clean` and compare against:

- canonical-v2 fixed SFT checkpoint: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v2-fixed`
- previous v3-clean eval of canonical-v2 fixed:
  `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v2-fixed-v3clean-heldout200-gpu7`

Primary metrics to compare:

- exact_match
- canonical_exact_match
- tool_call_success_rate
- observation_faithfulness_rate
- observation_coverage_avg
- hallucination_rate
