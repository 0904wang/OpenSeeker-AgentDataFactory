# Remote Generate Smoke

## Metadata

- Experiment name: remote-generate-smoke
- Date: 2026-06-09
- Goal: Verify the seed-file driven `generate` command on the remote server after fixing package discovery.
- Status: success
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Branch: `main`
- Commit: `96be6a8`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- Number of GPUs: 0

## Commands

Pull and install:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
git fetch origin --prune
git checkout main
git pull --ff-only origin main
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m pip install -e . pytest
```

Dry run:

```bash
PYTHONNOUSERSITE=1 python -m pytest
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 12 \
  --seed-file data/seeds/wikidata_seed_sample.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/generate-smoke
```

Monitoring:

```bash
cat /data/wzl/OpenSeeker-AgentDataFactory/results/generate-smoke/summary.csv
ls -lah /data/wzl/OpenSeeker-AgentDataFactory/results/generate-smoke
```

## Paths

- Log path: not applicable
- Results path: `/data/wzl/OpenSeeker-AgentDataFactory/results/generate-smoke`
- Data path: `/data/wzl/OpenSeeker-AgentDataFactory/results/generate-smoke/samples.jsonl`
- Checkpoint path: not applicable
- Run path: not applicable
- Local copied artifacts: not copied locally

## Raw Result Summary

```text
96be6a8
Successfully built openseeker-agent-data-factory
Successfully installed openseeker-agent-data-factory-0.1.0
..........                                                               [100%]
10 passed in 1.65s
OpenSeeker AgentDataFactory generation complete: accepted=12 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/generate-smoke
```

```text
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,tool_success_rate,trajectory_valid_rate,manual_sample_pass_rate
12,12,0,1.0,1.0,1.0,1.0,1.0,
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
| total | 12 | smoke-scale seed-file generation |
| accepted | 12 | verifier passed all smoke samples |
| rejected | 0 | no rejected samples |
| dedup_rate | 1.0 | deterministic question variants avoided duplicate text |
| solvability_rate | 1.0 | answer appears in evidence |
| evidence_hit_rate | 1.0 | tool results covered by evidence |
| tool_success_rate | 1.0 | final answer appears in tool results |
| trajectory_valid_rate | 1.0 | trajectory contains Thought, Action, and Final |
| manual_sample_pass_rate | not measured | manual audit is for 5k+ baseline |
| runtime | not measured | smoke validation only |
| throughput | not meaningful | count is 12 |

## Failures / Warnings

- Before this fix, remote editable install failed because setuptools discovered multiple top-level packages after `data/` was added.
- The fix explicitly configures package discovery to include only `openseeker_factory*` and excludes `data*`, `docs*`, `outputs*`, and `tests*`.
- A PowerShell here-string again added CRLF to the final `cat` path; the output files were then verified with a separate simple SSH command.
- This is not the 5k baseline experiment and does not justify resume claims about data scale or model improvement.

## Analysis

What the result means for the data synthesis system:

- The remote server can now install the project after adding the seed data directory.
- The new seed-file `generate` command works remotely.
- The deterministic question variants preserve strict duplicate filtering for repeated seed expansion.

What it means for the resume project:

- It is now fair to say the remote workflow supports seed-file driven generation.
- The next resume-relevant evidence target is a 5k baseline generation run with a local experiment record and, ideally, manual sample audit.

## Next Steps

- Push this experiment record to GitHub.
- Prepare the 5k baseline launch approval using `openseeker-20260609-baseline-5k`.
- Before launch, re-check GPU memory and report exact command, log path, and results path.

