# Remote Read-Only Preflight

## Metadata

- Experiment name: remote-readonly-preflight
- Date: 2026-06-09
- Goal: Verify SSH reachability and remote resource state before any setup, sync, dry run, or launch.
- Status: partial success
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Branch: not checked because the remote project directory does not exist yet
- Commit: not checked
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory` not checked because workspace is missing
- GPU selection: none
- Number of GPUs: 0

## Commands

Preflight:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 'set -e; echo "REMOTE_PWD=$(pwd)"; echo "TARGET_STATUS"; if [ -e /data/wzl/OpenSeeker-AgentDataFactory ]; then ls -ld /data/wzl/OpenSeeker-AgentDataFactory; else echo "MISSING /data/wzl/OpenSeeker-AgentDataFactory"; fi; echo "SYMLINK_STATUS"; if [ -e /home/user/wzl/OpenSeeker-AgentDataFactory ]; then ls -ld /home/user/wzl/OpenSeeker-AgentDataFactory; else echo "MISSING /home/user/wzl/OpenSeeker-AgentDataFactory"; fi; echo "TMUX"; command -v tmux || true; echo "CONDA"; eval "$(/home/user/anaconda3/bin/conda shell.bash hook)"; conda --version; echo "GPU"; nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader; echo "DISK"; df -h /data || true'
```

Conda path check:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 'echo "CONDA_PATH_CHECK"; ls -ld /home/user/anaconda3 /home/user/anaconda3/bin /home/user/anaconda3/bin/conda 2>&1 || true; echo "KNOWN_CONDA_CANDIDATES"; ls -ld /home/user/miniconda3 /home/user/miniforge3 /opt/conda /data/wzl 2>&1 || true; echo "PATH_CONDA"; command -v conda 2>&1 || true'
```

Verified conda activation form:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 "bash -lc 'source /home/user/anaconda3/etc/profile.d/conda.sh && type conda && conda --version && command -v tmux && nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader && df -h /data'"
```

Dry run:

```bash
not run
```

Launch:

```bash
not run
```

Monitoring:

```bash
not applicable
```

## Paths

- Log path: not created
- Results path: not created
- Data path: not created
- Checkpoint path: not created
- Run path: not created
- Local copied artifacts: none

## Raw Result Summary

```text
REMOTE_PWD=/home/user
TARGET_STATUS
MISSING /data/wzl/OpenSeeker-AgentDataFactory
SYMLINK_STATUS
MISSING /home/user/wzl/OpenSeeker-AgentDataFactory
TMUX
/usr/bin/tmux
CONDA
bash: 行 1: conda: 未找到命令
```

```text
CONDA_PATH_CHECK
drwxrwxr-x 30 user user  4096  3月  1 12:39 /home/user/anaconda3
drwxrwxr-x  6 user user 36864  5月  8 04:32 /home/user/anaconda3/bin
-rwxrwxr-x  1 user user   521  3月  1 12:39 /home/user/anaconda3/bin/conda
KNOWN_CONDA_CANDIDATES
ls: 无法访问 '/home/user/miniconda3': 没有那个文件或目录
ls: 无法访问 '/home/user/miniforge3': 没有那个文件或目录
ls: 无法访问 '/opt/conda': 没有那个文件或目录
drwxrwxr-x 14 user user 4096  6月  8 02:55 /data/wzl
PATH_CONDA
```

```text
conda 是函数
conda 26.1.1
/usr/bin/tmux
0, 18 MiB, 32607 MiB
1, 18 MiB, 32607 MiB
2, 18 MiB, 32607 MiB
3, 22497 MiB, 32607 MiB
4, 18 MiB, 32607 MiB
5, 18 MiB, 32607 MiB
6, 18 MiB, 32607 MiB
7, 18 MiB, 32607 MiB
文件系统        大小  已用  可用 已用% 挂载点
/dev/sda1       7.3T  2.0T  4.9T   29% /data
```

## Metrics

| Metric | Value | Notes |
| --- | --- | --- |
| SSH reachable | yes | remote `pwd` returned `/home/user` |
| target workspace exists | no | `/data/wzl/OpenSeeker-AgentDataFactory` missing |
| symlink exists | no | `/home/user/wzl/OpenSeeker-AgentDataFactory` missing |
| tmux available | yes | `/usr/bin/tmux` |
| conda available | yes with `source /home/user/anaconda3/etc/profile.d/conda.sh` | `eval "$(... hook)"` failed under this SSH quoting path |
| GPU free candidates | 0, 1, 2, 4, 5, 6, 7 | each reported 18 MiB used |
| busy GPU | 3 | 22497 MiB used |
| `/data` free space | 4.9T | 29% used |

## Failures / Warnings

- The approved remote workspace does not exist yet.
- The symlink entrypoint does not exist yet.
- The original `eval "$(/home/user/anaconda3/bin/conda shell.bash hook)"` command pattern failed through the current local PowerShell-to-SSH quoting path.
- `AGENTS.md` was updated to use `source /home/user/anaconda3/etc/profile.d/conda.sh`, which was verified over SSH.
- No remote directory was created, no dependency was installed, no code was synced, and no experiment was launched.

## Analysis

What the result means for the data synthesis system:

- The lab server is reachable and has enough currently idle GPUs for the next dry-run stage.
- The remote project workspace still needs approved setup before code sync or dry run.
- Conda initialization should use the verified `conda.sh` profile script in future remote commands.

What it means for the resume project:

- Remote execution is feasible, but no remote result can be claimed yet.
- The immediate next evidence target is a successful remote dry run that reproduces the local contract validation.

## Next Steps

- Ask for approval before creating `/data/wzl/OpenSeeker-AgentDataFactory` and the symlink under `/home/user/wzl`.
- Decide the approved code sync method for `/data/wzl/OpenSeeker-AgentDataFactory/repo`.
- Create or activate `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`.
- Run the configured remote dry run after setup.
- Record the remote dry run locally before treating it as complete.

