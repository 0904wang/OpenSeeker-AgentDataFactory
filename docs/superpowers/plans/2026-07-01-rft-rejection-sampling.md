# RFT Rejection Sampling Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reproducible RFT/ReST-EM stage that samples multiple trajectories, filters them with deterministic verifiers, exports accepted SFT data, and records pass-rate/diversity metrics.

**Architecture:** Keep model sampling and verifier filtering separate. Sampling writes candidate predictions JSONL; filtering scores candidates against gold OpenSeeker samples and exports accepted trajectories in samples/SFT/RL/summary formats.

**Tech Stack:** Python 3.10, pytest, Transformers/PEFT for remote sampling, existing OpenSeeker schema/evaluation utilities.

---

## Chunk 1: RFT Filter And Export

### Task 1: Candidate Filtering

**Files:**
- Create: `openseeker_factory/rft.py`
- Modify: `openseeker_factory/cli.py`
- Test: `tests/test_rft.py`

- [ ] **Step 1: Write failing tests for verifier-gated RFT export.**
- [ ] **Step 2: Run the focused test and confirm it fails because the RFT module/CLI does not exist.**
- [ ] **Step 3: Implement minimal candidate loading, scoring, accepted sample conversion, SFT/RL export, and summary metrics.**
- [ ] **Step 4: Run focused tests until green.**

### Task 2: Model Sampling Entry Point

**Files:**
- Modify: `openseeker_factory/rft.py`
- Modify: `openseeker_factory/cli.py`
- Test: `tests/test_rft.py`

- [ ] **Step 1: Write failing tests for sampling argument validation and candidate row shape helpers.**
- [ ] **Step 2: Implement `sample-rft-candidates` CLI plumbing and reusable sampled-generation helper.**
- [ ] **Step 3: Run focused tests and full pytest.**

## Chunk 2: Remote Experiment Readiness

### Task 3: Launchers And Documentation

**Files:**
- Create: `runs/launch_sft_mixed_v3_v4_v5blind_v6blindtoolchoice_2p4k_gpu0125_restore_a0.sh`
- Create: `docs/experiments/2026-07-01-rft-stage-a-plan.md`

- [ ] **Step 1: Add restore-A0 launcher matching the previous best 2.4k SFT config.**
- [ ] **Step 2: Record the Stage A plan and required approval gates.**
- [ ] **Step 3: Run local tests and remote smoke test before any real launch.**
