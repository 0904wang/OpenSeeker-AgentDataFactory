# Qwen3-8B Canonical-v4 Heldout200 Evaluation

## Goal

Evaluate whether the canonical-v4 evidence-conditioned SFT data improves tool-call and observation faithfulness on a v4-style heldout set. The comparison uses the same 200 canonical-v4 heldout samples for:

- Qwen3-8B LoRA SFT on canonical-v3 1k
- Qwen3-8B LoRA SFT on canonical-v4 1k

Canonical-v4 prompts include an explicit lookup observation block and instruct the model to copy those lookup values exactly in Observation lines.

## Remote Context

- Date: 2026-06-12
- Remote entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote workspace: `/data/wzl/OpenSeeker-AgentDataFactory`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Local launcher commit: `d23b499 Add canonical v4 heldout evaluation launchers`
- Remote sync mode: narrow launcher sync, because the remote experiment workspace had pre-existing dirty changes and was not safe for `git pull --ff-only`
- Remote repo HEAD observed during this run: `7b64c03` on `main`

## Inputs

- Heldout samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v4/samples.jsonl`
- Heldout SFT export: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v4/sft_conversations.jsonl`
- Heldout RL export: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v4/rl_rewards.jsonl`
- Heldout trace: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v4/trace.jsonl`
- Base model: `/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218`
- Canonical-v3 adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v3`
- Canonical-v4 adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v4`
- GPU: `CUDA_VISIBLE_DEVICES=7`

## Heldout Generation

Command:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 200 \
  --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_expanded.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v4 \
  --strategy evol_instruct \
  --teacher-backend none \
  --data-version canonical-v4 \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/heldout-eval-samples-200-canonical-v4.log
```

Audit result:

```text
samples_lines 200
sft_lines 200
rl_lines 200
trace_lines 200
task_type {'multi_hop_qa': 67, 'tool_use_qa': 67, 'noisy_context_retrieval_qa': 66}
data_version {'canonical-v4': 200}
observation_conditioning {'lookup_result_block': 200}
lookup_block_question_count 200
exact_copy_instruction_count 200
duplicate_questions 0
round_marker_count 0
quality_scores {1.0: 200}
verifier_passed 200
```

Generation summary:

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,evidence_faithfulness_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,question_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
200,200,0,1.0,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,0,0,
```

## Launch Commands

One failed local SSH wrapper attempt occurred before the v3 launch due to mismatched PowerShell/Bash quoting. It did not create a tmux session or start the evaluation script. The retry used the following explicit remote command and succeeded.

Canonical-v3 adapter on canonical-v4 heldout:

```bash
tmux new-session -d -s openseeker-20260612-eval-canonical-v3-v4heldout-gpu7 "bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_canonical_v3_v4heldout_gpu7.sh"
```

Canonical-v4 adapter on canonical-v4 heldout:

```bash
tmux new-session -d -s openseeker-20260612-eval-canonical-v4-v4heldout-gpu7 "bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_canonical_v4_v4heldout_gpu7.sh"
```

Launcher settings:

```text
samples: /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v4/samples.jsonl
limit: 200
batch_size: 2
max_new_tokens: 160
device: cuda
local_files_only: true
disable_thinking: true
```

## Outputs

Canonical-v3 adapter:

- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-canonical-v3-v4heldout200-gpu7.log`
- Results dir: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v3-v4heldout200-gpu7`
- Predictions: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v3-v4heldout200-gpu7/qwen3-8b-lora-sft-1k-canonical-v3-v4heldout200_predictions.jsonl`
- Summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v3-v4heldout200-gpu7/qwen3-8b-lora-sft-1k-canonical-v3-v4heldout200_summary.csv`

Canonical-v4 adapter:

- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-canonical-v4-v4heldout200-gpu7.log`
- Results dir: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v4-v4heldout200-gpu7`
- Predictions: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v4-v4heldout200-gpu7/qwen3-8b-lora-sft-1k-canonical-v4-v4heldout200_predictions.jsonl`
- Summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v4-v4heldout200-gpu7/qwen3-8b-lora-sft-1k-canonical-v4-v4heldout200_summary.csv`

Both prediction files contain 200 rows. Both tmux sessions exited normally after completion. GPU7 returned to idle memory usage after the runs.

## Metrics

Overall comparison:

