# 2026-06-12 Canonical V2 Fixed Generate 1k

## Metadata

- Experiment name: `canonical-v2-generate1k-fixed`
- Date: 2026-06-12 Asia/Shanghai
- Goal: Generate a 1,000-sample canonical-v2 fixed SFT/RL data slice after removing synthetic-round question leakage.
- Status: success
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote branch: `main`
- Remote commit observed before launch: `7b64c03`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- tmux session: `openseeker-20260612-canonical-v2-generate1k-fixed`

## Preconditions

Before launching, the generation code was fixed and verified so repeated seed variants no longer append `Use synthesis round N`. Repeated variants now use natural constraints such as:

```text
Use the birthplace clue rather than career context.
Start from <birthplace>, then resolve the country.
Follow the two-hop evidence chain before responding.
```

The canonical tool-call contract from canonical-v2 remains:

```text
wikidata_lookup[<entity>, P19]
wikidata_lookup[<birthplace>, P17]
```

## Tests And Dry Runs

Local verification:

```text
python -m pytest tests/test_pipeline.py
21 passed

python -m pytest
51 passed
```

Remote verification after narrow sync:

```text
PYTHONNOUSERSITE=1 python -m pytest tests/test_pipeline.py
21 passed in 0.14s

PYTHONNOUSERSITE=1 python -m pytest
51 passed in 4.21s
```

Remote 1k no-write dry-run:

```text
seed_rows 180
accepted=1000 rejected=0
question_repaired=0
round_marker_questions=0
tool_success_rate=1.0
trajectory_valid_rate=1.0
example_721: Answer by chaining facts: which country is tied to the capital or location of Ada Lovelace's birthplace? Use the birthplace clue rather than career context.
```

## Commands

Narrow sync before this run:

```bash
scp -P 29509 openseeker_factory/pipeline.py \
  user@ssh-22.e6.luyouxia.net:/data/wzl/OpenSeeker-AgentDataFactory/repo/openseeker_factory/pipeline.py

scp -P 29509 tests/test_pipeline.py \
  user@ssh-22.e6.luyouxia.net:/data/wzl/OpenSeeker-AgentDataFactory/repo/tests/test_pipeline.py
```

Launch:

```bash
tmux new-session -d -s openseeker-20260612-canonical-v2-generate1k-fixed \
  "bash -lc 'cd /data/wzl/OpenSeeker-AgentDataFactory/repo && \
  source /home/user/anaconda3/etc/profile.d/conda.sh && \
  conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && \
  PYTHONNOUSERSITE=1 python -m openseeker_factory.cli build-seeds \
    --out-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_canonical_v2_1k_fixed.jsonl \
    --limit 1000 && \
  PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
    --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_canonical_v2_1k_fixed.jsonl \
    --count 1000 \
    --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate1k-fixed \
    --batch-size 100 \
    --resume \
    2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/canonical-v2-generate1k-fixed.log'"
```

## Paths

- Seed file: `/data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_canonical_v2_1k_fixed.jsonl`
- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/canonical-v2-generate1k-fixed.log`
- Results dir: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate1k-fixed`
- Samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate1k-fixed/samples.jsonl`
- SFT export: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate1k-fixed/sft_conversations.jsonl`
- RL export: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate1k-fixed/rl_rewards.jsonl`
- Trace: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate1k-fixed/trace.jsonl`
- Summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate1k-fixed/summary.csv`
- Local record: `D:\resume\Data synthesis\docs\experiments\2026-06-12-canonical-v2-generate1k-fixed.md`

## Raw Result Summary

Generation log:

```text
batch complete: completed=900/1000 accepted=900 rejected=0
batch complete: completed=1000/1000 accepted=1000 rejected=0
OpenSeeker AgentDataFactory generation complete: accepted=1000 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v2-generate1k-fixed
```

`summary.csv`:

```text
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,evidence_faithfulness_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,question_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
1000,1000,0,1.0,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,0,0,
```

Output sizes:

```text
raw_generations.jsonl      1.4M
samples.jsonl              1.6M
sft_conversations.jsonl    587K
rl_rewards.jsonl           404K
trace.jsonl                1.6M
summary.csv                365B
```

## Audit Metrics

| Metric | Value | Notes |
| --- | ---: | --- |
| seed rows | 180 | Seed bank currently has 180 task rows; 1k repeats them with natural variants |
| samples | 1000 | Generated target size |
| sft_lines | 1000 | LLaMAFactory-ready export |
| rl_lines | 1000 | Reward export |
| trace_lines | 1000 | Full trace export |
| accepted | 1000 | All rows passed verifier |
| rejected | 0 | No rejected rows |
| multi_hop_qa | 334 | Task distribution |
| tool_use_qa | 333 | Task distribution |
| noisy_context_retrieval_qa | 333 | Task distribution |
| canonical_tool_rows | 1000 | All `tool_calls` use `P19/P17` |
| canonical_action_rows | 1000 | All trajectory Action lines use `P19/P17` |
| P19 actions | 1000 | One per sample |
| P17 actions | 1000 | One per sample |
| question_repaired_sources | 0 | Fixed from previous dry-run issue |
| round_marker_questions | 0 | No `Use synthesis round` leakage |
| duplicate_questions | 0 | Dedup verifier passed |
| noncanonical_count | 0 | No non-canonical Action lines |
| quality_score 1.0 rows | 1000 | All rows scored 1.0 |

Representative repeated-variant sample:

```text
Question: Answer by chaining facts: which country is tied to the capital or location of Ada Lovelace's birthplace? Use the birthplace clue rather than career context.
Tool calls: ['Ada Lovelace, P19', 'London, P17']
Trajectory:
Thought: Identify the entity's birthplace.
Action: wikidata_lookup[Ada Lovelace, P19]
Observation: London
Thought: Resolve the country from the intermediate location.
Action: wikidata_lookup[London, P17]
Observation: United Kingdom
Final: United Kingdom
```

## Failures / Warnings

- No runtime failure occurred.
- No GPU was used.
- `build-seeds --limit 1000` writes only 180 rows because the current seed bank contains 60 entities times 3 task variants. The 1k generation intentionally repeats those seeds with variant questions. This should be described as 1k generated samples over a 180-row seed bank, not 1k independent seed entities.

## Analysis

This run produces the first clean 1k canonical-v2 SFT/RL slice. It fixes both issues observed in earlier data:

- Natural property tool drift: all tool calls and Action lines now use canonical `P19/P17`.
- Synthetic-round leakage: repeated variants now use natural constraints and require no question repair.

This data is better suited for the next SFT than the previous cleaned 1k, because it directly teaches the verifier-preferred tool-call format. The next model-quality question is whether training on this data improves held-out `tool_call_success_rate` without losing the strong final-answer behavior from the cleaned adapter.

## Next Steps

- Copy/export `sft_conversations.jsonl` into the LLaMAFactory dataset registry as a new dataset, for example `openseeker_sft_1k_canonical_v2_fixed`.
- Run a 4-GPU Qwen3-8B LoRA SFT using the same training recipe as the previous cleaned 1k run.
- Evaluate on the heldout200 split and compare against:
  - old 1k LoRA rescore v2
  - cleaned 1k LoRA
  - canonical-v2 fixed 1k LoRA
