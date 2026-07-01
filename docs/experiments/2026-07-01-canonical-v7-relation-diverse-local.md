# Canonical v7 Relation-diverse Local Implementation

## Metadata

- Experiment name: canonical-v7-relation-diverse-local
- Date: 2026-07-01
- Goal: Implement and locally smoke-test a relation-diverse heldout/data version before spending remote GPU time on saturated v4/v5/v6 splits.
- Status: success
- Operator: Codex
- Local repo: `D:\resume\Data synthesis`
- Branch: `codex/v7-relation-diverse`

## Code Changes

- Added `canonical-v7-relation-diverse` to the data-version contract.
- Added relation profiles for:
  - `birthplace_country`
  - `education_country`
  - `employer_country`
  - `award_country`
- Generalized tool-plan construction so the first hop is relation-specific:
  - birthplace: `P19`
  - education: `P69`
  - employer: `P108`
  - award: `P166`
  - second hop: `P17`
- Added a v7 blind relation/tool-choice prompt that hides property IDs and `wikidata_lookup[...]` scaffolding from the user prompt.
- Added relation-diverse seed-bank support through `build-seeds --relation-diverse`.
- Updated the model-evaluation system prompt from a birthplace-specific instruction to a relation-neutral instruction so v7 evaluation does not leak the old P19/P17 path.

## Local Smoke Commands

```bash
python -m pytest tests/test_pipeline.py::test_factory_can_generate_canonical_v7_relation_diverse_heldout_samples tests/test_cli.py::test_cli_generate_supports_canonical_v7_relation_diverse_data_version tests/test_seed_bank.py::test_build_wikidata_seed_rows_supports_relation_diverse_rows tests/test_cli.py::test_cli_build_seeds_supports_relation_diverse_file -q
```

Result:

```text
4 passed
```

```bash
python -m pytest tests/test_evaluation.py::test_format_prompt_requires_bounded_lookup_and_final_line tests/test_evaluation.py::test_format_prompt_does_not_leak_birthplace_path_for_relation_diverse_samples -q
```

Result:

```text
2 passed
```

```bash
python -m openseeker_factory.cli build-seeds \
  --relation-diverse \
  --limit 8 \
  --out-file outputs/v7-smoke/relation_diverse_seeds.jsonl
```

Result:

```text
OpenSeeker seed build complete: rows=8 out_file=outputs\v7-smoke\relation_diverse_seeds.jsonl
```

```bash
python -m openseeker_factory.cli generate \
  --count 8 \
  --seed-file outputs/v7-smoke/relation_diverse_seeds.jsonl \
  --out-dir outputs/v7-smoke/generated \
  --data-version canonical-v7-relation-diverse
```

Result:

```text
OpenSeeker AgentDataFactory generation complete: accepted=8 rejected=0 out_dir=outputs\v7-smoke\generated
```

## Audit Summary

```text
rows 8
relations Counter({'birthplace_country': 2, 'education_country': 2, 'employer_country': 2, 'award_country': 2})
contains_property_ids_in_question 0
contains_lookup_template_in_question 0
tool_queries ['Alan Turing, P19', 'Alan Turing, P69', 'Alan Turing, P108', 'Alan Turing, P166']
```

Summary CSV:

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,evidence_faithfulness_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,question_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
8,8,0,1.0,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,0,0,
```

## Analysis

v7 addresses the weakness in the current project evidence: v4/v5/v6 are now saturated and still focus on the birthplace-to-country path family. The local v7 implementation keeps the same deterministic verifier and export interfaces, but it changes the relation distribution and hides property IDs in prompts.

The important safety check is that the model prompt does not leak `P19`, `P69`, `P108`, `P166`, `P17`, or `wikidata_lookup[...]`; the answer target must be inferred from natural-language candidate intents. This makes v7 a better diagnostic before running another RFT round or trying GRPO/RLVR.

One additional issue was found during implementation: the evaluator system prompt still instructed the model to find a birthplace first. That would contaminate v7 evaluation. The prompt is now relation-neutral: first identify the intermediate entity for the requested relation, then resolve that intermediate entity to the requested country.

## Next Steps

- Sync the branch to the remote repo after local tests pass.
- Build a remote v7 heldout200 seed file under `/data/wzl/OpenSeeker-AgentDataFactory/data/seeds`.
- Generate `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v7-relation-diverse`.
- Evaluate the current RFT changed checkpoint on v7 before deciding whether to train more data.
