# Experiment Roadmap

This roadmap converts OpenSeeker AgentDataFactory from a verified local scaffold into a resume-grade remote experiment project. Each completed experiment must have a local record under `docs/experiments/`.

## Current Milestone - v6 Closed Loop + RFT Round 1

Status: completed and recorded.

The project now has a verified closed loop:

```text
harder heldout design -> failure audit -> targeted synthetic data -> Qwen3-8B LoRA SFT -> RFT/ReST-EM rejection sampling -> regression evaluation
```

Current best result:

```text
2k mixed v3/v4/v5blind -> v6 observation_faithfulness 0.945
2.4k mixed v3/v4/v5blind/v6 -> v6 observation_faithfulness 0.985
3.5k SFT + RFT changed round1 -> v6 observation_faithfulness 1.000
v4 and v5 heldout core metrics stayed at 1.0
```

Key records:

```text
docs/experiments/2026-06-13-qwen3-8b-mixed-v6trained-v6-heldout200-eval.md
docs/experiments/2026-06-13-qwen3-8b-mixed-v6trained-v4-v5-regression-eval.md
docs/experiments/2026-07-01-rft-round1-a0-k4-t1p0.md
docs/experiments/2026-07-01-sft-rft-round1-changed-3p5k-gpu06.md
docs/experiments/2026-07-01-rftchanged-round1-v6-v4-v5-eval.md
```

RFT Stage A is complete for the current v4/v5/v6 heldout suite: the target v6 failures dropped from `3/200` to `0/200`, and v4/v5 stayed saturated. Do not spend more compute on RFT Round 2 against the same heldouts unless a harder split is added first.

Do not treat this as completion of 20k/50k scale or RL validation. The next high-value experiment is relation-diverse v7, not simply more same-template data.

## Phase 0 - Local Contract Validation

Goal: prove that schema, generation, filtering, and exports work.

Commands:

```bash
python -m pytest
python -m openseeker_factory.cli demo --count 3 --out-dir outputs/demo
```

Acceptance:

- tests pass
- `samples.jsonl`, `sft_conversations.jsonl`, `rl_rewards.jsonl`, `trace.jsonl`, and `summary.csv` are produced
- summary reports accepted/rejected counts and quality metrics

Status: implemented locally; rerun before remote sync.

## Phase 1 - Remote Smoke Test

Goal: prove the server environment can run the same contract.

Remote constraints:

- follow `AGENTS.md`
- use `/data/wzl/OpenSeeker-AgentDataFactory`
- run preflight first
- use 0 or 1 GPU
- no real long experiment before approval

Dry run:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
eval "$(/home/user/anaconda3/bin/conda shell.bash hook)"
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
python -m pytest
python -m openseeker_factory.cli demo --count 3 --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/dry-run
```

Acceptance:

- remote tests pass
- dry-run files are created under approved results path
- local experiment record is written

## Phase 2 - 5k Baseline Reproduction

Goal: reproduce the old resume baseline in the new schema.

Target output:

- 5k multi-hop / tool-use / noisy-context samples
- JSONL schema-compatible dataset
- quality summary
- trace sample inspection

Candidate command:

```bash
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate \
  --count 5000 \
  --seed-file data/seeds/wikidata_seed_sample.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/baseline-5k
```

`data/seeds/wikidata_seed_sample.jsonl` is a schema sample. Replace it with the real Wikidata-derived seed file before treating the run as a true 5k baseline.

Metrics:

- accepted count
- rejection rate
- dedup rate
- solvability rate
- evidence hit rate
- tool success rate
- trajectory valid rate
- manual sample pass rate from a 100-200 sample audit

Acceptance:

- all generated files are under approved remote result paths
- local record includes command, runtime, metrics, and failure analysis
- resume wording uses verified 5k numbers only

## Phase 3 - 20k Data Factory Run

Goal: show scale beyond the original project without jumping directly to the riskiest target.

Default GPU policy:

- prefer 1-2 GPUs
- use vLLM or local batch inference only after environment is verified
- do not use 4 GPUs without explicit approval

Target output:

- 20k accepted or generated samples, with accepted/rejected split stated clearly
- SFT conversation export
- RL reward-format export
- trace and summary logs

Acceptance:

- throughput and runtime are recorded
- quality metrics are compared against the 5k baseline
- local experiment record includes next-step thoughts

## Phase 4 - 50k Scale or Ablation

Choose only after Phase 3:

- scale to 50k if quality and throughput are stable
- or run ablations if failure modes are clearer than scaling value

Ablations:

- no Evol-Instruct
- no verifier
- no noisy-context tasks
- no trajectory denoise

Acceptance:

- one table compares accepted rate, quality metrics, and failure modes
- resume claims distinguish scale, filtering, and downstream effect

## Phase 5 - SFT / RFT / RL Validation

Goal: turn data quality into model behavior evidence.

Default model tier:

- Qwen 7B or 14B
- LoRA SFT first
- RFT / ReST-EM continued SFT after a strong SFT checkpoint
- verl / GRPO only after SFT and verifier reward are stable

Evaluation:

- answer EM/F1 or exact-match proxy
- multi-hop completion rate
- tool-call success rate
- hallucination rate
- average steps and trace failure types

Acceptance:

- compare baseline, old 5k, new 20k, and optional new 50k
- record model, commit, env, GPUs, command, logs, checkpoints, and metrics
- only then update resume with improvement numbers

Status update:

- Qwen3-8B LoRA SFT on 2k and 2.4k mixed synthetic data is completed.
- v4/v5/v6 heldout evaluations are completed.
- RFT Round 1 from the restored 2.4k A0 checkpoint is completed: sampled 9.6k candidates, accepted 9,429 all-pass candidates, retained 1,095 changed trajectories, and continued SFT to a 3.5k mixed dataset.
- RFT changed-only round1 reduced v6 blind tool-choice failures from `3/200` to `0/200` without v4/v5 regression.
- 20k/50k data scale and GRPO/RLVR validation remain future work.

## Phase 6 - v7 Relation-diverse Heldout

Goal: reduce overfitting to the current birthplace-to-country path family.

Candidate relation paths:

- person birthplace -> country
- person educated at -> institution country
- person employer -> headquarters country
- award -> conferring organization country
- publication venue -> country

Acceptance:

- v7 user prompts hide explicit relation IDs and tool schemas, similar to v6
- deterministic verifier checks exact intermediate evidence for each relation path
- heldout includes distractor relation intents
- evaluation reports answer, tool-call, trajectory, observation-faithfulness, and hallucination metrics
- targeted SFT improves v7 observation faithfulness without regressing v4/v5/v6
