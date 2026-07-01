# RFT Changed Round 1 Evaluation

## Metadata

- Experiment name: rftchanged-round1-v6-v4-v5-eval
- Date: 2026-07-01
- Goal: Evaluate the RFT changed-only SFT adapter on the target v6 heldout and v4/v5 regression heldouts.
- Status: success
- Operator: Codex
- Remote host: `user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Adapter path: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-3p5k-mixed-v3-v4-v5blind-v6-rftchanged-round1-20260701`
- GPU selection:
  - v6: `CUDA_VISIBLE_DEVICES=0`
  - v4: `CUDA_VISIBLE_DEVICES=6`
  - v5: `CUDA_VISIBLE_DEVICES=7`

## Commands

Launch:

```bash
tmux new-session -d -s openseeker-20260701-eval-rftchanged-v6-gpu0 \
  "bash /data/wzl/OpenSeeker-AgentDataFactory/repo/runs/launch_eval_rftchanged_round1_v6heldout_gpu0.sh"

tmux new-session -d -s openseeker-20260701-eval-rftchanged-v4-gpu6 \
  "bash /data/wzl/OpenSeeker-AgentDataFactory/repo/runs/launch_eval_rftchanged_round1_v4heldout_gpu6.sh"

tmux new-session -d -s openseeker-20260701-eval-rftchanged-v5-gpu7 \
  "bash /data/wzl/OpenSeeker-AgentDataFactory/repo/runs/launch_eval_rftchanged_round1_v5blindhard_gpu7.sh"
```

## Paths

- v6 samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v6-blind-tool-choice-hard/samples.jsonl`
- v6 results: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-rftchanged-round1-v6blindtoolchoice-heldout200-gpu0`
- v6 log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-rftchanged-round1-v6blindtoolchoice-heldout200-gpu0.log`
- v4 samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v4/samples.jsonl`
- v4 results: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-rftchanged-round1-v4heldout200-gpu6`
- v4 log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-rftchanged-round1-v4heldout200-gpu6.log`
- v5 samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v5-blind-hard/samples.jsonl`
- v5 results: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-rftchanged-round1-v5blindhard-heldout200-gpu7`
- v5 log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-rftchanged-round1-v5blindhard-heldout200-gpu7.log`

## Raw Result Summary

v6 heldout summary:

```csv
model_label,split,total,exact_match_rate,canonical_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,observation_faithfulness_rate,observation_coverage_avg,trajectory_valid_rate,hallucination_rate,correct_rate,canonical_alias_match_rate,missing_final_rate,trajectory_format_error_rate,tool_coverage_gap_rate,supported_but_wrong_answer_rate,unsupported_wrong_answer_rate
qwen3-8b-lora-sft-rftchanged-round1-v6blindtoolchoice-heldout200,overall,200,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
```

v4 heldout summary:

```csv
qwen3-8b-lora-sft-rftchanged-round1-v4heldout200,overall,200,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
```

v5 blind-hard heldout summary:

```csv
qwen3-8b-lora-sft-rftchanged-round1-v5blindhard-heldout200,overall,200,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
```

## Metrics

| Run | Data | Heldout | Failures | Observation Faithfulness | Tool Success | Trajectory Valid |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| SFT-only A0 | 2.4k mixed | v6 blind tool-choice | 3/200 | 0.985 | 1.000 | 1.000 |
| SFT + RFT Round 1 | 2.4k + 1,095 changed RFT | v6 blind tool-choice | 0/200 | 1.000 | 1.000 | 1.000 |
| SFT-only A0 | 2.4k mixed | v4 | 0/200 | 1.000 | 1.000 | 1.000 |
| SFT + RFT Round 1 | 2.4k + 1,095 changed RFT | v4 | 0/200 | 1.000 | 1.000 | 1.000 |
| SFT-only A0 | 2.4k mixed | v5 blind-hard | 0/200 | 1.000 | 1.000 | 1.000 |
| SFT + RFT Round 1 | 2.4k + 1,095 changed RFT | v5 blind-hard | 0/200 | 1.000 | 1.000 | 1.000 |

## Failures / Warnings

- Evaluation logs contain repeated generation-config warnings about `temperature`, `top_p`, and `top_k`; evaluation uses deterministic generation (`do_sample=False`), and all summaries were written successfully.
- This heldout is now saturated. Further claims should use a harder v7 heldout or a relation-diverse split.

## Analysis

RFT Round 1 produced the clean result the stage needed: the v6 target heldout improved from `3/200` failures to `0/200`, while v4 and v5 regression heldouts stayed fully saturated.

The important methodological point is that the training did not use all `9,429` verifier-passing RFT samples. It used only the `1,095` accepted trajectories that actually differed from the original gold trace, avoiding a shallow duplication loop.

For the resume project, the strongest wording is now:

```text
Implemented verifier-filtered RFT/ReST-EM from a Qwen3-8B SFT checkpoint. Sampled 9.6k trajectories, filtered 9,429 all-pass candidates, retained 1,095 non-duplicate changed trajectories for continued SFT, and reduced v6 blind tool-choice heldout failures from 3/200 to 0/200 without regressing v4/v5 heldouts.
```

## Next Steps

- Stop Stage A here unless a harder v7 heldout is added; current v4/v5/v6 are saturated.
- If continuing, build a v7 relation-diverse heldout before running RFT Round 2.
- Update README/resume material with the RFT result.
