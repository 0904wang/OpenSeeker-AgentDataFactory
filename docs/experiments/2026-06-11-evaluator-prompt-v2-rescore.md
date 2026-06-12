# 2026-06-11 Evaluator and Prompt V2 Rescore

## Status

Completed. Updated the OpenSeeker evaluator and model-evaluation prompt after the 200-sample held-out variant run exposed two residual issues:

- `tool_coverage_gap` sometimes counted equivalent lookup queries as misses.
- `missing_final` showed the inference prompt did not strongly stop the model at `Final: <country>`.

This experiment rescored existing predictions. It did not run new model inference or retrain the adapter.

## Goal

Reduce artificial tool-call failures and make the next model evaluation less likely to run past the final answer.

## Code Changes

Changed locally and synced narrowly to remote:

```text
README.md
openseeker_factory/evaluation.py
tests/test_evaluation.py
```

Evaluator changes:

- Normalize diacritics with Unicode decomposition, e.g. `Würzburg` -> `wurzburg`.
- Merge adjacent single-letter initials, e.g. `C. V. Raman` -> `cv raman`.
- Ignore query-intent tokens such as `birthplace`, `country`, `present`, and `where` when comparing lookup queries.
- Treat subset/superset content-token matches as equivalent for tool-call coverage.

Prompt changes:

- System prompt now instructs the model to use at most two `wikidata_lookup` calls.
- System prompt says the final line must be exactly `Final: <country>`.
- User prompt says to use only `Thought`, `Action`, `Observation`, and `Final` lines and to output nothing after `Final`.

## TDD Verification

Expected red run before implementation:

```text
python -m pytest tests/test_evaluation.py
4 failed, 8 passed
```

The failing tests covered:

- `Würzburg` matching `Wurzburg country`
- `CV Raman` matching `C. V. Raman birthplace`
- `La Haye` matching `La Haye en Touraine country`
- model prompt containing bounded lookup and required final-line instructions

Green runs after implementation:

```text
python -m pytest tests/test_evaluation.py
12 passed in 0.11s

python -m pytest tests/test_cli.py tests/test_evaluation.py
20 passed in 5.20s
```

Remote verification after narrow sync:

```text
python -m pytest tests/test_evaluation.py tests/test_cli.py
20 passed in 1.29s
```

## Remote Context

- SSH entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote branch: `main`
- Remote commit observed earlier: `7b64c03`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Previous predictions: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout200-canonical-gpu7/qwen3-8b-lora-sft-1k-heldout200-canonical_predictions.jsonl`
- Rescore output: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout200-canonical-rescore-v2`

## Rescore Command

```bash
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical/samples.jsonl \
  --prediction-file /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout200-canonical-gpu7/qwen3-8b-lora-sft-1k-heldout200-canonical_predictions.jsonl \
  --model-label qwen3-8b-lora-sft-1k-heldout200-rescore-v2 \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout200-canonical-rescore-v2
```

## Raw Summary

Previous LoRA summary:

```text
overall,200,exact=0.795,canonical=0.87,final=0.885,tool_success=0.81,tool_coverage_avg=0.8975,trajectory=0.885,tool_gap=0.145
```

V2 rescore:

```text
model_label,split,total,exact_match_rate,canonical_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,trajectory_valid_rate,hallucination_rate,correct_rate,canonical_alias_match_rate,missing_final_rate,trajectory_format_error_rate,tool_coverage_gap_rate,supported_but_wrong_answer_rate,unsupported_wrong_answer_rate
qwen3-8b-lora-sft-1k-heldout200-rescore-v2,overall,200,0.795,0.87,0.795,0.9,0.885,0.84,0.92,0.885,0.015,0.66,0.075,0.115,0.0,0.135,0.0,0.015
qwen3-8b-lora-sft-1k-heldout200-rescore-v2,multi_hop_qa,67,0.7761,0.8358,0.7761,0.9403,0.8358,0.7612,0.8806,0.8358,0.0,0.5373,0.0597,0.1642,0.0,0.2388,0.0,0.0
qwen3-8b-lora-sft-1k-heldout200-rescore-v2,noisy_context_retrieval_qa,66,0.8485,0.9545,0.8485,0.8485,1.0,0.8636,0.9318,1.0,0.0455,0.7576,0.1061,0.0,0.0,0.0909,0.0,0.0455
qwen3-8b-lora-sft-1k-heldout200-rescore-v2,tool_use_qa,67,0.7612,0.8209,0.7612,0.9104,0.8209,0.8955,0.9478,0.8209,0.0,0.6866,0.0597,0.1791,0.0,0.0746,0.0,0.0
```

## Interpretation

The evaluator change modestly improved tool scoring on the same predictions:

```text
tool_call_success_rate: 0.81 -> 0.84
tool_call_coverage_avg: 0.8975 -> 0.92
tool_coverage_gap_rate: 0.145 -> 0.135
```

The improvement is intentionally modest. Many remaining `tool_coverage_gap` samples are real protocol mismatches rather than only string-normalization issues. For example, some multi-hop predictions answer correctly but call the entity directly and never issue the expected birthplace-country lookup, or loop beyond the needed lookup sequence.

The prompt v2 change cannot affect this rescore because it only applies to future inference. It is expected to help future runs by reducing runaway lookup chains that caused `missing_final_rate=0.115`.

## Next Steps

- Run a small GPU inference smoke with prompt v2 on 20 to 30 held-out samples before another full 200-sample run.
- If `missing_final` remains high, add an evaluation-time stop sequence or reduce `max_new_tokens` after enough examples show the model can answer within the bounded format.
- For the next SFT data version, add negative examples or verifier rewrites that reject extra lookup chains after the country is found.
