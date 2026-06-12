# Canonical-v3 clean heldout and adapter re-evaluation

Date: 2026-06-12

## Goal

Add observation-level evidence faithfulness metrics, regenerate a clean 200-sample heldout split without legacy `Use synthesis round N` text, and re-evaluate the existing Qwen3-8B cleaned1k and canonical-v2 fixed1k LoRA adapters on the same split.

## Local Code Changes

- Added design note: `D:\resume\Data synthesis\docs\superpowers\specs\2026-06-12-canonical-v3-evaluation-design.md`
- Added implementation plan: `D:\resume\Data synthesis\docs\superpowers\plans\2026-06-12-canonical-v3-evaluation.md`
- Modified evaluator: `D:\resume\Data synthesis\openseeker_factory\evaluation.py`
- Modified tests: `D:\resume\Data synthesis\tests\test_evaluation.py`
- Added remote launchers:
  - `D:\resume\Data synthesis\runs\launch_eval_cleaned1k_v3clean_gpu7.sh`
  - `D:\resume\Data synthesis\runs\launch_eval_canonical_v2_fixed_v3clean_gpu7.sh`

New evaluator fields:

- Per prediction:
  - `observation_coverage`
  - `observation_faithfulness`
- Summary CSV:
  - `observation_faithfulness_rate`
  - `observation_coverage_avg`

Local verification:

```text
python -m pytest tests/test_evaluation.py -q
13 passed

python -m pytest -q
52 passed
```

Remote verification after narrow sync:

```text
python -m pytest tests/test_evaluation.py tests/test_cli.py
21 passed in 1.21s
```

## Clean Heldout Generation

Remote context:

- SSH: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Seed file: `/data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_expanded.jsonl`
- Seed rows: 120

Smoke command:

```bash
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 3 \
  --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_expanded.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-3-canonical-v3-clean-smoke \
  --strategy evol_instruct \
  --teacher-backend none
```

Smoke result:

```text
accepted=3 rejected=0
solvability=1.0 evidence_hit=1.0 evidence_faithfulness=1.0 tool_success=1.0 trajectory_valid=1.0
Use synthesis round marker count=0
```

Formal command:

```bash
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 200 \
  --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_expanded.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v3-clean \
  --strategy evol_instruct \
  --teacher-backend none \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/heldout-eval-samples-200-canonical-v3-clean.log
```

Formal heldout audit:

```text
samples: 200
sft_lines: 200
rl_lines: 200
trace_lines: 200
task_type: multi_hop_qa=67, tool_use_qa=67, noisy_context_retrieval_qa=66
round_marker: 0
canonical_p19: 200
canonical_p17: 200
duplicate_questions: 0
```

Generation summary:

```text
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,evidence_faithfulness_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,question_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
200,200,0,1.0,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,0,0,
```

## Adapter Re-Evaluation

Shared eval settings:

- Base model: `/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218`
- Samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v3-clean/samples.jsonl`
- GPU: `CUDA_VISIBLE_DEVICES=7`
- Batch size: 2
- Max new tokens: 160
- Offline mode: `HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`
- Warning observed in both runs: generation flags `temperature`, `top_p`, and `top_k` may be ignored. This was also present in earlier evals and did not block output.

### Cleaned1k Adapter

- Adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-cleaned`
- tmux: `openseeker-20260612-eval-cleaned1k-v3clean-gpu7`
- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-cleaned-v3clean-heldout200-gpu7.log`
- Results: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-cleaned-v3clean-heldout200-gpu7`

Summary:

```text
model_label,split,total,exact_match_rate,canonical_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,observation_faithfulness_rate,observation_coverage_avg,trajectory_valid_rate,hallucination_rate,correct_rate,canonical_alias_match_rate,missing_final_rate,trajectory_format_error_rate,tool_coverage_gap_rate,supported_but_wrong_answer_rate,unsupported_wrong_answer_rate
qwen3-8b-lora-sft-1k-cleaned-v3clean-heldout200,overall,200,0.885,0.915,0.8908,0.89,1.0,0.565,0.7825,0.55,0.56,1.0,0.085,0.565,0.0,0.0,0.0,0.35,0.0,0.085
qwen3-8b-lora-sft-1k-cleaned-v3clean-heldout200,multi_hop_qa,67,0.8657,0.8955,0.8731,0.8657,1.0,0.5373,0.7687,0.5224,0.5373,1.0,0.1045,0.5373,0.0,0.0,0.0,0.3582,0.0,0.1045
qwen3-8b-lora-sft-1k-cleaned-v3clean-heldout200,noisy_context_retrieval_qa,66,0.9242,0.9545,0.9242,0.9242,1.0,0.6061,0.803,0.6061,0.6061,1.0,0.0455,0.6061,0.0,0.0,0.0,0.3485,0.0,0.0455
qwen3-8b-lora-sft-1k-cleaned-v3clean-heldout200,tool_use_qa,67,0.8657,0.8955,0.8756,0.8806,1.0,0.5522,0.7761,0.5224,0.5373,1.0,0.1045,0.5522,0.0,0.0,0.0,0.3433,0.0,0.1045
```

Error counts:

```text
correct: 113
tool_coverage_gap: 70
unsupported_wrong_answer: 17
observation_faithful: 110
observation_unfaithful: 90
observation_coverage: 1.0 -> 110, 0.0 -> 86, 0.5 -> 4
```

Representative error:

```text
id: wikidata-alan-turing-multi-hop-7
gold: United Kingdom
prediction: wikidata_lookup[Alan Turing, birthplace] -> Manchester; wikidata_lookup[Manchester, country] -> United Kingdom; Final: United Kingdom
tool_call_coverage: 0.5
observation_coverage: 0.0
error_bucket: tool_coverage_gap
```

