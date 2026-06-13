# Qwen3-8B v6-trained Mixed SFT v4/v5 Regression Evaluation

## Goal

After adding 400 v6 blind tool-choice training rows and improving v6 heldout observation faithfulness, re-evaluate v4 and v5 blind-hard heldouts to check for regressions.

## Remote Context

- Date: 2026-06-13
- Remote entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote workspace: `/data/wzl/OpenSeeker-AgentDataFactory`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice`

## Launch

### v4 Heldout

Session:

```text
openseeker-20260613-eval-v6trained-v4-gpu5
```

Launcher:

```text
/data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_mixed_v3_v4_v5blind_v6trained_v4heldout_gpu5.sh
```

Samples:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v4/samples.jsonl
```

Results:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v4heldout200-gpu5
```

### v5 Blind-hard Heldout

Session:

```text
openseeker-20260613-eval-v6trained-v5-gpu6
```

Launcher:

```text
/data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_mixed_v3_v4_v5blind_v6trained_v5blindhard_gpu6.sh
```

Samples:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v5-blind-hard/samples.jsonl
```

Results:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v5blindhard-heldout200-gpu6
```

## Preflight

Before launch:

```text
5, 3493 MiB, 32607 MiB, 0 %
6, 3505 MiB, 32607 MiB, 0 %
```

Both GPUs were below the project-local `4000 MiB` free-GPU threshold. Result directories did not exist before launch.

## Raw Summaries

### v4 Heldout200

```csv
model_label,split,total,exact_match_rate,canonical_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,observation_faithfulness_rate,observation_coverage_avg,trajectory_valid_rate,hallucination_rate,correct_rate,canonical_alias_match_rate,missing_final_rate,trajectory_format_error_rate,tool_coverage_gap_rate,supported_but_wrong_answer_rate,unsupported_wrong_answer_rate
qwen3-8b-lora-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v4heldout200,overall,200,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
qwen3-8b-lora-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v4heldout200,multi_hop_qa,67,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
qwen3-8b-lora-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v4heldout200,noisy_context_retrieval_qa,66,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
qwen3-8b-lora-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v4heldout200,tool_use_qa,67,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
```

### v5 Blind-hard Heldout200

```csv
model_label,split,total,exact_match_rate,canonical_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,observation_faithfulness_rate,observation_coverage_avg,trajectory_valid_rate,hallucination_rate,correct_rate,canonical_alias_match_rate,missing_final_rate,trajectory_format_error_rate,tool_coverage_gap_rate,supported_but_wrong_answer_rate,unsupported_wrong_answer_rate
qwen3-8b-lora-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v5blindhard-heldout200,overall,200,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
qwen3-8b-lora-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v5blindhard-heldout200,multi_hop_qa,67,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
qwen3-8b-lora-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v5blindhard-heldout200,noisy_context_retrieval_qa,66,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
qwen3-8b-lora-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v5blindhard-heldout200,tool_use_qa,67,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
```

## Metrics

```text
v4 heldout200:
  exact_match_rate 1.0
  canonical_match_rate 1.0
  tool_call_success_rate 1.0
  observation_faithfulness_rate 1.0
  trajectory_valid_rate 1.0
  hallucination_rate 0.0
  correct_rate 1.0

v5 blind-hard heldout200:
  exact_match_rate 1.0
  canonical_match_rate 1.0
  tool_call_success_rate 1.0
  observation_faithfulness_rate 1.0
  trajectory_valid_rate 1.0
  hallucination_rate 0.0
  correct_rate 1.0
```

## Combined Comparison

```text
Previous 2k mixed v3/v4/v5blind adapter:
  v4 heldout: all core metrics 1.0
  v5 blind-hard: all core metrics 1.0
  v6 blind tool-choice: observation_faithfulness 0.945, observation_coverage 0.9725

New 2.4k mixed v3/v4/v5blind/v6 adapter:
  v4 heldout: all core metrics 1.0
  v5 blind-hard: all core metrics 1.0
  v6 blind tool-choice: observation_faithfulness 0.985, observation_coverage 0.9925
```

## Analysis

The v6-targeted mixed SFT did not regress the two earlier heldouts. The current best adapter preserves saturated v4/v5 results and improves v6 observation faithfulness by 4 absolute points.

The closed loop is now demonstrated:

```text
harder heldout design -> failure audit -> targeted synthetic data -> SFT -> regression evaluation
```

For the resume project, this is stronger than a raw SFT result because it shows a verifier-driven data improvement cycle and not just one training run.

## Next Steps

1. Update README with the 2k vs 2.4k comparison table.
2. Keep the v6 result as the current project milestone.
3. For a next technical step, implement v7 relation-diverse tasks so the project no longer depends mainly on the birthplace-to-country path.
