# Remote Setup and Dry-Run Approval Packet

This packet is the next safe step after the read-only remote preflight. Do not run the setup or dry-run commands until the user approves the exact action.

## Current Remote Facts

From `docs/experiments/2026-06-09-remote-readonly-preflight.md`:

- SSH entrypoint works: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- `/data/wzl/OpenSeeker-AgentDataFactory` is missing
- `/home/user/wzl/OpenSeeker-AgentDataFactory` is missing
- `tmux` exists at `/usr/bin/tmux`
- conda works when initialized with `source /home/user/anaconda3/etc/profile.d/conda.sh`
- GPU 0, 1, 2, 4, 5, 6, and 7 were below the 4000 MiB free threshold at preflight time
- GPU 3 was busy
- `/data` had about 4.9T free

## Step 1 - Approved Workspace Setup

Purpose: create only the approved project directories and symlink. This does not install packages, sync code, or start a run.

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 "bash -lc '
  set -e
  mkdir -p /data/wzl/OpenSeeker-AgentDataFactory/{repo,.conda-envs,data,logs,results,checkpoints,runs}
  mkdir -p /home/user/wzl
  ln -sfn /data/wzl/OpenSeeker-AgentDataFactory /home/user/wzl/OpenSeeker-AgentDataFactory
  ls -ld /data/wzl/OpenSeeker-AgentDataFactory
  ls -ld /home/user/wzl/OpenSeeker-AgentDataFactory
'"
```

Safety:

- Writes only under `/data/wzl/OpenSeeker-AgentDataFactory` and `/home/user/wzl`.
- Does not use `sudo`.
- Does not delete anything.
- Does not modify shell or SSH config.

## Step 2 - Code Sync Decision

The local path `D:\resume\Data synthesis` is not currently a git repository. Choose one sync strategy before dry run.

### Option A - Recommended GitHub Sync

Best for reproducibility and resume credibility.

Local actions:

```bash
git init
git add README.md AGENTS.md pyproject.toml openseeker_factory tests docs .gitignore
git commit -m "Create OpenSeeker AgentDataFactory scaffold"
git branch -M main
git remote add origin git@github.com:0904wang/OpenSeeker-AgentDataFactory.git
git push -u origin main
```

Remote actions after the repo exists:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 "bash -lc '
  set -e
  if [ ! -d /data/wzl/OpenSeeker-AgentDataFactory/repo/.git ]; then
    git clone git@github.com:0904wang/OpenSeeker-AgentDataFactory.git /data/wzl/OpenSeeker-AgentDataFactory/repo
  fi
  cd /data/wzl/OpenSeeker-AgentDataFactory/repo
  git fetch origin --prune
  git checkout main
  git pull --ff-only origin main
'"
```

### Option B - Temporary Narrow File Sync

Use only if the GitHub repo is not ready. This is less reproducible but acceptable for an initial smoke test if explicitly approved.

Local command from PowerShell:

```powershell
scp -P 29509 -r `
  README.md AGENTS.md pyproject.toml .gitignore openseeker_factory tests docs `
  user@ssh-22.e6.luyouxia.net:/data/wzl/OpenSeeker-AgentDataFactory/repo/
```

Safety:

- Copies only named project files and directories.
- Does not use broad cleanup.
- Does not copy cache, output, or checkpoint directories.

## Step 3 - Environment Setup

Only after workspace and code sync are approved.

Check if env exists:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 "bash -lc '
  source /home/user/anaconda3/etc/profile.d/conda.sh
  if [ -d /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory ]; then
    echo ENV_EXISTS
  else
    echo ENV_MISSING
  fi
'"
```

Create env if missing:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 "bash -lc '
  set -e
  source /home/user/anaconda3/etc/profile.d/conda.sh
  conda create -y -p /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory python=3.10
'"
```

Install the local package in editable mode:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 "bash -lc '
  set -e
  cd /data/wzl/OpenSeeker-AgentDataFactory/repo
  source /home/user/anaconda3/etc/profile.d/conda.sh
  conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
  python -m pip install -e . pytest
'"
```

This install is allowed only because it targets the approved project-local conda env.

## Step 4 - Remote Dry Run

Run only after setup succeeds.

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 "bash -lc '
  set -e
  cd /data/wzl/OpenSeeker-AgentDataFactory/repo
  source /home/user/anaconda3/etc/profile.d/conda.sh
  conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
  python -m pytest
  python -m openseeker_factory.cli demo --count 3 --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/dry-run
  cat /data/wzl/OpenSeeker-AgentDataFactory/results/dry-run/summary.csv
'"
```

Acceptance:

- Tests pass remotely.
- Dry-run output appears under `/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run`.
- Summary reports `total=3`, `accepted=3`, `rejected=0` for the deterministic demo.
- A local record is created under `docs/experiments/`.

## Step 5 - First Real Launch Requires Separate Approval

Do not run a real generation, SFT, RL, or 4-GPU job from this packet.

Before launch, report:

- repo and branch
- commit
- conda env
- selected GPUs
- number of GPUs
- exact tmux session name
- exact launch command
- exact log path
- exact results path
- checkpoint path if training is involved

