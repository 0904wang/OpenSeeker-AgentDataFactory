# Qwen3-8B canonical-v2 fixed 1k LoRA heldout200 evaluation

Date: 2026-06-12

## Goal

Evaluate the Qwen3-8B LoRA adapter trained on canonical-v2 fixed 1k SFT data against the existing 200-sample held-out canonical split. The primary question is whether canonical `P19/P17` SFT improves strict tool-call success compared with the previous cleaned-1k adapter.

## Remote Context

- Backend: SSH
- Entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Base model: `/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218`
- Adapter: `/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v2-fixed`
- GPU: `CUDA_VISIBLE_DEVICES=7`
- Launcher synced from local path: `D:\resume\Data synthesis\runs\launch_eval_canonical_v2_fixed_heldout200_gpu7.sh`
- Remote launcher path: `/data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_canonical_v2_fixed_heldout200_gpu7.sh`

## Preflight

Resource and path checks:

```text
GPU7: 18 MiB / 32607 MiB before launch
tmux sessions: none
heldout samples: 200
adapter checkpoint size: 698M
formal result dir: free
formal log path: free
```

Test command:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 \
  "cd /data/wzl/OpenSeeker-AgentDataFactory/repo && source /home/user/anaconda3/etc/profile.d/conda.sh && conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && PYTHONNOUSERSITE=1 python -m pytest tests/test_evaluation.py tests/test_cli.py"
```

Result:

```text
20 passed in 1.19s
```

One parallel SSH pytest attempt timed out before this retry. The retry passed without code or environment changes, so it was treated as transient SSH connection pressure rather than a test failure.

## Smoke Evaluation

Command:

```bash
CUDA_VISIBLE_DEVICES=7 PYTHONNOUSERSITE=1 python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical/samples.jsonl \
  --model-label qwen3-8b-lora-sft-1k-canonical-v2-fixed-smoke2 \
  --model-name-or-path /data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218 \
  --adapter-path /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v2-fixed \
  --limit 2 \
  --batch-size 2 \
  --max-new-tokens 160 \
  --device cuda \
  --local-files-only \
  --disable-thinking \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v2-fixed-heldout200-smoke2-gpu7
```

Smoke summary:

```text
overall,total=2,exact=1.0,canonical=1.0,final=1.0,tool_call_success=1.0,tool_call_coverage=1.0,trajectory_valid=1.0
```

Representative smoke output:

```text
Action: wikidata_lookup[James Clerk Maxwell, P19]
Observation: Edinburgh
Action: wikidata_lookup[Edinburgh, P17]
Observation: United Kingdom
Final: United Kingdom
```

## Launch

An initial direct nested SSH/tmux command failed with shell quoting:

```text
bash: -c: line 1: unexpected EOF while looking for matching `"'
bash: -c: line 2: syntax error: unexpected end of file
```

No tmux session, log, or GPU process was created. The run was then launched through a project-local launcher script.

Launcher:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd /data/wzl/OpenSeeker-AgentDataFactory/repo

source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory

export HF_HOME=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface
export TRANSFORMERS_CACHE=/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

CUDA_VISIBLE_DEVICES=7 PYTHONNOUSERSITE=1 python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical/samples.jsonl \
  --model-label qwen3-8b-lora-sft-1k-canonical-v2-fixed-heldout200 \
  --model-name-or-path /data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218 \
  --adapter-path /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-1k-canonical-v2-fixed \
  --limit 200 \
  --batch-size 2 \
  --max-new-tokens 160 \
  --device cuda \
  --local-files-only \
  --disable-thinking \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v2-fixed-heldout200-gpu7 \
  2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-canonical-v2-fixed-heldout200-gpu7.log
