# Qwen3-8B v6-trained Mixed SFT on v6 Blind Tool-choice Heldout200

## Goal

Evaluate the new 2.4k mixed v3/v4/v5blind/v6 adapter on the v6 blind tool-choice heldout200 split and compare it to the previous 2k mixed v3/v4/v5blind adapter.

Primary target metric:

```text
observation_faithfulness_rate
```

Previous 2k mixed adapter on this heldout:

```text
observation_faithfulness_rate 0.945
observation_coverage_avg 0.9725
answer/tool/trajectory/correct metrics 1.0
```

## Remote Context

- Date: 2026-06-13
- Remote entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote workspace: `/data/wzl/OpenSeeker-AgentDataFactory`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Evaluation session: `openseeker-20260613-eval-mixed-v6trained-v6heldout-gpu6`
- GPU selection: `CUDA_VISIBLE_DEVICES=6`
- Number of GPUs: 1

GPU7 was avoided because it still had more than 4000 MiB occupied. GPU6 was selected because it was below the project free-GPU threshold.

## Inputs

Samples:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v6-blind-tool-choice-hard/samples.jsonl
```

Adapter:

```text
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice
```

Base model:

```text
/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218
```

## Launch

Launcher:

```text
/data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_mixed_v3_v4_v5blind_v6trained_v6blindtoolchoice_gpu6.sh
```

Tmux command:

```bash
tmux new-session -d -s openseeker-20260613-eval-mixed-v6trained-v6heldout-gpu6 \
  "bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_mixed_v3_v4_v5blind_v6trained_v6blindtoolchoice_gpu6.sh"
```

Effective command:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
CUDA_VISIBLE_DEVICES=6 PYTHONNOUSERSITE=1 python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v6-blind-tool-choice-hard/samples.jsonl \
  --model-label qwen3-8b-lora-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v6blindtoolchoice-heldout200 \
  --model-name-or-path /data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218 \
  --adapter-path /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice \
  --limit 200 \
  --batch-size 2 \
  --max-new-tokens 160 \
  --device cuda \
  --local-files-only \
  --disable-thinking \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v6blindtoolchoice-heldout200-gpu6
```

## Output Paths

Results:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v6blindtoolchoice-heldout200-gpu6
```

Predictions:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v6blindtoolchoice-heldout200-gpu6/qwen3-8b-lora-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v6blindtoolchoice-heldout200_predictions.jsonl
```

Summary:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v6blindtoolchoice-heldout200-gpu6/qwen3-8b-lora-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v6blindtoolchoice-heldout200_summary.csv
```

Log:

```text
/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v6blindtoolchoice-heldout200-gpu6.log
```

## Raw Summary

```csv
model_label,split,total,exact_match_rate,canonical_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,observation_faithfulness_rate,observation_coverage_avg,trajectory_valid_rate,hallucination_rate,correct_rate,canonical_alias_match_rate,missing_final_rate,trajectory_format_error_rate,tool_coverage_gap_rate,supported_but_wrong_answer_rate,unsupported_wrong_answer_rate
qwen3-8b-lora-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v6blindtoolchoice-heldout200,overall,200,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.985,0.9925,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
qwen3-8b-lora-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v6blindtoolchoice-heldout200,multi_hop_qa,67,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.9851,0.9925,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
qwen3-8b-lora-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v6blindtoolchoice-heldout200,noisy_context_retrieval_qa,66,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.9848,0.9924,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
qwen3-8b-lora-sft-2p4k-mixed-v3-v4-v5blind-v6trained-v6blindtoolchoice-heldout200,tool_use_qa,67,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.9851,0.9925,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
```

## Metrics

Overall:

```text
total 200
exact_match_rate 1.0
canonical_match_rate 1.0
answer_f1_avg 1.0
gold_answer_mention_rate 1.0
final_answer_rate 1.0
tool_call_success_rate 1.0
tool_call_coverage_avg 1.0
observation_faithfulness_rate 0.985
observation_coverage_avg 0.9925
trajectory_valid_rate 1.0
hallucination_rate 0.0
correct_rate 1.0
```

By task type:

```text
multi_hop_qa: total 67, observation_faithfulness 0.9851, observation_coverage 0.9925, all answer/tool/correct metrics 1.0
noisy_context_retrieval_qa: total 66, observation_faithfulness 0.9848, observation_coverage 0.9924, all answer/tool/correct metrics 1.0
tool_use_qa: total 67, observation_faithfulness 0.9851, observation_coverage 0.9925, all answer/tool/correct metrics 1.0
```

## Error Audit

Audit result:

```text
total 200
observation_faithfulness_failed 3
failed_by_task_type {'multi_hop_qa': 1, 'tool_use_qa': 1, 'noisy_context_retrieval_qa': 1}
faithfulness_rate 0.985
coverage_avg 0.9925
```

Remaining failures:

```text
wikidata-yukihiro-matsumoto-multi-hop-118: expected ['Osaka', 'Japan'], observed ['Tokyo', 'Japan']
wikidata-yukihiro-matsumoto-tool-119: expected ['Osaka', 'Japan'], observed ['Tokyo', 'Japan']
wikidata-yukihiro-matsumoto-noisy-120: expected ['Osaka', 'Japan'], observed ['Tokyo', 'Japan']
```

All three failures are the same true intermediate evidence error across the three task formats. The final country remains correct because both `Osaka` and `Tokyo` resolve to Japan.

Compared with the previous 2k mixed adapter, the following v6 failure patterns disappeared:

```text
Braunschweig -> Brunswick
New York City -> New York
```

## Comparison

```text
2k mixed v3/v4/v5blind on v6:
  observation_faithfulness_rate 0.945
  observation_coverage_avg 0.9725
  observation failures 11/200

2.4k mixed v3/v4/v5blind/v6 on v6:
  observation_faithfulness_rate 0.985
  observation_coverage_avg 0.9925
  observation failures 3/200
```

The absolute observation-faithfulness gain is `+0.040`, and the failure count drops from 11 to 3.

## Analysis

Adding 400 v6 blind tool-choice training examples improved the exact intermediate-evidence contract on the harder v6 heldout while preserving all final-answer, canonical-answer, tool-call, and trajectory metrics at 1.0.

This supports the current data-factory loop: harder verifier-designed heldouts can reveal a weakness, and targeted synthetic data can reduce that weakness in the next SFT run.

The remaining failure is no longer an alias-normalization issue but a specific memorized or substituted birthplace fact for Yukihiro Matsumoto. This suggests the next improvement should either add entity-specific hard negatives or diversify beyond the current birthplace-to-country path family.

## Next Steps

1. Run v4 and v5 blind-hard regression evaluations for this adapter.
2. If v4/v5 stay saturated, update the README comparison table.
3. Consider a v7 relation-diverse heldout to avoid overfitting the P19/P17 reasoning family.
