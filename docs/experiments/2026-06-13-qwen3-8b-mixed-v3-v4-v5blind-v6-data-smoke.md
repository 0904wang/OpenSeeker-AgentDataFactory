# Qwen3-8B Mixed v3/v4/v5blind/v6 Data Build and Smoke

## Goal

Add `canonical-v6-blind-tool-choice-hard` training pressure to the existing mixed SFT recipe, without contaminating the v6 heldout split that exposed observation-faithfulness failures.

The intended full run is:

- 800 canonical-v3 rows
- 800 canonical-v4 rows
- 400 canonical-v5-blind-hard rows
- 400 canonical-v6-blind-tool-choice-hard rows generated with `--start-index 200`

The resulting LLaMA-Factory dataset has 2400 rows.

## Local Config

Local commit:

```text
120f9ae Add v6 mixed SFT config
```

Added:

```text
configs/llamafactory/qwen3_8b_lora_sft_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice.yaml
configs/llamafactory/qwen3_8b_lora_sft_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice_smoke.yaml
runs/launch_sft_mixed_v3_v4_v5blind_v6blindtoolchoice_2p4k_gpu0127.sh
```

Updated:

```text
configs/llamafactory/dataset_info.json
```

Local verification:

```text
python -m json.tool configs/llamafactory/dataset_info.json
python -m pytest -q
```

Result:

```text
dataset_info json ok
68 passed
```

## Remote Sync and Validation

Remote entrypoint:

```text
ssh user@ssh-22.e6.luyouxia.net -p 29509
```

Remote workspace:

```text
/data/wzl/OpenSeeker-AgentDataFactory
```

Narrow synced files:

```text
configs/llamafactory/dataset_info.json
configs/llamafactory/qwen3_8b_lora_sft_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice.yaml
configs/llamafactory/qwen3_8b_lora_sft_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice_smoke.yaml
runs/launch_sft_mixed_v3_v4_v5blind_v6blindtoolchoice_2p4k_gpu0127.sh
```

Remote validation:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m json.tool configs/llamafactory/dataset_info.json >/dev/null
PYTHONNOUSERSITE=1 python -m pytest \
  tests/test_cli.py::test_cli_generate_supports_start_index_for_disjoint_variants \
  tests/test_cli.py::test_cli_generate_supports_canonical_v6_blind_tool_choice_hard_data_version -q
```

Result:

```text
..                                                                       [100%]
```

Launcher line ending and safety check:

```text
/data/wzl/OpenSeeker-AgentDataFactory/runs/launch_sft_mixed_v3_v4_v5blind_v6blindtoolchoice_2p4k_gpu0127.sh crlf_count 0 contains_forbidden False
```

## v6 Train Data Generation

User approved generating data first. No SFT was launched at this stage.

Launcher:

```text
/data/wzl/OpenSeeker-AgentDataFactory/runs/launch_generate_v6train400_start200.sh
```

Session:

```text
openseeker-20260613-generate-v6train400
```

Command:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 400 \
  --start-index 200 \
  --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_expanded.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/train-samples-400-canonical-v6-blind-tool-choice-hard-start200 \
  --strategy evol_instruct \
  --teacher-backend none \
  --data-version canonical-v6-blind-tool-choice-hard \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/train-samples-400-canonical-v6-blind-tool-choice-hard-start200.log
```

Result:

```text
OpenSeeker AgentDataFactory generation complete: accepted=400 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/train-samples-400-canonical-v6-blind-tool-choice-hard-start200
```

Artifacts:

```text
raw_generations.jsonl 1.2M
rl_rewards.jsonl 521K
samples.jsonl 1.2M
sft_conversations.jsonl 642K
summary.csv 363B
trace.jsonl 1.3M
```

## Mixed Dataset Build

Output:

```text
/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice.jsonl
```

Audit:

```text
total_rows 2400
existing_rows 2000
v6_rows 400
v6_train_heldout_overlap 0
duplicate_v6_ids 0
out_size_bytes 2677094
```

The existing 2k mix is the previously recorded `800 v3 + 800 v4 + 400 v5blind` dataset. The new audit inferred `v3:1200, v4:800, v6:400` from prompt text because v3 and v5blind do not have unique prompt markers in the final ShareGPT export; this is an audit-label limitation, not a data build change.

The v6 user-prompt leakage check was scoped to user messages only and verified that v6 training prompts do not include:

```text
Available lookup observations
P19
P17
wikidata_lookup[entity
->
Use ReAct steps with
```

Assistant messages still contain canonical ReAct tool calls, which is expected for SFT targets.

The LLaMA-Factory registry was also copied to:

```text
/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/dataset_info.json
```

## SFT Smoke Test

Command:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
export HF_HOME=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface
export TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export PATH=/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory/bin:$PATH
CUDA_VISIBLE_DEVICES=7 PYTHONNOUSERSITE=1 llamafactory-cli train \
  configs/llamafactory/qwen3_8b_lora_sft_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice_smoke.yaml \
  2>&1 | /usr/bin/tee /data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice-smoke-gpu7.log
```

Result excerpt:

```text
Loading dataset openseeker_sft_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice.jsonl...
Generating train split: 2400 examples
Num examples = 8
Total optimization steps = 1
Saving model checkpoint to /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice-smoke
train_loss = 4.4453
train_runtime = 0:00:01.05
```

One initial smoke command failed before training because `tee` was not found after PATH was overwritten. The successful retry used `/usr/bin/tee` and preserved the conda PATH correctly.

## Planned Full SFT

Full config:

```text
/data/wzl/OpenSeeker-AgentDataFactory/repo/configs/llamafactory/qwen3_8b_lora_sft_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice.yaml
```

Full launcher:

```text
/data/wzl/OpenSeeker-AgentDataFactory/runs/launch_sft_mixed_v3_v4_v5blind_v6blindtoolchoice_2p4k_gpu0127.sh
```

Planned output:

```text
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice
```

Planned log:

```text
/data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice-gpu0127.log
```

The full 4-GPU SFT has not been launched in this record. It still requires a fresh GPU preflight and explicit user approval for the exact GPU selection.

## Analysis

The data side is ready for the v6-mixed SFT experiment. The key safety property is preserved: the new v6 training rows start at index 200 and have zero ID overlap with the existing v6 heldout200 split.

The smoke test confirms that LLaMA-Factory can load the new 2400-row ShareGPT dataset, tokenize it with the local Qwen3-8B snapshot, attach LoRA, run one optimization step, and write a checkpoint.

The next experiment should train this 2.4k adapter and evaluate on v4, v5 blind-hard, and v6 blind tool-choice. The main target metric is v6 observation faithfulness, currently `0.945` for the previous mixed v3/v4/v5blind adapter.

## Next Steps

1. Run a fresh GPU preflight.
2. Launch the full 4-GPU SFT only after approval for the exact GPUs.
3. Evaluate the new adapter on v4, v5 blind-hard, and v6 blind tool-choice heldouts.
4. Record whether v6 observation faithfulness improves without regressing answer/tool metrics.
