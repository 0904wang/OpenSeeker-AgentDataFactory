# Canonical v3 Evaluation Design

## Goal

Improve the OpenSeeker evaluation loop so it can distinguish correct canonical tool-call syntax from evidence-faithful tool observations, then regenerate a clean heldout split and re-evaluate existing adapters before another SFT run.

## Design

The current evaluator measures final-answer correctness, ReAct format, and tool-call query coverage. It does not verify whether `Observation:` lines match the expected `ToolCall.result` values. Canonical-v2 improved `P19/P17` syntax but exposed failures where the model used the right action format with wrong observations, such as `wikidata_lookup[Max Planck, P19] -> Munich` instead of the gold `Kiel`.

Canonical-v3 adds observation-level faithfulness to evaluation:

- Parse ordered `Action: ...` and `Observation: ...` pairs from predictions.
- Match actions against expected tool calls using the existing query matcher.
- For each matched expected tool call, require the following observation text to contain the expected result after answer normalization.
- Add per-row fields `observation_faithfulness` and `observation_coverage`.
- Add summary fields `observation_faithfulness_rate` and `observation_coverage_avg`.

After local tests pass, regenerate a clean heldout200 split with the current question templates so old `Use synthesis round N` markers disappear. Then evaluate both the cleaned1k and canonical-v2 fixed1k adapters on the same clean split to build a fair ablation table.

## Non-Goals

- Do not start a new SFT run in this step.
- Do not change the remote CUDA, conda base environment, or global Python packages.
- Do not delete prior checkpoints, logs, results, or data.

## Success Criteria

- Local tests cover observation-faithful and observation-unfaithful predictions.
- Existing evaluation summary output includes the new observation metrics.
- Clean heldout generation produces 200 accepted samples with no `Use synthesis round` questions.
- Remote re-evaluation produces comparable summaries for cleaned1k and canonical-v2 fixed1k.
