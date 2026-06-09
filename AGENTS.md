# OpenSeeker AgentDataFactory Remote Experiment Rules

This project is allowed to run OpenSeeker AgentDataFactory experiments on a shared remote GPU server, but only within the constraints in this file. These rules are hard constraints, not suggestions.

## Goal

Set up, run, monitor, and record remote experiments for a verifiable LLM synthetic data factory focused on:

- multi-hop QA data synthesis
- tool-use QA and ReAct trajectory generation
- noisy-context retrieval QA
- verifier-based filtering and rejection sampling
- Agent SFT / small-scale RL data export and evaluation

Target work includes:

- syncing this project to the approved remote workspace
- creating and using an isolated project-local conda environment
- running smoke tests, dry runs, and approved generation or training jobs
- monitoring logs and collecting results
- recording experiment metadata and outcomes

## Required Remote Config

This block is the source of truth for the `safe-remote-experiments` workflow.

```yaml
backend: ssh
ssh_alias: "user@ssh-22.e6.luyouxia.net -p 29509"
ssh_entrypoint: "ssh user@ssh-22.e6.luyouxia.net -p 29509"
work_dir: "/data/wzl/OpenSeeker-AgentDataFactory/repo"
allowed_paths:
  - "/data/wzl/OpenSeeker-AgentDataFactory"
  - "/home/user/wzl/OpenSeeker-AgentDataFactory"
  - "D:\\resume\\Data synthesis"
activate_env: "source /home/user/anaconda3/etc/profile.d/conda.sh && conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory"
scheduler: "tmux"
code_sync: "explicit git pull --ff-only or narrow file sync approved by the user"
branch: "main"
dry_run_command: "cd /data/wzl/OpenSeeker-AgentDataFactory/repo && source /home/user/anaconda3/etc/profile.d/conda.sh && conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && PYTHONNOUSERSITE=1 python -m pytest && PYTHONNOUSERSITE=1 python -m openseeker_factory.cli demo --count 3 --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/dry-run"
launch_command: "cd /data/wzl/OpenSeeker-AgentDataFactory/repo && source /home/user/anaconda3/etc/profile.d/conda.sh && conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && tmux new-session -d -s openseeker-YYYYMMDD-task-name \"CUDA_VISIBLE_DEVICES=0 PYTHONNOUSERSITE=1 python -m openseeker_factory.cli demo --count N --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/task-name 2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/task-name.log\""
log_path: "/data/wzl/OpenSeeker-AgentDataFactory/logs/task-name.log"
results_dir: "/data/wzl/OpenSeeker-AgentDataFactory/results/task-name"
monitor_commands:
  - "nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader"
  - "tmux list-sessions"
  - "tail -n 80 /data/wzl/OpenSeeker-AgentDataFactory/logs/task-name.log"
  - "ls -lah /data/wzl/OpenSeeker-AgentDataFactory/results/task-name"
stop_command: "tmux list-sessions && echo 'Stop requires user approval for the exact openseeker-* session before running tmux kill-session.'"
forbidden_commands:
  - "sudo"
  - "su"
  - "rm -rf"
  - "reboot"
  - "shutdown"
  - "systemctl"
  - "service"
  - "apt"
  - "yum"
  - "dnf"
  - "pip install outside the approved conda env"
  - "conda install outside the approved conda env"
  - "editing ~/.ssh/config"
  - "editing ~/.bashrc"
  - "cron edits"
  - "user-management commands"
approved_setup_command: "Only create directories under /data/wzl/OpenSeeker-AgentDataFactory and create / activate the approved conda environment when explicitly needed."
```

If any required field is missing, ambiguous, or contradicted by another file, stop and ask before any remote command.

## Hard Safety Constraints

