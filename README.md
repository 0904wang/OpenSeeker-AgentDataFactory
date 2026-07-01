# OpenSeeker AgentDataFactory

OpenSeeker AgentDataFactory is a resume-oriented but runnable synthetic data project for LLM agents. It upgrades the earlier OpenSeeker data synthesis experience from a small multi-hop QA pipeline into a verifiable data factory for:

- multi-hop QA
- tool-use QA
- noisy-context retrieval QA
- ReAct-style trajectories
- verifier-based filtering
- SFT and reward-format export

The implementation is intentionally compact and reproducible. It now covers the full experiment loop from deterministic data synthesis to remote LoRA SFT and heldout evaluation on a shared GPU server.

## Current Status

Verified:

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
- remote safety workflow with preflight, narrow sync, tmux launch, logs, checkpoints, and local experiment records
- Qwen3-8B LoRA SFT on mixed OpenSeeker synthetic data
- verifier-filtered RFT / ReST-EM continued SFT from a restored SFT checkpoint
- heldout evaluation with answer, tool-call, trajectory, hallucination, and observation-faithfulness metrics

Current best recorded experiment:

```text
Model: Qwen3-8B + LoRA
Base data: 2.4k mixed OpenSeeker SFT rows
RFT data: 1,095 verifier-passing changed trajectories retained from 9.6k sampled candidates
Final data: 3.5k SFT rows = 2.4k base + 1,095 changed RFT rows
RFT pass rate: 9,429 / 9,600 = 0.9822
Continued SFT: 2 GPUs, 1 epoch
Checkpoint: /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-3p5k-mixed-v3-v4-v5blind-v6-rftchanged-round1-20260701
```

Heldout results:

| Adapter | Heldout | Failures | Exact | Tool success | Observation faithfulness | Trajectory valid | Hallucination |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2k mixed v3/v4/v5blind | v4 heldout200 | 0/200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| 2k mixed v3/v4/v5blind | v5 blind-hard heldout200 | 0/200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| 2k mixed v3/v4/v5blind | v6 blind tool-choice heldout200 | 11/200 | 1.000 | 1.000 | 0.945 | 1.000 | 0.000 |
| 2.4k mixed v3/v4/v5blind/v6 A0 | v4 heldout200 | 0/200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| 2.4k mixed v3/v4/v5blind/v6 A0 | v5 blind-hard heldout200 | 0/200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| 2.4k mixed v3/v4/v5blind/v6 A0 | v6 blind tool-choice heldout200 | 3/200 | 1.000 | 1.000 | 0.985 | 1.000 | 0.000 |
| 3.5k SFT + RFT changed round1 | v4 heldout200 | 0/200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| 3.5k SFT + RFT changed round1 | v5 blind-hard heldout200 | 0/200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| 3.5k SFT + RFT changed round1 | v6 blind tool-choice heldout200 | 0/200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |

The v6 loop is the main project milestone: a harder heldout exposed observation-level evidence drift, targeted v6 synthetic data reduced failures from 11/200 to 3/200, and verifier-filtered RFT Round 1 removed the remaining 3/200 failures without regressing v4/v5.

Not claimed as completed:

- 20k / 50k synthetic data generation
- verl / GRPO results
- 4xRTX 5090 throughput numbers
- broad external benchmark improvements

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
68 passed
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

For remote teacher generation, prefer batched/resumable output instead of one large single-shot run:

```bash
python -m openseeker_factory.cli generate \
  --count 1000 \
  --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_expanded.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-batch50-c50 \
  --strategy magpie_self_instruct \
  --teacher-backend openai-compatible \
  --teacher-base-url https://api.deepseek.com \
  --teacher-model deepseek-v4-pro \
  --teacher-api-key-env DEEPSEEK_API_KEY \
  --teacher-timeout-s 60 \
  --teacher-concurrency 50 \
  --batch-size 50 \
  --resume
```

Batch mode appends raw teacher generations as they finish and refreshes `samples.jsonl`, `sft_conversations.jsonl`, `rl_rewards.jsonl`, `trace.jsonl`, and `summary.csv` after each completed batch. `--resume` loads `raw_generations.jsonl` and fills missing `seed_id` values, which is safer than resuming by line count when high-concurrency requests finish out of order.

### Canonical-v4 Evidence-Conditioned Data

