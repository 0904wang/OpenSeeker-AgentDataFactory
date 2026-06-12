# 2026-06-10 Qwen3-8B LoRA SFT 1k Evaluation, Pilot 60

## Status

Completed. A reusable `evaluate-model` CLI was added, tested locally and remotely, then used to compare base Qwen3-8B against the 1k LoRA SFT adapter on 60 OpenSeeker samples.

## Goal

Measure whether the Qwen3-8B LoRA adapter learned the OpenSeeker ReAct/tool-use output format and answer behavior beyond the base model. This is a pilot evaluation on training-distribution samples, not a final held-out generalization benchmark.

## Code Changes

Local and remote repo gained:

```text
openseeker_factory/evaluation.py
openseeker_factory/cli.py
tests/test_evaluation.py
tests/test_cli.py
```

New CLI:

```bash
python -m openseeker_factory.cli evaluate-model \
  --samples <samples.jsonl> \
  --model-label <label> \
  --model-name-or-path Qwen/Qwen3-8B \
  --adapter-path <optional-lora-adapter> \
  --limit <N> \
  --batch-size <N> \
  --max-new-tokens <N> \
  --device cuda \
  --local-files-only \
  --disable-thinking \
  --out-dir <result-dir>
```

Metrics:

```text
exact_match_rate: requires parsed `Final:` answer to match gold answer
answer_f1_avg: token F1 on parsed `Final:` answer
gold_answer_mention_rate: gold answer appears anywhere in raw output
final_answer_rate: output contains parseable `Final:`
tool_call_success_rate: all expected tool calls are covered by generated Action lines
tool_call_coverage_avg: average fraction of expected tool calls covered
trajectory_valid_rate: output contains Thought, Action, Observation, and Final
hallucination_rate: parsed Final answer is wrong and unsupported by evidence
```

## Verification

Local verification:

```text
python -m pytest tests/test_evaluation.py tests/test_cli.py
12 passed in 4.93s

python -m pytest
34 passed in 20.01s
```

Remote verification after narrow file sync:

```text
python -m pytest
34 passed in 4.15s
```

Remote prediction-file smoke:

```text
OpenSeeker model evaluation complete: model_label=eval-smoke samples=1
exact_match_rate=1.0
```

Remote 2-sample model smoke with `--disable-thinking`:

```text
qwen3-8b-base-smoke2-nothink:
  exact_match_rate=0.0
  gold_answer_mention_rate was positive in raw outputs but no `Final:` was emitted

qwen3-8b-lora-smoke2-nothink:
  exact_match_rate=1.0
  final_answer_rate=1.0
  tool_call_success_rate=1.0
  trajectory_valid_rate=1.0
```

## Remote Context

- SSH entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote branch: `main`
- Remote commit observed in launch log: `7b64c03`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Model cache: `/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers`
- Base model: `Qwen/Qwen3-8B`
- Adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k`
- Samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-b50-c50/samples.jsonl`
- GPU: `CUDA_VISIBLE_DEVICES=7`
- tmux session: `openseeker-20260610-eval-qwen3-8b-sft-1k-pilot60-gpu7`
- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-pilot60-gpu7.log`
- Results: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-pilot60-gpu7`

## Launch Command

The tmux run executed base evaluation first, then LoRA evaluation:

```bash
CUDA_VISIBLE_DEVICES=7 \
PYTHONNOUSERSITE=1 \
HF_HUB_OFFLINE=1 \
TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers \
python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-b50-c50/samples.jsonl \
  --model-label qwen3-8b-base \
  --model-name-or-path Qwen/Qwen3-8B \
  --limit 60 \
  --batch-size 2 \
  --max-new-tokens 160 \
  --device cuda \
  --local-files-only \
  --disable-thinking \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-pilot60-gpu7

CUDA_VISIBLE_DEVICES=7 \
PYTHONNOUSERSITE=1 \
HF_HUB_OFFLINE=1 \
TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers \
python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-b50-c50/samples.jsonl \
  --model-label qwen3-8b-lora-sft-1k \
  --model-name-or-path Qwen/Qwen3-8B \
  --adapter-path /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k \
  --limit 60 \
  --batch-size 2 \
  --max-new-tokens 160 \
  --device cuda \
  --local-files-only \
  --disable-thinking \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-pilot60-gpu7
```

