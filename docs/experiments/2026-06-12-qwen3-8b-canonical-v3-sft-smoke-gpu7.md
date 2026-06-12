# Qwen3-8B Canonical-v3 SFT Smoke on GPU7

## Goal

Verify that LLaMAFactory can load the canonical-v3 observation-grounded SFT dataset and complete a minimal Qwen3-8B LoRA SFT step before launching the full 1k-data 4-GPU run.

## Remote Context

- Date: 2026-06-12
- Remote entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote workspace: `/data/wzl/OpenSeeker-AgentDataFactory`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Local commit with config: `80e8125 Add canonical v3 SFT configs`
- Remote repo status: dirty pre-existing experiment workspace; config was synced by narrow file sync instead of `git pull --ff-only`

## Inputs

- Dataset registry: `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/dataset_info.json`
- Dataset file: `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_1k_canonical_v3.jsonl`
- Dataset size: 1000 JSONL rows
- Smoke config: `/data/wzl/OpenSeeker-AgentDataFactory/repo/configs/llamafactory/qwen3_8b_lora_sft_1k_canonical_v3_smoke.yaml`
- Base model: `/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218`
- GPU: `CUDA_VISIBLE_DEVICES=7`

## Preflight Evidence

GPU memory before smoke:

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

Remote pipeline smoke:

```text
tests/test_pipeline.py: 22 passed
```

Dataset registration check:

```text
registry ok: openseeker_sft_1k_canonical_v3.jsonl
rows ok: 1000
system prompt ok
```

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
  CUDA_VISIBLE_DEVICES=7 PYTHONNOUSERSITE=1 llamafactory-cli train configs/llamafactory/qwen3_8b_lora_sft_1k_canonical_v3_smoke.yaml 2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-1k-canonical-v3-smoke-gpu7.log
'
```

## Outputs

- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-1k-canonical-v3-smoke-gpu7.log`
- Checkpoint: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v3-smoke`
- Checkpoint size: about 99 MiB
- Adapter file: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v3-smoke/adapter_model.safetensors`

## Metrics

```text
Num examples = 8
Total optimization steps = 1
Trainable params = 21,823,488
Trainable ratio = 0.2657%
train_loss = 4.4453
train_runtime = 0:00:00.98
train_samples_per_second = 1.012
train_steps_per_second = 1.012
```

## Observations

- LLaMAFactory successfully loaded `openseeker_sft_1k_canonical_v3.jsonl`.
- The first rendered training example contains the intended grounding prompt:
  `Observation lines must match lookup observations from the evidence instead of memorized or localized facts.`
- The example trajectory uses canonical lookup actions and grounded observations:
  `wikidata_lookup[Ada Lovelace, P19] -> London` and `wikidata_lookup[London, P17] -> United Kingdom`.
- Offline model loading worked from the existing Qwen3-8B local snapshot.
- The smoke run wrote a LoRA adapter checkpoint, tokenizer files, trainer state, and train results under the approved checkpoint path.

## Conclusion

The canonical-v3 dataset is ready for a full Qwen3-8B LoRA SFT run. The smoke confirms that the dataset registry, JSONL format, prompt template, local model path, CUDA runtime, and LLaMAFactory training path are compatible.

## Next Step

Launch the full 1k canonical-v3 SFT run after user approval, preferably on GPUs `0,1,2,7` if the pre-launch GPU check still shows those devices under the 4000 MiB free threshold policy. After training, evaluate against the canonical-v3 clean heldout set and compare with the canonical-v2 fixed checkpoint.
