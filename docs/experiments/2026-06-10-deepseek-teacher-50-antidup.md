# DeepSeek Teacher 50 Anti-Dup

## Metadata

- Experiment name: deepseek-teacher-50-antidup-20260610
- Date: 2026-06-10
- Goal: Validate the duplicate-question rewrite path with a 50-sample DeepSeek-backed teacher generation.
- Status: success
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Branch: `main`
- Commit: `7b64c03`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- Number of GPUs: 0
- tmux session: `openseeker-20260610-deepseek-teacher-50-antidup`
- Model: `deepseek-v4-pro`
- Base URL: `https://api.deepseek.com`

## Commands

The API key was injected once through a FIFO read by the tmux child process. It was not written to repo files, experiment records, logs, or the launch command.

```bash
tmux new-session -d -s openseeker-20260610-deepseek-teacher-50-antidup \
  "bash -lc 'read -r DEEPSEEK_API_KEY < /data/wzl/OpenSeeker-AgentDataFactory/runs/deepseek-teacher-50-antidup-20260610.key.fifo; export DEEPSEEK_API_KEY; cd /data/wzl/OpenSeeker-AgentDataFactory/repo && source /home/user/anaconda3/etc/profile.d/conda.sh && conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate --count 50 --seed-file data/seeds/wikidata_seed_sample.jsonl --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-50-antidup-20260610 --teacher-backend openai-compatible --teacher-base-url https://api.deepseek.com --teacher-model deepseek-v4-pro --teacher-api-key-env DEEPSEEK_API_KEY --teacher-timeout-s 60 2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-50-antidup-20260610.log'"
```

## Paths

- Log path: `/data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-50-antidup-20260610.log`
- Results path: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-50-antidup-20260610`
- Samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-50-antidup-20260610/samples.jsonl`
- SFT export: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-50-antidup-20260610/sft_conversations.jsonl`
- RL reward export: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-50-antidup-20260610/rl_rewards.jsonl`
- Trace path: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-50-antidup-20260610/trace.jsonl`
- Checkpoint path: not applicable
- Run path: not applicable

## Raw Result Summary

```text
OpenSeeker AgentDataFactory generation complete: accepted=50 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-50-antidup-20260610
```

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
50,50,0,1.0,1.0,1.0,1.0,1.0,50,50,0,0.0,1,2,
```

Output files:

```text
rl_rewards.jsonl 50 lines
samples.jsonl 50 lines
sft_conversations.jsonl 50 lines
trace.jsonl 50 lines
```

Trace audit:

```text
rows 50
accepted 50
rejected 0
teacher_backend openai-compatible 50
teacher_errors 0
difficulty medium 31, easy 17, hard 2
accepted_task_type tool_use_qa 17, multi_hop_qa 17, noisy_context_retrieval_qa 16
duplicate_question_rewritten 19
teacher_trajectory_repaired 1
teacher_difficulty_normalized 2
```

Example accepted samples:

```text
wikidata-ada-1 score=1.0 difficulty=easy question=Ada Lovelace was born in a city that is the capital of a country. What is that country?
wikidata-curie-2 score=1.0 difficulty=medium question=What is the current country of Marie Curie's birthplace?
wikidata-turing-3 score=1.0 difficulty=medium question=Given that Alan Turing worked at Bletchley Park and the Turing Award is named after him, in which country was he born?
```

Example duplicate rewrites:

```text
wikidata-curie-14 original=What is the current country of Marie Curie's birthplace?
rewritten=What is the current country of Marie Curie's birthplace? Disambiguate this sample with seed wikidata-curie-14 and sample id wikidata-curie-14.

wikidata-turing-18 original=What country was Alan Turing born in?
rewritten=What country was Alan Turing born in? Disambiguate this sample with seed wikidata-turing-18 and sample id wikidata-turing-18.
```

## Comparison Against Previous Pilot

- Previous 30-sample run: 20 accepted, 10 rejected, dedup_rate 0.6667.
- Current 50-sample anti-dup run: 50 accepted, 0 rejected, dedup_rate 1.0.
- The improvement came from verifier-side duplicate rewrite, not from more seeds or GPU compute.
- The run converted 19 duplicate teacher questions into accepted disambiguated samples.

## Notes and Analysis

- This validates the anti-dup loop as a practical rejection-sampling improvement for the current small seed set.
- DeepSeek API reliability was good in this run: 50/50 calls succeeded, with no fallback samples.
- The verifier still caught useful teacher quality issues: one invalid/insufficient trajectory was repaired and two non-standard difficulty labels were normalized.
- The current rewrite text is deterministic and audit-friendly, but not semantically elegant enough for final large-scale data. It should be upgraded to a teacher rewrite or template bank before producing resume-scale 20k+ data.
- No GPU was used. This was an API-only generation run.

## Next Step Thoughts

- Add a cleaner duplicate rewrite strategy that asks the teacher for a meaning-preserving, non-duplicate question or uses richer template banks.
- Add duplicate cluster metadata to `trace_summary` so duplicate analysis is visible without ad hoc JSONL parsing.
- Run a 100-sample pilot after improving rewrite quality, and compare accepted rate, rewrite rate, repair rate, and difficulty normalization rate.
- Use the 50-sample result in the README as the first concrete ablation: verifier rejection only vs verifier plus anti-dup rewrite.