- Only operate under `/data/wzl/OpenSeeker-AgentDataFactory`, `/home/user/wzl/OpenSeeker-AgentDataFactory`, and the local project workspace `D:\resume\Data synthesis`.
- Treat `/data/wzl/OpenSeeker-AgentDataFactory` as the real remote workspace.
- Treat `/home/user/wzl/OpenSeeker-AgentDataFactory` only as a symlink entrypoint to the real workspace.
- Treat `D:\resume\Data synthesis` as an approved local project workspace for documentation, planning files, helper scripts, and repo-local artifacts.
- Never write project files outside the approved remote `wzl` paths or the approved local project workspace.
- Never use `sudo`, `su`, system package managers, service managers, firewall changes, cron edits, or user-management commands.
- Never modify `.bashrc`, `~/.ssh/config`, system CUDA drivers, or machine-wide settings.
- Never install anything into the `base` conda environment.
- Never run global `pip install` or install into system Python.
- Never run destructive cleanup commands such as `rm -rf` without explicit user approval for the exact path.
- Never delete `checkpoints`, `results`, `data`, or `logs` automatically.
- Never start a real generation, SFT, or RL run before reporting the plan and receiving user approval.

System-level CUDA driver changes are forbidden. Environment-local PyTorch and CUDA runtime packages are allowed only inside the approved conda environment.

## Remote Access

Use this exact SSH entrypoint:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509
```

Do not create SSH aliases by editing shell init files or SSH config. Do not rewrite SSH settings.

## Allowed Paths

Real workspace:

```bash
/data/wzl/OpenSeeker-AgentDataFactory
```

Symlink entrypoint:

```bash
/home/user/wzl/OpenSeeker-AgentDataFactory -> /data/wzl/OpenSeeker-AgentDataFactory
```

Allowed project subpaths:

```bash
/data/wzl/OpenSeeker-AgentDataFactory/repo
/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs
/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
/data/wzl/OpenSeeker-AgentDataFactory/data
/data/wzl/OpenSeeker-AgentDataFactory/logs
/data/wzl/OpenSeeker-AgentDataFactory/results
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints
/data/wzl/OpenSeeker-AgentDataFactory/runs
```

If a required directory is missing, it may be created with `mkdir -p` only under `/data/wzl/OpenSeeker-AgentDataFactory`.

If the symlink is missing, it may be created as:

```bash
mkdir -p /home/user/wzl
ln -sfn /data/wzl/OpenSeeker-AgentDataFactory /home/user/wzl/OpenSeeker-AgentDataFactory
```

## Repository Layout

Expected remote layout:

```text
/data/wzl/OpenSeeker-AgentDataFactory/
  repo/
  .conda-envs/
    openseeker-datafactory/
  data/
  logs/
  results/
  checkpoints/
  runs/
```

## Code Sync Policy

Use only one of these sync methods:

- `git pull --ff-only` from a known branch inside `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- a narrow file sync explicitly approved by the user
- a user-provided sync command that writes only under approved paths

Do not use `git add -A`, broad copy commands, or destructive cleanup as deployment shortcuts. Do not rewrite history or force push unless the user explicitly asks.

## Conda and Environment Policy

Always initialize conda explicitly with the `conda.sh` profile script. This form has been verified over the configured SSH entrypoint:

```bash
source /home/user/anaconda3/etc/profile.d/conda.sh
```

Do not rely on `.bashrc`.

Approved environment:

```bash
/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
```

Python target:

```text
Python 3.10
```

If the environment does not exist, it may be created only after confirming the active target path:

```bash
source /home/user/anaconda3/etc/profile.d/conda.sh
conda create -y -p /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory python=3.10
```

Activation example:

```bash
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
```

Allowed installation scope:

