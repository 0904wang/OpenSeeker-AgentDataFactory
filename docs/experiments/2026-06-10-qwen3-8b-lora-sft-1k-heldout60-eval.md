# 2026-06-10 Qwen3-8B LoRA SFT 1k Held-Out 60 Evaluation

## Status

Completed. The Qwen3-8B base model and the 1k OpenSeeker LoRA adapter were evaluated on a 60-sample held-out deterministic OpenSeeker split generated from seed rows offset after the original training seed bank.

## Goal

Check whether the 1k LoRA SFT adapter generalizes beyond the first training-distribution sample slice. This is a small held-out entity/template split, not yet a final external benchmark.

## Remote Context

- SSH entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote branch: `main`
- Remote commit observed in launch log: `7b64c03`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Base model: `Qwen/Qwen3-8B`
- Adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k`
- GPU: `CUDA_VISIBLE_DEVICES=7`
- tmux session: `openseeker-20260610-heldout-eval-qwen3-8b-sft-1k-gpu7`
- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-heldout60-gpu7.log`
- Held-out samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-60/samples.jsonl`
- Eval results: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout60-gpu7`

## Verification Before Launch

Local tests after adding held-out seed offsets and evaluation coverage:

```text
python -m pytest
36 passed in 15.80s
```

Remote tests after narrow file sync:

```text
python -m pytest
36 passed in 4.57s
```

Held-out generation completed:

```text
OpenSeeker seed build complete: rows=60 out_file=/data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_heldout_60.jsonl
OpenSeeker AgentDataFactory generation complete: accepted=60 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-60
```

Held-out sample summary:

```text
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
60,60,0,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,0,
```

## Launch Command

The approved tmux session ran held-out seed building, deterministic sample generation, base evaluation, and LoRA evaluation:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory

PYTHONNOUSERSITE=1 python -m openseeker_factory.cli build-seeds \
  --source wikidata \
  --limit 60 \
  --offset 120 \
  --out /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_heldout_60.jsonl

PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_heldout_60.jsonl \
  --count 60 \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-60

CUDA_VISIBLE_DEVICES=7 \
PYTHONNOUSERSITE=1 \
HF_HUB_OFFLINE=1 \
TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers \
python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-60/samples.jsonl \
  --model-label qwen3-8b-base-heldout \
  --model-name-or-path Qwen/Qwen3-8B \
  --limit 60 \
  --batch-size 2 \
  --max-new-tokens 160 \
  --device cuda \
  --local-files-only \
  --disable-thinking \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout60-gpu7

CUDA_VISIBLE_DEVICES=7 \
PYTHONNOUSERSITE=1 \
HF_HUB_OFFLINE=1 \
TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers \
python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-60/samples.jsonl \
  --model-label qwen3-8b-lora-sft-1k-heldout \
  --model-name-or-path Qwen/Qwen3-8B \
  --adapter-path /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k \
  --limit 60 \
  --batch-size 2 \
  --max-new-tokens 160 \
  --device cuda \
  --local-files-only \
  --disable-thinking \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout60-gpu7
```

## Result Files

Fresh files written by this run:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout60-gpu7/qwen3-8b-base-heldout_predictions.jsonl
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout60-gpu7/qwen3-8b-base-heldout_summary.csv
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout60-gpu7/qwen3-8b-lora-sft-1k-heldout_predictions.jsonl
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-heldout60-gpu7/qwen3-8b-lora-sft-1k-heldout_summary.csv
```

Note: `comparison_summary.csv` existed from an earlier run in the same directory and had an older timestamp. The metrics below use the two fresh per-model summary files.

## Raw Summary

Base Qwen3-8B:

```text
model_label,split,total,exact_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,trajectory_valid_rate,hallucination_rate
qwen3-8b-base-heldout,overall,60,0.0,0.0,0.9,0.0,0.0,0.0,0.0,0.0
qwen3-8b-base-heldout,multi_hop_qa,20,0.0,0.0,0.85,0.0,0.0,0.0,0.0,0.0
qwen3-8b-base-heldout,noisy_context_retrieval_qa,20,0.0,0.0,0.95,0.0,0.0,0.0,0.0,0.0
qwen3-8b-base-heldout,tool_use_qa,20,0.0,0.0,0.9,0.0,0.0,0.0,0.0,0.0
```

