# 2026-06-10 Seed Expand 1k Quality Audit

## Status

Completed with remediation. The first audit found a training-quality issue in duplicate-question rewriting. The rewrite policy was fixed, the 1,000-sample dataset was re-exported from existing raw generations with `--resume`, and the follow-up audit passed the leakage check.

## Input

- Remote result path: `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-b50-c50`
- Local audit path: `D:\resume\Data synthesis\outputs\audits\seed-expand-1k-b50-c50`
- Local files copied for audit:
  - `samples.jsonl`
  - `summary.csv`

## Automatic Metrics

The remote summary was:

```text
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
1000,1000,0,1.0,1.0,1.0,1.0,1.0,1000,997,3,0.003,15,45,
```

Local automatic audit with fixed random seed `20260610`:

```text
total_rows=1000
audit_sample_size=100
unique_question_rate_full=1.0
duplicate_question_groups_full=0
task_type_counts_full={'multi_hop_qa': 334, 'tool_use_qa': 333, 'noisy_context_retrieval_qa': 333}
difficulty_counts_full={'hard': 64, 'medium': 652, 'easy': 284}
fallback_count_full=3
trajectory_repaired_count_full=15
difficulty_normalized_count_full=45
quality_score_min_full=1.0
quality_score_avg_full=1.0
not_duplicate_rate_full=1.0
answer_supported_rate_full=1.0
evidence_coverage_rate_full=1.0
tool_success_rate_full=1.0
trajectory_valid_rate_full=1.0
```

Audit artifacts:

```text
D:\resume\Data synthesis\outputs\audits\seed-expand-1k-b50-c50\audit_summary.csv
D:\resume\Data synthesis\outputs\audits\seed-expand-1k-b50-c50\audit_sample_100.jsonl
D:\resume\Data synthesis\outputs\audits\seed-expand-1k-b50-c50\audit_excerpts_10.json
```

## Initial Manual/Heuristic Finding

The deterministic verifier accepted all rows, but 419/1,000 questions include internal duplicate-rewrite text:

```text
Disambiguate this sample with seed ... and sample id ...
```

Examples:

```text
wikidata-niels-bohr-tool-17 | In which country was Niels Bohr born? Disambiguate this sample with seed wikidata-niels-bohr-tool-17 and sample id wikidata-niels-bohr-tool-17.
wikidata-jane-goodall-noisy-78 | What is the birthplace country of Jane Goodall? Disambiguate this sample with seed wikidata-jane-goodall-noisy-78 and sample id wikidata-jane-goodall-noisy-78.
wikidata-lise-meitner-tool-89 | In which country was Lise Meitner born? Disambiguate this sample with seed wikidata-lise-meitner-tool-89 and sample id wikidata-lise-meitner-tool-89.
```

Breakdown:

```text
leaky_duplicate_rewrite_count=419
task_counts={'tool_use_qa': 115, 'noisy_context_retrieval_qa': 133, 'multi_hop_qa': 171}
```

## Analysis

The data factory's verifier correctly checks support, tool-call consistency, and trajectory validity, but the current duplicate-question rewrite is too literal for training data. It makes questions unique by appending metadata-oriented text, which improves deterministic dedup metrics but leaks implementation details into the user prompt. This is unsuitable for SFT because a student model could learn unnatural prompt artifacts.

This is useful engineering evidence: automatic verifier metrics are necessary but not sufficient. The project needs a prompt-quality verifier or a cleaner rewrite policy before training.

## Remediation

The duplicate rewrite policy was changed from an internal metadata suffix to natural task constraints, for example:

```text
Use the birthplace clue rather than career context.
Start from <location>, then resolve the country.
Confirm the location linked to <entity> before naming the country.
```

A regression test now ensures final questions do not contain:

```text
Disambiguate this sample
sample id
seed
```

Verification:

```text
local pytest: 27 passed in 18.62s
remote pytest: 27 passed in 4.23s
remote re-export: resume: loaded=1000 remaining=0
```

The re-export did not call the teacher API again. It loaded the 1,000 existing raw generations and re-ran verification/export with the fixed rewrite policy.

## Follow-Up Audit

After re-export:

```text
total_rows=1000
audit_sample_size=100
random_seed=20260610
unique_question_rate_full=1.0
duplicate_question_groups_full=0
leaky_duplicate_rewrite_count_full=0
task_type_counts_full={'multi_hop_qa': 334, 'tool_use_qa': 333, 'noisy_context_retrieval_qa': 333}
difficulty_counts_full={'hard': 64, 'medium': 652, 'easy': 284}
fallback_count_full=3
trajectory_repaired_count_full=15
difficulty_normalized_count_full=45
quality_score_min_full=1.0
quality_score_avg_full=1.0
not_duplicate_rate_full=1.0
answer_supported_rate_full=1.0
evidence_coverage_rate_full=1.0
tool_success_rate_full=1.0
trajectory_valid_rate_full=1.0
```

Updated local audit artifacts:

```text
D:\resume\Data synthesis\outputs\audits\seed-expand-1k-b50-c50\audit_summary.csv
D:\resume\Data synthesis\outputs\audits\seed-expand-1k-b50-c50\audit_sample_100.jsonl
D:\resume\Data synthesis\outputs\audits\seed-expand-1k-b50-c50\audit_excerpts_10.json
```

## Decision

The re-exported 1k dataset is acceptable for a small SFT pilot. It is still a pilot dataset, not a final resume-scale 20k/50k dataset, because the seed bank remains small and repeated across variants.

## Next Steps

- Start with Qwen 7B LoRA SFT on the re-exported `sft_conversations.jsonl`.
- Keep the 1k run as an SFT smoke/pilot, then scale to 5k only after training/eval scripts are proven.
- Add prompt-quality checks to CI so automatic verifier metrics cannot hide user-facing prompt artifacts again.
