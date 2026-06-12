# 2026-06-11 Teacher Trajectory Faithfulness Repair

## Goal

Prevent teacher-generated ReAct trajectories from entering SFT export when they are syntactically valid but use an unsupported intermediate observation. The factory should repair those trajectories to the deterministic seed-derived trajectory before verification and export, then record the repair reason in sample metadata.

## Code Scope

- Local repo: `D:\resume\Data synthesis`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Branch: `main`
- Remote commit before narrow sync: `7b64c03`
- Files synchronized to remote:
  - `README.md`
  - `openseeker_factory/pipeline.py`
  - `tests/test_pipeline.py`

## Effective Change

- Added a regression test with a fake teacher that returns a valid-looking ReAct trajectory for Ada Lovelace but hallucinates `Cambridge` as the birthplace.
- `AgentDataFactory.generate_trajectory` now validates teacher trajectory drafts for:
  - ReAct format
  - expected tool result coverage, including intermediate birthplace and final answer
- If either check fails, the sample falls back to the deterministic seed-derived trajectory.
- Repaired samples record:
  - `source.teacher_trajectory_repaired=true`
  - `source.teacher_trajectory_repair_reason=react_format` or `evidence_faithfulness`
- README now documents the export-time repair behavior.

## Commands

Local red/green and regression commands:

```bash
python -m pytest tests/test_pipeline.py
python -m pytest tests/test_cli.py tests/test_pipeline.py
python -m pytest
```

Remote preflight:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 'pwd && test -d /data/wzl/OpenSeeker-AgentDataFactory/repo && cd /data/wzl/OpenSeeker-AgentDataFactory/repo && git branch --show-current && git rev-parse --short HEAD && command -v tmux && source /home/user/anaconda3/etc/profile.d/conda.sh && conda --version && nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader && df -h /data/wzl/OpenSeeker-AgentDataFactory'
```

Narrow sync:

```bash
scp -P 29509 README.md user@ssh-22.e6.luyouxia.net:/data/wzl/OpenSeeker-AgentDataFactory/repo/README.md
scp -P 29509 openseeker_factory/pipeline.py user@ssh-22.e6.luyouxia.net:/data/wzl/OpenSeeker-AgentDataFactory/repo/openseeker_factory/pipeline.py
scp -P 29509 tests/test_pipeline.py user@ssh-22.e6.luyouxia.net:/data/wzl/OpenSeeker-AgentDataFactory/repo/tests/test_pipeline.py
```

Remote verification:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 'cd /data/wzl/OpenSeeker-AgentDataFactory/repo && source /home/user/anaconda3/etc/profile.d/conda.sh && conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && PYTHONNOUSERSITE=1 python -m pytest tests/test_pipeline.py tests/test_cli.py'

ssh user@ssh-22.e6.luyouxia.net -p 29509 'cd /data/wzl/OpenSeeker-AgentDataFactory/repo && source /home/user/anaconda3/etc/profile.d/conda.sh && conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && PYTHONNOUSERSITE=1 python -m pytest'
```

Remote status check:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 'tmux list-sessions 2>/dev/null || true; nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader'
```

## Results

Local verification:

```text
tests/test_pipeline.py: 15 passed in 0.19s
tests/test_cli.py tests/test_pipeline.py: 23 passed in 4.04s
full local pytest: 45 passed in 15.80s
```

Remote verification:

```text
tests/test_pipeline.py tests/test_cli.py: 23 passed in 1.31s
full remote pytest: 45 passed in 4.59s
```

Remote preflight summary:

```text
remote branch: main
remote commit before sync: 7b64c03
tmux: /usr/bin/tmux
conda: 26.1.1
disk: /data has 4.9T available
GPU memory after verification:
0 3506 MiB, 1 3505 MiB, 2 3507 MiB, 3 25985 MiB,
4 26101 MiB, 5 3493 MiB, 6 3505 MiB, 7 18 MiB
active openseeker tmux sessions: none observed
```

## Analysis

The previous verifier could reject unfaithful trajectories after generation, but accepted teacher drafts were still decided primarily by ReAct shape. This change moves the faithfulness gate earlier: teacher trajectory drafts are checked against deterministic tool results before export, so SFT data keeps teacher question variation while preserving seed-grounded tool observations.

This is useful for the resume project because it turns verifier logic into a data-quality intervention, not only an offline score. The resulting data factory can now report both rejection and repair behavior for teacher-generated synthetic data.

## Risks

- The repair currently falls back to deterministic seed-derived trajectories. This is reliable but less diverse than a teacher rewrite loop.
- The current faithfulness check is string-based on expected tool results. It is appropriate for the Wikidata seed setting, but richer tool environments should use executed tool traces or structured verifier outputs.
- Future high-volume generation should track `teacher_trajectory_repaired` and `teacher_trajectory_repair_reason` distributions to ensure the teacher backend is not producing too many repaired samples.

## Next Steps

- Add these repair counters to generation summaries if not already exposed in downstream reports.
- Run the next 1k or 5k teacher generation with repair metrics recorded.
- Compare SFT results for deterministic-only trajectories vs teacher-question plus repaired-faithful trajectories.
