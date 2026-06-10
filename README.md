# OpenSeeker AgentDataFactory

OpenSeeker AgentDataFactory is a resume-oriented but runnable synthetic data project for LLM agents. It upgrades the earlier OpenSeeker data synthesis experience from a small multi-hop QA pipeline into a verifiable data factory for:

- multi-hop QA
- tool-use QA
- noisy-context retrieval QA
- ReAct-style trajectories
- verifier-based filtering
- SFT and reward-format export

The local implementation is intentionally small and deterministic. It proves the project contract, schema, exports, and verification loop before moving long-running generation or training to the remote GPU server.

## Current Status

Verified locally:

- `seed_expand`
- `evolve_task`
- `generate_trajectory`
- `verify_and_filter`
- JSONL sample export
- Agent SFT conversation export
- RL reward-format export
- trace JSONL and summary CSV export
- CLI demo run
- pytest coverage for schema, pipeline, exports, and CLI

Not yet claimed as completed:

- 20k / 50k synthetic data generation
- Qwen 7B / 14B SFT results
- verl / GRPO results
- 4xRTX 5090 throughput numbers
- downstream benchmark improvements

Those belong to the experiment roadmap and must be recorded under `docs/experiments/` after they actually run.

## Research Basis

The project design borrows from three open-source lines:

| Category | Projects | What to borrow |
| --- | --- | --- |
| Instruction synthesis | Stanford Alpaca, Self-Instruct, WizardLM, Magpie | seed instruction generation, task evolution, complexity expansion |
| Data pipelines | Distilabel, Bespoke Curator, Meta Synthetic Data Kit, DataDreamer | structured outputs, batch generation, retry/cache, local model backends |
| Agent/verifiable data | CAMEL, ToolBench, AgentTuning, OpenThoughts, Loong | tool-use trajectories, verifier filtering, reasoning data curation |

See `docs/research/github-synthetic-data-projects.md` for the curated list and resume relevance.

## Install

```bash
python -m pip install -e .
python -m pip install pytest
```

The current package has no runtime third-party dependency. `pytest` is only needed for tests.

## Run Tests

```bash
python -m pytest
```

Expected local result at the time of writing:

```text
7 passed
```

## Run Demo

```bash
python -m openseeker_factory.cli demo --count 3 --out-dir outputs/demo
```

Expected files:

```text
outputs/demo/
  samples.jsonl
  sft_conversations.jsonl
  rl_rewards.jsonl
  trace.jsonl
  summary.csv
```

## Generate From Seed File

Use `generate` for baseline-scale runs from a JSONL seed file:

```bash
python -m openseeker_factory.cli generate \
  --count 5000 \
  --seed-file data/seeds/wikidata_seed_sample.jsonl \
  --out-dir outputs/baseline-5k
```

`data/seeds/wikidata_seed_sample.jsonl` is a small format example. For a real 5k baseline, replace it with a Wikidata-derived seed file and keep the same schema.

## Optional Teacher Backend

`generate` can also draft tasks through an OpenAI-compatible endpoint. For DeepSeek official API:

```bash
python -m openseeker_factory.cli generate \
  --count 10 \
  --seed-file data/seeds/wikidata_seed_sample.jsonl \
  --out-dir outputs/teacher-demo \
  --teacher-backend openai-compatible \
  --teacher-base-url https://api.deepseek.com \
  --teacher-model deepseek-v4-pro \
  --teacher-api-key-env DEEPSEEK_API_KEY
```

Set the API key in the environment variable named by `--teacher-api-key-env`.

## Data Schema

Every sample uses this JSONL contract:

```text
id
task_type
question
answer
gold_evidence
tool_calls
trajectory
verifier_result
difficulty
source
quality_score
```

Allowed `task_type` values:

- `multi_hop_qa`
- `tool_use_qa`
- `noisy_context_retrieval_qa`

Verifier checks currently include:

- `not_duplicate`
- `answer_supported`
- `evidence_coverage`
- `tool_success`
- `trajectory_valid`

## Seed File Schema

Each seed JSONL row must contain:

```text
id
task_type
entity
relation
intermediate
answer
evidence
noisy_context
```

`noisy_context` may be an empty list. The generator repeats seeds as needed and creates deterministic question variants so duplicate filtering can remain strict.

## Remote Experiments

Remote execution is governed by `AGENTS.md` and the `safe-remote-experiments` contract.

Remote root:

```bash
/data/wzl/OpenSeeker-AgentDataFactory
```

Approved long-running process manager:

```text
tmux
```

Before any real remote run:

1. Run preflight checks.
2. Run a smoke test and dry run.
3. Report exact command, GPUs, tmux session, log path, results path, and checkpoint path if applicable.
4. Wait for user approval.
5. Record completed experiments locally under `docs/experiments/`.

First baseline command candidate:

```bash
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 5000 \
  --seed-file data/seeds/wikidata_seed_sample.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/baseline-5k
```

This candidate still requires user approval before remote execution.

## Resume Boundary

Use the current project in a resume only as a verified system scaffold until remote experiments are run. Do not claim 20k/50k data scale, 4x5090 throughput, Qwen SFT improvements, or GRPO gains until there is a local experiment record with evidence.
