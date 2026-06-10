# Remote Streaming Dry Run

## Metadata

- Experiment name: streaming-dry-run-20260610
- Date: 2026-06-10
- Goal: Verify that `generate` writes `raw_generations.jsonl` during generation on the remote server.
- Status: success
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Code commit: `73a5425` locally, deployed to remote by narrow file sync
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- Number of GPUs: 0
- Teacher backend: none
- Teacher concurrency: `3`

## Commands

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m pytest
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 6 \
  --seed-file data/seeds/wikidata_seed_sample.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/streaming-dry-run \
  --teacher-concurrency 3
```

## Paths

- Results path: `/data/wzl/OpenSeeker-AgentDataFactory/results/streaming-dry-run`
- Raw generations: `/data/wzl/OpenSeeker-AgentDataFactory/results/streaming-dry-run/raw_generations.jsonl`
- Trace path: `/data/wzl/OpenSeeker-AgentDataFactory/results/streaming-dry-run/trace.jsonl`
- Checkpoint path: not applicable

## Raw Result Summary

```text
21 passed in 4.47s
OpenSeeker AgentDataFactory generation complete: accepted=6 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/streaming-dry-run
```

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
6,6,0,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,0,
```

Output files:

```text
raw_generations.jsonl 6 lines
```

## Notes and Analysis

- The remote environment can run the streaming checkpoint code.
- `raw_generations.jsonl` is written with one line per completed generation.
- In concurrent mode, raw generations are written in completion order, while final exports are ordered after verifier processing.
- This provides partial-output protection for long teacher-backed runs.

## Next Step Thoughts

- Use this streaming path before attempting 1000+ teacher samples.
- The next data-quality bottleneck is seed diversity, not concurrency.
