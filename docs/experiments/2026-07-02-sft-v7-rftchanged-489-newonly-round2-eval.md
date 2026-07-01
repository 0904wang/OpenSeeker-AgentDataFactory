# SFT v7 RFT Changed 489 New-only Round 2 Evaluation

## Metadata

- Experiment name: sft-v7-rftchanged-489-newonly-round2
- Date: 2026-07-02
- Goal: Test the clean RFT/ReST-EM continuation setup: start from the current 3.5k RFT-changed checkpoint and train only on verifier-accepted v7 changed trajectories.
- Status: success
- Operator: Codex
- Remote host: `user@ssh-22.e6.luyouxia.net -p 29509`
- Isolated worktree: `/data/wzl/OpenSeeker-AgentDataFactory/runs/repo-v7-relation-diverse-20260701`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Base model: `/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218`
- Start adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-3p5k-mixed-v3-v4-v5blind-v6-rftchanged-round1-20260701`
- Output adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-v7rftchanged-489-newonly-round2-20260702`
- GPU selection: training `CUDA_VISIBLE_DEVICES=0,6`; v7 eval `CUDA_VISIBLE_DEVICES=0`; regression evals `0,6,7`

## Commands

New-only dataset materialization:

```bash
python - <<'PY'
# Read /data/wzl/OpenSeeker-AgentDataFactory/data/rft/rft_v7_train268_changed_sft_conversations.jsonl
# Write /data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_v7_rftchanged_489_newonly.jsonl
# Register openseeker_sft_v7_rftchanged_489_newonly in data/llamafactory/dataset_info.json
PY
```

Training launcher:

```bash
/data/wzl/OpenSeeker-AgentDataFactory/runs/repo-v7-relation-diverse-20260701/runs/launch_sft_v7_rftchanged_489_newonly_gpu06.sh
```

Effective training config:

```yaml
adapter_name_or_path: /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-3p5k-mixed-v3-v4-v5blind-v6-rftchanged-round1-20260701
dataset: openseeker_sft_v7_rftchanged_489_newonly
max_samples: 489
output_dir: /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-v7rftchanged-489-newonly-round2-20260702
learning_rate: 2.0e-5
num_train_epochs: 1.0
per_device_train_batch_size: 1
gradient_accumulation_steps: 8
```

v7 evaluation:

```bash
CUDA_VISIBLE_DEVICES=0 PYTHONNOUSERSITE=1 python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v7-relation-diverse/samples.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-v7rftchanged-489-newonly-round2-v7relationdiverse-heldout200-gpu0 \
  --model-label qwen3-8b-lora-sft-v7rftchanged-489-newonly-round2-v7relationdiverse-heldout200 \
  --model-name-or-path /data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218 \
  --adapter-path /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-v7rftchanged-489-newonly-round2-20260702 \
  --batch-size 2 \
  --max-new-tokens 160 \
  --device cuda \
  --local-files-only \
  --disable-thinking
```

Regression evaluations used the same adapter on:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v4/samples.jsonl
/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v5-blind-hard/samples.jsonl
/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v6-blind-tool-choice-hard/samples.jsonl
```

## Paths

- New-only SFT data: `/data/wzl/OpenSeeker-AgentDataFactory/data/llamafactory/openseeker_sft_v7_rftchanged_489_newonly.jsonl`
- Training config: `/data/wzl/OpenSeeker-AgentDataFactory/runs/repo-v7-relation-diverse-20260701/configs/llamafactory/qwen3_8b_lora_sft_v7_rftchanged_489_newonly_round2.yaml`
- Training log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/20260702-sft-v7-rftchanged-489-newonly-gpu06.log`
- v7 eval summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-v7rftchanged-489-newonly-round2-v7relationdiverse-heldout200-gpu0/qwen3-8b-lora-sft-v7rftchanged-489-newonly-round2-v7relationdiverse-heldout200_summary.csv`
- v4 eval summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-v7rftchanged-489-newonly-round2-v4heldout200-gpu6/qwen3-8b-lora-sft-v7rftchanged-489-newonly-round2-v4heldout200_summary.csv`
- v5 eval summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-v7rftchanged-489-newonly-round2-v5blindhard-heldout200-gpu7/qwen3-8b-lora-sft-v7rftchanged-489-newonly-round2-v5blindhard-heldout200_summary.csv`
- v6 eval summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-v7rftchanged-489-newonly-round2-v6blindtoolchoice-heldout200-gpu0/qwen3-8b-lora-sft-v7rftchanged-489-newonly-round2-v6blindtoolchoice-heldout200_summary.csv`

