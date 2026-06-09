# Remote Dry Run

## Metadata

- Experiment name: remote-dry-run
- Date: 2026-06-09
- Goal: Clone the GitHub project to the approved remote workspace, create the approved conda env, install the local package, and reproduce the local contract validation remotely.
- Status: success
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Branch: `main`
- Commit: `fe9efa9`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- Number of GPUs: 0

## Commands

Preflight and setup:

```bash
mkdir -p /data/wzl/OpenSeeker-AgentDataFactory/{repo,.conda-envs,data,logs,results,checkpoints,runs}
mkdir -p /home/user/wzl
ln -sfn /data/wzl/OpenSeeker-AgentDataFactory /home/user/wzl/OpenSeeker-AgentDataFactory
git clone https://github.com/0904wang/OpenSeeker-AgentDataFactory.git /data/wzl/OpenSeeker-AgentDataFactory/repo
```

Environment:

```bash
source /home/user/anaconda3/etc/profile.d/conda.sh
conda create -y -p /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory python=3.10
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m pip install -e . pytest
```

Dry run:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m pytest
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli demo --count 3 --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/dry-run
```

Monitoring:

```bash
ls -lah /data/wzl/OpenSeeker-AgentDataFactory/results/dry-run
cat /data/wzl/OpenSeeker-AgentDataFactory/results/dry-run/summary.csv
head -n 1 /data/wzl/OpenSeeker-AgentDataFactory/results/dry-run/samples.jsonl
```

## Paths

- Log path: not applicable
- Results path: `/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run`
- Data path: `/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run/samples.jsonl`
- Checkpoint path: not applicable
- Run path: not applicable
- Local copied artifacts: not copied locally

## Raw Result Summary

```text
fe9efa9
Python 3.10.20
.......                                                                  [100%]
7 passed in 0.05s
```

```text
OpenSeeker AgentDataFactory demo complete: accepted=3 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run
```

```text
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,tool_success_rate,trajectory_valid_rate,manual_sample_pass_rate
3,3,0,1.0,1.0,1.0,1.0,1.0,
```

Remote result files:

```text
rl_rewards.jsonl
samples.jsonl
sft_conversations.jsonl
summary.csv
trace.jsonl
```

## Metrics

| Metric | Value | Notes |
| --- | --- | --- |
| total | 3 | deterministic demo samples |
| accepted | 3 | verifier passed all demo samples |
| rejected | 0 | no rejected sample in dry run |
| dedup_rate | 1.0 | no duplicate question |
| solvability_rate | 1.0 | answer appears in evidence |
| evidence_hit_rate | 1.0 | tool results covered by evidence |
| tool_success_rate | 1.0 | final answer appears in tool results |
| trajectory_valid_rate | 1.0 | trajectory contains Thought, Action, and Final |
| manual_sample_pass_rate | not measured | manual audit is for larger runs |
| runtime | not measured | command-level success only |
| throughput | not meaningful | demo scale is too small |

## Failures / Warnings

- First SSH clone attempt using `git@github.com:0904wang/OpenSeeker-AgentDataFactory.git` failed because the remote server did not have a GitHub SSH key with access.
- HTTPS clone succeeded.
- First dry-run attempt loaded pytest from `/home/user/.local`, which pulled unrelated user-level plugins and failed with `ModuleNotFoundError: No module named 'antlr4'`.
- Setting `PYTHONNOUSERSITE=1` isolated the conda env and fixed the issue.
- A later `cat` command failed once because a PowerShell here-string passed CRLF into the remote shell path. The dry-run outputs existed and were verified with a separate command.

## Analysis

What the result means for the data synthesis system:

- The repository can be cloned from GitHub over HTTPS into the approved remote workspace.
- The project-local conda environment works and can run tests independently when user site packages are disabled.
- The remote server reproduces the local contract validation: schema, verifier, exports, and CLI demo are all executable remotely.

What it means for the resume project:

- It is now fair to say the project has a verified remote dry-run workflow on the lab server.
- It is still not fair to claim large-scale 20k/50k generation, model SFT/RL results, or 4-GPU throughput.

## Next Steps

- Push this experiment record and `PYTHONNOUSERSITE=1` command updates to GitHub.
- Plan the first 5k baseline generation command.
- Before any real run, report exact GPUs, tmux session name, log path, results path, and command for user approval.