- active env is `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- `pip`, `uv`, and `conda` installs that clearly target the active approved env
- PyTorch CUDA runtime packages inside the approved env
- commands that run Python in the approved env must set `PYTHONNOUSERSITE=1` to avoid loading packages from `/home/user/.local`

Forbidden installation scope:

- `base` environment
- system Python
- global `pip`
- system CUDA driver
- OS package managers

If dependencies are missing and no approved setup command covers them, stop and ask instead of installing ad hoc.

## GPU Policy

This is a shared 8-GPU machine.

Hard limits:

- never use more than 4 GPUs
- always check free memory before selecting GPUs
- a GPU counts as free only if used memory is below `4000 MiB`
- prefer 1 to 2 GPUs by default
- do not use 4 GPUs without explicit user approval for that exact run

Preferred check:

```bash
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader
```

If GPU usage is ambiguous or too crowded, stop and report instead of guessing.

## Required Directory Conventions

All experiment inputs and outputs must stay under the approved workspace.

Data:

```bash
/data/wzl/OpenSeeker-AgentDataFactory/data
```

Logs:

```bash
/data/wzl/OpenSeeker-AgentDataFactory/logs
```

Results:

```bash
/data/wzl/OpenSeeker-AgentDataFactory/results
```

Checkpoints:

```bash
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints
```

Runs:

```bash
/data/wzl/OpenSeeker-AgentDataFactory/runs
```

## Execution Workflow

Follow this sequence strictly.

### 1. Preflight

Before any setup or run:

- verify SSH access
- verify current working directory
- verify allowed paths exist or create only the approved missing paths
- verify symlink exists or create it
- verify `tmux` exists
- verify conda hook works
- inspect GPU memory usage
- inspect CPU and memory status when relevant
- inspect disk usage for `/data/wzl/OpenSeeker-AgentDataFactory`
- verify `log_path` and `results_dir` are inside approved paths

Example preflight:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 '\
  pwd && \
  mkdir -p /data/wzl/OpenSeeker-AgentDataFactory/{repo,.conda-envs,data,logs,results,checkpoints,runs} && \
  mkdir -p /home/user/wzl && \
  ln -sfn /data/wzl/OpenSeeker-AgentDataFactory /home/user/wzl/OpenSeeker-AgentDataFactory && \
  test -d /data/wzl/OpenSeeker-AgentDataFactory && \
  command -v tmux && \
  source /home/user/anaconda3/etc/profile.d/conda.sh && \
  conda --version && \
  nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader && \
  df -h /data/wzl/OpenSeeker-AgentDataFactory'
```

### 2. Code Sync

Sync code using the configured method only. Prefer a narrow, explicit update.

If `/data/wzl/OpenSeeker-AgentDataFactory/repo` is a git repository:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
git fetch origin --prune
git checkout main
git pull --ff-only origin main
```

If it is not a git repository, stop and ask for the approved clone or sync command.

### 3. Environment Setup

If the approved env is missing:

- create only `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- activate that env
- install only dependencies needed for this project and task

Never install into `base`.

### 4. Smoke Test and Dry Run

Before any real run:

- run `python -m pytest`
- run a minimal generation dry run
- use the smallest safe config possible
- prefer 1 GPU or CPU for dry runs unless the test requires CUDA

Default dry run:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 '\
  cd /data/wzl/OpenSeeker-AgentDataFactory/repo && \
  source /home/user/anaconda3/etc/profile.d/conda.sh && \
  conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && \
  PYTHONNOUSERSITE=1 python -m pytest && \
  PYTHONNOUSERSITE=1 python -m openseeker_factory.cli demo --count 3 --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/dry-run'
```

If the smoke test fails, stop and report after at most one automatic retry.

### 5. Report Before Launch

After the smoke test succeeds, report all of the following before launching:

- selected repo and branch
- selected conda env
- selected GPUs
- number of GPUs
- exact launch command
- exact `tmux` session name
- exact log path
- expected checkpoint path if training is involved
- expected results path

Wait for user approval before the real launch.

### 6. Launch

Only after user approval:

- start one experiment per `tmux` session
- redirect stdout and stderr to a log file under `/data/wzl/OpenSeeker-AgentDataFactory/logs`
- keep the launch command explicit and reproducible
- include `CUDA_VISIBLE_DEVICES=...` in GPU jobs

Example launch pattern after user approval:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 '\
  cd /data/wzl/OpenSeeker-AgentDataFactory/repo && \
  source /home/user/anaconda3/etc/profile.d/conda.sh && \
  conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && \
  tmux new-session -d -s openseeker-YYYYMMDD-task-name \
  "CUDA_VISIBLE_DEVICES=0 PYTHONNOUSERSITE=1 python -m openseeker_factory.cli demo --count N --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/task-name 2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/task-name.log"'
```

## tmux Rules

`tmux` is the approved long-running process manager for this project.

Allowed operations:

- `tmux new-session`
- `tmux list-sessions`
- `tmux capture-pane`
- `tmux attach-session` if needed for inspection

Use one session per experiment.

Session naming format:

```text
openseeker-YYYYMMDD-task-name
```