```

tmux launch:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 \
  "if tmux has-session -t openseeker-20260612-eval-canonical-v2-fixed1k-heldout200-gpu7 2>/dev/null; then echo 'session already exists: openseeker-20260612-eval-canonical-v2-fixed1k-heldout200-gpu7'; else tmux new-session -d -s openseeker-20260612-eval-canonical-v2-fixed1k-heldout200-gpu7 'bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_canonical_v2_fixed_heldout200_gpu7.sh' && echo 'started: openseeker-20260612-eval-canonical-v2-fixed1k-heldout200-gpu7'; fi"
```

## Outputs

- tmux session: `openseeker-20260612-eval-canonical-v2-fixed1k-heldout200-gpu7`
- Log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/eval-qwen3-8b-sft-1k-canonical-v2-fixed-heldout200-gpu7.log`
- Results dir: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v2-fixed-heldout200-gpu7`
- Predictions: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v2-fixed-heldout200-gpu7/qwen3-8b-lora-sft-1k-canonical-v2-fixed-heldout200_predictions.jsonl`
- Summary: `/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-1k-canonical-v2-fixed-heldout200-gpu7/qwen3-8b-lora-sft-1k-canonical-v2-fixed-heldout200_summary.csv`

Completion evidence:

```text
tmux sessions: none after completion
GPU7: 18 MiB / 32607 MiB after completion
predictions size: 178768 bytes
summary size: 1024 bytes
log lines: 104
```

## Raw Summary

```text
model_label,split,total,exact_match_rate,canonical_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,trajectory_valid_rate,hallucination_rate,correct_rate,canonical_alias_match_rate,missing_final_rate,trajectory_format_error_rate,tool_coverage_gap_rate,supported_but_wrong_answer_rate,unsupported_wrong_answer_rate
qwen3-8b-lora-sft-1k-canonical-v2-fixed-heldout200,overall,200,0.94,0.955,0.94,0.94,1.0,0.8,0.9,1.0,0.045,0.785,0.015,0.0,0.0,0.155,0.0,0.045
qwen3-8b-lora-sft-1k-canonical-v2-fixed-heldout200,multi_hop_qa,67,0.9552,0.9552,0.9552,0.9552,1.0,0.7761,0.8881,1.0,0.0448,0.7761,0.0,0.0,0.0,0.1791,0.0,0.0448
qwen3-8b-lora-sft-1k-canonical-v2-fixed-heldout200,noisy_context_retrieval_qa,66,0.9091,0.9545,0.9091,0.9091,1.0,0.8485,0.9242,1.0,0.0455,0.803,0.0455,0.0,0.0,0.1061,0.0,0.0455
qwen3-8b-lora-sft-1k-canonical-v2-fixed-heldout200,tool_use_qa,67,0.9552,0.9552,0.9552,0.9552,1.0,0.7761,0.8881,1.0,0.0448,0.7761,0.0,0.0,0.0,0.1791,0.0,0.0448
```

## Metrics

| Metric | Value |
| --- | ---: |
| total | 200 |
| exact_match_rate | 0.94 |
| canonical_match_rate | 0.955 |
| answer_f1_avg | 0.94 |
| final_answer_rate | 1.0 |
| tool_call_success_rate | 0.80 |
| tool_call_coverage_avg | 0.90 |
| trajectory_valid_rate | 1.0 |
| hallucination_rate | 0.045 |
| correct_rate | 0.785 |
| tool_coverage_gap_rate | 0.155 |
| unsupported_wrong_answer_rate | 0.045 |

Error buckets:

```text
correct: 157
tool_coverage_gap: 31
canonical_alias_match: 3
unsupported_wrong_answer: 9
```

Task buckets:

```text
multi_hop_qa: correct=52, tool_coverage_gap=12, unsupported_wrong_answer=3
tool_use_qa: correct=52, tool_coverage_gap=12, unsupported_wrong_answer=3
noisy_context_retrieval_qa: correct=53, tool_coverage_gap=7, canonical_alias_match=3, unsupported_wrong_answer=3
```

Coverage distribution:

```text
tool_call_coverage=1.0: 160
tool_call_coverage=0.5: 40
```

## Comparison With Cleaned 1k Adapter

| Run | Exact | Canonical | Final | Tool success | Coverage avg | Trajectory | Correct | Tool gap | Unsupported wrong |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| cleaned1k heldout200 | 1.000 | 1.000 | 1.000 | 0.650 | 0.825 | 1.000 | 0.650 | 0.350 | 0.000 |
| canonical-v2 fixed1k heldout200 | 0.940 | 0.955 | 1.000 | 0.800 | 0.900 | 1.000 | 0.785 | 0.155 | 0.045 |

Delta:

```text
tool_call_success_rate: +0.150
tool_call_coverage_avg: +0.075
correct_rate: +0.135
tool_coverage_gap_rate: -0.195
exact_match_rate: -0.060
unsupported_wrong_answer_rate: +0.045
```

## Representative Errors

Tool coverage gap with correct final answer:

```text
id: wikidata-max-planck-multi-hop-4
gold: Germany
predicted: Germany
expected: Max Planck birthplace -> Kiel; Kiel country -> Germany
prediction: wikidata_lookup[Max Planck, P19] -> Munich; wikidata_lookup[Munich, P17] -> Germany; Final: Germany
```

Wrong answer from historical or memorized entity knowledge:

```text
id: wikidata-gregor-mendel-multi-hop-49
gold: Czech Republic
predicted: Austria
expected: Gregor Mendel birthplace -> Hyncice; Hyncice country -> Czech Republic
prediction: wikidata_lookup[Gregor Mendel, P19] -> Heinzendorf; wikidata_lookup[Heinzendorf, P17] -> Austria; Final: Austria
```

Canonical alias match:

```text
id: wikidata-mary-anning-noisy-21
gold: United Kingdom
predicted: England
expected: Lyme Regis country -> United Kingdom
prediction: wikidata_lookup[Lyme Regis, P17] -> England; Final: England
```

## Analysis

The canonical-v2 fixed SFT did what it was designed to do: it increased strict tool-call behavior. Tool-call success improved from 0.65 to 0.80, average coverage improved from 0.825 to 0.90, and the tool coverage gap rate dropped from 0.35 to 0.155.

The tradeoff is that final-answer accuracy regressed from 1.0 to 0.94 and unsupported wrong answers appeared at 0.045. The failure mode is not malformed ReAct output; trajectory validity stayed at 1.0. Instead, the model often uses the desired `P19/P17` syntax but fills observations from pretrained knowledge or historical aliases rather than the synthetic heldout evidence. This is visible in Max Planck, Paul Dirac, Gregor Mendel, and Mary Anning examples.

This suggests the next iteration should train or evaluate with stronger evidence conditioning, not only canonical tool syntax. The data factory should make the observation values verifier-critical and possibly include contrastive/noisy examples where memorized historical place names conflict with the synthetic gold evidence.

There is also a heldout hygiene issue: some heldout questions still contain older synthetic text such as `Use synthesis round N`. That should be regenerated with the newer question template before using the heldout result as a polished benchmark number.

## Resume Interpretation

This result is useful because it shows an engineering loop:

- cleaned1k fixed final-answer format but left tool-call coverage weak
- canonical-v2 fixed improved verifier-level tool use by 15 percentage points
- stricter evaluation exposed a new evidence-faithfulness failure mode

For a resume bullet, avoid claiming a blanket win on all metrics. A defensible statement is: canonicalized trajectory SFT improved tool-call success from 65% to 80% on a 200-sample heldout split while preserving 100% trajectory validity, then error analysis identified evidence-faithfulness regressions for the next verifier/data iteration.

## Next Steps

1. Regenerate a clean heldout200 split using the latest question templates so no question contains `Use synthesis round N`.
2. Add an evidence-faithfulness decoding/evaluation check that penalizes observations not matching gold evidence, even when the final answer is correct.
3. Generate a small canonical-v3 dataset with contrastive observation grounding and train another 1k LoRA.
4. Re-evaluate base, cleaned1k, canonical-v2, and canonical-v3 under the same clean heldout split for a stronger ablation table.
