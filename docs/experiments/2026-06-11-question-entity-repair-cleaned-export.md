# 2026-06-11 Question Entity Repair Cleaned Export

## Goal

Fix the quality gap found in the 1k audit: samples could pass evidence/trajectory verification while the user-facing question mentioned the wrong entity or exposed deterministic template markers such as `Use synthesis round N`.

## Code Change

Implemented question-level repair and verification in `openseeker_factory/pipeline.py`:

- Added `question_entity_alignment` verifier check.
- Added `question_repaired` metric in `summary.csv`.
- If a question misses the expected entity, contains a different known seed entity, or contains `Use synthesis round`, the factory rewrites the question from the seed/tool plan.
- The repair is applied both during generation and inside `verify_and_filter`, so existing `raw_generations.jsonl` can be re-exported without calling the teacher API again.
- Repaired samples record:
  - `source.question_repaired=true`
  - `source.question_repair_reason=entity_alignment` or `synthetic_round_marker`
  - `source.original_question=<raw question>`

## Tests

Local:

```text
python -m pytest tests/test_pipeline.py
18 passed in 0.18s

python -m pytest tests/test_cli.py tests/test_pipeline.py
26 passed in 4.29s

python -m pytest
48 passed in 16.98s
```

Remote:

```text
python -m pytest tests/test_pipeline.py tests/test_cli.py
26 passed in 1.31s

python -m pytest
48 passed in 4.21s
```

## Cleaned Re-Export

No new API calls were made. The original raw generations were copied and re-exported through the updated verifier:

```bash
src=/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611/raw_generations.jsonl
dst_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611-cleaned
mkdir -p "$dst_dir"
cp "$src" "$dst_dir/raw_generations.jsonl"

cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 1000 \
  --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_expanded.jsonl \
  --out-dir "$dst_dir" \
  --strategy magpie_self_instruct \
  --teacher-backend none \
  --batch-size 100 \
  --resume
```

Cleaned summary:

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,evidence_faithfulness_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,question_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
1000,1000,0,1.0,1.0,1.0,1.0,1.0,1.0,1000,978,22,0.022,11,26,34,
```

## Cleaned Audit

Structural audit:

```json
{
  "total": 1000,
  "issue_rows": 461,
  "issue_counts": {
    "question_not_question_mark": 461
  },
  "quality_scores": {
    "1.0": 1000
  },
  "verifier_passed": 1000,
  "react_shape_passed": 1000,
  "tool_results_covered": 1000,
  "answer_supported": 1000
}
```

Entity alignment audit:

```json
{
  "total": 1000,
  "rows_with_any_issue": 0,
  "issue_counts": {},
  "expected_entity_missing_rows": 0,
  "foreign_entity_rows": 0,
  "repaired_rows": 11,
  "repaired_rows_with_alignment_issue": 0,
  "fallback_rows": 22,
  "fallback_rows_with_synthetic_round_marker": 0,
  "duplicate_rewrite_rows": 423,
  "duplicate_rewrite_rows_with_foreign_entity": 0
}
```

## Remote Artifacts

- Cleaned result dir: `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611-cleaned`
- Cleaned SFT file: `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611-cleaned/sft_conversations.jsonl`
- Cleaned RL file: `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611-cleaned/rl_rewards.jsonl`
- Cleaned trace: `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611-cleaned/trace.jsonl`
- Cleaned summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611-cleaned/summary.csv`
- Cleaned quality audit: `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611-cleaned/quality_audit_20260611_summary.json`
- Cleaned entity audit: `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611-cleaned/entity_alignment_audit_20260611_summary.json`

## Analysis

The main SFT-blocking issue from the previous audit is fixed. The cleaned 1k export has:

- 1,000 accepted samples
- 0 rejected samples
- 26 question repairs
- 0 entity alignment issues
- 0 synthetic round markers
- 100% verifier/evidence/tool/trajectory pass rates

The remaining 461 `question_not_question_mark` rows are mostly command-style prompts, not factual errors. They are acceptable for an agent SFT dataset, but if the dataset should look like a pure QA benchmark, a later style-normalization pass can convert those prompts into question-form text.

## Next Step

Use the cleaned 1k as the SFT candidate, or run one more style-normalization pass if we want all user prompts to be interrogative. For scaling to 5k, use this updated verifier and lower teacher concurrency to 50 to reduce fallback bursts.
