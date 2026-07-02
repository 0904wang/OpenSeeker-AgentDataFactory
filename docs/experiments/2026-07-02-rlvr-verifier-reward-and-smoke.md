# RLVR Verifier Reward and Smoke Runs

## Metadata

- Experiment name: rlvr-verifier-reward-and-smoke
- Date: 2026-07-02
- Goal: Start Stage B RLVR by turning the deterministic verifier into a dense reward and running small GRPO/ARPO-style policy optimization smoke experiments.
- Status: success
- Operator: Codex
- Remote host: `user@ssh-22.e6.luyouxia.net -p 29509`
- Isolated worktree: `/data/wzl/OpenSeeker-AgentDataFactory/runs/repo-v7-relation-diverse-20260701`
- Local commits:
  - `a38c079 Add verifier reward scoring for RLVR`
  - `2c62a28 Add minimal verifier RLVR smoke trainer`
  - `d0ea5fb Fix RLVR LoRA gradient checkpointing`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- RL libraries found: `trl==0.9.6`, `peft`, `transformers`, `accelerate`; `verl` not installed in this project env.
- Start adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-v7rftchanged-489-newonly-round2-20260702`

## Reward Design

Two verifier rewards were implemented:

```text
binary_all_pass_reward = 1 iff:
  answer_supported
  tool_success
  evidence_faithfulness
  trajectory_valid
```

Weighted dense reward:

```text
reward =
  0.25 * answer_score
+ 0.30 * tool_score
+ 0.35 * evidence_score
+ 0.10 * format_score
```

Caps:

```text
format_score == 0          -> max 0.20
tool_score == 0            -> max 0.45
answer correct + tool gap  -> max 0.65
wrong answer               -> max 0.45
hallucination proxy        -> max 0.35
```

The reward is not differentiable through the verifier; it is a dense scalar for policy-gradient optimization.

## Commands

Reward smoke on existing v7 RFT candidates:

```bash
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli score-verifier-rewards \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/train-samples-400-canonical-v7-relation-diverse-start200/samples.jsonl \
  --prediction-file /data/wzl/OpenSeeker-AgentDataFactory/results/rft-v7-train268-k4-t1p0-20260702/candidate_predictions.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/reward-smoke-v7-train268-k4-weighted-20260702 \
  --model-label qwen3-8b-rftchanged-round1-v7-train268-k4-t1p0 \
  --reward-mode weighted
```

GRPO smoke:

```bash
CUDA_VISIBLE_DEVICES=0 PYTHONNOUSERSITE=1 python -m openseeker_factory.cli train-rlvr-smoke \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/train-samples-400-canonical-v7-relation-diverse-start200/samples.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/rlvr-smoke-grpo-v7-limit16-g4-weighted-20260702 \
  --model-label qwen3-8b-rlvr-smoke-grpo-v7-limit16-g4-weighted \
  --model-name-or-path /data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218 \
  --adapter-path /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-v7rftchanged-489-newonly-round2-20260702 \
  --algorithm grpo \
  --reward-mode weighted \
  --limit 16 \
  --num-generations 4 \
  --max-new-tokens 120 \
  --learning-rate 5e-7 \
  --num-train-epochs 1 \
  --device cuda \
  --local-files-only \
  --disable-thinking \
  --seed 20260703
