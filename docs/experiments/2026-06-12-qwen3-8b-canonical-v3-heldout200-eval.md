# Qwen3-8B Canonical-v3 Heldout200 Evaluation

## Goal

Evaluate the canonical-v3 observation-grounded Qwen3-8B LoRA adapter on the clean 200-sample canonical-v3 heldout split, then compare it with prior cleaned1k and canonical-v2-fixed adapters under the same evaluator and heldout file.

## Remote Context

- Date: 2026-06-12
- Remote entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote workspace: `/data/wzl/OpenSeeker-AgentDataFactory`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU: `CUDA_VISIBLE_DEVICES=7`
- tmux session: `openseeker-20260612-eval-canonical-v3-v3clean-heldout200-gpu7`

## Inputs

- Heldout samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v3-clean/samples.jsonl`
- Heldout size: 200
- Base model: `/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218`
- Adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v3`
- Launcher: `/data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_canonical_v3_v3clean_gpu7.sh`

## Command

```bash
tmux new-session -d -s openseeker-20260612-eval-canonical-v3-v3clean-heldout200-gpu7 \
  "bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_canonical_v3_v3clean_gpu7.sh"
```

The launcher ran:

```bash
CUDA_VISIBLE_DEVICES=7 PYTHONNOUSERSITE=1 python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v3-clean/samples.jsonl \
  --model-label qwen3-8b-lora-sft-1k-canonical-v3-v3clean-heldout200 \
  --model-name-or-path /data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218 \
  --adapter-path /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v3 \
  --limit 200 \
  --batch-size 2 \
  --max-new-tokens 160 \
  --device cuda \
  --local-files-only \
  --disable-thinking \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v3-v3clean-heldout200-gpu7
```

## Outputs

- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-canonical-v3-v3clean-heldout200-gpu7.log`
- Results dir: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v3-v3clean-heldout200-gpu7`
- Predictions: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v3-v3clean-heldout200-gpu7/qwen3-8b-lora-sft-1k-canonical-v3-v3clean-heldout200_predictions.jsonl`
- Summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v3-v3clean-heldout200-gpu7/qwen3-8b-lora-sft-1k-canonical-v3-v3clean-heldout200_summary.csv`

The run completed normally. GPU7 returned to idle and the tmux session exited.

## Summary Metrics

```csv
model_label,split,total,exact_match_rate,canonical_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,observation_faithfulness_rate,observation_coverage_avg,trajectory_valid_rate,hallucination_rate,correct_rate,canonical_alias_match_rate,missing_final_rate,trajectory_format_error_rate,tool_coverage_gap_rate,supported_but_wrong_answer_rate,unsupported_wrong_answer_rate
qwen3-8b-lora-sft-1k-canonical-v3-v3clean-heldout200,overall,200,0.925,0.97,0.9275,0.925,1.0,0.95,0.975,0.715,0.8025,1.0,0.03,0.875,0.045,0.0,0.0,0.05,0.0,0.03
qwen3-8b-lora-sft-1k-canonical-v3-v3clean-heldout200,multi_hop_qa,67,0.9104,0.9552,0.9179,0.9104,1.0,0.9552,0.9776,0.7313,0.806,1.0,0.0448,0.8657,0.0448,0.0,0.0,0.0448,0.0,0.0448
qwen3-8b-lora-sft-1k-canonical-v3-v3clean-heldout200,noisy_context_retrieval_qa,66,0.9242,0.9848,0.9242,0.9242,1.0,0.9394,0.9697,0.6667,0.7803,1.0,0.0152,0.8636,0.0606,0.0,0.0,0.0606,0.0,0.0152
qwen3-8b-lora-sft-1k-canonical-v3-v3clean-heldout200,tool_use_qa,67,0.9403,0.9701,0.9403,0.9403,1.0,0.9552,0.9776,0.7463,0.8209,1.0,0.0299,0.8955,0.0299,0.0,0.0,0.0448,0.0,0.0299
```

Prediction row counts from JSONL:

