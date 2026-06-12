# Canonical v3 Evaluation Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add observation-level evidence faithfulness metrics to evaluation, regenerate a clean heldout200 split, and re-evaluate existing Qwen3-8B LoRA adapters.

**Architecture:** Keep generation and evaluation responsibilities separate. `openseeker_factory.evaluation` will parse action-observation pairs and score observation faithfulness; the existing CLI remains unchanged except for richer output rows and summary CSVs.

**Tech Stack:** Python 3.10, pytest, existing OpenSeeker CLI, remote SSH/tmux workflow from `AGENTS.md`.

---

## Chunk 1: Local Observation-Faithfulness Metrics

### Task 1: Add failing tests for observation faithfulness

**Files:**
- Modify: `tests/test_evaluation.py`

- [ ] Add tests showing that a prediction with canonical actions but wrong observations gets full tool-call coverage but fails observation faithfulness.
- [ ] Add tests showing that correct observations pass observation faithfulness.
- [ ] Add summary assertions for `observation_faithfulness_rate` and `observation_coverage_avg`.
- [ ] Run `python -m pytest tests/test_evaluation.py -q` and verify the new tests fail before implementation.

### Task 2: Implement observation-faithfulness scoring

**Files:**
- Modify: `openseeker_factory/evaluation.py`

- [ ] Add an action-observation parser that pairs each parsed action with the following observation line.
- [ ] Reuse the existing action-to-tool-call matcher.
- [ ] Add `observation_coverage(prediction, tool_calls)` returning matched faithful observations divided by expected tool calls.
- [ ] Add row fields `observation_coverage` and `observation_faithfulness`.
- [ ] Add summary fields `observation_coverage_avg` and `observation_faithfulness_rate`.
- [ ] Run `python -m pytest tests/test_evaluation.py -q`.
- [ ] Run `python -m pytest -q`.

## Chunk 2: Remote Clean Heldout and Re-Evaluation

### Task 3: Sync local evaluator changes to remote

**Files:**
- Sync narrow files only:
  - `openseeker_factory/evaluation.py`
  - `tests/test_evaluation.py`

- [ ] Run remote `pytest tests/test_evaluation.py tests/test_cli.py`.
- [ ] Stop if remote tests fail twice.

### Task 4: Generate clean heldout200

**Remote output:**
- `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v3-clean`

- [ ] Run a remote dry run with count 3.
- [ ] Report exact heldout generation command.
- [ ] Generate 200 samples with current deterministic pipeline.
- [ ] Verify 200 rows, no rejected rows, no `Use synthesis round`, and summary metrics are 1.0 for evidence/tool/trajectory checks.

### Task 5: Re-evaluate existing adapters on clean heldout200

**Adapters:**
- cleaned1k: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-cleaned`
- canonical-v2 fixed1k: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v2-fixed`

- [ ] Run smoke eval for each adapter with limit 2 on GPU7.
- [ ] Report exact formal eval commands.
- [ ] Launch formal heldout200 evals under tmux or run directly if short, using GPU7.
- [ ] Collect summary CSVs and representative error buckets.

### Task 6: Record experiment locally

**Files:**
- Create: `docs/experiments/2026-06-12-canonical-v3-clean-heldout-and-reeval.md`

- [ ] Include commands, paths, raw summaries, new observation metrics, comparison table, errors, and next-step recommendation.
- [ ] Verify the local record exists and remote summaries are readable.
