# Canonical-v3 1k data generation

Date: 2026-06-12

## Goal

Generate a 1k canonical-v3 SFT/RL dataset that explicitly trains observation faithfulness: actions use canonical Wikidata property IDs and observations must match the gold lookup results instead of memorized or localized facts.

## Local Code Changes

- Plan: `D:\resume\Data synthesis\docs\superpowers\plans\2026-06-12-canonical-v3-data.md`
- Modified: `D:\resume\Data synthesis\openseeker_factory\pipeline.py`
- Modified: `D:\resume\Data synthesis\tests\test_pipeline.py`

New sample metadata:

- `source.data_version = canonical-v3`
- `source.observation_grounding = gold_tool_results`
- `source.observation_grounding_policy = observations_must_match_expected_tool_results`
- `verifier_result.checks.observation_faithfulness`

SFT system prompt now explicitly says observations must match lookup observations from evidence rather than memorized or localized facts.

Local verification:

```text
python -m pytest tests/test_pipeline.py -q
22 passed

python -m pytest -q
53 passed
```

## Remote Context

- SSH: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Seed file: `/data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_expanded.jsonl`
- Seed rows: 120
- Remote tests after narrow sync:

```text
tests/test_pipeline.py: 22 passed in 0.14s
full pytest: 53 passed in 4.26s
```

## Smoke

The first smoke SSH attempt timed out before connection. The exact same command succeeded on one retry.

Command:

```bash
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 3 \
  --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_expanded.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v3-generate3-smoke \
  --strategy evol_instruct \
  --teacher-backend none
```

Smoke audit:

```text
samples 3
source_versions ['canonical-v3']
grounding ['gold_tool_results']
obs_checks [True, True, True]
sft_prompt_contains True
accepted=3 rejected=0
solvability=1.0 evidence_hit=1.0 evidence_faithfulness=1.0 tool_success=1.0 trajectory_valid=1.0
```

## Formal Generation

Command:

```bash
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 1000 \
  --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_expanded.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v3-generate1k \
  --strategy evol_instruct \
  --teacher-backend none \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/canonical-v3-generate1k.log
```

Outputs:

- Results dir: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v3-generate1k`
- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/canonical-v3-generate1k.log`
- Samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v3-generate1k/samples.jsonl`
- SFT: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v3-generate1k/sft_conversations.jsonl`
- RL: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v3-generate1k/rl_rewards.jsonl`
- Trace: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v3-generate1k/trace.jsonl`
- Summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v3-generate1k/summary.csv`

## Audit

```text
samples 1000
sft_lines 1000
rl_lines 1000
trace_lines 1000
task_type {'multi_hop_qa': 334, 'tool_use_qa': 333, 'noisy_context_retrieval_qa': 333}
source_versions {'canonical-v3': 1000}
grounding {'gold_tool_results': 1000}
obs_check_true 1000
obs_check_missing 0
sft_prompt_grounding 1000
rl_obs_check_true 1000
canonical_p19 1000
canonical_p17 1000
round_marker 0
duplicate_questions 0
quality_scores {1.0: 1000}
```

Summary:

```text
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,evidence_faithfulness_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,question_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
1000,1000,0,1.0,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,0,0,
```

## Analysis

The generated v3 dataset meets the mechanical target: every row has canonical `P19/P17` tool calls, gold observation grounding metadata, a verifier check for observation faithfulness, and an SFT system prompt that tells the model not to substitute memorized or localized facts.

This dataset is still deterministic and based on the current 120-row seed file repeated to 1k. It is appropriate for a 1k ablation run against canonical-v2 fixed1k, but not yet enough to claim broad data diversity. The next result should be judged by heldout behavior, especially `observation_faithfulness_rate`, not by generation summary alone.

## Next Steps

1. Register `openseeker_sft_1k_canonical_v3` in LLaMAFactory dataset config.
2. Copy `sft_conversations.jsonl` into `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_1k_canonical_v3.jsonl`.
3. Run a smoke SFT with Qwen3-8B.
4. If smoke passes, run 4-GPU LoRA SFT.
5. Evaluate the v3 adapter on `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v3-clean/samples.jsonl`.