```

ARPO-style branch smoke used the same command with `--algorithm arpo`.

## Paths

- Weighted reward smoke: `/data/wzl/OpenSeeker-AgentDataFactory/results/reward-smoke-v7-train268-k4-weighted-20260702`
- Binary reward smoke: `/data/wzl/OpenSeeker-AgentDataFactory/results/reward-smoke-v7-train268-k4-binary-20260702`
- GRPO limit16/G4: `/data/wzl/OpenSeeker-AgentDataFactory/results/rlvr-smoke-grpo-v7-limit16-g4-weighted-20260702`
- ARPO limit16/G4: `/data/wzl/OpenSeeker-AgentDataFactory/results/rlvr-smoke-arpo-v7-limit16-g4-weighted-20260702`
- GRPO v7 eval: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-rlvr-smoke-grpo-limit16g4-v7heldout200-gpu0`
- ARPO v7 eval: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-rlvr-smoke-arpo-limit16g4-v7heldout200-gpu1`

## Reward Smoke Result

Weighted reward on 1,072 existing v7 RFT candidates:

| Split | Rows | Reward avg | Binary pass | Answer avg | Tool avg | Evidence avg | Format avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| overall | 1,072 | 0.8904 | 0.7612 | 0.9023 | 0.9562 | 0.8573 | 1.0000 |
| multi_hop_qa | 624 | 0.9453 | 0.8574 | 0.9679 | 0.9760 | 0.9038 | 1.0000 |
| tool_use_qa | 224 | 0.8769 | 0.6384 | 1.0000 | 0.8616 | 0.7812 | 1.0000 |
| noisy_context_retrieval_qa | 224 | 0.7509 | 0.6161 | 0.6217 | 0.9955 | 0.8036 | 1.0000 |

Relation reward:

| Relation | Rows | Reward avg | Binary pass | Main signal |
| --- | ---: | ---: | ---: | --- |
| birthplace_country | 400 | 0.9873 | 0.9275 | saturated |
| education_country | 224 | 0.8769 | 0.6384 | tool/evidence path errors |
| employer_country | 224 | 0.8702 | 0.7321 | mixed answer/evidence errors |
| award_country | 224 | 0.7509 | 0.6161 | wrong-answer/hallucination signal |

## RLVR Smoke Results

Small GRPO/ARPO smoke runs used only 16 prompts and 4 rollouts per prompt. These are not final RL results; they validate that rollout, reward, advantage, update, checkpoint save, and evaluation work end to end.

| Run | Rollouts | Reward avg | Binary pass | Effective train steps | v7 strict correct |
| --- | ---: | ---: | ---: | ---: | ---: |
| RFT round2 baseline | n/a | n/a | n/a | n/a | 0.665 |
| GRPO limit16/G4 | 64 | 0.9289 | 0.8906 | 8 | 0.670 |
| ARPO branch limit16/G4 | 64 | 0.8820 | 0.7969 | 12 | 0.660 |

v7 summary after GRPO smoke:

```csv
overall,200,exact=0.915,tool=0.735,obs=0.560,hallucination=0.085,correct=0.670
tool_use_qa,50,exact=1.000,tool=0.560,obs=0.460,correct=0.560
```

v7 summary after ARPO-style smoke:

```csv
overall,200,exact=0.910,tool=0.730,obs=0.560,hallucination=0.090,correct=0.660
tool_use_qa,50,exact=1.000,tool=0.560,obs=0.460,correct=0.560
```

Relation deltas relative to RFT round2:

| Relation | RFT round2 | GRPO smoke | ARPO smoke |
| --- | ---: | ---: | ---: |
| birthplace_country | 1.000 | 1.000 | 1.000 |
| education_country | 0.540 | 0.560 | 0.560 |
| employer_country | 0.620 | 0.620 | 0.600 |
| award_country | 0.500 | 0.500 | 0.480 |

## Failures / Warnings

- First GRPO smoke failed because LoRA + gradient checkpointing needed `enable_input_require_grads()`. Fixed in `d0ea5fb`.
- `trl` is installed but version `0.9.6` does not provide `GRPOTrainer`; `verl` is not installed in the OpenSeeker env. The current RLVR trainer is a project-local smoke implementation, not a replacement for a production verl run.
- ARPO implementation here is only an ARPO-style branch rollout smoke: it branches after the first generated `Observation:`. It does not yet implement the full paper's entropy-triggered adaptive branch sampling.
- Tiny RL updates can move metrics by only a few examples; treat `0.670` vs `0.665` as a chain-validation result, not a statistically meaningful improvement.

## Analysis

The reward is usable. It reproduces the RFT all-pass rate via the binary reward and gives dense separation on the known hard cases: award rows get the lowest average reward, education rows expose tool/evidence deficits even when the final answer is correct, and format is saturated.

The GRPO smoke is a valid first RLHF/RLVR row: it sampled multiple trajectories, computed group advantages, applied LoRA policy-gradient updates, saved an adapter, and evaluated on v7 heldout200. The metric moved from `0.665` to `0.670`, which is small but confirms the loop is operational.

The ARPO-style run also works mechanically, but the current branch heuristic is too crude. It generated more effective train steps than GRPO at the same budget, but did not improve heldout performance. The next ARPO iteration should branch before or at the first tool action using token entropy or relation-intent uncertainty, not after a mostly deterministic first observation.

## Next Steps

- Scale GRPO to 64-128 focused v7 prompts with `num_generations=4` and evaluate v7 plus v4/v5/v6 regression.
- Improve ARPO branch selection to target the first `Action:` / relation-choice point, ideally using action-token entropy or a cheap proxy from sampled action diversity.
- Keep reward fixed between GRPO and ARPO comparisons so any change is attributable to rollout/optimization strategy rather than reward shaping.
