# Qwen3-8B Canonical-v4 SFT Smoke on GPU7

## Goal

Verify that LLaMAFactory can load the canonical-v4 evidence-conditioned SFT dataset and complete a minimal Qwen3-8B LoRA SFT step before launching the full 1k-data 4-GPU run.

## Remote Context

- Date: 2026-06-12
- Remote entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote workspace: `/data/wzl/OpenSeeker-AgentDataFactory`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Local config commit: `4568a12 Add canonical v4 SFT configs`
- Remote sync mode: narrow config sync, because the remote experiment workspace had pre-existing dirty changes and `git pull --ff-only` was not safe.

## Inputs

- Dataset registry: `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/dataset_info.json`
- Dataset file: `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_1k_canonical_v4.jsonl`
- Dataset size: 1000 JSONL rows
- Smoke config: `/data/wzl/OpenSeeker-AgentDataFactory/repo/configs/llamafactory/qwen3_8b_lora_sft_1k_canonical_v4_smoke.yaml`
- Base model: `/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218`
- GPU: `CUDA_VISIBLE_DEVICES=7`

## Preflight

- Dataset registry check passed for `openseeker_sft_1k_canonical_v4`.
- Dataset rows: 1000.
- First SFT row contains the canonical-v4 copy instruction and `Available lookup observations:` user block.
- GPU7 was idle before launch.
- Smoke and full checkpoint targets did not exist before smoke launch.

## Command

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 '
  cd /data/wzl/OpenSeeker-AgentDataFactory/repo &&
  source /home/user/anaconda3/etc/profile.d/conda.sh &&
  conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory &&
  export HF_HOME=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface &&
  export TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers &&
  export HF_HUB_OFFLINE=1 &&
  export TRANSFORMERS_OFFLINE=1 &&
  export PATH=/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory/bin:$PATH &&
  CUDA_VISIBLE_DEVICES=7 PYTHONNOUSERSITE=1 llamafactory-cli train configs/llamafactory/qwen3_8b_lora_sft_1k_canonical_v4_smoke.yaml 2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-1k-canonical-v4-smoke-gpu7.log
'
```

## Outputs

- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-1k-canonical-v4-smoke-gpu7.log`
- Checkpoint: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v4-smoke`
- Checkpoint size: about 99 MiB
- Adapter file: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v4-smoke/adapter_model.safetensors`

## Metrics

```text
Num examples = 8
Total optimization steps = 1
Trainable params = 21,823,488
Trainable ratio = 0.2657%
train_loss = 3.7699
train_runtime = 0:00:01.01
train_samples_per_second = 0.984
train_steps_per_second = 0.984
```

## Observations

- LLaMAFactory successfully loaded `openseeker_sft_1k_canonical_v4.jsonl`.
- The rendered training example contains the intended v4 user block:
  `Available lookup observations`.
- The system prompt includes the intended copy constraint:
  `Observation lines must copy the provided lookup observation values exactly`.
- Offline model loading worked from the existing Qwen3-8B local snapshot.
- The smoke run wrote a LoRA adapter checkpoint, tokenizer files, trainer state, and train results under the approved checkpoint path.

## Conclusion

The canonical-v4 dataset is ready for a full Qwen3-8B LoRA SFT run. The smoke confirms that the dataset registry, JSONL format, lookup-conditioned prompt, local model path, CUDA runtime, and LLaMAFactory training path are compatible.

## Next Step

Launch the full 1k canonical-v4 SFT run after user approval, using the same 4-GPU setup as the v2/v3 controlled runs if GPUs `0,1,2,7` are still free by the project policy.
