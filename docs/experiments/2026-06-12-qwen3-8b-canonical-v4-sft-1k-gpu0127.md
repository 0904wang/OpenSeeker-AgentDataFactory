# Qwen3-8B Canonical-v4 1k SFT on 4 GPUs

## Goal

Train a Qwen3-8B LoRA adapter on the canonical-v4 evidence-conditioned OpenSeeker SFT dataset. Canonical-v4 includes explicit lookup observation blocks in the user prompt, targeting the observation-faithfulness gap found in canonical-v3 evaluation.

## Remote Context

- Date: 2026-06-12
- Remote entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote workspace: `/data/wzl/OpenSeeker-AgentDataFactory`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Local config commit: `4568a12 Add canonical v4 SFT configs`
- Smoke record commit: `2541f7b Record canonical v4 SFT smoke`
- Remote sync mode: narrow config sync, because the remote experiment workspace had pre-existing dirty changes and `git pull --ff-only` was not safe.

## Inputs

- Dataset: `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_1k_canonical_v4.jsonl`
- Dataset rows: 1000
- Dataset source: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v4-generate1k/sft_conversations.jsonl`
- Dataset registry: `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/dataset_info.json`
- Config: `/data/wzl/OpenSeeker-AgentDataFactory/repo/configs/llamafactory/qwen3_8b_lora_sft_1k_canonical_v4.yaml`
- Base model: `/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218`
- GPUs: `CUDA_VISIBLE_DEVICES=0,1,2,7`
- tmux session: `openseeker-20260612-sft-canonical-v4-1k-gpu0127`

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
7, 18 MiB, 32607 MiB
```

Checkpoint path was clear before launch:

```text
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v4
```

Smoke prerequisite:

- single-GPU smoke SFT completed on GPU7
- smoke train_loss: `3.7699`
- remote v4 dataset registry and prompt checks passed

## Launch Command

```bash
tmux new-session -d -s openseeker-20260612-sft-canonical-v4-1k-gpu0127 "bash -lc 'cd /data/wzl/OpenSeeker-AgentDataFactory/repo && source /home/user/anaconda3/etc/profile.d/conda.sh && conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && export HF_HOME=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface && export TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers && export HF_HUB_OFFLINE=1 && export TRANSFORMERS_OFFLINE=1 && export PATH=/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory/bin:$PATH && CUDA_VISIBLE_DEVICES=0,1,2,7 PYTHONNOUSERSITE=1 llamafactory-cli train configs/llamafactory/qwen3_8b_lora_sft_1k_canonical_v4.yaml 2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-1k-canonical-v4-gpu0127.log'"
```

## Outputs

- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-1k-canonical-v4-gpu0127.log`
- Final checkpoint: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v4`
- Step checkpoint: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v4/checkpoint-30`
- Adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v4/adapter_model.safetensors`
- Training curve: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v4/training_loss.png`
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
  "total_flos": 8645586630737920.0,
  "train_loss": 0.6520256591339906,
  "train_runtime": 56.8618,
  "train_samples_per_second": 16.707,
  "train_steps_per_second": 0.528
}
```

Loss trace:

```text
step 5:  loss=2.7528, lr=9.7383e-05
step 10: loss=0.7570, lr=8.2369e-05
step 15: loss=0.2621, lr=5.8089e-05
step 20: loss=0.1016, lr=3.1493e-05
step 25: loss=0.0260, lr=1.0195e-05
step 30: loss=0.0126, lr=2.9310e-07
```

Runtime notes:

- Run completed normally and the tmux session exited.
- GPU memory returned to idle levels after completion.
- LLaMAFactory saved both `checkpoint-30` and the final adapter directory.
- No eval loss was plotted because this SFT config reports training metrics only.

## Interpretation

The run successfully trains a canonical-v4 evidence-conditioned adapter with the same 4-GPU Qwen3-8B LoRA setup used for canonical-v2 and canonical-v3. The training loss is lower than canonical-v3's 0.9266, which is expected because v4 exposes the lookup observations directly in the prompt and should be easier for the model to imitate.

This does not by itself prove better heldout behavior. The correct next measurement is whether the adapter improves observation faithfulness when evaluated with a v4-style prompt that includes the available lookup observations. Evaluating v4 only on the old v3-clean prompt would be an intentionally mismatched setup because the v4 training contract assumes observation conditioning.

## Next Step

Build or reuse a v4-conditioned heldout split and evaluate:

- canonical-v3 adapter with v4-style prompts
- canonical-v4 adapter with v4-style prompts

Primary comparison metrics:

- exact_match_rate
- canonical_match_rate
- tool_call_success_rate
- observation_faithfulness_rate
- observation_coverage_avg
- hallucination_rate

The key target is to move observation faithfulness meaningfully above the canonical-v3 result of 71.5% without losing 95% tool-call success.
