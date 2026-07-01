# Canonical v7 Relation-diverse Train268 Generation

## Metadata

- Experiment name: canonical-v7-relation-diverse-train268-generation
- Date: 2026-07-02
- Goal: Generate a targeted v7 relation-diverse training prompt pool for the next RFT/ReST-EM pass after v7 heldout exposed relation-path failures.
- Status: success
- Operator: Codex
- Remote host: `user@ssh-22.e6.luyouxia.net -p 29509`
- Isolated worktree: `/data/wzl/OpenSeeker-AgentDataFactory/runs/repo-v7-relation-diverse-20260701`
- Commit: `d16a529`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- Number of GPUs: 0

## Commands

Preflight:

```bash
tmux ls
test -d /data/wzl/OpenSeeker-AgentDataFactory/runs/repo-v7-relation-diverse-20260701
test -d /data/wzl/OpenSeeker-AgentDataFactory/results/train-samples-400-canonical-v7-relation-diverse-start200
test -f /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_relation_diverse_v7_train.jsonl
```

Launch:

```bash
tmux new-session -d -s openseeker-20260701-v7-train400-gen \
  "bash -lc 'set -e; cd /data/wzl/OpenSeeker-AgentDataFactory/runs/repo-v7-relation-diverse-20260701; \
  source /home/user/anaconda3/etc/profile.d/conda.sh; \
  conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory; \
  PYTHONNOUSERSITE=1 python -m openseeker_factory.cli build-seeds \
    --relation-diverse \
    --out-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_relation_diverse_v7_train.jsonl; \
  PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
    --count 400 \
    --start-index 200 \
    --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_relation_diverse_v7_train.jsonl \
    --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/train-samples-400-canonical-v7-relation-diverse-start200 \
    --data-version canonical-v7-relation-diverse' \
  > /data/wzl/OpenSeeker-AgentDataFactory/logs/v7-train400-gen-start200-20260701.log 2>&1"
```

Monitoring:

```bash
tail -n 40 /data/wzl/OpenSeeker-AgentDataFactory/logs/v7-train400-gen-start200-20260701.log
cat /data/wzl/OpenSeeker-AgentDataFactory/results/train-samples-400-canonical-v7-relation-diverse-start200/summary.csv
```

## Paths

- Log path: `/data/wzl/OpenSeeker-AgentDataFactory/logs/v7-train400-gen-start200-20260701.log`
- Results path: `/data/wzl/OpenSeeker-AgentDataFactory/results/train-samples-400-canonical-v7-relation-diverse-start200`
- Seed file: `/data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_relation_diverse_v7_train.jsonl`
- Samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/train-samples-400-canonical-v7-relation-diverse-start200/samples.jsonl`
- SFT conversations: `/data/wzl/OpenSeeker-AgentDataFactory/results/train-samples-400-canonical-v7-relation-diverse-start200/sft_conversations.jsonl`

## Raw Result Summary

```text
OpenSeeker AgentDataFactory generation complete: accepted=268 rejected=132 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/train-samples-400-canonical-v7-relation-diverse-start200
```

Generation summary:

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,evidence_faithfulness_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,question_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
400,268,132,0.67,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,0,0,
```

Audit:

```text
rows 268
relations {'birthplace_country': 100, 'education_country': 56, 'employer_country': 56, 'award_country': 56}
task_types {'multi_hop_qa': 156, 'tool_use_qa': 56, 'noisy_context_retrieval_qa': 56}
versions {'canonical-v7-relation-diverse': 268}
property_id_leaks 0
lookup_template_leaks 0
trace_rows 400 passed 268 failed 132
fail_relations {'education_country': 44, 'employer_country': 44, 'award_country': 44}
fail_reasons {'not_duplicate': 132}
```

## Metrics

| Metric | Value | Notes |
| --- | ---: | --- |
| requested total | 400 | `--count 400 --start-index 200` |
| accepted | 268 | verifier-passed and non-duplicate rows |
| rejected | 132 | all rejected by `not_duplicate` |
| dedup_rate | 0.67 | unique accepted rate |
| solvability_rate | 1.0 | accepted rows |
| evidence_hit_rate | 1.0 | accepted rows |
| evidence_faithfulness_rate | 1.0 | accepted rows |
| tool_success_rate | 1.0 | accepted rows |
| trajectory_valid_rate | 1.0 | accepted rows |
| property_id_leaks | 0 | question text checked for `P19/P17/P69/P108/P166` |
| lookup_template_leaks | 0 | question text checked for `wikidata_lookup[` |

## Failures / Warnings

- The intended 400-row prompt pool collapsed to 268 unique rows because relation-diverse variants repeat after the available entity/profile template combinations.
- The accepted pool is imbalanced: `birthplace_country` has 100 rows, while `education_country`, `employer_country`, and `award_country` have 56 each.
- The output directory name keeps the original 400-row request. Downstream records should call this dataset `train268` to avoid overstating the accepted count.

## Analysis

The data quality checks passed cleanly; the limitation is coverage, not correctness. The 268 accepted rows are still useful for a focused v7 RFT sampling pass because v7 heldout failures are semantic relation-path failures, and these prompts force the model to select among birthplace, education, employer, and award intents without property ID hints.

For the resume project, this gives a concrete example of verifier-gated data generation: the factory requested 400 rows, rejected 132 duplicates, and preserved only rows with fully supported evidence, tool calls, and ReAct traces. The rejected count is also a useful engineering signal that the seed/variant space needs expansion before scaling v7 to thousands of rows.

## Next Steps

- Sample K=4 RFT candidates from the 268 accepted prompts using the current Qwen3-8B RFT-changed checkpoint.
- Run `rft-filter` and audit pass rate, changed trajectory count, and relation-wise failures.
- If the changed accepted set is useful, build a focused continued-SFT mixture and evaluate on v7 heldout200 plus v4/v5/v6 regression.
