# 2026-06-12 Canonical V2 Generate 100 Fixed Variant Index

## Metadata

- Experiment name: `canonical-v2-generate100-fixed`
- Date: 2026-06-12 Asia/Shanghai
- Goal: Fix the `seed_expand` variant-index logic that caused unnecessary `question_repaired` rows, then regenerate a 100-sample canonical-v2 data slice.
- Status: success
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- tmux session: `openseeker-20260612-canonical-v2-generate100-fixed`

## Code Change Summary

`seed_expand` previously used the global generated row number as `variant_index`. For a 100-row seed file with unique seed rows, this made rows after the fourth template variant look like repeated synthesis rounds, so the question repair pass stripped `Use synthesis round N` from 96 rows.

The fix keeps global numbering for sample IDs but changes `variant_index` to the per-base-seed repetition count:

```text
id index: global index + 1
variant_index: floor(global index / number_of_base_seeds) + 1
```

For a unique 100-row seed file, every row now has `variant_index=1`; repeated generation over a smaller seed set still advances the per-seed variant count.

## Tests

Local verification:

```text
python -m pytest tests/test_pipeline.py
21 passed in 0.26s

python -m pytest
51 passed in 15.80s
```

Remote verification after narrow sync:

```text
PYTHONNOUSERSITE=1 python -m pytest tests/test_pipeline.py
21 passed in 0.14s

PYTHONNOUSERSITE=1 python -m pytest
51 passed in 4.18s
```

Remote no-write diagnostic:

```text
{'total': 100, 'accepted': 100, 'rejected': 0, 'dedup_rate': 1.0, 'solvability_rate': 1.0, 'evidence_hit_rate': 1.0, 'evidence_faithfulness_rate': 1.0, 'tool_success_rate': 1.0, 'trajectory_valid_rate': 1.0, 'teacher_attempted': 0, 'teacher_succeeded': 0, 'teacher_failed': 0, 'teacher_fallback_rate': 0.0, 'teacher_trajectory_repaired': 0, 'question_repaired': 0, 'teacher_difficulty_normalized': 0, 'manual_sample_pass_rate': None}
variant_prefix [1, 1, 1, 1, 1, 1]
```

## Commands

Narrow sync:

```bash
scp -P 29509 openseeker_factory/pipeline.py \
  user@ssh-22.e6.luyouxia.net:/data/wzl/OpenSeeker-AgentDataFactory/repo/openseeker_factory/pipeline.py

scp -P 29509 tests/test_pipeline.py \
  user@ssh-22.e6.luyouxia.net:/data/wzl/OpenSeeker-AgentDataFactory/repo/tests/test_pipeline.py
```

Launch:

```bash
tmux new-session -d -s openseeker-20260612-canonical-v2-generate100-fixed \
  "bash -lc 'cd /data/wzl/OpenSeeker-AgentDataFactory/repo && \
  source /home/user/anaconda3/etc/profile.d/conda.sh && \
  conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && \
  PYTHONNOUSERSITE=1 python -m openseeker_factory.cli build-seeds \
    --out-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_canonical_v2_100_fixed.jsonl \
    --limit 100 && \
  PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
    --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_canonical_v2_100_fixed.jsonl \
    --count 100 \
    --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate100-fixed \
    --batch-size 50 \
    --resume \
    2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/canonical-v2-generate100-fixed.log'"
```

## Paths

- Seed file: `/data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_canonical_v2_100_fixed.jsonl`
- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/canonical-v2-generate100-fixed.log`
- Results dir: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate100-fixed`
- Samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate100-fixed/samples.jsonl`
- SFT export: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate100-fixed/sft_conversations.jsonl`
- RL export: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate100-fixed/rl_rewards.jsonl`
- Trace: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate100-fixed/trace.jsonl`
- Summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate100-fixed/summary.csv`
- Local record: `D:\resume\Data synthesis\docs\experiments\2026-06-12-canonical-v2-generate100-fixed.md`

## Raw Result Summary

Log excerpt:

```text
batch complete: completed=50/100 accepted=50 rejected=0
batch complete: completed=100/100 accepted=100 rejected=0
OpenSeeker AgentDataFactory generation complete: accepted=100 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate100-fixed
```

`summary.csv`:

```text
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,evidence_faithfulness_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,question_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
100,100,0,1.0,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,0,0,
```

## Audit Metrics

| Metric | Value | Notes |
| --- | ---: | --- |
| samples | 100 | Seed-bank slice |
| sft_lines | 100 | SFT export line count |
| accepted | 100 | All rows passed verifier |
| rejected | 0 | No rejected rows |
| multi_hop_qa | 34 | Task distribution |
| tool_use_qa | 33 | Task distribution |
| noisy_context_retrieval_qa | 33 | Task distribution |
| canonical_tool_rows | 100 | All `tool_calls` use `P19/P17` |
| canonical_action_rows | 100 | All trajectory Action lines use `P19/P17` |
| P19 actions | 100 | One per sample |
| P17 actions | 100 | One per sample |
| question_repaired_sources | 0 | Fixed from previous 96 |
| round_marker_questions | 0 | No `Use synthesis round` leakage |
| noncanonical_count | 0 | No non-canonical Action lines |
| quality_score 1.0 rows | 100 | All rows scored 1.0 |

Representative sample:

```text
Question: Use the available lookup tool to identify the present-day country associated with Marie Curie's birthplace.
Tool calls: ['Marie Curie, P19', 'Warsaw, P17']
Trajectory:
Thought: Identify the entity's birthplace.
Action: wikidata_lookup[Marie Curie, P19]
Observation: Warsaw
Thought: Resolve the country from the intermediate location.
Action: wikidata_lookup[Warsaw, P17]
Observation: Poland
Final: Poland
```

## Failures / Warnings

- An initial remote no-write diagnostic failed because PowerShell-to-SSH heredoc quoting stripped Python string quotes. The code tests had already passed, and the diagnostic was rerun via stdin successfully.
- No generation failure occurred.
- No GPU was used.

## Analysis

The template repair issue is fixed. The previous canonical-v2 100-row run had good canonical tool metrics but `question_repaired=96`, which meant many questions were generated with synthetic-round markers and repaired afterward. This fixed run keeps the same canonical tool behavior while reducing `question_repaired` to 0.

This is now a cleaner source slice for scaling. It avoids teaching artificial synthesis-round wording and keeps the tool-use supervision aligned with the stricter `P19/P17` verifier. The next training experiment should use a larger fixed canonical-v2 SFT export rather than the earlier repaired-after-the-fact slice.

## Next Steps

- Generate canonical-v2 fixed 1k data.
- Export it to LLaMAFactory and train a new Qwen3-8B LoRA adapter.
- Re-run heldout200 evaluation and compare `tool_call_success_rate`, `tool_coverage_gap_rate`, `final_answer_rate`, and exact match against the cleaned 1k adapter.
