# DeepSeek Teacher 10 Retry2

## Metadata

- Experiment name: deepseek-teacher-10-retry2-20260610
- Date: 2026-06-10
- Goal: Retry the first real DeepSeek-backed teacher generation after API-key sanitation fixes.
- Status: completed with all samples rejected by verifier
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Branch: `main`
- Commit: `ba5f2c9`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- Number of GPUs: 0
- tmux session: `openseeker-20260610-deepseek-teacher-10-retry2`
- Model: `deepseek-v4-pro`
- Base URL: `https://api.deepseek.com`

## Commands

The API key was passed as a one-time environment variable from stdin and was not written to repo files or the experiment record.

```bash
tmux new-session -d -s openseeker-20260610-deepseek-teacher-10-retry2 \
  "bash -lc 'cd /data/wzl/OpenSeeker-AgentDataFactory/repo && source /home/user/anaconda3/etc/profile.d/conda.sh && conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate --count 10 --seed-file data/seeds/wikidata_seed_sample.jsonl --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-10-retry2-20260610 --teacher-backend openai-compatible --teacher-base-url https://api.deepseek.com --teacher-model deepseek-v4-pro --teacher-api-key-env DEEPSEEK_API_KEY 2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-10-retry2-20260610.log'"
```

## Paths

- Log path: `/data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-10-retry2-20260610.log`
- Results path: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-10-retry2-20260610`
- Trace path: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-10-retry2-20260610/trace.jsonl`
- Checkpoint path: not applicable
- Run path: not applicable

## Raw Result Summary

```text
OpenSeeker AgentDataFactory generation complete: accepted=0 rejected=10 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-10-retry2-20260610
```

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,tool_success_rate,trajectory_valid_rate,manual_sample_pass_rate
10,0,10,0.8,1.0,1.0,1.0,0.0,
```

Output files:

```text
rl_rewards.jsonl 0 lines
samples.jsonl 0 lines
sft_conversations.jsonl 0 lines
trace.jsonl 10 lines
summary.csv 165 bytes
```

Example rejection:

```text
reasons: ["trajectory_valid"]
trajectory: ["Find Ada Lovelace's birthplace: London.", "Find the country of which London is the capital: United Kingdom."]
```

## Notes and Analysis

- The DeepSeek API path is now authenticated and reachable.
- All samples failed because the teacher-generated trajectory did not follow the verifier-required ReAct format with `Thought:`, `Action:`, `Observation:`, and `Final:`.
- Evidence, answer support, and tool success all passed, so the rejection is specifically a trajectory-format issue.
- The dedup rate was `0.8` because the small seed file repeats tasks over 10 samples.
- No GPU was used.

## Next Step Thoughts

- Add a deterministic trajectory repair/fallback when a teacher draft has an invalid ReAct trajectory.
- Keep the teacher-drafted question and difficulty, but mark repaired trajectories in `source` so resume claims remain honest.
- Retry with 10 samples after the repair to verify the DeepSeek path can produce accepted samples.
