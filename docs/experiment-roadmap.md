# Experiment Roadmap

This roadmap converts OpenSeeker AgentDataFactory from a verified local scaffold into a resume-grade remote experiment project. Each completed experiment must have a local record under `docs/experiments/`.

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

## Phase 5 - SFT / RL Validation

Goal: turn data quality into model behavior evidence.

Default model tier:

- Qwen 7B or 14B
- LoRA SFT first
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
