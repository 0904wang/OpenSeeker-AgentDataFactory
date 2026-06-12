# Canonical-v4 Evidence-Conditioned Data Design

## Goal

Improve observation faithfulness by training on prompts that expose the expected lookup observations explicitly, instead of relying on the model to reconstruct `Observation:` lines from pretrained memory.

## Background

Canonical-v3 improved heldout tool-call success to 95.0% but observation faithfulness stayed at 71.5%. Error analysis showed that the model often emits syntactically correct actions while filling observations with memorized or localized facts such as `England` instead of `United Kingdom`, or place variants that do not match the verifier's gold tool result.

This means the next data iteration should not only scale sample count. It should change the supervised task contract so the model learns to copy tool observations from provided lookup results.

## Design

Add a new data version, `canonical-v4`, while leaving `canonical-v3` as the default for backward compatibility.

For v4 samples, the user-facing question will include a deterministic lookup result block:

```text
Available lookup observations:
- wikidata_lookup[Ada Lovelace, P19] -> London
- wikidata_lookup[London, P17] -> United Kingdom

Use these lookup observations exactly when writing Observation lines.
```

The target trajectory remains canonical ReAct:

```text
Action: wikidata_lookup[Ada Lovelace, P19]
Observation: London
Action: wikidata_lookup[London, P17]
Observation: United Kingdom
Final: United Kingdom
```

The SFT system prompt will also mention that `Observation:` lines must copy the provided lookup observation values exactly. This makes v4 closer to a real agent setting where the environment returns observations and the model must organize them into a valid trajectory.

## Conflict Metadata

Each v4 sample should record source metadata that makes the data auditable:

- `data_version=canonical-v4`
- `observation_conditioning=lookup_result_block`
- `observation_grounding=provided_lookup_results`
- `conflict_types=[country_alias, birthplace_alias, noisy_context]` when applicable
- `lookup_observation_block=true`

The metadata does not need a new schema field; it lives under `sample.source`.

## Scope

This change covers generation and SFT export only. It does not modify the evaluator yet. A later heldout-v4 evaluation can use the same prompt-conditioning idea so v4 training and evaluation are aligned.

Out of scope for this change:

- real external Wikidata calls
- new task types
- 5k/10k remote generation
- SFT configs
- model evaluation prompt changes

## Success Criteria

- Existing v3 generation remains unchanged by default.
- CLI can generate v4 artifacts using `--data-version canonical-v4`.
- v4 generated samples include lookup observation blocks in questions.
- v4 SFT system prompt explicitly tells the model to copy provided lookup observations.
- v4 source metadata records the new data version and conditioning policy.
- Verifier still accepts v4 deterministic samples with 100% quality on local tests.
