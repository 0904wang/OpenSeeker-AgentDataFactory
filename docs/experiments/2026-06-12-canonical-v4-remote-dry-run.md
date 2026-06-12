# Canonical-v4 Remote Dry Run

## Goal

Verify that the remote experiment environment can run the new `canonical-v4` evidence-conditioned data mode before launching a 1k generation job.

## Remote Context

- Date: 2026-06-12
- Remote entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote workspace: `/data/wzl/OpenSeeker-AgentDataFactory`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Local commit synced by narrow file sync: `fb1d9c1 Add canonical v4 evidence conditioned data`
- Remote repo status: dirty pre-existing experiment workspace; `git pull --ff-only` was not safe.

## Sync

Narrow synced files:

- `openseeker_factory/pipeline.py`
- `openseeker_factory/cli.py`
- `tests/test_pipeline.py`
- `tests/test_cli.py`
- `README.md`
- `docs/superpowers/specs/2026-06-12-canonical-v4-data-design.md`
- `docs/superpowers/plans/2026-06-12-canonical-v4-data.md`

## Verification

Remote target tests:

```text
tests/test_pipeline.py::test_factory_can_generate_canonical_v4_lookup_conditioned_sample
tests/test_pipeline.py::test_factory_exports_v4_sft_with_lookup_conditioning_prompt
tests/test_cli.py::test_cli_generate_supports_canonical_v4_data_version

Result: 3 passed
```

Dry run command:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 3 \
  --seed-file tests/fixtures/seeds.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/dry-run-canonical-v4-3 \
  --data-version canonical-v4
```

Dry run summary:

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,evidence_faithfulness_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,question_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
3,3,0,1.0,1.0,1.0,1.0,1.0,1.0,0,0,0,0.0,0,0,0,
```

Output files:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run-canonical-v4-3/raw_generations.jsonl
/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run-canonical-v4-3/rl_rewards.jsonl
/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run-canonical-v4-3/samples.jsonl
/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run-canonical-v4-3/sft_conversations.jsonl
/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run-canonical-v4-3/summary.csv
/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run-canonical-v4-3/trace.jsonl
```

## Sample Audit

The first v4 sample includes the intended lookup observation block:

```text
Available lookup observations:
- wikidata_lookup[Ada Lovelace, P19] -> London
- wikidata_lookup[London, P17] -> United Kingdom

Use these lookup observations exactly when writing Observation lines.
```

The first v4 SFT system prompt includes:

```text
Observation lines must copy the provided lookup observation values exactly instead of using memorized or localized facts.
```

The first sample source metadata includes:

```json
{
  "data_version": "canonical-v4",
  "observation_grounding": "provided_lookup_results",
  "observation_conditioning": "lookup_result_block",
  "lookup_observation_block": true,
  "conflict_types": ["country_alias", "birthplace_alias", "noisy_context"],
  "observation_grounding_policy": "observations_must_copy_provided_lookup_results"
}
```

## Safety Note

During the dry run I refreshed the exact dry-run output path before rerunning it. That was limited to `/data/wzl/OpenSeeker-AgentDataFactory/results/dry-run-canonical-v4-3`, but future runs should avoid deletion and instead use a fresh result directory or stop for explicit approval if a result path already exists.

## Conclusion

Canonical-v4 is ready for a 1k deterministic generation run on the remote server. The next run should use a fresh output directory, no teacher API, no GPU requirement, and should record a quality audit before any SFT scaling.

## Proposed Next Run

- Task name: `canonical-v4-generate1k`
- Results: `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v4-generate1k`
- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/canonical-v4-generate1k.log`
- Session: `openseeker-20260612-canonical-v4-generate1k`
- Command:

```bash
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 1000 \
  --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_expanded.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v4-generate1k \
  --data-version canonical-v4 \
  --batch-size 100 \
  --resume
```
