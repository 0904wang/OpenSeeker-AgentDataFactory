# 2026-06-11 Qwen3-8B LoRA SFT 1k Held-Out 200 Canonical Evaluation

## Status

Completed. Ran a 200-sample variant-expanded held-out evaluation comparing base Qwen3-8B against the 1k OpenSeeker LoRA adapter with canonical answer matching and error bucket metrics enabled.

This run used 60 held-out seed rows from offset 120 and expanded them into 200 question variants. It should be described as a 200-sample held-out variant evaluation, not 200 independent held-out entities.

## Goal

Measure whether the Qwen3-8B LoRA adapter still follows the OpenSeeker Agent protocol at a larger held-out variant scale, and separate strict exact-match errors from canonical alias matches, missing final answers, tool coverage gaps, and unsupported wrong answers.

## Remote Context

- SSH entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote branch: `main`
- Remote commit observed in launch log: `7b64c03`
- Local date: `2026-06-11 Asia/Shanghai`
- Remote run timestamp: `2026-06-10 16:07-16:21 UTC`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Base model: `Qwen/Qwen3-8B`
- Adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k`
- GPU: `CUDA_VISIBLE_DEVICES=7`
- tmux session: `openseeker-20260610-heldout200-canonical-eval-gpu7`
- Runner: `/data/wzl/OpenSeeker-AgentDataFactory/runs/heldout200-canonical-eval-gpu7.sh`
- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-heldout200-canonical-gpu7.log`
- Samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical`
- Eval results: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout200-canonical-gpu7`

## Pre-Launch Verification

The canonical evaluator changes were tested locally and remotely before launch:

```text
Local:  python -m pytest -> 38 passed in 13.79s
Remote: python -m pytest -> 38 passed in 4.17s
Remote canonical dry run: 2-sample LoRA GPU run wrote canonical_match_rate and error bucket rates
```

GPU preflight showed GPU7 available before launch:

```text
7, 667, 32607
```

## Launch Command

The approved tmux session ran:

```bash
tmux new-session -d -s openseeker-20260610-heldout200-canonical-eval-gpu7 \
  "bash -lc '/data/wzl/OpenSeeker-AgentDataFactory/runs/heldout200-canonical-eval-gpu7.sh 2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-heldout200-canonical-gpu7.log'"
```

The runner executed:

```bash
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli build-seeds \
  --out-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_heldout_60_offset120.jsonl \
  --limit 60 \
  --offset 120

PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_heldout_60_offset120.jsonl \
  --count 200 \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical \
  --batch-size 50 \
  --resume

CUDA_VISIBLE_DEVICES=7 \
PYTHONNOUSERSITE=1 \
HF_HUB_OFFLINE=1 \
TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers \
python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical/samples.jsonl \
  --model-label qwen3-8b-base-heldout200-canonical \
  --model-name-or-path Qwen/Qwen3-8B \
  --limit 200 \
  --batch-size 2 \
  --max-new-tokens 160 \
  --device cuda \
  --local-files-only \
  --disable-thinking \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout200-canonical-gpu7

CUDA_VISIBLE_DEVICES=7 \
PYTHONNOUSERSITE=1 \
HF_HUB_OFFLINE=1 \
TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers \
python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical/samples.jsonl \
  --model-label qwen3-8b-lora-sft-1k-heldout200-canonical \
  --model-name-or-path Qwen/Qwen3-8B \
  --adapter-path /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k \
  --limit 200 \
  --batch-size 2 \
  --max-new-tokens 160 \
  --device cuda \
  --local-files-only \
  --disable-thinking \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout200-canonical-gpu7
```

## Generation Summary

```text
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
200,200,0,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,0,
```