Use `--data-version canonical-v4` when the goal is to train observation-faithful ReAct traces. Canonical-v4 keeps the same schema and canonical `P19` / `P17` tool calls, but augments each question with explicit lookup results:

```text
Available lookup observations:
- wikidata_lookup[Ada Lovelace, P19] -> London
- wikidata_lookup[London, P17] -> United Kingdom

Use these lookup observations exactly when writing Observation lines.
```

The SFT export also strengthens the system message so `Observation:` lines must copy the provided lookup observation values exactly instead of using memorized or localized facts. This is meant to target failure modes such as `England` vs `United Kingdom`, historical aliases, spelling variants, and noisy context leakage.

Example:

```bash
python -m openseeker_factory.cli generate \
  --count 1000 \
  --seed-file data/seeds/wikidata_seed_expanded.jsonl \
  --out-dir outputs/canonical-v4-1k \
  --data-version canonical-v4 \
  --batch-size 100 \
  --resume
```

### Canonical-v6 Blind Tool-choice Data

Use `--data-version canonical-v6-blind-tool-choice-hard` for the current hardest deterministic split. It withholds the explicit lookup observation block, visible `P19` / `P17` relation IDs, `wikidata_lookup[entity, ...]` scaffolding, and `->` lookup-result hints from the user prompt.

Instead, the prompt asks the model to choose relevant lookup intents from natural-language candidates with distractors:

```text
Tool choice challenge:
- Write a concise ReAct trace with the lookup tool when needed.
- Decide which lookup intents are relevant; some listed intents are distractors.
- Do not use nationality, citizenship, residence, award, or workplace clues as the final country.
- The final answer must be the country supported by the birthplace location chain.

Candidate lookup intents:
- birth location of the named person
- current country or sovereign state containing a place
- citizenship or nationality of the named person
- main workplace, residence, or career country
- field of work or award country
```

This split is useful when answer accuracy is already saturated and you need observation-level metrics to expose whether the model is faithfully reproducing the intermediate evidence.

### Canonical-v7 Relation-diverse Data

Use `--data-version canonical-v7-relation-diverse` when v4/v5/v6 are saturated and the next question is whether the model generalizes beyond the birthplace-to-country path family. v7 keeps the blind tool-choice structure from v6 but adds relation profiles:

| Relation profile | First lookup | Second lookup | Target |
| --- | --- | --- | --- |
| `birthplace_country` | person -> birthplace | place -> country | country of the birthplace |
| `education_country` | person -> education institution | institution -> country | country of the education institution |
| `employer_country` | person -> employer | organization -> country | country of the employer |
| `award_country` | person -> award | award -> country | country associated with the award |

The user prompt hides property IDs such as `P19`, `P69`, `P108`, `P166`, and `P17`; it only exposes natural-language candidate lookup intents plus distractors.

Build a relation-diverse seed file:

```bash
python -m openseeker_factory.cli build-seeds \
  --relation-diverse \
  --out-file outputs/v7-relation-diverse-seeds.jsonl
```

Generate v7 samples:

```bash
python -m openseeker_factory.cli generate \
  --count 200 \
  --seed-file outputs/v7-relation-diverse-seeds.jsonl \
  --out-dir outputs/v7-relation-diverse-heldout200 \
  --data-version canonical-v7-relation-diverse
```

Local smoke status: 8 generated, 8 accepted, no property IDs or `wikidata_lookup[...]` templates leaked into questions. Remote heldout generation and model evaluation still need a separate approved launch.

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

## Evaluate Model Outputs

Use `evaluate-model` to score a base model, a LoRA adapter, or an existing prediction file against OpenSeeker samples:

```bash
python -m openseeker_factory.cli evaluate-model \
  --samples outputs/demo/samples.jsonl \
  --prediction-file outputs/demo/predictions.jsonl \
  --model-label fake-model \
  --out-dir outputs/eval
```

The evaluator keeps strict `exact_match_rate` for resume-safe reporting and also writes `canonical_match_rate` for country/region aliases such as `England` or `Scotland` mapping to `United Kingdom`. Prediction rows include `error_bucket`; summary CSV files include stable bucket rates for:

```text
correct
canonical_alias_match
missing_final
trajectory_format_error
tool_coverage_gap
supported_but_wrong_answer
unsupported_wrong_answer
```

