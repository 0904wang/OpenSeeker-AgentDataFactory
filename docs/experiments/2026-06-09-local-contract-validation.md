# Local Contract Validation

## Metadata

- Experiment name: local-contract-validation
- Date: 2026-06-09
- Goal: Validate the local OpenSeeker AgentDataFactory schema, pipeline, verifier, exports, and CLI demo before remote execution.
- Status: success
- Operator: Codex
- Remote host: not used
- Repo path: `D:\resume\Data synthesis`
- Branch: not a git repository at this path
- Commit: not available
- Conda env: local Python environment
- GPU selection: none
- Number of GPUs: 0

## Commands

Preflight:

```bash
Get-ChildItem -Force
```

Dry run:

```bash
python -m pytest
python -m openseeker_factory.cli demo --count 3 --out-dir outputs/local-contract-validation
```

Launch:

```bash
not applicable
```

Monitoring:

```bash
Get-Content outputs/local-contract-validation/summary.csv
Get-Content outputs/local-contract-validation/samples.jsonl -TotalCount 1
```

## Paths

- Log path: not applicable
- Results path: `D:\resume\Data synthesis\outputs\local-contract-validation`
- Data path: `D:\resume\Data synthesis\outputs\local-contract-validation\samples.jsonl`
- Checkpoint path: not applicable
- Run path: not applicable
- Local copied artifacts: not applicable

## Raw Result Summary

```text
.......                                                                  [100%]
7 passed in 0.14s

OpenSeeker AgentDataFactory demo complete: accepted=3 rejected=0 out_dir=outputs\local-contract-validation

total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,tool_success_rate,trajectory_valid_rate,manual_sample_pass_rate
3,3,0,1.0,1.0,1.0,1.0,1.0,
```

## Metrics

| Metric | Value | Notes |
| --- | --- | --- |
| total | 3 | demo samples only |
| accepted | 3 | deterministic demo verifier |
| rejected | 0 | no rejected sample in this demo |
| dedup_rate | 1.0 | no duplicate question |
| solvability_rate | 1.0 | answers supported by evidence |
| evidence_hit_rate | 1.0 | tool results appear in evidence |
| tool_success_rate | 1.0 | final answer appears in tool results |
| trajectory_valid_rate | 1.0 | ReAct trace includes thought/action/final |
| manual_sample_pass_rate | not measured | manual audit is for 5k+ runs |
| runtime | < 1 second for demo command | shell wall time was about 3.6 seconds including process startup |
| throughput | not meaningful | demo scale is too small |

## Failures / Warnings

- This validates the software contract only.
- It does not prove 20k / 50k generation quality.
- It does not include Qwen SFT, RL, or 4x5090 throughput.
- The workspace path is not a git repository, so branch and commit are unavailable for this local validation.

## Analysis

What the result means for the data synthesis system:

- The local package can generate all three target task types: multi-hop QA, tool-use QA, and noisy-context retrieval QA.
- The schema, verifier fields, SFT export, reward-format export, trace output, and summary output are all executable.
- The current verifier is deterministic and suitable for contract validation, but must be expanded before large-scale claims.

What it means for the resume project:

- It is now fair to describe the project as a runnable data factory scaffold with tested exports and verifier gating.
- It is not yet fair to claim large-scale sample counts, training improvements, or 4x5090 speedups.

## Next Steps

- Sync or clone the project into `/data/wzl/OpenSeeker-AgentDataFactory/repo` following `AGENTS.md`.
- Run remote preflight and remote dry run.
- Replace the demo knowledge graph with real Wikidata-derived seeds.
- Run a 5k baseline reproduction before attempting 20k generation.
- Add manual audit records before moving metrics into resume bullets.