### Canonical-v2 Fixed1k Adapter

- Adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v2-fixed`
- tmux: `openseeker-20260612-eval-canonical-v2-v3clean-gpu7`
- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-canonical-v2-fixed-v3clean-heldout200-gpu7.log`
- Results: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v2-fixed-v3clean-heldout200-gpu7`

Summary:

```text
model_label,split,total,exact_match_rate,canonical_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,observation_faithfulness_rate,observation_coverage_avg,trajectory_valid_rate,hallucination_rate,correct_rate,canonical_alias_match_rate,missing_final_rate,trajectory_format_error_rate,tool_coverage_gap_rate,supported_but_wrong_answer_rate,unsupported_wrong_answer_rate
qwen3-8b-lora-sft-1k-canonical-v2-fixed-v3clean-heldout200,overall,200,0.925,0.965,0.9308,0.93,1.0,0.945,0.9725,0.72,0.8,1.0,0.035,0.87,0.04,0.0,0.0,0.055,0.0,0.035
qwen3-8b-lora-sft-1k-canonical-v2-fixed-v3clean-heldout200,multi_hop_qa,67,0.9104,0.9403,0.9179,0.9104,1.0,0.9552,0.9776,0.7463,0.806,1.0,0.0597,0.8657,0.0299,0.0,0.0,0.0448,0.0,0.0597
qwen3-8b-lora-sft-1k-canonical-v2-fixed-v3clean-heldout200,noisy_context_retrieval_qa,66,0.9242,0.9697,0.9242,0.9242,1.0,0.9394,0.9697,0.6818,0.7803,1.0,0.0303,0.8636,0.0455,0.0,0.0,0.0606,0.0,0.0303
qwen3-8b-lora-sft-1k-canonical-v2-fixed-v3clean-heldout200,tool_use_qa,67,0.9403,0.9851,0.9502,0.9552,1.0,0.9403,0.9701,0.7313,0.8134,1.0,0.0149,0.8806,0.0448,0.0,0.0,0.0597,0.0,0.0149
```

Error counts:

```text
correct: 174
unsupported_wrong_answer: 7
canonical_alias_match: 8
tool_coverage_gap: 11
observation_faithful: 144
observation_unfaithful: 56
observation_coverage: 1.0 -> 144, 0.5 -> 32, 0.0 -> 24
```

Representative error:

```text
id: wikidata-marie-curie-multi-hop-4
gold: Poland
prediction: wikidata_lookup[Marie Curie, P19] -> Warszawa; wikidata_lookup[Warszawa, P17] -> Polska; Final: Polska
tool_call_coverage: 1.0
observation_coverage: 0.0
error_bucket: unsupported_wrong_answer
```

## Comparison

| Metric | cleaned1k | canonical-v2 fixed1k | Delta |
| --- | ---: | ---: | ---: |
| exact_match_rate | 0.885 | 0.925 | +0.040 |
| canonical_match_rate | 0.915 | 0.965 | +0.050 |
| final_answer_rate | 1.000 | 1.000 | +0.000 |
| tool_call_success_rate | 0.565 | 0.945 | +0.380 |
| tool_call_coverage_avg | 0.7825 | 0.9725 | +0.190 |
| observation_faithfulness_rate | 0.550 | 0.720 | +0.170 |
| observation_coverage_avg | 0.560 | 0.800 | +0.240 |
| trajectory_valid_rate | 1.000 | 1.000 | +0.000 |
| hallucination_rate | 0.085 | 0.035 | -0.050 |
| correct_rate | 0.565 | 0.870 | +0.305 |
| tool_coverage_gap_rate | 0.350 | 0.055 | -0.295 |
| unsupported_wrong_answer_rate | 0.085 | 0.035 | -0.050 |

## Analysis

The clean heldout split materially changes the interpretation compared with the older heldout200. Removing legacy `Use synthesis round N` text gives a cleaner task surface and exposes the actual model behavior. Canonical-v2 fixed1k is substantially better than cleaned1k on the same split: strict tool-call success increases by 38 points, correct rate increases by 30.5 points, and hallucination proxy decreases by 5 points.

The new observation metrics are useful. Canonical-v2 fixed1k reaches 0.945 tool-call success but only 0.72 observation faithfulness. That means the model often learns the right action syntax while still substituting memorized or localized facts into observations. Examples include `Warszawa/Polska` for Marie Curie, `Woolsthorpe/England` for Isaac Newton, and natural place aliases that do not match the synthetic gold evidence.

This is a good resume story because it demonstrates a verifier-driven loop rather than only model training: the first canonical SFT fixed tool syntax, the next evaluator found evidence-faithfulness failures, and the project now has a concrete target for canonical-v3 data.

## Next Steps

1. Build canonical-v3 SFT data that explicitly trains observation faithfulness:
   - Include the exact gold observation strings from `tool_calls`.
   - Add negative/contrastive cases where historical names, local language aliases, or common-knowledge places are rejected.
   - Add a source/verifier tag for observation-faithfulness.
2. Add an optional stricter error bucket for `observation_faithfulness_gap` so rows with correct final answers but wrong observations are distinguishable from generic `correct` or `tool_coverage_gap`.
3. Train a canonical-v3 1k LoRA and evaluate on `heldout-eval-samples-200-canonical-v3-clean`.
4. Only after canonical-v3 improves both `tool_call_success_rate` and `observation_faithfulness_rate`, scale data to 5k or 20k.