```text
rows 200
exact_match 185
canonical_match 194
tool_call_success 190
observation_faithfulness 143
trajectory_valid 200
hallucination_proxy 6
```

Error buckets:

```text
correct 175
canonical_alias_match 9
tool_coverage_gap 10
unsupported_wrong_answer 6
```

## Same-Heldout Comparison

All rows below use `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v3-clean/samples.jsonl`.

| Model | Exact | Canonical | Tool Success | Tool Coverage | Observation Faithful | Observation Coverage | Trajectory Valid | Hallucination | Correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| cleaned1k | 0.885 | 0.915 | 0.565 | 0.7825 | 0.550 | 0.5600 | 1.000 | 0.085 | 0.565 |
| canonical-v2 fixed1k | 0.925 | 0.965 | 0.945 | 0.9725 | 0.720 | 0.8000 | 1.000 | 0.035 | 0.870 |
| canonical-v3 1k | 0.925 | 0.970 | 0.950 | 0.9750 | 0.715 | 0.8025 | 1.000 | 0.030 | 0.875 |

## Interpretation

Canonical-v3 clearly beats the earlier cleaned1k adapter on the metrics that matter for the AgentDataFactory story: tool-call success rises from 56.5% to 95.0%, observation faithfulness rises from 55.0% to 71.5%, and hallucination falls from 8.5% to 3.0%.

Compared with canonical-v2 fixed1k, canonical-v3 is almost a tie. It improves canonical answer match by 0.5 points, tool-call success by 0.5 points, observation coverage by 0.25 points, correct bucket rate by 0.5 points, and hallucination by 0.5 points. It slightly regresses observation faithfulness from 72.0% to 71.5%. This is not a strong win, but it is a controlled, non-regressing iteration overall.

The main remaining failure is not ReAct format: trajectory validity is 100%. The remaining issue is evidence-faithful observations. Typical cases still reflect pretrained or aliased world knowledge instead of the verifier's exact synthetic evidence, for example Isaac Newton resolving to `England` while the gold answer is `United Kingdom`, or birthplace strings with spelling variants that break exact observation verification.

## Example Failure Patterns

Canonical alias with non-faithful observation:

```text
id: wikidata-isaac-newton-multi-hop-13
gold_answer: United Kingdom
prediction:
Thought: Identify Isaac Newton's birthplace.
Action: wikidata_lookup[Isaac Newton, P19]
Observation: Woolsthorpe
Thought: Resolve the country of the intermediate location.
Action: wikidata_lookup[Woolsthorpe, P17]
Observation: England
Final: England
```

Tool coverage gap despite correct final answer:

```text
id: wikidata-katherine-johnson-multi-hop-22
gold_answer: United States
prediction:
Thought: Identify the entity's birthplace.
Action: wikidata_lookup[Katherine Johnson, P19]
Observation: Hampton
Thought: Resolve the country from the intermediate location.
Action: wikidata_lookup[Hampton, P17]
Observation: United States
Final: United States
```

## Resume-Safe Claim

The strongest defensible resume statement from this iteration is:

```text
Built a verifiable Agent synthetic-data pipeline for multi-hop Wikidata QA and ReAct tool trajectories; after canonical action and observation-grounded SFT on Qwen3-8B, heldout tool-call success improved from 56.5% to 95.0%, observation faithfulness from 55.0% to 71.5%, and hallucination rate dropped from 8.5% to 3.0% on a 200-sample clean heldout split.
```

Avoid claiming that canonical-v3 substantially beats canonical-v2 fixed; the controlled result is a near-tie with small mixed deltas.

## Next Step

The next useful experiment is not another identical 1k SFT run. Better options:

1. Add stricter observation-denoising or contrastive examples where historical aliases conflict with the gold tool result.
2. Add a verifier-aware rewrite pass for observations before SFT export.
3. Scale canonical-v3 from 1k to 5k or 10k after adding more entity diversity, then evaluate whether observation faithfulness improves beyond the current 71.5%.
4. Add a prediction-time deterministic tool executor to replace model-generated Observation lines, then measure how much of the remaining gap is caused by generation versus policy.
