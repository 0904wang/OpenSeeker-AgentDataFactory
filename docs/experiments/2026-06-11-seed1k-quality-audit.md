# 2026-06-11 Seed1k Quality Audit

## Goal

Audit the completed 1,000-sample teacher generation run before using it for SFT. The audit checks verifier/trajectory correctness, stratified samples across teacher/fallback/repaired groups, and question-entity alignment.

## Input

- Remote result dir: `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611`
- Input samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611/samples.jsonl`
- Prior generation summary:

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,evidence_faithfulness_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
1000,1000,0,1.0,1.0,1.0,1.0,1.0,1.0,1000,978,22,0.022,11,34,
```

## Commands

Remote target tests before audit:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m pytest tests/test_pipeline.py tests/test_cli.py
```

Result:

```text
23 passed in 1.28s
```

Audit scripts:

```bash
/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory/bin/python \
  /data/wzl/OpenSeeker-AgentDataFactory/runs/audit-seed1k-repair-20260611.py

/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory/bin/python \
  /data/wzl/OpenSeeker-AgentDataFactory/runs/audit-entity-alignment-seed1k-20260611.py
```

## Remote Audit Artifacts

- `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611/quality_audit_20260611.jsonl`
- `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611/quality_audit_20260611.csv`
- `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611/quality_audit_20260611_summary.json`
- `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611/QUALITY_AUDIT_20260611.md`
- `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611/entity_alignment_audit_20260611.jsonl`
- `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611/entity_alignment_audit_20260611.csv`
- `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611/entity_alignment_audit_20260611_summary.json`
- `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611/ENTITY_ALIGNMENT_AUDIT_20260611.md`

## Structural Audit Result

Raw summary:

```json
{
  "total": 1000,
  "audit_sampled": 500,
  "groups": {
    "teacher": 967,
    "repaired": 11,
    "fallback": 22
  },
  "task_type": {
    "multi_hop_qa": 334,
    "tool_use_qa": 333,
    "noisy_context_retrieval_qa": 333
  },
  "difficulty": {
    "easy": 272,
    "medium": 651,
    "hard": 77
  },
  "issue_rows": 460,
  "issue_counts": {
    "question_not_question_mark": 460
  },
  "repair_reasons": {
    "none": 989,
    "react_format": 11
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

Interpretation:

- Verifier, ReAct shape, tool result coverage, and answer support all passed for 1,000/1,000 samples.
- The large automatic issue count is from 460 questions not ending in `?`. This is a style/form issue and not a factual failure by itself.
- Some fallback questions include deterministic template text such as `Use synthesis round N`, which should be removed before treating the dataset as polished SFT data.

## Entity Alignment Audit Result

Raw summary:

```json
{
  "total": 1000,
  "rows_with_any_issue": 26,
  "issue_counts": {
    "expected_entity_missing_from_question": 3,
    "foreign_entity_in_question": 3,
    "repaired_question_semantic_mismatch": 4,
    "duplicate_rewrite_kept_foreign_entity": 1,
    "synthetic_round_marker_in_question": 22
  },
  "groups": {
    "teacher": 967,
    "repaired": 11,
    "fallback": 22
  },
  "issue_by_group": {
    "teacher": {},
    "repaired": {
      "expected_entity_missing_from_question": 3,
      "foreign_entity_in_question": 3,
      "repaired_question_semantic_mismatch": 4,
      "duplicate_rewrite_kept_foreign_entity": 1
    },
    "fallback": {
      "synthetic_round_marker_in_question": 22
    }
  },
  "expected_entity_missing_rows": 3,
  "foreign_entity_rows": 3,
  "repaired_rows": 11,
  "repaired_rows_with_alignment_issue": 4,
  "fallback_rows": 22,
  "fallback_rows_with_synthetic_round_marker": 22,
  "duplicate_rewrite_rows": 423,
  "duplicate_rewrite_rows_with_foreign_entity": 1
}
```

Important sampled failures:

- `wikidata-rachel-carson-noisy-81`: question says `Albert Einstein`, but seed/evidence/trajectory are Rachel Carson.
- `wikidata-subrahmanyan-chandrasekhar-tool-305`: question says `Marie Curie`, but seed/evidence/trajectory are Subrahmanyan Chandrasekhar.
- `wikidata-rachel-carson-tool-680`: question says `the person who discovered penicillin`, but seed/evidence/trajectory are Rachel Carson.
- Several fallback rows are factually correct but contain template text like `Use synthesis round 176.`

## Analysis

The 1k dataset is strong on deterministic verifier metrics, but it is not clean enough to call SFT-ready without a small question-level cleanup pass.

The main gap is that trajectory repair currently preserves teacher-drafted questions even when the teacher question names the wrong entity. The deterministic trajectory repair fixes the answer path, but the user-facing prompt can still be semantically misaligned. This is exactly the kind of issue a verifier needs to catch before training.

The fallback rows are usable after text cleanup, but `Use synthesis round N` is synthetic scaffolding and should not be exposed to the student model.

## Recommendation

Do not train on this exact 1k file as-is. First add a question-entity alignment verifier and rewrite path:

- if question does not contain the expected entity, rewrite question from seed;
- if question contains a foreign known entity, rewrite question from seed;
- if fallback question contains `Use synthesis round N`, remove that marker or use a natural deterministic template;
- keep `evidence_faithfulness` as-is for trajectory verification.

After cleanup, regenerate or rewrite the affected rows, then rerun this audit. The issue target before SFT should be:

- entity alignment issues: 0
- synthetic round marker: 0
- verifier pass: 100%
- evidence/tool/trajectory coverage: 100%

## Next Step

Implement `question_entity_alignment` as a verifier check and add a deterministic `question_repaired` fallback for teacher/repaired/fallback rows. This is a small code change with high value because it closes the main quality gap found in this audit.