Before launching, include the exact session name in the approval report. Do not kill a session without first reporting what it is and why it should be killed.

## Monitoring Rules

Approved monitoring methods:

- `nvidia-smi`
- `ps`
- `tmux list-sessions`
- `tmux capture-pane`
- `tail` on a specific log file under `/data/wzl/OpenSeeker-AgentDataFactory/logs`
- `ls` / `du` on approved result, checkpoint, and run directories
- TensorBoard only with event logs under `/data/wzl/OpenSeeker-AgentDataFactory/logs`, `/data/wzl/OpenSeeker-AgentDataFactory/results`, `/data/wzl/OpenSeeker-AgentDataFactory/runs`, or approved subdirectories

Example monitoring:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 '\
  nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader && \
  tmux list-sessions && \
  tail -n 80 /data/wzl/OpenSeeker-AgentDataFactory/logs/task-name.log && \
  ls -lah /data/wzl/OpenSeeker-AgentDataFactory/results/task-name'
```

When reporting progress:

- show raw command output first
- then provide a short interpretation

Never claim a run is healthy without checking actual log output.

## Experiment Record Rules

After every experiment completes, record the effective information needed for future continuation, including:

- experiment goal and exact command or launcher
- repo, branch, commit, environment, GPU selection, and key runtime settings
- data paths, checkpoint paths, log paths, result paths, and run paths
- final status, metrics, errors, warnings, and relevant raw log excerpts
- analysis, conclusions, open risks, and next-step recommendations

Every completed experiment must be recorded locally under `D:\resume\Data synthesis\docs\experiments` before treating the experiment as complete. A remote `EXPERIMENT_RECORD.md` is allowed and encouraged, but it does not replace the required local record.

The local record must include the raw result summary, the exact commands used, links or paths to logs/results/checkpoints, observed metrics, failure notes if any, analysis of what the result means, and concrete next-step thoughts for the resume project.

Suggested record locations:

```bash
/data/wzl/OpenSeeker-AgentDataFactory/results/<task-name>/EXPERIMENT_RECORD.md
D:\resume\Data synthesis\docs\experiments\<task-name>.md
```

## Stop Rules

Allowed stop behavior:

- identify the exact `tmux` session
- identify the exact process or command being stopped
- report the reason
- wait for user approval before stopping unless the user already explicitly asked to stop it

Default stop command is intentionally non-destructive:

```bash
tmux list-sessions && echo 'Stop requires user approval for the exact openseeker-* session before running tmux kill-session.'
```

## Failure Rules

For sync, install, smoke test, dry run, launch, or monitoring failures:

- retry automatically at most once
- if the second attempt fails, stop and report
- include the exact failing command
- include the exact stderr or log excerpt
- do not silently change system config
- do not silently change SSH config
- do not silently switch package indexes, mirrors, models, datasets, or GPUs unless the user approves or the run config explicitly permits it

If model or dataset download fails once on the default Hugging Face endpoint, retry only when the user approves an explicit mirror such as `HF_ENDPOINT=https://hf-mirror.com`, and record that mirror in the log or approval payload.

## Forbidden Operations

Never do any of the following:

- `sudo`
- `su`
- `apt`
- `yum`
- `dnf`
- `reboot`
- `shutdown`
- `systemctl`
- `service`
- editing `.bashrc`
- editing `~/.ssh/config`
- changing the system CUDA driver
- installing into `base`
- global `pip install`
- broad deletion commands
- deleting `data`
- deleting `logs`
- deleting `checkpoints`
- deleting `results`
- deleting `runs`
- starting 4-GPU jobs without explicit approval
- starting real generation, SFT, or RL jobs without a successful smoke test
- starting real generation, SFT, or RL jobs without an approval report

## Default Command Patterns

Use explicit `cd` and explicit conda initialization in remote commands.

Example remote shell pattern:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 '\
  cd /data/wzl/OpenSeeker-AgentDataFactory/repo && \
  source /home/user/anaconda3/etc/profile.d/conda.sh && \
  conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && \
  PYTHONNOUSERSITE=1 python --version'
```

Example GPU check:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 '\
  nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader'
```

## Decision Rule

If an action is useful but not explicitly allowed here, do not assume permission. Stop and ask.
