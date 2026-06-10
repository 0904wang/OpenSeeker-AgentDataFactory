# DeepSeek Teacher 100 Concurrency100

## Metadata

- Experiment name: deepseek-teacher-100-concurrency100-20260610
- Date: 2026-06-10
- Goal: Stress-test DeepSeek-backed teacher generation with `--teacher-concurrency 100`.
- Status: success
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Branch: `main`
- Code commit: `50ba94e` locally, deployed to remote by narrow file sync because remote GitHub HTTPS pull was unavailable
- Remote base commit: `7b64c03`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- Number of GPUs: 0
- tmux session: `openseeker-20260610-deepseek-teacher-100-concurrency100`
- Model: `deepseek-v4-pro`
- Base URL: `https://api.deepseek.com`
- Teacher concurrency: `100`

## Commands

The API key was injected once through a FIFO read by the tmux child process. It was not written to repo files, experiment records, logs, or the launch command.

```bash
tmux new-session -d -s openseeker-20260610-deepseek-teacher-100-concurrency100 \
  "bash -lc 'read -r DEEPSEEK_API_KEY < /data/wzl/OpenSeeker-AgentDataFactory/runs/deepseek-teacher-100-concurrency100-20260610.key.fifo; export DEEPSEEK_API_KEY; cd /data/wzl/OpenSeeker-AgentDataFactory/repo && source /home/user/anaconda3/etc/profile.d/conda.sh && conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate --count 100 --seed-file data/seeds/wikidata_seed_sample.jsonl --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-100-concurrency100-20260610 --teacher-backend openai-compatible --teacher-base-url https://api.deepseek.com --teacher-model deepseek-v4-pro --teacher-api-key-env DEEPSEEK_API_KEY --teacher-timeout-s 60 --teacher-concurrency 100 2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-100-concurrency100-20260610.log'"
```

## Paths

- Log path: `/data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-100-concurrency100-20260610.log`
- Results path: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-100-concurrency100-20260610`
- Samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-100-concurrency100-20260610/samples.jsonl`
- SFT export: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-100-concurrency100-20260610/sft_conversations.jsonl`
- RL reward export: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-100-concurrency100-20260610/rl_rewards.jsonl`
- Trace path: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-100-concurrency100-20260610/trace.jsonl`
- Checkpoint path: not applicable
- Run path: not applicable

## Raw Result Summary

```text
OpenSeeker AgentDataFactory generation complete: accepted=100 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-100-concurrency100-20260610
```

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
100,100,0,1.0,1.0,1.0,1.0,1.0,100,100,0,0.0,1,1,
```

Output files:

```text
rl_rewards.jsonl 100 lines
samples.jsonl 100 lines
sft_conversations.jsonl 100 lines
trace.jsonl 100 lines
```

Trace audit:

```text
rows 100
accepted 100
rejected 0
teacher_errors 0
difficulty medium 65, easy 25, hard 10
accepted_task_type multi_hop_qa 34, noisy_context_retrieval_qa 33, tool_use_qa 33
duplicate_question_rewritten 47
teacher_trajectory_repaired 1
teacher_difficulty_normalized 1
```

Example accepted samples:

```text
wikidata-ada-1 score=1.0 difficulty=medium question=Which country is the birthplace of Ada Lovelace located in?
wikidata-curie-2 score=1.0 difficulty=easy question=Marie Curie spent much of her career in Paris, but she was born in Warsaw. In which modern-day country is Warsaw located?
wikidata-turing-3 score=1.0 difficulty=easy question=What country was Alan Turing born in?
```

## Comparison Against Prior Throughput

- Serial 50 anti-dup run: about 22 minutes.
- Concurrent 50 run with concurrency 10: about 3 minutes.
- Concurrent 100 run with concurrency 100: about 2.5 minutes, with 100 accepted and zero fallback.
- The official model-side concurrency headroom appears sufficient for this scale; no API-limit failure was observed.

## Notes and Analysis

- CPU load was already high on the shared server, but this API-only job completed quickly and did not require GPU memory.
- The high concurrency mainly stressed outbound network/API latency, not local CPU.
- Progress logs are completion-order based, so sample ids appear out of order while progress counts stay monotonic.
- Final artifacts remain sorted by seed index because the pipeline reorders completed futures before verifier/export.
- This is a good scaling signal, but the current pipeline still writes artifacts only at the end.

## Next Step Thoughts

- Before 1000+ generation, implement streaming writes for trace/sample output so partial work survives interruption.
- After streaming is added, run a 1000-sample pilot with `--teacher-concurrency 100` or a staged concurrency sweep.
- Expand the seed set; 47/100 duplicate rewrites shows the current three-seed source is the bigger data-quality bottleneck.
