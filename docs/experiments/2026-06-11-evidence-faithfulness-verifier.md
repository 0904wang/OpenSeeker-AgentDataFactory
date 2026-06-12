# 2026-06-11 Evidence Faithfulness Verifier

## Status

Completed. Added an `evidence_faithfulness` verifier check to the data-generation pipeline and audited the prompt v2 smoke30 predictions against the expected intermediate birthplace evidence.

## Goal

Catch samples where the final country is correct but the trajectory changes or invents the intermediate birthplace. This directly targets the `tool_coverage_gap` findings from prompt v2 smoke30.

## Code Changes

Changed locally and synced narrowly to remote:

```text
README.md
openseeker_factory/pipeline.py
tests/test_pipeline.py
```

New verifier check:

```text
evidence_faithfulness
```

Definition:

```text
The trajectory must mention every expected tool result from the sample tool plan, including the seed intermediate birthplace and final country.
```

Metrics now include:

```text
evidence_faithfulness_rate
```

## TDD Verification

Red run before implementation:

```text
python -m pytest tests/test_pipeline.py
2 failed, 12 passed
```

The failing tests covered:

- rejecting a sample that answered `United Kingdom` but changed Ada Lovelace's intermediate location from `London` to `Cambridge`
- accepting a normal faithful deterministic trajectory and exposing `evidence_faithfulness_rate=1.0`

Green runs after implementation:

```text
python -m pytest tests/test_pipeline.py
14 passed in 0.21s

python -m pytest tests/test_cli.py tests/test_pipeline.py
22 passed in 3.79s

python -m pytest
44 passed in 15.32s
```

Remote verification after narrow sync:

```text
python -m pytest tests/test_pipeline.py tests/test_cli.py
22 passed in 1.28s
```

## Remote Context

- SSH entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote branch: `main`
- Remote commit observed earlier: `7b64c03`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Audited samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical/samples.jsonl`
- Audited predictions: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-promptv2-smoke30-gpu7/qwen3-8b-lora-sft-1k-promptv2-smoke30_predictions.jsonl`

## Prompt V2 Smoke30 Faithfulness Audit

Audit result:

```text
total: 30
evidence_faithful: 21
unfaithful: 9
```

The 9 unfaithful predictions match the smoke30 `tool_coverage_gap` count. Representative failures:

```text
wikidata-max-planck-noisy-6:
  expected: Kiel -> Germany
  generated: Hilbertstadt -> Germany

wikidata-werner-heisenberg-multi-hop-10:
  expected: Wurzburg -> Germany
  generated: Munich -> Germany

wikidata-paul-dirac-tool-14:
  expected: Bristol -> United Kingdom
  generated: Bracknell -> United Kingdom

wikidata-c-v-raman-tool-26:
  expected: Tiruchirappalli -> India
  generated: Thiruvananthapuram -> India

wikidata-sophie-germain-tool-29:
  expected: Paris -> France
  generated: Toulous -> France
```

## Interpretation

The new verifier makes the project claim stronger: answer correctness alone is not enough. A sample can only pass if its trajectory preserves the intended evidence path.

This is especially important for Agent data synthesis because SFT on unfaithful trajectories can teach the student model to fabricate plausible observations while still ending at the right answer. `evidence_faithfulness` turns that failure mode into a measurable reject/rewrite signal.

## Resume-Safe Takeaway

Possible wording:

```text
Added an evidence-faithfulness verifier that rejects trajectories whose final answer is correct but whose tool observations drift from the expected Wikidata intermediate facts, exposing 9/30 prompt-v2 smoke failures that exact match alone would miss.
```

## Next Steps

- Use `evidence_faithfulness` during teacher generation so unfaithful synthetic samples enter reject/rewrite instead of SFT export.
- Add a teacher rewrite prompt that preserves `entity -> expected birthplace -> expected country`.
- Re-export SFT v2 data after applying the stricter verifier, then run a small LoRA refresh or compare data-quality metrics before retraining.
