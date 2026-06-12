# Canonical-v4 Data Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an opt-in `canonical-v4` data mode that conditions samples on explicit lookup observation blocks to target observation faithfulness.

**Architecture:** Keep the existing schema and default v3 behavior. Thread a `data_version` option through `AgentDataFactory`, CLI `demo`, CLI `generate`, and export logic. In v4 mode, augment questions with a lookup observation block, update source metadata, and use a stronger SFT system prompt.

**Tech Stack:** Python 3.10, pytest, existing OpenSeeker factory CLI and deterministic pipeline.

---

## Chunk 1: Pipeline Data Version

### Task 1: Add v4 pipeline tests

**Files:**
- Modify: `tests/test_pipeline.py`

- [ ] Add a test proving default generation remains `canonical-v3` and does not include `Available lookup observations:`.
- [ ] Add a test constructing `AgentDataFactory.from_demo_knowledge_graph(data_version="canonical-v4")`, generating one accepted sample, and asserting:
  - `sample.source["data_version"] == "canonical-v4"`
  - question contains `Available lookup observations:`
  - question contains both expected `wikidata_lookup[...] -> ...` rows
  - verifier `observation_faithfulness` remains true
  - `lookup_observation_block` and `observation_conditioning` metadata exist.
- [ ] Run the v4 test and verify it fails before production code changes.

### Task 2: Implement data_version in pipeline

**Files:**
- Modify: `openseeker_factory/pipeline.py`

- [ ] Add a data version argument to `AgentDataFactory.__init__`, `from_demo_knowledge_graph`, and `from_seed_file`.
- [ ] Validate `data_version` is one of `canonical-v3` or `canonical-v4`.
- [ ] In `generate_trajectory`, keep current v3 metadata for v3 and set v4 metadata for v4.
- [ ] For v4 only, wrap `task.question` with a lookup observation block built from `task.tool_plan`.
- [ ] Ensure duplicate question rewrite still appends natural constraints after the v4 block without breaking entity alignment.
- [ ] Run targeted pipeline tests.

## Chunk 2: SFT Export and CLI

### Task 3: Add SFT export tests

**Files:**
- Modify: `tests/test_pipeline.py`

- [ ] Add a test exporting a v4 sample to SFT JSONL.
- [ ] Assert the system prompt mentions copying provided lookup observations exactly.
- [ ] Assert user content contains the lookup block.
- [ ] Verify v3 SFT prompt keeps the prior wording.

### Task 4: Add CLI data-version flag

**Files:**
- Modify: `openseeker_factory/cli.py`
- Modify: `tests/test_cli.py`

- [ ] Add `--data-version` to `demo` and `generate`.
- [ ] Thread the value into factory constructors.
- [ ] Add a CLI test that runs `generate --data-version canonical-v4` and checks `samples.jsonl` source metadata plus SFT user content.
- [ ] Run targeted CLI tests.

## Chunk 3: Documentation and Verification

### Task 5: Update README

**Files:**
- Modify: `README.md`

- [ ] Document `--data-version canonical-v4`.
- [ ] Explain v4's explicit lookup observation block and intended use.
- [ ] Update local expected pytest count if changed.

### Task 6: Verify and commit

**Files:**
- All touched files

- [ ] Run `python -m pytest -q`.
- [ ] Run a local v4 demo/generate smoke command and inspect JSONL.
- [ ] Commit with message `Add canonical v4 evidence-conditioned data`.
- [ ] Push to `origin main`.
