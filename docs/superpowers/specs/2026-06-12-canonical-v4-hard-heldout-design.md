# Canonical-v4-hard Heldout Design

## Goal

Add a reproducible harder heldout profile for OpenSeeker AgentDataFactory that stresses verifier-backed trajectory quality after canonical-v4 answer accuracy saturated.

## Design

The project will add a new data version named `canonical-v4-hard`. It keeps the existing sample schema and exports, so downstream SFT/RL/evaluation code can consume it without format changes. Compared with `canonical-v4`, each hard sample will still include the correct lookup observation block, but the user prompt will add controlled traps:

- alias trap text containing plausible but non-canonical country or birthplace names
- a distractor lookup observation that must not be copied into the two required Observation lines
- stronger wording that requires copying only the relevant P19 and P17 lookup results

The source metadata will make the profile auditable:

- `data_version=canonical-v4-hard`
- `heldout_profile=v4-hard`
- `difficulty_factors=["alias_trap", "distractor_lookup", "noisy_context", "strict_observation_copy"]`
- `distractor_lookup_observation=true`

All generated samples use `difficulty="hard"`. Gold `tool_calls` remain the two canonical calls, so the existing evaluator continues measuring whether the model emits the required tool trajectory without needing evaluator changes.

## Scope

In scope:

- local TDD for generation behavior
- CLI support for `--data-version canonical-v4-hard`
- remote heldout generation under `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v4-hard`
- evaluation of base Qwen3-8B, canonical-v3 adapter, and canonical-v4 adapter on the same hard heldout
- local experiment record under `docs/experiments`

Out of scope:

- new SFT training
- new model download
- changing evaluator metric definitions
- using an external LLM teacher for hard heldout generation

## Success Criteria

- Local tests pass.
- Hard heldout generation accepts 200/200 samples with no duplicate questions.
- Every hard sample has the lookup block, a distractor lookup observation, hard difficulty, and v4-hard metadata.
- Evaluation produces comparable summary CSVs for base, v3, and v4.
- Results are recorded locally before the experiment is treated as complete.
