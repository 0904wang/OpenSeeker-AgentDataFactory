# DeepSeek Teacher 10 Retry5 Success

## Metadata

- Experiment name: deepseek-teacher-10-retry5-20260610
- Date: 2026-06-10
- Goal: Run a small DeepSeek-backed teacher generation after adding timeout fallback and difficulty normalization.
- Status: success
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Branch: `main`
- Commit: `b8fea91`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- Number of GPUs: 0
- tmux session: `openseeker-20260610-deepseek-teacher-10-retry5`
- Model: `deepseek-v4-pro`
- Base URL: `https://api.deepseek.com`

## Commands

The API key was passed as a one-time environment variable inherited by the tmux process. It was not passed through `tmux -e` and did not appear in the process command line.

```bash
tmux new-session -d -s openseeker-20260610-deepseek-teacher-10-retry5 \
  "bash -lc 'cd /data/wzl/OpenSeeker-AgentDataFactory/repo && source /home/user/anaconda3/etc/profile.d/conda.sh && conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate --count 10 --seed-file data/seeds/wikidata_seed_sample.jsonl --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-10-retry5-20260610 --teacher-backend openai-compatible --teacher-base-url https://api.deepseek.com --teacher-model deepseek-v4-pro --teacher-api-key-env DEEPSEEK_API_KEY 2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-10-retry5-20260610.log'"
```

## Paths

- Log path: `/data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-10-retry5-20260610.log`
- Results path: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-10-retry5-20260610`
- Samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-10-retry5-20260610/samples.jsonl`
- SFT export: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-10-retry5-20260610/sft_conversations.jsonl`
- RL reward export: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-10-retry5-20260610/rl_rewards.jsonl`
- Trace path: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-10-retry5-20260610/trace.jsonl`
- Checkpoint path: not applicable
- Run path: not applicable

## Raw Result Summary

```text
OpenSeeker AgentDataFactory generation complete: accepted=10 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-10-retry5-20260610
```

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,tool_success_rate,trajectory_valid_rate,manual_sample_pass_rate
10,10,0,1.0,1.0,1.0,1.0,1.0,
```

Output files:

```text
rl_rewards.jsonl 10 lines
samples.jsonl 10 lines
sft_conversations.jsonl 10 lines
trace.jsonl 10 lines
summary.csv 165 bytes
```

Trace audit:

```text
rows 10
accepted 10
teacher_errors 5
trajectory_repaired 0
invalid_difficulty_normalized 0
```

Example accepted DeepSeek draft:

```text
question: Which country has as its capital the city where Ada Lovelace was born?
difficulty: easy
source.teacher_backend: openai-compatible
```

## Notes and Analysis

- This is the first successful real API-backed teacher run in the project.
- Five samples were directly drafted by DeepSeek and passed verifier checks.
- Five samples hit teacher API timeout and fell back to deterministic generation. They are marked with `source.teacher_backend_error`.
- Because fallback is enabled, the headline `accepted=10` should be described as "DeepSeek-backed with deterministic fallback," not as 10 fully teacher-generated samples.
- No GPU was used.

## Next Step Thoughts

- Improve observability by logging per-sample teacher status during generation instead of only printing a final summary.
- Add an optional retry count or longer timeout for DeepSeek teacher calls.
- Run a 30-50 sample API-backed pilot after adding per-sample progress logging, then inspect teacher/fallback ratios before scaling.
