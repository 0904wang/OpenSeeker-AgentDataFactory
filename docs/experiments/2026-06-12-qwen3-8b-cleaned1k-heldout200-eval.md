# 2026-06-12 Qwen3-8B Cleaned 1k LoRA Held-Out 200 Evaluation

## Metadata

- Experiment name: `qwen3-8b-lora-sft-1k-cleaned-heldout200`
- Date: 2026-06-12 Asia/Shanghai
- Goal: Evaluate the cleaned 1k Qwen3-8B LoRA adapter on the existing 200-sample held-out variant split.
- Status: success
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Branch: `main`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Base model snapshot: `/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218`
- Adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-cleaned`
- GPU selection: `CUDA_VISIBLE_DEVICES=7`
- Number of GPUs: 1

## Commands

Preflight:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 '
  nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader &&
  tmux list-sessions 2>/dev/null || true &&
  test -f /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical/samples.jsonl &&
  wc -l /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical/samples.jsonl &&
  test -f /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-cleaned/adapter_model.safetensors &&
  cd /data/wzl/OpenSeeker-AgentDataFactory/repo &&
  source /home/user/anaconda3/etc/profile.d/conda.sh &&
  conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory &&
  PYTHONNOUSERSITE=1 python -m pytest tests/test_evaluation.py tests/test_cli.py
'
```

Preflight result:

```text
GPU7: 18 MiB / 32607 MiB
samples: 200
adapter_model.safetensors: 167M
tests: 20 passed in 1.19s
```

Smoke test:

```bash
CUDA_VISIBLE_DEVICES=7 PYTHONNOUSERSITE=1 python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical/samples.jsonl \
  --model-label qwen3-8b-lora-sft-1k-cleaned-smoke2 \
  --model-name-or-path /data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218 \
  --adapter-path /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-cleaned \
  --limit 2 \
  --batch-size 2 \
  --max-new-tokens 160 \
  --device cuda \
  --local-files-only \
  --disable-thinking \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-cleaned-heldout200-smoke2-gpu7
```

Smoke result:

```text
overall,total=2,exact=1.0,canonical=1.0,final=1.0,tool_call_success=1.0,trajectory_valid=1.0
```

Launch:

```bash
tmux new-session -d -s openseeker-20260612-eval-cleaned1k-heldout200-gpu7 \
  "bash -lc 'cd /data/wzl/OpenSeeker-AgentDataFactory/repo && \
  source /home/user/anaconda3/etc/profile.d/conda.sh && \
  conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && \
  export HF_HOME=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface && \
  export TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers && \
  export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 && \
  CUDA_VISIBLE_DEVICES=7 PYTHONNOUSERSITE=1 python -m openseeker_factory.cli evaluate-model \
    --samples /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical/samples.jsonl \
    --model-label qwen3-8b-lora-sft-1k-cleaned-heldout200 \
    --model-name-or-path /data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218 \
    --adapter-path /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-cleaned \
    --limit 200 \
    --batch-size 2 \
    --max-new-tokens 160 \
    --device cuda \
    --local-files-only \
    --disable-thinking \
    --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-cleaned-heldout200-gpu7 \
    2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-cleaned-heldout200-gpu7.log'"
```

Monitoring:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 '
  nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader &&
  ps -u user -o pid,etime,pcpu,pmem,cmd | grep "evaluate-model" | grep -v grep || true &&
  tmux list-sessions 2>/dev/null || true &&
  tail -n 50 /data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-cleaned-heldout200-gpu7.log &&
  ls -lah /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-cleaned-heldout200-gpu7
'
```

## Paths

- Samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical/samples.jsonl`
- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-cleaned-heldout200-gpu7.log`
- Results dir: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-cleaned-heldout200-gpu7`
- Predictions: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-cleaned-heldout200-gpu7/qwen3-8b-lora-sft-1k-cleaned-heldout200_predictions.jsonl`
- Summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-cleaned-heldout200-gpu7/qwen3-8b-lora-sft-1k-cleaned-heldout200_summary.csv`
- Local record: `D:\resume\Data synthesis\docs\experiments\2026-06-12-qwen3-8b-cleaned1k-heldout200-eval.md`

## Raw Result Summary

```text
model_label,split,total,exact_match_rate,canonical_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,trajectory_valid_rate,hallucination_rate,correct_rate,canonical_alias_match_rate,missing_final_rate,trajectory_format_error_rate,tool_coverage_gap_rate,supported_but_wrong_answer_rate,unsupported_wrong_answer_rate
qwen3-8b-lora-sft-1k-cleaned-heldout200,overall,200,1.0,1.0,1.0,1.0,1.0,0.65,0.825,1.0,0.0,0.65,0.0,0.0,0.0,0.35,0.0,0.0
qwen3-8b-lora-sft-1k-cleaned-heldout200,multi_hop_qa,67,1.0,1.0,1.0,1.0,1.0,0.6567,0.8284,1.0,0.0,0.6567,0.0,0.0,0.0,0.3433,0.0,0.0
qwen3-8b-lora-sft-1k-cleaned-heldout200,noisy_context_retrieval_qa,66,1.0,1.0,1.0,1.0,1.0,0.6212,0.8106,1.0,0.0,0.6212,0.0,0.0,0.0,0.3788,0.0,0.0
qwen3-8b-lora-sft-1k-cleaned-heldout200,tool_use_qa,67,1.0,1.0,1.0,1.0,1.0,0.6716,0.8358,1.0,0.0,0.6716,0.0,0.0,0.0,0.3284,0.0,0.0
```

