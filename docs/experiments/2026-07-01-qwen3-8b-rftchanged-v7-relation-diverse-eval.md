# Qwen3-8B RFT Changed Round 1 on v7 Relation-diverse Heldout200

## Metadata

- Experiment name: qwen3-8b-rftchanged-v7-relation-diverse-eval
- Date: 2026-07-01
- Goal: Evaluate the current best Qwen3-8B RFT-changed adapter on a harder relation-diverse heldout after v4/v5/v6 saturation.
- Status: success
- Operator: Codex
- Remote host: `user@ssh-22.e6.luyouxia.net -p 29509`
- Isolated worktree: `/data/wzl/OpenSeeker-AgentDataFactory/runs/repo-v7-relation-diverse-20260701`
- Commit: `d16a529`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Base model: `/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218`
- Adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-3p5k-mixed-v3-v4-v5blind-v6-rftchanged-round1-20260701`
- GPU: `CUDA_VISIBLE_DEVICES=0`

## Commands

Remote smoke:

```bash
PYTHONNOUSERSITE=1 python -m pytest \
  tests/test_pipeline.py::test_factory_can_generate_canonical_v7_relation_diverse_heldout_samples \
  tests/test_cli.py::test_cli_generate_supports_canonical_v7_relation_diverse_data_version \
  tests/test_seed_bank.py::test_build_wikidata_seed_rows_supports_relation_diverse_rows \
  tests/test_cli.py::test_cli_build_seeds_supports_relation_diverse_file \
  tests/test_evaluation.py::test_format_prompt_does_not_leak_birthplace_path_for_relation_diverse_samples -q
```

Heldout generation:

```bash
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli build-seeds \
  --relation-diverse \
  --out-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_relation_diverse_v7_heldout200.jsonl

PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 200 \
  --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_relation_diverse_v7_heldout200.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v7-relation-diverse \
  --data-version canonical-v7-relation-diverse
```

Evaluation:

```bash
CUDA_VISIBLE_DEVICES=0 PYTHONNOUSERSITE=1 python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v7-relation-diverse/samples.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-rftchanged-round1-v7relationdiverse-heldout200-gpu0 \
  --model-label qwen3-8b-lora-sft-rftchanged-round1-v7relationdiverse-heldout200 \
  --model-name-or-path /data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218 \
  --adapter-path /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-3p5k-mixed-v3-v4-v5blind-v6-rftchanged-round1-20260701 \
  --batch-size 2 \
  --max-new-tokens 160 \
  --device cuda \
  --local-files-only \
  --disable-thinking
```

## Paths

- Seed file: `/data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_relation_diverse_v7_heldout200.jsonl`
- Heldout samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v7-relation-diverse/samples.jsonl`
- Heldout generation result dir: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v7-relation-diverse`
- Evaluation result dir: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-rftchanged-round1-v7relationdiverse-heldout200-gpu0`
- Predictions: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-rftchanged-round1-v7relationdiverse-heldout200-gpu0/qwen3-8b-lora-sft-rftchanged-round1-v7relationdiverse-heldout200_predictions.jsonl`
- Summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-rftchanged-round1-v7relationdiverse-heldout200-gpu0/qwen3-8b-lora-sft-rftchanged-round1-v7relationdiverse-heldout200_summary.csv`
- Evaluation log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-rftchanged-round1-v7relationdiverse-heldout200-gpu0.log`

## Heldout Generation Audit

```text
rows 200
relations {'birthplace_country': 50, 'education_country': 50, 'employer_country': 50, 'award_country': 50}
versions {'canonical-v7-relation-diverse': 200}
property_id_leaks 0
lookup_template_leaks 0
hard_rows 200
```

Generation summary:

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,evidence_faithfulness_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,question_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
200,200,0,1.0,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,0,0,
```

## Raw Evaluation Summary

