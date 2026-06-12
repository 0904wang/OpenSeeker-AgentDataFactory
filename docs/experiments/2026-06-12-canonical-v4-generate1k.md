# Canonical-v4 Generate 1k

## Goal

Generate a 1k canonical-v4 evidence-conditioned SFT dataset on the remote server. Canonical-v4 adds explicit lookup observation blocks to the user prompt so later SFT can train the model to copy tool observations instead of using memorized or localized facts.

## Remote Context

- Date: 2026-06-12
- Remote entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote workspace: `/data/wzl/OpenSeeker-AgentDataFactory`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Code source: local commit `fb1d9c1 Add canonical v4 evidence conditioned data`, synced by narrow file sync because the remote experiment workspace had pre-existing dirty changes.
- Dry-run prerequisite: `docs/experiments/2026-06-12-canonical-v4-remote-dry-run.md`

## Inputs

- Seed file: `/data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_expanded.jsonl`
- Seed rows: 120
- Target generated samples: 1000
- Data version: `canonical-v4`
- Teacher backend: none
- GPU: not used

## Launch

- tmux session: `openseeker-20260612-canonical-v4-generate1k`
- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/canonical-v4-generate1k.log`
- Results: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v4-generate1k`

Command:

```bash
tmux new-session -d -s openseeker-20260612-canonical-v4-generate1k \
  "bash -lc 'cd /data/wzl/OpenSeeker-AgentDataFactory/repo && source /home/user/anaconda3/etc/profile.d/conda.sh && conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate --count 1000 --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_expanded.jsonl --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v4-generate1k --data-version canonical-v4 --batch-size 100 --resume 2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/canonical-v4-generate1k.log'"
```

## Outputs

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v4-generate1k/raw_generations.jsonl
/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v4-generate1k/rl_rewards.jsonl
/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v4-generate1k/samples.jsonl
/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v4-generate1k/sft_conversations.jsonl
/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v4-generate1k/summary.csv
/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v4-generate1k/trace.jsonl
```

Directory size:

```text
7.6M /data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v4-generate1k
```

## Summary

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,evidence_faithfulness_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,question_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
1000,1000,0,1.0,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,0,0,
```

## Audit

```text
samples 1000
sft_lines 1000
rl_lines 1000
trace_lines 1000
task_type {'multi_hop_qa': 334, 'tool_use_qa': 333, 'noisy_context_retrieval_qa': 333}
data_version {'canonical-v4': 1000}
observation_conditioning {'lookup_result_block': 1000}
observation_grounding {'provided_lookup_results': 1000}
lookup_block_question_count 1000
exact_copy_instruction_count 1000
sft_copy_prompt_count 1000
quality_scores {1.0: 1000}
verifier_passed 1000
observation_faithful_checks 1000
duplicate_questions 0
round_marker 0
conflict_types {('country_alias', 'birthplace_alias', 'noisy_context'): 1000}
```

First question:

```text
Answer by chaining facts: which country is tied to the capital or location of Ada Lovelace's birthplace?

Available lookup observations:
- wikidata_lookup[Ada Lovelace, P19] -> London
- wikidata_lookup[London, P17] -> United Kingdom

Use these lookup observations exactly when writing Observation lines.
```

First SFT system prompt:

```text
You are a ReAct agent that must cite tool observations. Actions must use the provided lookup schema, and Observation lines must copy the provided lookup observation values exactly instead of using memorized or localized facts.
```

## Interpretation

The generated 1k v4 dataset satisfies the intended data contract: every sample is lookup-block conditioned, every SFT row carries the stronger observation-copying instruction, and verifier quality is 100%. The dataset is ready for a controlled Qwen3-8B LoRA SFT run.

This data is not meant to prove more knowledge diversity than v3; it targets a different failure mode. The previous canonical-v3 heldout evaluation showed strong tool-call success but only 71.5% observation faithfulness. V4 directly trains the model to condition `Observation:` lines on provided lookup results, so the next comparison should measure whether observation faithfulness improves under an aligned v4 heldout or v4-style evaluation prompt.

## Next Step

Register `sft_conversations.jsonl` as `openseeker_sft_1k_canonical_v4` in LLaMAFactory and run a Qwen3-8B LoRA SFT with the same 4-GPU setup as v2/v3:

- dataset: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v4-generate1k/sft_conversations.jsonl`
- checkpoint target: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v4`
- compare after training against v3 under a v4-conditioned heldout prompt.
