# Canonical v3 Data Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add canonical-v3 data annotations and SFT wording that explicitly train observation faithfulness, then generate and audit a 1k canonical-v3 dataset remotely.

**Architecture:** Keep the base sample JSONL schema backward-compatible by adding metadata to `source` and verifier checks instead of changing dataclasses. Strengthen the SFT system message and RL verifier metadata so downstream training can distinguish canonical tool syntax from observation grounding.

**Tech Stack:** Python 3.10, pytest, OpenSeeker CLI, existing SSH/tmux remote workflow.

---

## Chunk 1: Local Canonical-v3 Sample Metadata

### Task 1: Add failing tests

**Files:**
- Modify: `tests/test_pipeline.py`

- [ ] Assert accepted samples include verifier check `observation_faithfulness`.
- [ ] Assert accepted sample `source` includes `data_version=canonical-v3` and `observation_grounding=gold_tool_results`.
- [ ] Assert SFT system prompt explicitly says observations must match lookup evidence.
- [ ] Assert RL export includes `observation_faithfulness` in `verifier_checks`.
- [ ] Run `python -m pytest tests/test_pipeline.py -q` and confirm failures before implementation.

### Task 2: Implement metadata and prompt wording

**Files:**
- Modify: `openseeker_factory/pipeline.py`

- [ ] Add `observation_faithfulness` verifier check using the same expected-result logic as `evidence_faithfulness`.
- [ ] Add source metadata in `generate_trajectory`.
- [ ] Strengthen SFT system message without changing assistant target trajectory.
- [ ] Run `python -m pytest tests/test_pipeline.py -q`.
- [ ] Run `python -m pytest -q`.

## Chunk 2: Remote 1k Generation and Audit

### Task 3: Sync and test remotely

**Files:**
- Sync narrow files:
  - `openseeker_factory/pipeline.py`
  - `tests/test_pipeline.py`

- [ ] Run remote `python -m pytest tests/test_pipeline.py`.
- [ ] Stop if it fails twice.

### Task 4: Generate canonical-v3 1k

**Remote output:**
- `/data/wzl/OpenSeeker-AgentDataFactory/results/canonical-v3-generate1k`

- [ ] Run count=3 smoke.
- [ ] Generate count=1000 deterministic data with current seed file.
- [ ] Audit rows, task distribution, duplicate questions, P19/P17, round markers, verifier metrics, source tags, and SFT system prompt.

### Task 5: Record locally

**Files:**
- Create: `docs/experiments/2026-06-12-canonical-v3-generate1k.md`

- [ ] Include commands, output paths, summary metrics, audit numbers, risks, and next step recommendation.
