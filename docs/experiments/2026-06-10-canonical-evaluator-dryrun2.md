# 2026-06-10 Canonical Evaluator Dry Run 2

## Status

Completed. Added canonical answer matching and error bucket metrics to the OpenSeeker evaluator, synced the narrow code change to the remote repo, and ran a 2-sample GPU LoRA evaluation dry run.

## Goal

Fix the evaluation blind spots found in the held-out 60 run:

- country/region aliases such as `England` or `Scotland` versus `United Kingdom`
- missing `Final:` answers
- correct final answers with incomplete tool-call coverage
- wrong unsupported answers versus supported but non-canonical answers

## Code Changes

Changed locally and synced narrowly to remote:

```text
README.md
openseeker_factory/evaluation.py
tests/test_evaluation.py
```

New per-prediction fields:

```text
canonical_match
error_bucket
```

New summary fields:

```text
canonical_match_rate
correct_rate
canonical_alias_match_rate
missing_final_rate
trajectory_format_error_rate
tool_coverage_gap_rate
supported_but_wrong_answer_rate
unsupported_wrong_answer_rate
```

## Verification

Local:

```text
python -m pytest tests/test_evaluation.py
8 passed in 0.10s

python -m pytest tests/test_cli.py tests/test_evaluation.py
16 passed in 3.73s

python -m pytest
38 passed in 13.79s
```

Remote:

```text
python -m pytest tests/test_evaluation.py tests/test_cli.py
16 passed in 1.20s

python -m pytest
38 passed in 4.17s
```

Remote prediction-file smoke:

```text
canonical-smoke,overall,1,exact_match_rate=0.0,canonical_match_rate=1.0,canonical_alias_match_rate=1.0
```

## Remote Context

- SSH entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote branch: `main`
- Remote commit observed: `7b64c03`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU: `CUDA_VISIBLE_DEVICES=7`
- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-canonical-dryrun2-gpu7.log`
- Results: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-dryrun2-gpu7`

Preflight showed GPU7 free before and after the dry run:

```text
7, 667, 32607
```

## Dry Run Command

```bash
CUDA_VISIBLE_DEVICES=7 \
PYTHONNOUSERSITE=1 \
HF_HUB_OFFLINE=1 \
TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers \
python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-60/samples.jsonl \
  --model-label qwen3-8b-lora-sft-1k-canonical-dryrun2 \
  --model-name-or-path Qwen/Qwen3-8B \
  --adapter-path /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k \
  --limit 2 \
  --batch-size 2 \
  --max-new-tokens 160 \
  --device cuda \
  --local-files-only \
  --disable-thinking \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-dryrun2-gpu7
```

## Raw Summary

```text
model_label,split,total,exact_match_rate,canonical_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,trajectory_valid_rate,hallucination_rate,correct_rate,canonical_alias_match_rate,missing_final_rate,trajectory_format_error_rate,tool_coverage_gap_rate,supported_but_wrong_answer_rate,unsupported_wrong_answer_rate
qwen3-8b-lora-sft-1k-canonical-dryrun2,overall,2,0.0,0.5,0.0,0.5,0.5,1.0,1.0,0.5,0.0,0.0,0.5,0.5,0.0,0.0,0.0,0.0
qwen3-8b-lora-sft-1k-canonical-dryrun2,multi_hop_qa,1,0.0,1.0,0.0,0.0,1.0,1.0,1.0,1.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0
qwen3-8b-lora-sft-1k-canonical-dryrun2,tool_use_qa,1,0.0,0.0,0.0,1.0,0.0,1.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0
```

## Interpretation

The evaluator now separates strict exact match from canonical alias match. In the dry run, one sample that would have failed strict exact match is counted as `canonical_alias_match`, while another is bucketed as `missing_final`. This directly addresses the error analysis from the held-out 60 run.

## Next Step

Run a larger `heldout200-variant` evaluation using the same 60 held-out seed rows repeated through question variants. The run should be labeled as variant-expanded held-out evaluation, not 200 independent held-out entities.
