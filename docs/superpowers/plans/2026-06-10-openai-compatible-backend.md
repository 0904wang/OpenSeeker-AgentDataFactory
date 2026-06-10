# OpenAI-Compatible Backend Hook Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a tested OpenAI-compatible teacher backend hook so the factory can use vLLM or any `/v1/chat/completions` endpoint for task drafting while keeping deterministic verification.

**Architecture:** Keep the existing deterministic pipeline as the default baseline. Add a small `ChatBackend` boundary and an `OpenAICompatibleChatBackend` implemented with the Python standard library, then let `AgentDataFactory` optionally use that backend to draft evolved tasks. The deterministic verifier remains the quality gate.

**Tech Stack:** Python 3.10, stdlib `urllib`, dataclasses, pytest, local fake HTTP server for tests.

---

## Chunk 1: Backend Boundary

**Files:**
- Create: `openseeker_factory/backends.py`
- Test: `tests/test_backends.py`

- [ ] Write a failing test that starts a local fake `/v1/chat/completions` server and asserts `OpenAICompatibleChatBackend.complete_json(...)` returns parsed JSON content.
- [ ] Run `python -m pytest tests/test_backends.py -q` and verify it fails because the backend module does not exist.
- [ ] Implement `ChatBackend` protocol and `OpenAICompatibleChatBackend` using stdlib `urllib.request`.
- [ ] Re-run `python -m pytest tests/test_backends.py -q` and verify it passes.

## Chunk 2: Pipeline Hook

**Files:**
- Modify: `openseeker_factory/pipeline.py`
- Test: `tests/test_pipeline.py`

- [ ] Write a failing test with a fake backend that returns a teacher draft overriding question, trajectory, and difficulty.
- [ ] Run the focused test and verify it fails because `AgentDataFactory` does not accept a backend.
- [ ] Add optional `teacher_backend` to `AgentDataFactory` and use it in `evolve_task` / `generate_trajectory` without changing default deterministic behavior.
- [ ] Re-run focused tests and the full pipeline tests.

## Chunk 3: CLI Integration

**Files:**
- Modify: `openseeker_factory/cli.py`
- Test: `tests/test_cli.py`
- Modify: `README.md`

- [ ] Write a failing CLI test for `generate --teacher-backend openai-compatible --teacher-base-url ... --teacher-model ...`.
- [ ] Implement CLI flags and backend construction.
- [ ] Document the optional OpenAI-compatible path and required environment variables.
- [ ] Run `python -m pytest`.

## Chunk 4: Remote Readiness

**Files:**
- Modify: `docs/remote-approval-packet.md`

- [ ] Add a small LLM dry-run approval packet that uses an OpenAI-compatible endpoint and writes to a timestamped result directory.
- [ ] Commit, push, sync the remote repo with `git pull --ff-only` or local `origin/main` fast-forward if GitHub HTTPS is flaky.
