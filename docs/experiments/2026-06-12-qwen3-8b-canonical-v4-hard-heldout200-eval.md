# Qwen3-8B Canonical-v4-hard Heldout200 Evaluation

## Goal

Create and evaluate a harder canonical-v4 heldout split with alias traps and distractor lookup observations. The purpose was to test whether canonical-v4 SFT remains stronger than canonical-v3 SFT when the prompt contains misleading but controlled distractors.

## Remote Context

- Date: 2026-06-12
- Remote entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote workspace: `/data/wzl/OpenSeeker-AgentDataFactory`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Local code commit: `591536a Add canonical v4 hard heldout profile`
- Remote sync mode: narrow file sync, because the remote repo had pre-existing dirty changes and was not safe for `git pull --ff-only`

## Code Change

Added a new reproducible data version:

```text
canonical-v4-hard
```

Key behavior:

- keeps the existing JSONL schema and evaluator contract
- preserves the correct `Available lookup observations` block
- adds hard constraints with alias traps
- adds a distractor P27 lookup observation
- marks every sample as `difficulty=hard`
- sets `source.heldout_profile=v4-hard`
- sets `source.difficulty_factors=["alias_trap", "distractor_lookup", "noisy_context", "strict_observation_copy"]`

Local verification:

```text
python -m pytest tests/test_pipeline.py::test_factory_can_generate_canonical_v4_hard_heldout_sample tests/test_cli.py::test_cli_generate_supports_canonical_v4_hard_data_version -q
..                                                                       [100%]

python -m pytest -q
...........................................................              [100%]
```

## Heldout Generation

Command:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 200 \
  --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_expanded.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v4-hard \
  --strategy evol_instruct \
  --teacher-backend none \
  --data-version canonical-v4-hard \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/heldout-eval-samples-200-canonical-v4-hard.log
```

Audit:

```text
samples 200
sft_conversations 200
rl_rewards 200
trace 200
task_type {'multi_hop_qa': 67, 'tool_use_qa': 67, 'noisy_context_retrieval_qa': 66}
data_version {'canonical-v4-hard': 200}
heldout_profile {'v4-hard': 200}
difficulty {'hard': 200}
lookup_block 200
distractor_block 200
do_not_copy 200
p27_distractor 200
duplicate_questions 0
verifier_passed 200
```

Generation summary:

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,evidence_faithfulness_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,question_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
200,200,0,1.0,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,0,0,
```

## Evaluation Commands

All evaluations used GPU7 sequentially. GPU7 was idle before each launch.

Base Qwen3-8B:

```bash
tmux new-session -d -s openseeker-20260612-eval-base-v4hard-gpu7 "bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_base_qwen3_8b_v4hard_gpu7.sh"
```

Canonical-v3 SFT adapter:

```bash
tmux new-session -d -s openseeker-20260612-eval-canonical-v3-v4hard-gpu7 "bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_canonical_v3_v4hard_gpu7.sh"
```

Canonical-v4 SFT adapter:

```bash
tmux new-session -d -s openseeker-20260612-eval-canonical-v4-v4hard-gpu7 "bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_canonical_v4_v4hard_gpu7.sh"
```

Common settings:

```text
samples: /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v4-hard/samples.jsonl
limit: 200
batch_size: 2
max_new_tokens: 160
device: cuda
local_files_only: true
disable_thinking: true
```

## Outputs

Base Qwen3-8B:

- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-base-v4hard-heldout200-gpu7.log`
- Results: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-base-v4hard-heldout200-gpu7`
- Summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-base-v4hard-heldout200-gpu7/qwen3-8b-base-v4hard-heldout200_summary.csv`

Canonical-v3 SFT:

- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-canonical-v3-v4hard-heldout200-gpu7.log`
- Results: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v3-v4hard-heldout200-gpu7`
- Summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v3-v4hard-heldout200-gpu7/qwen3-8b-lora-sft-1k-canonical-v3-v4hard-heldout200_summary.csv`

Canonical-v4 SFT:

- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-canonical-v4-v4hard-heldout200-gpu7.log`
- Results: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v4-v4hard-heldout200-gpu7`
- Summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v4-v4hard-heldout200-gpu7/qwen3-8b-lora-sft-1k-canonical-v4-v4hard-heldout200_summary.csv`

All prediction files contain 200 rows. All tmux sessions exited normally. GPU7 returned to idle memory after completion.

## Metrics

Overall:

| Model | Total | Exact | Canonical | Tool success | Observation faithfulness | Observation coverage | Trajectory valid | Correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen3-8B base | 200 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| canonical-v3 SFT 1k | 200 | 1.000 | 1.000 | 0.975 | 0.975 | 0.9875 | 1.000 | 0.975 |
| canonical-v4 SFT 1k | 200 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

Task-level verifier metrics:

| Model | Split | Total | Tool success | Observation faithfulness | Observation coverage | Correct |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Qwen3-8B base | multi_hop_qa | 67 | 1.000 | 1.000 | 1.000 | 1.000 |
| Qwen3-8B base | noisy_context_retrieval_qa | 66 | 1.000 | 1.000 | 1.000 | 1.000 |
| Qwen3-8B base | tool_use_qa | 67 | 1.000 | 1.000 | 1.000 | 1.000 |
| canonical-v3 SFT 1k | multi_hop_qa | 67 | 0.9851 | 0.9851 | 0.9925 | 0.9851 |
| canonical-v3 SFT 1k | noisy_context_retrieval_qa | 66 | 1.000 | 1.000 | 1.000 | 1.000 |
| canonical-v3 SFT 1k | tool_use_qa | 67 | 0.9403 | 0.9403 | 0.9701 | 0.9403 |
| canonical-v4 SFT 1k | multi_hop_qa | 67 | 1.000 | 1.000 | 1.000 | 1.000 |
| canonical-v4 SFT 1k | noisy_context_retrieval_qa | 66 | 1.000 | 1.000 | 1.000 | 1.000 |
| canonical-v4 SFT 1k | tool_use_qa | 67 | 1.000 | 1.000 | 1.000 | 1.000 |

Prediction error buckets:

```text
base: {'correct': 200}
canonical-v3: {'correct': 195, 'tool_coverage_gap': 5}
canonical-v4: {'correct': 200}
```

Canonical-v3 failure distribution:

```text
tool_call_success false by task: {'tool_use_qa': 4, 'multi_hop_qa': 1}
observation_faithfulness false by task: {'tool_use_qa': 4, 'multi_hop_qa': 1}
example failing ids: ['wikidata-ada-lovelace-tool-2', 'wikidata-emmy-noether-tool-44', 'wikidata-abdus-salam-tool-68']
```

## Interpretation

The positive result is that canonical-v4 SFT still removes the trajectory gap seen in canonical-v3. On this harder split, canonical-v3 has 5 verifier failures, mostly in `tool_use_qa`, while canonical-v4 has none.

The more important negative result is that `canonical-v4-hard` is still too easy as a final generalization benchmark. Base Qwen3-8B also reaches 100% across answer and verifier metrics because the prompt exposes the exact lookup observations and explicitly tells the model what to copy. This makes the split useful as a contract regression test, but not enough for claiming that SFT improves the base model.

For resume purposes, this experiment is still valuable because it documents engineering rigor: after answer metrics saturated, we created a stricter heldout, found it could distinguish v3 from v4 on trajectory quality, and also discovered that exposing exact observations can make the base model saturate.

## Next Step

Build a `canonical-v5-blind-hard` or `v4-hard-blind` split that does not directly expose the answer in the user prompt.

Recommended design:

- keep tools and gold `tool_calls` in the sample schema
- remove `Available lookup observations` from the user prompt for evaluation samples
- keep noisy evidence and alias traps in the prompt
- require the model to generate P19/P17 calls and infer observations from its tool-use training pattern
- optionally score with a simulated tool executor that fills observations after model actions

This next split should evaluate base, v3, and v4 again. The expected useful signal is lower base trajectory faithfulness and a clearer SFT improvement.
