# Qwen3-8B Mixed v3/v4/v5blind SFT Data Build and Smoke

## Goal

Prepare a mixed SFT training set that preserves the easy canonical behavior from v3, the exposed-observation tool contract from v4, and the blind hard generalization pressure from v5. Run a LLaMAFactory smoke test before launching the full SFT job.

The intended full run is:

- 800 canonical-v3 SFT rows
- 800 canonical-v4 SFT rows
- 400 canonical-v5-blind-hard SFT rows generated from a disjoint seed index range
- Qwen3-8B LoRA SFT with LLaMAFactory

## Remote Context

- Date: 2026-06-12
- Remote entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote workspace: `/data/wzl/OpenSeeker-AgentDataFactory`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Local code commit: `86772e0 Add mixed v3 v4 v5blind SFT config`
- Remote sync mode: narrow file sync, because the remote repo has pre-existing dirty changes and is not safe for `git pull --ff-only`

## Code and Config

Local commit `86772e0` added:

- `generate --start-index` support for disjoint train/heldout sample generation
- LLaMAFactory dataset registry entry `openseeker_sft_2k_mixed_v3_v4_v5blind`
- full SFT config: `configs/llamafactory/qwen3_8b_lora_sft_2k_mixed_v3_v4_v5blind.yaml`
- smoke config: `configs/llamafactory/qwen3_8b_lora_sft_2k_mixed_v3_v4_v5blind_smoke.yaml`
- full launcher: `/data/wzl/OpenSeeker-AgentDataFactory/runs/launch_sft_mixed_v3_v4_v5blind_2k_gpu0127.sh`
- evaluation launchers for v4 heldout and v5 blind-hard heldout

Remote validation:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m pytest tests/test_cli.py::test_cli_generate_supports_start_index_for_disjoint_variants -q
PYTHONNOUSERSITE=1 python -m json.tool configs/llamafactory/dataset_info.json >/dev/null
```

Result:

```text
.                                                                        [100%]
```

## v5 Blind-hard Training Data

Command:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 400 \
  --start-index 200 \
  --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_expanded.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/train-samples-400-canonical-v5-blind-hard-start200 \
  --strategy evol_instruct \
  --teacher-backend none \
  --data-version canonical-v5-blind-hard \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/train-samples-400-canonical-v5-blind-hard-start200.log
```

Result:

```text
OpenSeeker AgentDataFactory generation complete: accepted=400 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/train-samples-400-canonical-v5-blind-hard-start200
```

Audit:

```text
samples.jsonl 400
sft_conversations.jsonl 400
rl_rewards.jsonl 400
trace.jsonl 400
summary.csv:
400,400,0,1.0,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,0,0,
heldout_overlap_count 0
data_versions Counter({'canonical-v5-blind-hard': 400})
task_types Counter({'noisy_context_retrieval_qa': 134, 'multi_hop_qa': 133, 'tool_use_qa': 133})
```

The `--start-index 200` split keeps this train set disjoint from the 200-row v5 blind-hard heldout set generated from the default start index.

## Mixed Dataset Build

Output:

```text
/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_2k_mixed_v3_v4_v5blind.jsonl
```

Mix:

```text
total_rows 2000
source_counts {'v3': 800, 'v4': 800, 'v5blind': 400}
duplicate_ids 0
lookup_block_user_messages 800
arrow_in_v5_user_messages 0
missing_messages 0
bad_roles 0
```

Notes:

- The 800 lookup-block prompts are expected from canonical-v4.
- The v5 blind-hard rows do not expose `->` path answers in the user prompt.
- LLaMAFactory registry was also copied to `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/dataset_info.json`.

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
CUDA_VISIBLE_DEVICES=7 PYTHONNOUSERSITE=1 \
  /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory/bin/llamafactory-cli train \
  configs/llamafactory/qwen3_8b_lora_sft_2k_mixed_v3_v4_v5blind_smoke.yaml \
  2>&1 | /usr/bin/tee /data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-2k-mixed-v3-v4-v5blind-smoke-gpu7.log
```

Result:

```text
Num examples = 8
Total optimization steps = 1
trainable params: 21,823,488 || all params: 8,212,558,848 || trainable%: 0.2657
train_loss = 4.4453
train_runtime = 0:00:01.00
Saving model checkpoint to /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2k-mixed-v3-v4-v5blind-smoke
```

This proves that the mixed dataset registry, offline Qwen3-8B snapshot, LoRA setup, and checkpoint writing path are usable.

## Full SFT Launch Status

Planned full launch:

```bash
tmux new-session -d -s openseeker-20260612-sft-mixed-v3-v4-v5blind-2k-gpu0127 \
  "bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_sft_mixed_v3_v4_v5blind_2k_gpu0127.sh"
```

Planned full config:

```text
dataset: openseeker_sft_2k_mixed_v3_v4_v5blind
max_samples: 2000
output_dir: /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2k-mixed-v3-v4-v5blind
log: /data/wzl/OpenSeeker-AgentDataFactory/logs/qwen3-8b-openseeker-sft-2k-mixed-v3-v4-v5blind-gpu0127.log
CUDA_VISIBLE_DEVICES=0,1,2,7
```

The full 4-GPU SFT was not launched because the GPU preflight failed the project rule that a GPU counts as free only below `4000 MiB`.

Observed GPU state:

```text
0, 4293 MiB, 32607 MiB, 0 %
1, 4293 MiB, 32607 MiB, 0 %
2, 4295 MiB, 32607 MiB, 0 %
3, 25985 MiB, 32607 MiB, 0 %
4, 26101 MiB, 32607 MiB, 0 %
5, 4281 MiB, 32607 MiB, 0 %
6, 4293 MiB, 32607 MiB, 0 %
7, 806 MiB, 32607 MiB, 0 %
```

Process attribution:

```text
GPU0/1/2/5/6/7: spt_known_optimized_experiment.py, parent 1481397, elapsed about 38 minutes
GPU3/4: scripts/launch_local_server.py deepseek-moe-16b-sft, elapsed over 2 days
```

Per `AGENTS.md`, the mixed 4-GPU SFT should only be launched when the selected cards satisfy the memory rule and after the exact launch payload is approved.

## Analysis

The data side is ready for the mixed SFT experiment. The smoke result removes the main configuration risk: LLaMAFactory can load the 2k dataset, tokenize it, instantiate Qwen3-8B from local cache, attach LoRA, run one optimization step, and save a checkpoint.

The remaining blocker is scheduling, not implementation. GPU7 alone is free enough for short smoke/eval jobs, but the requested 4-card SFT route using 0/1/2/7 is currently blocked because 0/1/2 exceed the free-memory threshold and are tied to an unrelated 6-GPU training job.

## Next Steps

Recommended next action:

1. Wait until GPUs `0,1,2,7` are below `4000 MiB`, then launch the planned tmux job.
2. After training, evaluate the mixed adapter on both:
   - v4 heldout: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v4/samples.jsonl`
   - v5 blind-hard heldout: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v5-blind-hard/samples.jsonl`
3. Compare against the strongest previous results:
   - v4 heldout: canonical-v4 SFT reached exact/canonical/tool/obs/correct = 1.0
   - v5 blind-hard: canonical-v3 SFT reached exact 0.930, canonical 1.000, tool_success 1.000, observation_faithfulness 0.930, correct 0.930

Fallback option:

- Run the same 2k mixed LoRA SFT on GPU7 only. This will take longer, but it avoids interfering with the unrelated 6-GPU job. It should be treated as a separate approved run with a separate launcher, log path, and experiment record.
