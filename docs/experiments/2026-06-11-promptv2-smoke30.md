# 2026-06-11 Prompt V2 LoRA Smoke 30

## Status

Completed. Ran a 30-sample GPU smoke evaluation of the Qwen3-8B 1k LoRA adapter using the prompt v2 changes from `openseeker_factory/evaluation.py`.

This was a smoke test to check whether prompt v2 reduces missing final answers. It was not a new full benchmark.

## Goal

Validate whether the stronger inference prompt reduces the `missing_final` failures seen in the 200-sample held-out variant run.

Prompt v2 requires:

- at most two `wikidata_lookup` calls
- stop once the country is known
- final line exactly `Final: <country>`
- no text after `Final`

## Remote Context

- SSH entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote branch: `main`
- Remote commit observed: `7b64c03`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Model: `Qwen/Qwen3-8B`
- Adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k`
- Samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical/samples.jsonl`
- GPU: `CUDA_VISIBLE_DEVICES=7`
- tmux session: `openseeker-20260611-promptv2-smoke30-gpu7`
- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-promptv2-smoke30-gpu7.log`
- Results: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-promptv2-smoke30-gpu7`

## Preflight

Preflight showed GPU7 free:

```text
7, 18, 32607
```

The run wrote no checkpoints and used one GPU for evaluation only.

## Launch Command

```bash
CUDA_VISIBLE_DEVICES=7 \
PYTHONNOUSERSITE=1 \
HF_HUB_OFFLINE=1 \
TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers \
python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical/samples.jsonl \
  --model-label qwen3-8b-lora-sft-1k-promptv2-smoke30 \
  --model-name-or-path Qwen/Qwen3-8B \
  --adapter-path /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k \
  --limit 30 \
  --batch-size 2 \
  --max-new-tokens 160 \
  --device cuda \
  --local-files-only \
  --disable-thinking \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-promptv2-smoke30-gpu7
```

## Raw Summary

```text
model_label,split,total,exact_match_rate,canonical_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,trajectory_valid_rate,hallucination_rate,correct_rate,canonical_alias_match_rate,missing_final_rate,trajectory_format_error_rate,tool_coverage_gap_rate,supported_but_wrong_answer_rate,unsupported_wrong_answer_rate
qwen3-8b-lora-sft-1k-promptv2-smoke30,overall,30,1.0,1.0,1.0,1.0,1.0,0.7,0.85,1.0,0.0,0.7,0.0,0.0,0.0,0.3,0.0,0.0
qwen3-8b-lora-sft-1k-promptv2-smoke30,multi_hop_qa,10,1.0,1.0,1.0,1.0,1.0,0.7,0.85,1.0,0.0,0.7,0.0,0.0,0.0,0.3,0.0,0.0
qwen3-8b-lora-sft-1k-promptv2-smoke30,noisy_context_retrieval_qa,10,1.0,1.0,1.0,1.0,1.0,0.7,0.85,1.0,0.0,0.7,0.0,0.0,0.0,0.3,0.0,0.0
qwen3-8b-lora-sft-1k-promptv2-smoke30,tool_use_qa,10,1.0,1.0,1.0,1.0,1.0,0.7,0.85,1.0,0.0,0.7,0.0,0.0,0.0,0.3,0.0,0.0
```

## Error Buckets

```text
correct: 21
tool_coverage_gap: 9
missing_final: 0
unsupported_wrong_answer: 0
```

Representative `tool_coverage_gap` examples:

```text
wikidata-max-planck-noisy-6: predicted Germany, but used invented/intermediate location Hilbertstadt
wikidata-werner-heisenberg-multi-hop-10: predicted Germany, but used Munich instead of the seed birthplace
wikidata-paul-dirac-tool-14: predicted United Kingdom, but used Bracknell instead of the seed birthplace
wikidata-c-v-raman-tool-26: predicted India, but used Thiruvananthapuram instead of the seed birthplace
```

## Interpretation

Prompt v2 achieved the immediate goal on this smoke sample:

```text
missing_final_rate: 0.115 in heldout200 -> 0.0 in smoke30
final_answer_rate: 0.885 in heldout200 -> 1.0 in smoke30
trajectory_valid_rate: 0.885 in heldout200 -> 1.0 in smoke30
```

However, tool coverage remains the main issue:

```text
tool_call_success_rate: 0.7
tool_coverage_gap_rate: 0.3
```

The non-correct samples are mostly evidence-chain problems, not final-answer problems. The model often produces the correct country while changing the intermediate birthplace. This is a useful verifier finding: exact answer metrics can look perfect while the tool trajectory is not faithful to the intended evidence path.

## Next Steps

- Do not launch a full 200-sample prompt v2 run yet if the goal is to improve the model; smoke30 already shows the next bottleneck is evidence faithfulness.
- Add a trajectory/evidence verifier that checks whether generated observations contain the expected intermediate birthplace from the seed.
- For SFT v2, include rejection/rewrite examples where the final country is correct but the intermediate location is unsupported.
- Consider lowering `max_new_tokens` only after the evidence-faithfulness issue is addressed; prompt v2 already fixed missing final answers in this smoke.