Result files:

```text
predictions size: 179K
summary size: 914 bytes
tmux session exited after completion
GPU7 returned to 18 MiB after completion
```

## Metrics

| Metric | Value | Notes |
| --- | ---: | --- |
| total | 200 | Held-out variant split, not 200 independent entities |
| exact_match_rate | 1.0 | All predictions had exact final answers |
| canonical_match_rate | 1.0 | No alias-only corrections needed |
| final_answer_rate | 1.0 | Missing-final issue disappeared in this run |
| trajectory_valid_rate | 1.0 | Output format remained parseable |
| tool_call_success_rate | 0.65 | Main remaining weakness |
| tool_call_coverage_avg | 0.825 | Many rows had partial tool coverage |
| hallucination_rate | 0.0 | No unsupported wrong-answer bucket |
| correct_rate | 0.65 | Correct requires answer and tool coverage |
| tool_coverage_gap_rate | 0.35 | 70 of 200 rows |

## Comparison Context

These rows are useful for interpretation, but they are not a perfectly controlled same-prompt comparison: the base and old-adapter rows come from earlier held-out canonical runs/rescoring, while the cleaned adapter row is a fresh generation under the current evaluator prompt.

| Model / run | Exact | Canonical | Final | Tool success | Trajectory | Tool gap | Unsupported wrong |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Base Qwen3-8B, earlier canonical run | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Old 1k LoRA, rescore v2 | 0.795 | 0.87 | 0.885 | 0.84 | 0.885 | 0.135 | 0.015 |
| Cleaned 1k LoRA, fresh run | 1.0 | 1.0 | 1.0 | 0.65 | 1.0 | 0.35 | 0.0 |

## Error Buckets

```text
correct: 130
tool_coverage_gap: 70
```

By task:

```text
multi_hop_qa: correct=44, tool_coverage_gap=23
tool_use_qa: correct=45, tool_coverage_gap=22
noisy_context_retrieval_qa: correct=41, tool_coverage_gap=25
```

Representative tool-gap behavior:

```text
Max Planck: Final answer Germany was correct, but the generated calls used natural property names like birthplace/country and the first observation was not the expected P19 evidence.
Werner Heisenberg: Final answer Germany was correct, but coverage was 0.5 because the tool-call format did not fully match the expected Wikidata property chain.
Paul Dirac: Final answer United Kingdom was correct, but several variants only partially covered the expected two-step lookup chain.
```

## Failures / Warnings

- Transformers emitted repeated warnings that generation flags `temperature`, `top_p`, and `top_k` were not valid under this generation mode. The run still completed and wrote predictions plus summary.
- `TRANSFORMERS_CACHE` is deprecated, but it was kept to force offline reuse of the existing model cache.
- The metric result is strong on answer format but weaker on verifier tool coverage. It should not be summarized as a blanket improvement over the previous adapter.

## Analysis

The cleaned 1k adapter fixed the most visible output-contract issues: every held-out variant had a parseable `Final` answer, every final answer matched the gold label exactly, and every trajectory was syntactically valid. This is a major improvement for answer-format reliability compared with the earlier held-out 200 run.

The tradeoff is that verifier-level tool behavior regressed. The model often produced natural-language tool keys such as `birthplace` and `country`, or mixed an incorrect observation with a correct final answer. The evaluator therefore counted many rows as `tool_coverage_gap`, leaving `correct_rate` at 0.65 even though exact answer accuracy was 1.0.

For the data factory, this suggests the repair/cleaning pass made the answer contract much cleaner but did not enforce tool-call canonicalization strongly enough. The next data iteration should add more canonical `wikidata_lookup[entity, P19]` and `wikidata_lookup[place, P17]` examples, plus a verifier or rewrite rule that rejects natural property names when the expected property ID is known.

For resume use, report both sides of the result: the cleaned adapter achieved perfect answer/final/trajectory rates on the held-out variant split, but the stricter verifier exposed a remaining tool-call coverage gap. That is a better engineering story than only quoting exact match.

## Next Steps

- Add a trajectory canonicalization pass that rewrites or rejects tool calls using natural property names when the seed has known `P19` and `P17` evidence.
- Add an SFT data audit metric for `property_id_call_rate`, measuring how often trajectories use canonical `P19`/`P17` rather than free-form tool keys.
- Rerun a small 100-sample cleaned-v2 generation and evaluate whether tool-call success recovers without losing final-answer reliability.
- Consider evaluating the old and cleaned adapters again under exactly the same current prompt to remove comparison ambiguity.
