# Canonical-v6 Blind Tool-choice Hard Heldout

## Goal

Create a harder heldout split after the mixed v3/v4/v5blind SFT reached perfect scores on both v4 and v5 blind-hard heldouts.

The new profile removes the largest v5 prompt leakage:

- no `Available lookup observations`
- no `P19` / `P17` property ID hints
- no `wikidata_lookup[entity, ...]` schema scaffold in the user prompt
- no `->` lookup result leakage
- no fixed "Use ReAct steps with ..." instruction

The model must infer the relevant lookup intents from natural-language task text and distractor intent options.

## Local Code Change

Added data version:

```text
canonical-v6-blind-tool-choice-hard
```

Files changed:

```text
openseeker_factory/pipeline.py
openseeker_factory/cli.py
tests/test_pipeline.py
tests/test_cli.py
runs/launch_eval_mixed_v3_v4_v5blind_v6blindtoolchoice_gpu7.sh
```

Local commit:

```text
b7f8323 Add harder blind tool choice heldout
```

GitHub push was attempted twice but failed due network errors:

```text
Recv failure: Connection was reset
Failed to connect to github.com port 443
```

## Local Verification

TDD red state:

```text
python -m pytest tests/test_pipeline.py::test_factory_can_generate_canonical_v6_blind_tool_choice_hard_heldout_sample tests/test_cli.py::test_cli_generate_supports_canonical_v6_blind_tool_choice_hard_data_version -q
FF
```

Expected failure:

```text
data_version must be one of ['canonical-v3', 'canonical-v4', 'canonical-v4-hard', 'canonical-v5-blind-hard']
invalid choice: 'canonical-v6-blind-tool-choice-hard'
```

After implementation:

```text
python -m pytest tests/test_pipeline.py::test_factory_can_generate_canonical_v6_blind_tool_choice_hard_heldout_sample tests/test_cli.py::test_cli_generate_supports_canonical_v6_blind_tool_choice_hard_data_version -q
..                                                                       [100%]

python -m pytest tests/test_pipeline.py tests/test_cli.py -q
.........................................                                [100%]

python -m pytest -q
................................................................         [100%]
```

## Remote Sync

Remote repo still had pre-existing dirty changes and an old commit, so this used approved narrow file sync instead of `git pull --ff-only`.

Synced files:

```text
openseeker_factory/cli.py
openseeker_factory/pipeline.py
tests/test_cli.py
tests/test_pipeline.py
```

Remote validation:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m pytest \
  tests/test_pipeline.py::test_factory_can_generate_canonical_v6_blind_tool_choice_hard_heldout_sample \
  tests/test_cli.py::test_cli_generate_supports_canonical_v6_blind_tool_choice_hard_data_version -q
```

Result:

```text
..                                                                       [100%]
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
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v6-blind-tool-choice-hard \
  --strategy evol_instruct \
  --teacher-backend none \
  --data-version canonical-v6-blind-tool-choice-hard \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/heldout-eval-samples-200-canonical-v6-blind-tool-choice-hard.log
```

Result:

```text
OpenSeeker AgentDataFactory generation complete: accepted=200 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v6-blind-tool-choice-hard
```

## Heldout Audit

Artifacts:

```text
samples 200
sft_conversations 200
rl_rewards 200
trace 200
```

Distribution:

```text
task_type {'multi_hop_qa': 67, 'tool_use_qa': 67, 'noisy_context_retrieval_qa': 66}
data_version {'canonical-v6-blind-tool-choice-hard': 200}
profile {'v6-blind-tool-choice-hard': 200}
conditioning {'blind_tool_selection': 200}
lookup_block_flag {False: 200}
difficulty {'hard': 200}
```

Leakage checks:

```text
contains_available_lookup_block 0
contains_arrow 0
contains_P19 0
contains_P17 0
contains_wikidata_lookup_entity 0
contains_use_react_steps_with 0
contains_tool_choice_challenge 200
contains_candidate_lookup_intents 200
contains_noisy_context 200
duplicate_questions 0
verifier_passed 200
```

Generation summary:

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,evidence_faithfulness_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,question_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
200,200,0,1.0,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,0,0,
```

Example prompt:

```text
Answer by chaining facts: which country is tied to the capital or location of Ada Lovelace's birthplace?

Tool choice challenge:
- Write a concise ReAct trace with the lookup tool when needed.
- Decide which lookup intents are relevant; some listed intents are distractors.
- Do not use nationality, citizenship, residence, award, or workplace clues as the final country.
- The final answer must be the country supported by the birthplace location chain.

Candidate lookup intents:
- birth location of the named person
- current country or sovereign state containing a place
- citizenship or nationality of the named person
- main workplace, residence, or career country
- field of work or award country

Alias trap: England, UK and United States may look relevant but are not sufficient.
Noisy context:
- Ada Lovelace is associated with early computing.
- Early computing is not sufficient by itself to identify Ada Lovelace's birthplace country.
```

## Evaluation Status

Prepared launcher:

```text
/data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_mixed_v3_v4_v5blind_v6blindtoolchoice_gpu7.sh
runs/launch_eval_mixed_v3_v4_v5blind_v6blindtoolchoice_gpu7.sh
```

Planned command:

```bash
tmux new-session -d -s openseeker-20260613-eval-mixed-v6blindtoolchoice-gpu7 \
  "bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_mixed_v3_v4_v5blind_v6blindtoolchoice_gpu7.sh"
```

Evaluation was not launched yet because GPU7 was busy with another active process:

```text
7, 7310 MiB, 32607 MiB, 81 %
GPU7 process: /home/user/anaconda3/bin/python, about 7286 MiB
```

The user's previous approval to break the `4000 MiB` threshold applied to the mixed 4-GPU SFT run. It was not treated as blanket approval to launch this later GPU7 evaluation on top of another active job.

## Analysis

The v6 heldout closes the obvious v5 leakage channel. v5 still told the model exactly which Wikidata properties to use; v6 only gives natural-language candidate intents and distractors. This makes it a better next diagnostic for whether the mixed adapter learned the task semantics or mostly learned the explicit P19/P17 prompt pattern.

The deterministic generator and verifier still use the same gold tool plan internally, so v6 is harder as a prompt/evaluation condition but not yet a fundamentally new graph-reasoning benchmark. If the mixed adapter also saturates v6, the next split should vary relation type, tool schema, or require selecting among multiple entities in the prompt.

## Next Steps

1. Launch the prepared v6 evaluation when GPU7 is idle, or after explicit user approval to share the busy GPU.
2. Record v6 evaluation metrics locally under `docs/experiments`.
3. If v6 also saturates, implement a v7 relation-diverse split with additional properties and a larger tool-choice space.