| Model | Total | Exact | Canonical | F1 | Tool success | Observation faithfulness | Observation coverage | Trajectory valid | Hallucination | Correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| canonical-v3 SFT 1k | 200 | 1.000 | 1.000 | 1.000 | 0.970 | 0.970 | 0.985 | 1.000 | 0.000 | 0.970 |
| canonical-v4 SFT 1k | 200 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 |

Task-level comparison:

| Model | Split | Total | Exact | Tool success | Observation faithfulness | Observation coverage | Correct |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| canonical-v3 SFT 1k | multi_hop_qa | 67 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| canonical-v3 SFT 1k | noisy_context_retrieval_qa | 66 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| canonical-v3 SFT 1k | tool_use_qa | 67 | 1.000 | 0.9104 | 0.9104 | 0.9552 | 0.9104 |
| canonical-v4 SFT 1k | multi_hop_qa | 67 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| canonical-v4 SFT 1k | noisy_context_retrieval_qa | 66 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| canonical-v4 SFT 1k | tool_use_qa | 67 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

Error bucket check using top-level prediction fields:

```text
canonical-v3 predictions: {'correct': 194, 'tool_coverage_gap': 6}
canonical-v3 tool_call_success false: 6
canonical-v3 observation_faithfulness false: 6
canonical-v3 failures by task: {'tool_use_qa': 6}
canonical-v4 predictions: {'correct': 200}
canonical-v4 tool_call_success false: 0
canonical-v4 observation_faithfulness false: 0
```

## Raw Completion Excerpts

Canonical-v3:

```text
OpenSeeker model evaluation complete: model_label=qwen3-8b-lora-sft-1k-canonical-v3-v4heldout200 samples=200 predictions=/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v3-v4heldout200-gpu7/qwen3-8b-lora-sft-1k-canonical-v3-v4heldout200_predictions.jsonl summary=/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v3-v4heldout200-gpu7/qwen3-8b-lora-sft-1k-canonical-v3-v4heldout200_summary.csv
```

Canonical-v4:

```text
OpenSeeker model evaluation complete: model_label=qwen3-8b-lora-sft-1k-canonical-v4-v4heldout200 samples=200 predictions=/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v4-v4heldout200-gpu7/qwen3-8b-lora-sft-1k-canonical-v4-v4heldout200_predictions.jsonl summary=/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v4-v4heldout200-gpu7/qwen3-8b-lora-sft-1k-canonical-v4-v4heldout200_summary.csv
```

## Interpretation

Canonical-v4 fixes the remaining tool-use trajectory gap on the v4-conditioned heldout split. The v3 adapter already answers all heldout questions correctly when the prompt contains the lookup block, but it still misses complete tool/observation coverage on 6 of 67 tool-use cases. The v4 adapter reaches 100% on answer correctness, tool-call success, observation faithfulness, and trajectory validity across all three task types.

The result is strong evidence that the v4 data contract is useful for teaching the model to align Observation lines with provided lookup results. It also exposes that this heldout set may now be too easy for answer accuracy: exact and canonical answer rates are saturated for both adapters. The differentiating value is currently in verifier metrics, especially tool-call coverage and observation faithfulness.

## Risks and Notes

- The remote repo itself was still on an older commit during execution; the required launcher/code files were deployed by narrow sync. Future reproduction should either clean the remote repo state or use a fresh clone under the approved workspace.
- The heldout set uses the same seed source and synthetic pattern family as training data. It is useful for regression testing the v4 contract, but not enough as a final generalization claim.
- The evaluator logs repeated Transformers warnings about ignored generation flags. These did not stop execution or affect output writing, but the launchers can be simplified later to avoid noisy logs.
- A local prediction schema check showed metric fields are top-level fields, not nested under `metrics`; the record above uses the summary CSV and top-level prediction fields.

## Next Step

Use this as the positive regression result for canonical-v4, then make the next experiment harder before scaling training:

- create a harder heldout split with unseen templates, entity aliases, missing/noisy evidence, and distractor lookup values
- evaluate base Qwen3-8B, canonical-v3 SFT, and canonical-v4 SFT on the harder split
- if v4 still improves verifier metrics, scale generation from 1k to 5k or 10k and run one larger SFT
- keep resume claims centered on verifier-backed trajectory quality rather than answer EM alone, because answer accuracy is saturated on the current heldout
