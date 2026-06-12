# 2026-06-12 Canonical V2 Generate 100

## Metadata

- Experiment name: `canonical-v2-generate100`
- Date: 2026-06-12 Asia/Shanghai
- Goal: Generate a 100-sample cleaned-v2 data slice after enforcing canonical Wikidata tool calls in generation and teacher-trajectory verification.
- Status: success
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Code sync: narrow file sync for `openseeker_factory/pipeline.py` and `tests/test_pipeline.py`
- GPU selection: none
- tmux session: `openseeker-20260612-canonical-v2-generate100`

## Code Change Summary

The generation path was updated before this run:

- Default `tool_plan` now uses canonical queries:
  - `wikidata_lookup[<entity>, P19]`
  - `wikidata_lookup[<birthplace>, P17]`
- Deterministic trajectories now emit the same canonical action queries.
- Teacher-drafted trajectories are rejected and repaired if they contain the expected observations but do not cover the expected canonical tool calls.
- The generation verifier's `tool_success` now requires both the answer tool result and exact canonical tool-call coverage.

## Preflight And Tests

Local verification:

```text
python -m pytest
50 passed in 16.17s
```

Remote verification after narrow sync:

```text
PYTHONNOUSERSITE=1 python -m pytest tests/test_pipeline.py
20 passed in 0.14s

PYTHONNOUSERSITE=1 python -m pytest
50 passed in 4.42s
```

Remote dry-run sample check:

```json
"tool_calls": [
  {"tool": "wikidata_lookup", "query": "Ada Lovelace, P19", "result": "London"},
  {"tool": "wikidata_lookup", "query": "London, P17", "result": "United Kingdom"}
]
```

Dry-run trajectory:

```text
Action: wikidata_lookup[Ada Lovelace, P19]
Action: wikidata_lookup[London, P17]
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
tmux new-session -d -s openseeker-20260612-canonical-v2-generate100 \
  "bash -lc 'cd /data/wzl/OpenSeeker-AgentDataFactory/repo && \
  source /home/user/anaconda3/etc/profile.d/conda.sh && \
  conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && \
  PYTHONNOUSERSITE=1 python -m openseeker_factory.cli build-seeds \
    --out-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_canonical_v2_100.jsonl \
    --limit 100 && \
  PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
    --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_canonical_v2_100.jsonl \
    --count 100 \
    --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate100 \
    --batch-size 50 \
    --resume \
    2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/canonical-v2-generate100.log'"
```

Monitoring:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 '
  tmux list-sessions 2>/dev/null || true &&
  ps -u user -o pid,etime,pcpu,pmem,cmd | grep "openseeker_factory.cli" | grep -v grep || true &&
  tail -n 80 /data/wzl/OpenSeeker-AgentDataFactory/logs/canonical-v2-generate100.log &&
  ls -lah /data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate100
'
```

## Paths

- Seed file: `/data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_canonical_v2_100.jsonl`
- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/canonical-v2-generate100.log`
- Results dir: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate100`
- Samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate100/samples.jsonl`
- SFT export: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate100/sft_conversations.jsonl`
- RL export: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate100/rl_rewards.jsonl`
- Trace: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate100/trace.jsonl`
- Summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate100/summary.csv`
- Local record: `D:\resume\Data synthesis\docs\experiments\2026-06-12-canonical-v2-generate100.md`

## Raw Result Summary

```text
OpenSeeker AgentDataFactory generation complete: accepted=100 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate100
```

`summary.csv`:

```text
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,evidence_faithfulness_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,question_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
100,100,0,1.0,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,96,0,
```

Result files:

```text
raw_generations.jsonl 153K
rl_rewards.jsonl       38K
samples.jsonl         171K
sft_conversations.jsonl 56K
summary.csv           364B
trace.jsonl           177K
```

## Audit Metrics

| Metric | Value | Notes |
| --- | ---: | --- |
| total | 100 | Seed-bank slice |
| accepted | 100 | All generated rows passed verifier |
| rejected | 0 | No rejects |
| task multi_hop_qa | 34 | Balanced by seed task order |
| task tool_use_qa | 33 | Balanced by seed task order |
| task noisy_context_retrieval_qa | 33 | Balanced by seed task order |
| tool_call_canonical_rows | 100 | All `tool_calls` are `P19/P17` |
| trajectory_action_canonical_rows | 100 | All generated Action lines are `P19/P17` |
| trajectory P19 actions | 100 | One per sample |
| trajectory P17 actions | 100 | One per sample |
| tool_success_rate | 1.0 | Requires canonical action coverage after this patch |
| trajectory_valid_rate | 1.0 | All rows have ReAct + Final |
| evidence_faithfulness_rate | 1.0 | Observations match expected evidence |
| quality_score 1.0 rows | 100 | All rows scored 1.0 |
| question_repaired | 96 | See notes below |

Non-canonical action examples:

```text
[]
```

## First Sample

```json
{
  "id": "wikidata-ada-lovelace-multi-hop-1",
  "task_type": "multi_hop_qa",
  "answer": "United Kingdom",
  "tool_calls": [
    {"tool": "wikidata_lookup", "query": "Ada Lovelace, P19", "result": "London"},
    {"tool": "wikidata_lookup", "query": "London, P17", "result": "United Kingdom"}
  ],
  "trajectory": [
    "Thought: Identify the entity's birthplace.",
    "Action: wikidata_lookup[Ada Lovelace, P19]",
    "Observation: London",
    "Thought: Resolve the country from the intermediate location.",
    "Action: wikidata_lookup[London, P17]",
    "Observation: United Kingdom",
    "Final: United Kingdom"
  ]
}
```

## Failures / Warnings

- No generation failure occurred.
- The command pipes only the `generate` command through `tee`; the preceding `build-seeds` completion line is not in the log. The seed file was verified separately with `wc -l`.
- `question_repaired=96` is high because `seed_expand` uses a global `variant_index`; for a 100-row seed file, variants after the first four receive `Use synthesis round N`, then the question repair pass strips that marker. The exported questions are repaired, but this is a signal that the template/variant-index logic should be cleaned up.

## Analysis

This run confirms the cleaned-v2 generation change fixes the specific failure mode found in the held-out evaluation: tool calls no longer drift into natural property names such as `birthplace` or `country`. The generated SFT rows now explicitly teach canonical `P19/P17` Action calls, and the verifier rejects or repairs teacher trajectories that do not follow that tool contract.

The result is suitable as a small data-quality milestone, not yet as a model-quality claim. It proves the factory can produce a canonicalized 100-row slice with perfect deterministic verifier metrics. The next useful experiment is to scale the canonicalized generation to 1k or mix it with teacher-generated questions, then run SFT/evaluation to see whether held-out `tool_call_success_rate` improves without losing the perfect `Final` answer behavior seen in the cleaned 1k adapter.

The high question repair count should be addressed before scaling too far, because it indicates many questions are repaired after generation rather than generated correctly on the first pass. That does not invalidate this data slice, but it is not the cleanest production behavior.

## Next Steps

- Fix `seed_expand` or question templating so unique seed-file rows do not trigger synthetic-round markers.
- Generate a canonical-v2 1k dataset after the template cleanup.
- Export canonical-v2 SFT data to LLaMAFactory and run a small LoRA SFT.
- Re-evaluate heldout200 and compare specifically on `tool_call_success_rate` and `tool_coverage_gap_rate`.