Qwen3-8B LoRA SFT 1k:

```text
model_label,split,total,exact_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,trajectory_valid_rate,hallucination_rate
qwen3-8b-lora-sft-1k-heldout,overall,60,0.8167,0.8167,0.9167,0.9,0.8333,0.9083,0.9,0.0833
qwen3-8b-lora-sft-1k-heldout,multi_hop_qa,20,0.8,0.8,0.95,0.85,0.8,0.9,0.85,0.05
qwen3-8b-lora-sft-1k-heldout,noisy_context_retrieval_qa,20,0.85,0.85,0.85,1.0,0.8,0.9,1.0,0.15
qwen3-8b-lora-sft-1k-heldout,tool_use_qa,20,0.8,0.8,0.95,0.85,0.9,0.925,0.85,0.05
```

## Failure Notes

Base model:

- `exact_failures=60/60`.
- It often mentioned the correct gold answer somewhere in free-form output (`gold_answer_mention_rate=0.9`) but did not emit a parseable `Final:` line or valid OpenSeeker trajectory.
- This confirms the base model has factual recall but does not follow the project-specific Agent protocol under the evaluation prompt.

LoRA adapter:

- `exact_failures=11/60`.
- Failure distribution: `multi_hop_qa=4`, `noisy_context_retrieval_qa=3`, `tool_use_qa=4`.
- Several failures still had correct evidence mentions and successful tool coverage, but no parseable `Final:` line.
- Some errors reflect label granularity in seed facts, for example `Scotland` or `Austria` predicted where the gold label was `United Kingdom` or `Czech Republic`.

Representative LoRA failures:

```text
wikidata-james-clerk-maxwell-multi-hop-1: predicted Scotland, gold United Kingdom
wikidata-james-clerk-maxwell-tool-2: gold mentioned but no parseable Final answer
wikidata-paul-dirac-tool-14: gold mentioned but no parseable Final answer
wikidata-gregor-mendel-noisy-51: predicted Austria, gold Czech Republic
```

## Interpretation

Compared with the base model, the LoRA adapter learned the required OpenSeeker output contract and retained most answer behavior on the held-out split:

```text
exact_match_rate: 0.0 -> 0.8167
final_answer_rate: 0.0 -> 0.9
tool_call_success_rate: 0.0 -> 0.8333
trajectory_valid_rate: 0.0 -> 0.9
hallucination_rate: 0.0 -> 0.0833
```

The drop from the earlier training-distribution pilot (`exact_match_rate=0.9167`) to held-out (`0.8167`) is expected and useful: it gives a more honest resume-safe signal that the 1k SFT has learned format and tool behavior but still overfits some entity/country surface forms.

## Resume-Safe Takeaway

Possible wording after one larger held-out run:

```text
Built an OpenSeeker Agent data factory with verifier-filtered multi-hop/tool-use trajectories, trained a Qwen3-8B LoRA SFT pilot on 1k synthetic Agent samples, and added a base-vs-adapter evaluation harness. On a 60-sample held-out entity split, the adapter improved exact match from 0.0 to 0.8167 and tool-call success from 0.0 to 0.8333 while maintaining trajectory validity at 0.9.
```

Keep this as a pilot result until the held-out split is expanded and seed facts are externally verified.

## Risks and Next Steps

- The held-out data is deterministic and generated from the local seed bank; it is not yet an external benchmark.
- Some seed labels encode modern country names, while model answers may use birthplace regions or historical countries. Add alias/canonicalization before treating exact match as final.
- Create a larger held-out evaluation, ideally 200 to 500 samples, after verifying seed facts against Wikidata or another source.
- Add per-error bucketing for `missing_final`, `wrong_country_alias`, `tool_coverage_gap`, and `entity_drift`.
- Consider a second SFT run with more diverse teacher-generated trajectories once held-out evaluation is stable.
