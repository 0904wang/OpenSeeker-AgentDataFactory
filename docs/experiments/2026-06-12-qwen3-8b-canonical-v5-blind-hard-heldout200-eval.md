# Qwen3-8B Canonical-v5 Blind-hard Heldout200 Evaluation

## Goal

Evaluate a blind hard heldout split that does not expose `Available lookup observations` in the user prompt. This split was created after `canonical-v4-hard` saturated because the prompt directly exposed the lookup values.

## Remote Context

- Date: 2026-06-12
- Remote entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote workspace: `/data/wzl/OpenSeeker-AgentDataFactory`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Local code commit: `c3d5b97 Add canonical v5 blind hard heldout`
- Remote sync mode: narrow file sync, because the remote repo had pre-existing dirty changes and was not safe for `git pull --ff-only`

## Code Change

Added a new evaluation-only data version:

```text
canonical-v5-blind-hard
```

Key behavior:

- no `Available lookup observations` block in the user prompt
- no `->` lookup result leakage in the user prompt
- keeps gold `tool_calls`, trajectory, answer, and verifier schema unchanged
- includes noisy context, alias traps, and strict P19/P17 tool schema instructions
- marks samples with `difficulty=hard`
- sets `source.heldout_profile=v5-blind-hard`
- sets `source.observation_conditioning=blind_tool_generation`
- sets `source.lookup_observation_block=false`

Local verification:

```text
python -m pytest tests/test_pipeline.py::test_factory_can_generate_canonical_v5_blind_hard_heldout_sample tests/test_cli.py::test_cli_generate_supports_canonical_v5_blind_hard_data_version -q
..                                                                       [100%]

python -m pytest -q
.............................................................            [100%]
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
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v5-blind-hard \
  --strategy evol_instruct \
  --teacher-backend none \
  --data-version canonical-v5-blind-hard \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/heldout-eval-samples-200-canonical-v5-blind-hard.log
```

Audit:

```text
samples 200
sft_conversations 200
rl_rewards 200
trace 200
task_type {'multi_hop_qa': 67, 'tool_use_qa': 67, 'noisy_context_retrieval_qa': 66}
data_version {'canonical-v5-blind-hard': 200}
profile {'v5-blind-hard': 200}
conditioning {'blind_tool_generation': 200}
lookup_block_flag {False: 200}
difficulty {'hard': 200}
contains_lookup_block 0
contains_arrow 0
contains_schema_instruction 200
contains_alias_trap 200
contains_noisy_context 200
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
tmux new-session -d -s openseeker-20260612-eval-base-v5blindhard-gpu7 "bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_base_qwen3_8b_v5blindhard_gpu7.sh"
```

Canonical-v3 SFT adapter:

```bash
tmux new-session -d -s openseeker-20260612-eval-canonical-v3-v5blindhard-gpu7 "bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_canonical_v3_v5blindhard_gpu7.sh"
```

Canonical-v4 SFT adapter:

```bash
tmux new-session -d -s openseeker-20260612-eval-canonical-v4-v5blindhard-gpu7 "bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_canonical_v4_v5blindhard_gpu7.sh"
```

Common settings:

```text
samples: /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v5-blind-hard/samples.jsonl
limit: 200
batch_size: 2
max_new_tokens: 160
device: cuda
local_files_only: true
disable_thinking: true
```

## Metrics

Overall comparison:

| Model | Exact | Canonical | F1 | Tool success | Observation faithfulness | Observation coverage | Hallucination | Correct |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen3-8B base | 0.835 | 0.975 | 0.897 | 0.935 | 0.890 | 0.925 | 0.020 | 0.795 |
| canonical-v3 SFT 1k | 0.930 | 1.000 | 0.930 | 1.000 | 0.930 | 0.965 | 0.000 | 0.930 |
| canonical-v4 SFT 1k | 0.770 | 0.880 | 0.830 | 0.815 | 0.760 | 0.8175 | 0.120 | 0.680 |

Task-level comparison:

| Model | Split | Exact | Canonical | Tool success | Observation faithfulness | Correct |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Qwen3-8B base | multi_hop_qa | 0.8507 | 0.9851 | 0.9701 | 0.9254 | 0.8209 |
| Qwen3-8B base | noisy_context_retrieval_qa | 0.8182 | 0.9697 | 0.9091 | 0.8636 | 0.7727 |
| Qwen3-8B base | tool_use_qa | 0.8358 | 0.9701 | 0.9254 | 0.8806 | 0.7910 |
| canonical-v3 SFT 1k | multi_hop_qa | 0.9403 | 1.000 | 1.000 | 0.9403 | 0.9403 |
| canonical-v3 SFT 1k | noisy_context_retrieval_qa | 0.9242 | 1.000 | 1.000 | 0.9242 | 0.9242 |
| canonical-v3 SFT 1k | tool_use_qa | 0.9254 | 1.000 | 1.000 | 0.9254 | 0.9254 |
| canonical-v4 SFT 1k | multi_hop_qa | 0.7313 | 0.8358 | 0.8060 | 0.7612 | 0.6716 |
| canonical-v4 SFT 1k | noisy_context_retrieval_qa | 0.8030 | 0.9091 | 0.8030 | 0.7424 | 0.6667 |
| canonical-v4 SFT 1k | tool_use_qa | 0.7761 | 0.8955 | 0.8358 | 0.7761 | 0.7015 |

Prediction error buckets:

```text
base: {'correct': 159, 'canonical_alias_match': 26, 'tool_coverage_gap': 10, 'missing_final': 1, 'unsupported_wrong_answer': 4}
canonical-v3: {'correct': 186, 'canonical_alias_match': 14}
canonical-v4: {'correct': 136, 'canonical_alias_match': 21, 'tool_coverage_gap': 19, 'unsupported_wrong_answer': 24}
```

Failure distribution:

```text
base tool_call_success false by task: {'noisy_context_retrieval_qa': 6, 'tool_use_qa': 5, 'multi_hop_qa': 2}
base observation_faithfulness false by task: {'multi_hop_qa': 5, 'noisy_context_retrieval_qa': 9, 'tool_use_qa': 8}
base hallucination by task: {'tool_use_qa': 2, 'noisy_context_retrieval_qa': 1, 'multi_hop_qa': 1}

canonical-v3 tool_call_success false by task: {}
canonical-v3 observation_faithfulness false by task: {'multi_hop_qa': 4, 'tool_use_qa': 5, 'noisy_context_retrieval_qa': 5}
canonical-v3 hallucination by task: {}

canonical-v4 tool_call_success false by task: {'multi_hop_qa': 13, 'noisy_context_retrieval_qa': 13, 'tool_use_qa': 11}
canonical-v4 observation_faithfulness false by task: {'noisy_context_retrieval_qa': 17, 'multi_hop_qa': 16, 'tool_use_qa': 15}
canonical-v4 hallucination by task: {'multi_hop_qa': 11, 'tool_use_qa': 7, 'noisy_context_retrieval_qa': 6}
```

## Interpretation

This is the first heldout split in this project that meaningfully separates the base model from SFT adapters. Removing the direct lookup observation block drops base Qwen3-8B to `0.795` correct and `0.890` observation faithfulness.

Canonical-v3 SFT is the strongest model on blind-hard. It reaches `1.000` canonical match and `1.000` tool-call success, with `0.930` correct and no hallucination proxy cases. This suggests the canonical-v3 trajectory training teaches a more general two-step P19/P17 pattern.

Canonical-v4 SFT is worse than both base and canonical-v3 on blind-hard. The likely reason is contract mismatch: canonical-v4 training strongly conditions the model to copy an explicit lookup observation block, so when that block is removed it loses robustness and produces more tool coverage gaps and hallucinated answers.

This is a useful negative result. It shows that canonical-v4 is excellent for copy-conditioned verifier contracts, but the next training dataset should not be pure v4. A better training mix should combine:

- v3-style blind tool generation
- v4-style observation-conditioned copy tasks
- v5 blind-hard alias/noisy tasks

## Resume-safe Takeaway

The best project claim is not "v4 is always better." The defensible claim is:

- built multiple verifier-backed heldout profiles after answer accuracy saturated
- identified prompt leakage in observation-conditioned evaluation
- created a blind-hard benchmark that exposed generalization differences
- found that pure observation-copy SFT overfits the exposed-observation contract
- used the result to design a mixed-data training plan targeting both tool generation and observation faithfulness

## Next Step

Run one mixed-data SFT, not a larger pure-v4 SFT:

- 40% canonical-v3 / blind trajectory data
- 40% canonical-v4 observation-conditioned copy data
- 20% canonical-v5 blind-hard data

Train Qwen3-8B LoRA for one epoch on 2k-5k mixed samples, then evaluate on:

- canonical-v4 heldout for copy-conditioned faithfulness
- canonical-v5 blind-hard heldout for blind tool generation

The target is to retain v4's `1.000` copy-conditioned score while recovering v3-like blind-hard robustness.