## Result Files

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-pilot60-gpu7/qwen3-8b-base_predictions.jsonl
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-pilot60-gpu7/qwen3-8b-base_summary.csv
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-pilot60-gpu7/qwen3-8b-lora-sft-1k_predictions.jsonl
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-pilot60-gpu7/qwen3-8b-lora-sft-1k_summary.csv
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-pilot60-gpu7/comparison_summary.csv
```

## Raw Summary

```text
model_label,split,total,exact_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,trajectory_valid_rate,hallucination_rate
qwen3-8b-base,overall,60,0.0,0.0,0.7333,0.0,0.0,0.0,0.0,0.0
qwen3-8b-base,multi_hop_qa,20,0.0,0.0,0.75,0.0,0.0,0.0,0.0,0.0
qwen3-8b-base,noisy_context_retrieval_qa,20,0.0,0.0,0.6,0.0,0.0,0.0,0.0,0.0
qwen3-8b-base,tool_use_qa,20,0.0,0.0,0.85,0.0,0.0,0.0,0.0,0.0
qwen3-8b-lora-sft-1k,overall,60,0.9167,0.9167,0.9333,0.9833,0.9,0.95,0.9833,0.0667
qwen3-8b-lora-sft-1k,multi_hop_qa,20,0.9,0.9,0.9,1.0,0.9,0.95,1.0,0.1
qwen3-8b-lora-sft-1k,noisy_context_retrieval_qa,20,0.9,0.9,0.9,1.0,0.9,0.95,1.0,0.1
qwen3-8b-lora-sft-1k,tool_use_qa,20,0.95,0.95,1.0,0.95,0.9,0.95,0.95,0.0
```

## Interpretation

The base model often knows the answer in natural language: `gold_answer_mention_rate=0.7333`. However, it does not follow the project Agent protocol under this prompt: `final_answer_rate=0.0`, `tool_call_success_rate=0.0`, and `trajectory_valid_rate=0.0`.

The LoRA adapter strongly changes the output format and task behavior:

```text
exact_match_rate: 0.0 -> 0.9167
final_answer_rate: 0.0 -> 0.9833
tool_call_success_rate: 0.0 -> 0.9
trajectory_valid_rate: 0.0 -> 0.9833
```

This is useful evidence that even a small 1k SFT pilot can teach Qwen3-8B the OpenSeeker ReAct/tool-call format. It should be presented as a pilot result, not as final held-out performance, because the eval samples come from the same 1k teacher-generated distribution used for SFT.

## Failure Notes

Base model noncompliance:

- Frequently answered in prose or pseudo-code instead of `Thought/Action/Observation/Final`.
- Often mentioned correct country names, but without parseable `Final:`.
- Sometimes used unapproved tool names such as `search` or `get_birthplace`.

LoRA remaining errors:

- Some United Kingdom answers became `England`, which counts as unsupported final answer under the current verifier.
- One sample drifted to a Marie Curie trajectory while the question was Charles Darwin.
- Several correct final answers had tool-call coverage `0.5` because the generated Action query omitted either the birthplace suffix or country suffix.
- One sample produced ReAct observations and gold answer but was truncated before `Final:`.

Representative LoRA failure excerpts:

```text
wikidata-isaac-newton-noisy-15: Final: England, gold United Kingdom
wikidata-charles-darwin-multi-hop-34: drifted to Marie Curie / Warsaw / Poland
wikidata-charles-darwin-noisy-36: Final: England, gold United Kingdom
wikidata-michael-faraday-tool-41: final correct, tool_call_coverage=0.5
```

## Resume-Safe Takeaway

Potential resume wording after a held-out follow-up:

```text
Built a Qwen3-8B LoRA SFT pilot over 1k verifier-filtered OpenSeeker Agent trajectories and added a base-vs-adapter evaluation harness. On a 60-sample training-distribution pilot, the adapter improved ReAct-format exact match from 0.0 to 0.9167 and tool-call success from 0.0 to 0.9 while preserving answer evidence checks.
```

Do not present this as final benchmark performance until a held-out seed/entity split is run.

## Next Steps

- Build a held-out evaluation set from entities not present in the 1k SFT data.
- Add an alias-aware answer normalizer for geopolitical cases such as `England` vs `United Kingdom`, while keeping strict mode for verifier reporting.
- Improve tool-call matching or train stricter query formatting so correct answers do not lose tool-call credit.
- Scale to 5k SFT data only after the held-out eval script and reporting table are stable.
