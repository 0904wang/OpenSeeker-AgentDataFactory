# Canonical v7 Relation-diverse Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `canonical-v7-relation-diverse` as a harder heldout/data version that tests blind tool-choice generalization beyond the current birthplace-to-country path family.

**Architecture:** Keep the existing `SeedTask -> EvolvedTask -> AgentDataSample -> verifier/export` pipeline and introduce relation profiles inside `openseeker_factory/pipeline.py`. A profile maps a seed relation to the first-hop and second-hop lookup intents, property ids, prompt wording, distractors, and trajectory thoughts. Existing v3-v6 behavior remains unchanged.

**Tech Stack:** Python dataclasses, existing CLI argparse choices, pytest.

---

## Chunk 1: Relation-profile behavior

### Task 1: Add failing pipeline tests

**Files:**
- Modify: `tests/test_pipeline.py`
- Modify after red: `openseeker_factory/pipeline.py`

- [ ] Add a test that creates non-birthplace seeds for `education_country`, `employer_country`, and `award_country`.
- [ ] Assert `canonical-v7-relation-diverse` generates hard samples with hidden property IDs, source metadata `heldout_profile=v7-relation-diverse`, and a `relation_profile` per sample.
- [ ] Assert tool plans use relation-specific queries instead of always `P19/P17`.
- [ ] Run the targeted tests and verify they fail because v7 is unsupported.
- [ ] Add relation profile implementation and rerun targeted tests until green.

## Chunk 2: CLI support

### Task 2: Add failing CLI test and parser choice

**Files:**
- Modify: `tests/test_cli.py`
- Modify after red: `openseeker_factory/cli.py`

- [ ] Add a CLI test for `generate --data-version canonical-v7-relation-diverse`.
- [ ] Verify it fails with invalid choice.
- [ ] Add the new data version to CLI choices.
- [ ] Verify the CLI test passes.

## Chunk 3: Documentation and verification

### Task 3: Update docs and run full tests

**Files:**
- Modify: `README.md`
- Modify: `docs/experiment-roadmap.md`
- Add: `docs/experiments/2026-07-01-canonical-v7-relation-diverse-local.md`

- [ ] Document what v7 changes and why it should precede more RFT/RLVR work.
- [ ] Record local implementation and smoke evidence.
- [ ] Run `python -m pytest`.
- [ ] Commit and push the branch.