## Result Files

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout200-canonical-gpu7/qwen3-8b-base-heldout200-canonical_predictions.jsonl
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout200-canonical-gpu7/qwen3-8b-base-heldout200-canonical_summary.csv
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout200-canonical-gpu7/qwen3-8b-lora-sft-1k-heldout200-canonical_predictions.jsonl
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout200-canonical-gpu7/qwen3-8b-lora-sft-1k-heldout200-canonical_summary.csv
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout200-canonical-gpu7/comparison_summary.csv
```

## Raw Summary

```text
model_label,split,total,exact_match_rate,canonical_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,trajectory_valid_rate,hallucination_rate,correct_rate,canonical_alias_match_rate,missing_final_rate,trajectory_format_error_rate,tool_coverage_gap_rate,supported_but_wrong_answer_rate,unsupported_wrong_answer_rate
qwen3-8b-base-heldout200-canonical,overall,200,0.0,0.0,0.0,0.845,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0
qwen3-8b-lora-sft-1k-heldout200-canonical,overall,200,0.795,0.87,0.795,0.9,0.885,0.81,0.8975,0.885,0.015,0.65,0.075,0.115,0.0,0.145,0.0,0.015
```

Per task for LoRA:

```text
multi_hop_qa,67,exact=0.7761,canonical=0.8358,final=0.8358,tool_success=0.806,trajectory=0.8358
noisy_context_retrieval_qa,66,exact=0.8485,canonical=0.9545,final=1.0,tool_success=0.8182,trajectory=1.0
tool_use_qa,67,exact=0.7612,canonical=0.8209,final=0.8209,tool_success=0.806,trajectory=0.8209
```

## Error Buckets

Base model:

```text
missing_final: 200
```

LoRA adapter:

```text
correct: 130
canonical_alias_match: 15
missing_final: 23
tool_coverage_gap: 29
unsupported_wrong_answer: 3
```

Representative LoRA non-correct examples:

```text
canonical_alias_match:
  wikidata-james-clerk-maxwell-multi-hop-1: predicted Scotland, gold United Kingdom
  wikidata-alexander-fleming-tool-56: predicted Scotland, gold United Kingdom

missing_final:
  wikidata-james-clerk-maxwell-tool-2: gold mentioned, tool coverage 1.0, no parseable Final
  wikidata-paul-dirac-tool-14: gold mentioned, tool coverage 1.0, no parseable Final

tool_coverage_gap:
  wikidata-werner-heisenberg-multi-hop-10: predicted Germany, tool_call_coverage 0.5
  wikidata-c-v-raman-tool-26: predicted India, tool_call_coverage 0.0

unsupported_wrong_answer:
  wikidata-gregor-mendel-noisy-51: predicted Austria, gold Czech Republic
  wikidata-gregor-mendel-noisy-111: predicted Austria, gold Czech Republic
  wikidata-gregor-mendel-noisy-171: predicted Austria, gold Czech Republic
```

## Interpretation

This run strengthens the earlier 60-sample held-out result. The base model frequently mentions the correct answer in free-form text (`gold_answer_mention_rate=0.845`) but completely fails the project protocol (`final_answer_rate=0.0`, `trajectory_valid_rate=0.0`, `tool_call_success_rate=0.0`).

The 1k LoRA adapter generalizes the OpenSeeker format to a larger held-out variant set:

```text
strict exact match: 0.0 -> 0.795
canonical match: 0.0 -> 0.87
final answer rate: 0.0 -> 0.885
tool-call success: 0.0 -> 0.81
trajectory validity: 0.0 -> 0.885
unsupported wrong answer rate: 0.0 -> 0.015
```

The remaining error structure is useful for the next engineering iteration:

- `missing_final` means the model often follows the reasoning pattern but truncates or omits the final contract.
- `tool_coverage_gap` means the final answer is often right but the generated Action queries do not fully cover expected tool calls.
- `canonical_alias_match` confirms that country/region normalization is necessary for fair reporting.
- The only unsupported wrong-answer cluster is Gregor Mendel, where `Austria` competes with the seed-bank gold label `Czech Republic`.

## Resume-Safe Takeaway

Potential resume wording:

```text
Built a verifier-filtered OpenSeeker Agent data factory and trained a Qwen3-8B LoRA SFT pilot on 1k synthetic multi-hop/tool-use trajectories. On a 200-sample held-out variant evaluation, the adapter improved strict exact match from 0.0 to 0.795, canonical answer match to 0.87, tool-call success to 0.81, and trajectory validity to 0.885 over the base model.
```

Use the phrase `held-out variant evaluation`, not `200 independent held-out entities`.

## Next Steps

- Add a stricter prompt or SFT examples that always end with `Final: <answer>` to reduce `missing_final_rate=0.115`.
- Improve Action query templates and verifier tolerance for equivalent tool queries to reduce `tool_coverage_gap_rate=0.145`.
- Verify seed facts against Wikidata and add historical/current country aliases for cases like Gregor Mendel.
- Expand the seed bank before claiming a larger independent held-out benchmark.
- After seed verification, rerun a 500-sample variant evaluation or build a 200-entity independent held-out split.
