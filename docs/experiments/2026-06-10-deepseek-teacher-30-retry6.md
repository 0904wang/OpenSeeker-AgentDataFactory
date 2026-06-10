# DeepSeek Teacher 30 Retry6

## Metadata

- Experiment name: deepseek-teacher-30-retry6-20260610
- Date: 2026-06-10
- Goal: Run a 30-sample DeepSeek-backed teacher generation after adding per-sample progress logging and teacher fallback metrics.
- Status: success with verifier rejections
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Branch: `main`
- Commit: `e5e34f8`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- Number of GPUs: 0
- tmux session: `openseeker-20260610-deepseek-teacher-30-retry6`
- Model: `deepseek-v4-pro`
- Base URL: `https://api.deepseek.com`

## Commands

The API key was injected once through a FIFO read by the tmux child process. It was not written to repo files, experiment records, logs, or the launch command.

```bash
tmux new-session -d -s openseeker-20260610-deepseek-teacher-30-retry6 \
  "bash -lc 'read -r DEEPSEEK_API_KEY < /data/wzl/OpenSeeker-AgentDataFactory/runs/deepseek-teacher-30-retry6-20260610.key.fifo; export DEEPSEEK_API_KEY; cd /data/wzl/OpenSeeker-AgentDataFactory/repo && source /home/user/anaconda3/etc/profile.d/conda.sh && conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate --count 30 --seed-file data/seeds/wikidata_seed_sample.jsonl --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-30-retry6-20260610 --teacher-backend openai-compatible --teacher-base-url https://api.deepseek.com --teacher-model deepseek-v4-pro --teacher-api-key-env DEEPSEEK_API_KEY --teacher-timeout-s 60 2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-30-retry6-20260610.log'"
```

## Paths

- Log path: `/data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-30-retry6-20260610.log`
- Results path: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-30-retry6-20260610`
- Samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-30-retry6-20260610/samples.jsonl`
- SFT export: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-30-retry6-20260610/sft_conversations.jsonl`
- RL reward export: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-30-retry6-20260610/rl_rewards.jsonl`
- Trace path: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-30-retry6-20260610/trace.jsonl`
- Checkpoint path: not applicable
- Run path: not applicable

## Raw Result Summary

```text
OpenSeeker AgentDataFactory generation complete: accepted=20 rejected=10 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-30-retry6-20260610
```

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
30,20,10,0.6667,1.0,1.0,1.0,1.0,30,30,0,0.0,0,0,
```

Output files:

```text
rl_rewards.jsonl 20 lines
samples.jsonl 20 lines
sft_conversations.jsonl 20 lines
trace.jsonl 30 lines
```

Trace audit:

```text
rows 30
accepted 20
rejected 10
teacher_backend openai-compatible 30
teacher_errors 0
difficulty medium 21, easy 7, hard 2
accepted_task_type noisy_context_retrieval_qa 8, multi_hop_qa 8, tool_use_qa 4
rejected_task_type tool_use_qa 6, noisy_context_retrieval_qa 2, multi_hop_qa 2
reasons not_duplicate 10
```

Example accepted samples:

```text
wikidata-ada-1 score=1.0 difficulty=medium question=What country is Ada Lovelace's birthplace the capital of?
wikidata-curie-2 score=1.0 difficulty=easy question=What is the current country of Marie Curie's birthplace?
```

First rejected sample:

```text
wikidata-ada-4 score=0.8 reasons=not_duplicate question=What country is Ada Lovelace's birthplace the capital of?
```

## Notes and Analysis

- This is the first 30-sample real DeepSeek teacher pilot with per-sample progress logging.
- All 30 teacher calls succeeded. There were no API timeouts, no deterministic fallbacks, no trajectory repairs, and no difficulty normalizations.
- The verifier accepted 20 samples and rejected 10 samples only because of duplicated questions.
- The exported SFT and RL datasets contain 20 accepted samples. The full trace preserves all 30 attempted samples for audit.
- The 0.6667 dedup rate is a useful signal: the current three-seed demo corpus is too small for scaling without stronger question diversification.
- No GPU was used. This was an API-only generation run.

## Next Step Thoughts

- Add a stronger question diversification step before increasing sample count, for example prompt-level anti-dup constraints or a rewrite-on-duplicate loop.
- Export duplicate clusters in the trace summary so duplicate analysis does not require manual JSONL inspection.
- Run a 50-sample pilot only after the duplicate rewrite path is implemented; otherwise the same three-seed source will likely waste API calls.
- For resume material, describe this run as a real teacher-backed pilot with verifier rejection sampling, not as a fully scaled dataset.