## Raw Training Summary

```json
{
  "epoch": 1.0,
  "train_loss": 0.044000939048569776,
  "train_runtime": 56.9121,
  "train_samples_per_second": 8.153,
  "train_steps_per_second": 0.51
}
```

LLaMAFactory reported:

```text
Num examples = 464
Num Epochs = 1
Total train batch size = 16
Total optimization steps = 29
Number of trainable parameters = 43,646,976
```

## Main Metrics

Comparison against the previous v7 baseline checkpoint:

| Split | Model | Exact | Tool success | Observation faithfulness | Hallucination | Strict correct |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| v7 heldout200 | 3.5k RFT-changed round1 | 0.860 | 0.720 | 0.500 | 0.140 | 0.605 |
| v7 heldout200 | +489 new-only RFT SFT | 0.915 | 0.730 | 0.555 | 0.085 | 0.665 |

Regression checks:

| Heldout | Exact | Tool success | Observation faithfulness | Hallucination | Strict correct |
| --- | ---: | ---: | ---: | ---: | ---: |
| canonical-v4 heldout200 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 |
| canonical-v5 blind hard heldout200 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 |
| canonical-v6 blind tool-choice heldout200 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 |

v7 relation breakdown:

| Relation profile | Correct before | Correct after | Exact after | Tool success after | Obs faith after | Hallucination after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| birthplace_country | 1.000 | 1.000 | 1.000 | 1.000 | 0.860 | 0.000 |
| education_country | 0.540 | 0.540 | 1.000 | 0.540 | 0.440 | 0.000 |
| employer_country | 0.580 | 0.620 | 0.980 | 0.640 | 0.480 | 0.020 |
| award_country | 0.300 | 0.500 | 0.680 | 0.740 | 0.440 | 0.320 |

Error buckets after training:

```text
correct: 133
tool_coverage_gap: 50
unsupported_wrong_answer: 17
```

## Failures / Warnings

- A replay-mix configuration (`3.5k old + 268 v7 gold + 489 v7 changed`) was briefly started and stopped after the user clarified that the clean RFT comparison should train only on new data. It did not produce an adapter; the partial directory only contains training metadata and should not be treated as a result.
- v7 still has substantial room left: `education_country` remains stuck at `0.540` strict correct because the model often answers correctly while selecting the wrong first-hop relation, and `award_country` still has `16/50` unsupported wrong answers.
- GPU1/6/7 showed non-OpenSeeker processes after evaluation; inspection showed they belonged to `/home/user/JC/...` jobs, so no cleanup was performed.

## Analysis

The clean new-only RFT continuation worked: strict v7 correctness improved by `+0.060` absolute and hallucination dropped by `-0.055` without regressing saturated v4/v5/v6 heldouts. This gives a clean table row for Stage A RFT:

| Run | Data | v7 heldout failures | v7 strict correct |
| --- | --- | ---: | ---: |
| SFT + RFT round1 baseline | 3.5k mixed | 79/200 | 0.605 |
| + RFT v7 round2 new-only | +489 changed trajectories | 67/200 | 0.665 |

The gain is concentrated where expected: `award_country` improved from `0.300` to `0.500`, while birthplace stayed saturated. Education did not improve on strict correctness, so the next data step should target relation intent disambiguation for `education_country` and improve award answer support.

For the resume project, this is a strong result because it demonstrates a real closed loop: sample K=4 trajectories, verifier-filter to changed accepted traces, continued-SFT on only new data, then heldout and regression evaluation.

## Next Steps

- Build a v7 RFT round3 prompt set focused on education and award failures, preferably with more entity diversity and fewer repeated birthplace variants.
- Add resume-capable or sharded RFT sampling before scaling beyond K=4 and a few hundred prompts.
- Consider the replay-mix version only after the clean RFT table is finalized; it may be useful as the final model but should remain a separate experiment.
