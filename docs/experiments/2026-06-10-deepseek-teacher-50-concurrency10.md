# DeepSeek Teacher 50 Concurrency10

## Metadata

- Experiment name: deepseek-teacher-50-concurrency10-20260610
- Date: 2026-06-10
- Goal: Benchmark concurrent DeepSeek-backed teacher generation after adding `--teacher-concurrency`.
- Status: success
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Branch: `main`
- Code commit: `50ba94e` locally, deployed to remote by narrow file sync because GitHub HTTPS push/pull was unavailable
- Remote base commit: `7b64c03`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- Number of GPUs: 0
- tmux session: `openseeker-20260610-deepseek-teacher-50-concurrency10`
- Model: `deepseek-v4-pro`
- Base URL: `https://api.deepseek.com`
- Teacher concurrency: `10`

## Commands

The API key was injected once through a FIFO read by the tmux child process. It was not written to repo files, experiment records, logs, or the launch command.

```bash
tmux new-session -d -s openseeker-20260610-deepseek-teacher-50-concurrency10 \
  "bash -lc 'read -r DEEPSEEK_API_KEY < /data/wzl/OpenSeeker-AgentDataFactory/runs/deepseek-teacher-50-concurrency10-20260610.key.fifo; export DEEPSEEK_API_KEY; cd /data/wzl/OpenSeeker-AgentDataFactory/repo && source /home/user/anaconda3/etc/profile.d/conda.sh && conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate --count 50 --seed-file data/seeds/wikidata_seed_sample.jsonl --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-50-concurrency10-20260610 --teacher-backend openai-compatible --teacher-base-url https://api.deepseek.com --teacher-model deepseek-v4-pro --teacher-api-key-env DEEPSEEK_API_KEY --teacher-timeout-s 60 --teacher-concurrency 10 2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-50-concurrency10-20260610.log'"
```

## Paths

- Log path: `/data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-50-concurrency10-20260610.log`
- Results path: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-50-concurrency10-20260610`
- Samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-50-concurrency10-20260610/samples.jsonl`
- SFT export: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-50-concurrency10-20260610/sft_conversations.jsonl`
- RL reward export: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-50-concurrency10-20260610/rl_rewards.jsonl`
- Trace path: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-50-concurrency10-20260610/trace.jsonl`
- Checkpoint path: not applicable
- Run path: not applicable

## Raw Result Summary

```text
OpenSeeker AgentDataFactory generation complete: accepted=50 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-50-concurrency10-20260610
```

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
50,50,0,1.0,1.0,1.0,1.0,1.0,50,50,0,0.0,0,2,
```

Output files:

```text
rl_rewards.jsonl 50 lines
samples.jsonl 50 lines
sft_conversations.jsonl 50 lines
trace.jsonl 50 lines
```

Trace audit:

```text
rows 50
accepted 50
rejected 0
teacher_errors 0
difficulty medium 32, easy 13, hard 5
accepted_task_type tool_use_qa 17, multi_hop_qa 17, noisy_context_retrieval_qa 16
duplicate_question_rewritten 18
teacher_trajectory_repaired 0
teacher_difficulty_normalized 2
```

Example accepted samples:

```text
wikidata-ada-1 score=1.0 difficulty=medium question=Which country has as its capital the city where Ada Lovelace was born?
wikidata-curie-2 score=1.0 difficulty=easy question=Which country is Marie Curie's birthplace, Warsaw, located in?
wikidata-turing-3 score=1.0 difficulty=medium question=In which country was Alan Turing born?
```

## Comparison Against Serial 50-Sample Run

- Serial 50 anti-dup run: about 22 minutes, 50 accepted, 0 rejected, 0 fallback.
- Concurrent 50 anti-dup run with concurrency 10: about 3 minutes, 50 accepted, 0 rejected, 0 fallback.
- Throughput improved by roughly 7x without hurting verifier metrics in this small benchmark.

## Notes and Analysis

- `--teacher-concurrency 10` is stable for a 50-sample benchmark with the current DeepSeek endpoint.
- Progress logs are completion-order based, so sample ids appear out of order while progress counts remain monotonic.
- Final exported artifacts remain ordered by original seed index because the pipeline reorders completed futures before verification/export.
- This confirms that API latency, not local CPU or GPU, was the bottleneck in previous serial runs.
- The next scaling blocker is not request concurrency; it is lack of streaming JSONL writes and limited seed diversity.

## Next Step Thoughts

- Run a 200-sample benchmark with `--teacher-concurrency 10` or `20` to validate stability at a higher count.
- Implement streaming trace/sample writes before 1000+ runs so partial results survive interruptions.
- Expand the seed set before using generated data for training, because duplicate rewrites are still frequent.
