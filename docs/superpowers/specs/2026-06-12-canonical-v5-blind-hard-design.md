# Canonical-v5-blind-hard Heldout Design

## Goal

Add a harder evaluation-only heldout profile that does not expose the answer through `Available lookup observations`. This is intended to separate base Qwen3-8B from SFT adapters after canonical-v4-hard saturated.

## Design

The project will add a new data version:

```text
canonical-v5-blind-hard
```

It keeps the existing sample schema, including gold `tool_calls`, gold answer, verifier outputs, SFT export, RL export, and trace export. The important change is the user prompt:

- no `Available lookup observations` block
- no explicit `wikidata_lookup[entity, P19] -> birthplace` answer in the prompt
- includes noisy context and alias traps
- includes strict instructions to produce ReAct tool calls with P19 and P17
- asks the model to ignore distractor nationality / career / residence clues

The gold trajectory still contains the canonical two-step ReAct path:

```text
Action: wikidata_lookup[entity, P19]
Observation: birthplace
Action: wikidata_lookup[birthplace, P17]
Observation: country
Final: country
```

The evaluator can run unchanged because it scores model predictions against the sample's gold `tool_calls` and expected observations.

## Metadata

Every sample should include:

- `source.data_version=canonical-v5-blind-hard`
- `source.heldout_profile=v5-blind-hard`
- `source.observation_conditioning=blind_tool_generation`
- `source.lookup_observation_block=false`
- `source.distractor_lookup_observation=false`
- `source.difficulty_factors=["blind_observation_generation", "alias_trap", "noisy_context", "strict_tool_schema"]`
- `difficulty=hard`

## Scope

In scope:

- CLI support for `--data-version canonical-v5-blind-hard`
- local tests and smoke generation
- remote heldout generation under `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v5-blind-hard`
- base/v3/v4 evaluation using the existing evaluator
- local experiment record

Out of scope:

- simulated tool execution that edits model output
- new training
- external teacher generation

## Success Criteria

- Local tests pass.
- The generated prompt does not contain `Available lookup observations`.
- The generated prompt contains the target entity, noisy context, alias traps, and strict P19/P17 tool schema instructions.
- 200 remote samples are generated and verified.
- Evaluation summaries are produced for base, canonical-v3 SFT, and canonical-v4 SFT.
