# Remote Resync Dry Run

## Metadata

- Experiment name: remote-resync-dry-run
- Date: 2026-06-10
- Goal: Verify that the remote repo can be updated from GitHub over HTTPS and that the approved conda environment still passes the project smoke test after sync.
- Status: success
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Branch: `main`
- Commit: `7ca6b25`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- Number of GPUs: 0

## Commands

Remote preflight:

```bash
pwd
mkdir -p /data/wzl/OpenSeeker-AgentDataFactory/{repo,.conda-envs,data,logs,results,checkpoints,runs}
mkdir -p /home/user/wzl
ln -sfn /data/wzl/OpenSeeker-AgentDataFactory /home/user/wzl/OpenSeeker-AgentDataFactory
test -d /data/wzl/OpenSeeker-AgentDataFactory
command -v tmux
source /home/user/anaconda3/etc/profile.d/conda.sh
conda --version
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader
df -h /data/wzl/OpenSeeker-AgentDataFactory
```

Code sync:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
git fetch origin --prune
git checkout main
git pull --ff-only origin main
git rev-parse HEAD
git status --short --branch
```

Smoke test and dry run:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m pytest
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli demo --count 3 --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/dry-run
```

Result inspection:

```bash
cat /data/wzl/OpenSeeker-AgentDataFactory/results/dry-run/summary.csv
head -n 1 /data/wzl/OpenSeeker-AgentDataFactory/results/dry-run/samples.jsonl
```

## Paths

- Log path: not applicable
- Results path: `/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run`
- Data path: `/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run/samples.jsonl`
- SFT export: `/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run/sft_conversations.jsonl`
- RL reward export: `/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run/rl_rewards.jsonl`
- Trace path: `/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run/trace.jsonl`
- Checkpoint path: not applicable
- Run path: not applicable

## Raw Result Summary

```text
Remote repo before sync: 96be6a8
Remote repo after sync: 7ca6b25
Local/GitHub main: 7ca6b25
```

```text
..........                                                               [100%]
10 passed in 1.80s
```

```text
OpenSeeker AgentDataFactory demo complete: accepted=3 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run
```

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,tool_success_rate,trajectory_valid_rate,manual_sample_pass_rate
3,3,0,1.0,1.0,1.0,1.0,1.0,
```

Remote result files:

```text
rl_rewards.jsonl 938 bytes
samples.jsonl 4061 bytes
sft_conversations.jsonl 1707 bytes
summary.csv 163 bytes
trace.jsonl 4259 bytes
```

## Notes and Analysis

- The server-side repo was one commit behind GitHub and fast-forwarded cleanly over HTTPS.
- The approved conda environment remained usable after sync; no package installation or environment mutation was needed.
- This run used CPU only and did not start a long-running tmux job.
- The demo output confirms the current local contract: JSONL sample export, Agent SFT export, RL reward export, trace JSONL, and summary CSV are all produced.
- The quality metrics are perfect only because this is a deterministic 3-sample smoke test; they should not be presented as real model-quality evidence.

## Next Step Thoughts

- The next useful remote run is a small approved tmux generation job that writes to a timestamped results directory instead of reusing `results/dry-run`.
- Before that launch, prepare an approval payload with exact command, selected GPU, session name, log path, output path, and sample count.
- Use 1 GPU by default; the preflight showed GPUs 0, 1, 2, 5, 6, and 7 below 4000 MiB, while GPUs 3 and 4 were occupied.
- For resume material, treat this result as infrastructure validation, not as a core experimental result.