```csv
model_label,split,total,exact_match_rate,canonical_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,observation_faithfulness_rate,observation_coverage_avg,trajectory_valid_rate,hallucination_rate,correct_rate,canonical_alias_match_rate,missing_final_rate,trajectory_format_error_rate,tool_coverage_gap_rate,supported_but_wrong_answer_rate,unsupported_wrong_answer_rate
qwen3-8b-lora-sft-rftchanged-round1-v7relationdiverse-heldout200,overall,200,0.86,0.86,0.8675,0.86,1.0,0.72,0.86,0.5,0.6175,1.0,0.14,0.605,0.0,0.0,0.0,0.255,0.0,0.14
qwen3-8b-lora-sft-rftchanged-round1-v7relationdiverse-heldout200,multi_hop_qa,100,0.98,0.98,0.98,0.98,1.0,0.81,0.905,0.67,0.74,1.0,0.02,0.79,0.0,0.0,0.0,0.19,0.0,0.02
qwen3-8b-lora-sft-rftchanged-round1-v7relationdiverse-heldout200,noisy_context_retrieval_qa,50,0.48,0.48,0.51,0.48,1.0,0.72,0.86,0.3,0.47,1.0,0.52,0.3,0.0,0.0,0.0,0.18,0.0,0.52
qwen3-8b-lora-sft-rftchanged-round1-v7relationdiverse-heldout200,tool_use_qa,50,1.0,1.0,1.0,1.0,1.0,0.54,0.77,0.36,0.52,1.0,0.0,0.54,0.0,0.0,0.0,0.46,0.0,0.0
```

## Relation Breakdown

| Relation profile | Total | Correct | Correct rate | Exact | Tool success | Observation faithfulness | Trajectory valid | Hallucination |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| birthplace_country | 50 | 50 | 1.000 | 1.000 | 1.000 | 0.860 | 1.000 | 0.000 |
| education_country | 50 | 27 | 0.540 | 1.000 | 0.540 | 0.360 | 1.000 | 0.000 |
| employer_country | 50 | 29 | 0.580 | 0.960 | 0.620 | 0.480 | 1.000 | 0.040 |
| award_country | 50 | 15 | 0.300 | 0.480 | 0.720 | 0.300 | 1.000 | 0.520 |

Overall error buckets:

```text
correct: 121
tool_coverage_gap: 51
unsupported_wrong_answer: 28
```

## Failure Examples

Education tool-choice drift:

```text
id: wikidata-v7-alan-turing-education-2
gold answer: United Kingdom
predicted answer: United Kingdom
bucket: tool_coverage_gap

Action: wikidata_lookup[Alan Turing, P108]
Observation: King's College London
Action: wikidata_lookup[King's College London, P17]
Observation: United Kingdom
Final: United Kingdom
```

The answer is correct, but the model used employer/workplace style `P108` instead of the education relation `P69`, so the trace is not verifiably faithful to the requested path.

Award hallucination:

```text
id: wikidata-v7-alan-turing-award-4
gold answer: United Kingdom
predicted answer: United States
bucket: unsupported_wrong_answer

Action: wikidata_lookup[Alan Turing, P110]
Observation: Turing Award
Action: wikidata_lookup[Turing Award, P17]
Observation: United States
Final: United States
```

The model falls back to a plausible real-world award association instead of following the synthetic gold award path.

## Analysis

This is the first heldout in the project that breaks the saturated v4/v5/v6 story. The current RFT checkpoint remains excellent on the original birthplace path (`50/50` correct), but relation-diverse tool choice is not solved:

- `education_country` and `employer_country` often keep the final answer correct while selecting the wrong first-hop relation or intermediate entity.
- `award_country` is the hardest profile, with `0.300` correct rate and `0.520` hallucination proxy rate.
- Trajectory format remains stable at `1.000`, so the failure is semantic tool/relation selection rather than ReAct formatting.
- Overall exact answer accuracy (`0.86`) is much higher than strict correct rate (`0.605`), which confirms why strict verifier-based scoring matters: many answers are right but unsupported by the required tool path.

The result is useful rather than disappointing: v7 now provides a meaningful next target for data generation, SFT, and RFT. It prevents the project from claiming victory on saturated birthplace-only heldouts.

## Next Steps

- Generate targeted v7 training data, likely 800-1,200 rows balanced across `education_country`, `employer_country`, and `award_country`.
- Prefer a focused v7 SFT/RFT pass before GRPO/RLVR; the model currently needs supervised relation-path coverage more than reward tuning.
- Add a post-eval audit table to compare:
  - current RFT checkpoint on v7
  - v7-targeted SFT
  - optional v7 RFT round
- Keep v4/v5/v6 regression evaluation after any v7 training.