For tool-use scoring, query matching normalizes punctuation, initials, and diacritics so equivalent calls such as `CV Raman` vs `C. V. Raman` and `Würzburg` vs `Wurzburg` do not become artificial tool-coverage failures. Model evaluation prompts also require at most two `wikidata_lookup` calls and a final line in the form `Final: <country>`.

The evaluator also reports `observation_faithfulness_rate` and `observation_coverage_avg`. These metrics check whether the `Observation:` text following a matched tool call contains the expected gold tool result, catching cases where a model uses the right `P19/P17` action syntax but fills the observation with unsupported memorized or localized facts.

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
- `evidence_faithfulness`
- `tool_success`
- `trajectory_valid`

`evidence_faithfulness` checks that the generated trajectory mentions the expected tool results, including the seed's intermediate birthplace and final country. This catches cases where a model answers the country correctly while drifting to an unsupported intermediate location.

When a teacher backend drafts a ReAct trajectory, the factory validates both the required ReAct shape and this evidence-faithfulness constraint before export. Invalid or evidence-drifting teacher trajectories are repaired by falling back to the deterministic seed-derived trajectory, and the sample `source` records `teacher_trajectory_repaired=true` plus a `teacher_trajectory_repair_reason`.

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

Example generation command:

```bash
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 5000 \
  --seed-file data/seeds/wikidata_seed_sample.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/baseline-5k \
  --batch-size 100 \
  --resume
```

This candidate still requires user approval before remote execution.

## Experiment Records

Every completed remote experiment is recorded under `docs/experiments/`. Key records for the current milestone:

| Record | Purpose |
| --- | --- |
| `2026-06-13-canonical-v6-blind-tool-choice-hard-heldout.md` | v6 harder heldout design, generation, and leakage audit |
| `2026-06-13-qwen3-8b-mixed-v6-blind-tool-choice-heldout200-eval.md` | previous 2k mixed adapter on v6 heldout |
| `2026-06-13-qwen3-8b-mixed-v3-v4-v5blind-v6-data-smoke.md` | v6 train400 generation, 2.4k dataset build, smoke test |
| `2026-06-13-qwen3-8b-mixed-v3-v4-v5blind-v6-sft-gpu0125.md` | 4-GPU Qwen3-8B LoRA SFT run |
| `2026-06-13-qwen3-8b-mixed-v6trained-v6-heldout200-eval.md` | v6 heldout improvement after targeted SFT |
| `2026-06-13-qwen3-8b-mixed-v6trained-v4-v5-regression-eval.md` | v4/v5 regression evaluation |
| `2026-07-01-rft-round1-a0-k4-t1p0.md` | RFT Round 1 sampling audit from the restored A0 SFT checkpoint |
| `2026-07-01-sft-rft-round1-changed-3p5k-gpu06.md` | continued SFT on 1,095 changed RFT trajectories mixed with the 2.4k base |
| `2026-07-01-rftchanged-round1-v6-v4-v5-eval.md` | RFT changed-only round1 evaluation on v6 plus v4/v5 regression heldouts |
| `2026-07-01-canonical-v7-relation-diverse-local.md` | local v7 relation-diverse implementation and smoke audit |

## Limitations and Next Steps

Current limitations:

- The strongest verified loop still focuses on the birthplace-to-country path family.
- The current best scale is 3.5k SFT rows after RFT, not 20k/50k.
- The reported improvement is on the project heldout suite, not on broad public agent benchmarks.
- RFT / ReST-EM continued SFT is verified; verl / GRPO verifier-reward RL is not yet run.
- `canonical-v7-relation-diverse` is implemented and locally smoke-tested, but remote heldout evaluation is not yet run.

Recommended next technical step:

```text
remote canonical-v7 relation-diverse heldout200 generation and evaluation
```

The v7 split now adds relation paths beyond birthplace-to-country, including education institution to country, employer to country, and award to country. The next evidence-producing step is to generate a remote v7 heldout200 and evaluate the current RFT checkpoint against it.

## Resume Boundary

Resume wording may now claim the verified Qwen3-8B LoRA SFT loop, the RFT / ReST-EM rejection-sampling pass, and the v6 heldout improvement above. Do not claim 20k/50k data scale, GRPO gains, or broad benchmark improvements until there is a local experiment record with evidence.
