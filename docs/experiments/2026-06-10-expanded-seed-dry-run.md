# Expanded Seed Dry Run

## Metadata

- Experiment name: expanded-seed-dry-run-20260610
- Date: 2026-06-10
- Goal: Verify the expanded Wikidata-style seed bank and confirm it can drive deterministic generation on the remote server.
- Status: success
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Code commit: `b3e99a4` locally, deployed to remote by narrow file sync
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- Number of GPUs: 0
- Teacher backend: none
- Teacher concurrency: `4`

## Commands

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m pytest
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli build-seeds \
  --out-file /data/wzl/OpenSeeker-AgentDataFactory/results/expanded-seed-build/wikidata_seed_expanded.jsonl
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 12 \
  --seed-file data/seeds/wikidata_seed_expanded.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/expanded-seed-dry-run \
  --teacher-concurrency 4
```

## Paths

- Expanded seed artifact: `data/seeds/wikidata_seed_expanded.jsonl`
- Remote build output: `/data/wzl/OpenSeeker-AgentDataFactory/results/expanded-seed-build/wikidata_seed_expanded.jsonl`
- Dry-run results: `/data/wzl/OpenSeeker-AgentDataFactory/results/expanded-seed-dry-run`
- Raw generations: `/data/wzl/OpenSeeker-AgentDataFactory/results/expanded-seed-dry-run/raw_generations.jsonl`
- Trace path: `/data/wzl/OpenSeeker-AgentDataFactory/results/expanded-seed-dry-run/trace.jsonl`
- Checkpoint path: not applicable

## Raw Result Summary

```text
24 passed in 9.47s
OpenSeeker seed build complete: rows=120 out_file=/data/wzl/OpenSeeker-AgentDataFactory/results/expanded-seed-build/wikidata_seed_expanded.jsonl
120 /data/wzl/OpenSeeker-AgentDataFactory/results/expanded-seed-build/wikidata_seed_expanded.jsonl
OpenSeeker AgentDataFactory generation complete: accepted=12 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/expanded-seed-dry-run
```

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
12,12,0,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,0,
```

Output files:

```text
wikidata_seed_expanded.jsonl 120 lines
raw_generations.jsonl 12 lines
```

## Notes and Analysis

- The seed bank now expands from 3 demo rows to 120 rows: 40 entities across 3 task types.
- The expanded seed file can be regenerated with `python -m openseeker_factory.cli build-seeds`.
- The deterministic dry run accepted all 12 checked samples and preserved streaming raw generations.
- This should reduce duplicate pressure in the next DeepSeek teacher run, but 120 seeds is still a pilot-scale seed bank rather than a full Wikidata crawl.

## Next Step Thoughts

- Run a DeepSeek teacher pilot against `data/seeds/wikidata_seed_expanded.jsonl`, for example 500 or 1000 samples with `--teacher-concurrency 100`.
- Compare duplicate rewrite rate against the old 3-seed runs.
- Later, replace this curated fact bank with a Wikidata query/export path for thousands of factual seeds.
