# Qwen3-8B Mixed SFT on v6 Blind Tool-choice Heldout200

## Goal

Evaluate the mixed v3/v4/v5blind Qwen3-8B LoRA adapter on the new `canonical-v6-blind-tool-choice-hard` heldout split.

The v6 split was created after the mixed adapter saturated both v4 and v5 blind-hard heldouts. It removes the main v5 leakage channels:

- no explicit `Available lookup observations`
- no visible `P19` / `P17` relation IDs
- no visible `wikidata_lookup[entity, ...]` scaffold
- no `->` lookup result hints
- no fixed "Use ReAct steps with ..." instruction

The intent is to test whether the model can choose the relevant lookup intent from natural language and distractor intent options, rather than only following an exposed property/schema template.

## Remote Context

- Date: 2026-06-13
- Remote entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote workspace: `/data/wzl/OpenSeeker-AgentDataFactory`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Local code commits before evaluation: `b7f8323 Add harder blind tool choice heldout`, `ab73b52 Record v6 heldout generation`
- Remote code sync: approved narrow file sync for `openseeker_factory/cli.py`, `openseeker_factory/pipeline.py`, `tests/test_cli.py`, `tests/test_pipeline.py`
- Evaluation session: `openseeker-20260613-eval-mixed-v6blindtoolchoice-gpu7`
- GPU selection: `CUDA_VISIBLE_DEVICES=7`
- Number of GPUs: 1

Remote repo note: the remote git checkout still had pre-existing dirty/untracked files and an older commit, so this evaluation used the approved narrow file sync path instead of `git pull --ff-only`.

## Inputs

Heldout samples:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v6-blind-tool-choice-hard/samples.jsonl
```

Adapter:

```text
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2k-mixed-v3-v4-v5blind
```

Base model snapshot:

```text
/data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218
```

## Preflight

Before launch, GPU7 was idle enough for the single-GPU evaluation:

```text
GPU7: 18 MiB used, 0% utilization
```

Input artifacts were present:

```text
heldout samples: 200 rows
adapter_model.safetensors: 167M
```

Remote target tests for the synced v6 code had already passed:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python -m pytest \
  tests/test_pipeline.py::test_factory_can_generate_canonical_v6_blind_tool_choice_hard_heldout_sample \
  tests/test_cli.py::test_cli_generate_supports_canonical_v6_blind_tool_choice_hard_data_version -q
```

Result:

```text
..                                                                       [100%]
```

## Launch

Launcher:

```text
/data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_mixed_v3_v4_v5blind_v6blindtoolchoice_gpu7.sh
```

Tmux launch command:

```bash
ssh user@ssh-22.e6.luyouxia.net -p 29509 \
  'tmux new-session -d -s openseeker-20260613-eval-mixed-v6blindtoolchoice-gpu7 "bash /data/wzl/OpenSeeker-AgentDataFactory/runs/launch_eval_mixed_v3_v4_v5blind_v6blindtoolchoice_gpu7.sh" && tmux list-sessions'
```

Effective evaluation command:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
CUDA_VISIBLE_DEVICES=7 PYTHONNOUSERSITE=1 python -m openseeker_factory.cli evaluate-model \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/results/heldout-eval-samples-200-canonical-v6-blind-tool-choice-hard/samples.jsonl \
  --model-label qwen3-8b-lora-sft-2k-mixed-v3-v4-v5blind-v6blindtoolchoice-heldout200 \
  --model-name-or-path /data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218 \
  --adapter-path /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2k-mixed-v3-v4-v5blind \
  --limit 200 \
  --batch-size 2 \
  --max-new-tokens 160 \
  --device cuda \
  --local-files-only \
  --disable-thinking \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-2k-mixed-v3-v4-v5blind-v6blindtoolchoice-heldout200-gpu7
```

## Output Paths

Results:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-2k-mixed-v3-v4-v5blind-v6blindtoolchoice-heldout200-gpu7
```

Prediction file:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-2k-mixed-v3-v4-v5blind-v6blindtoolchoice-heldout200-gpu7/qwen3-8b-lora-sft-2k-mixed-v3-v4-v5blind-v6blindtoolchoice-heldout200_predictions.jsonl
```

Summary file:

```text
/data/wzl/OpenSeeker-AgentDataFactory/results/eval-qwen3-8b-sft-2k-mixed-v3-v4-v5blind-v6blindtoolchoice-heldout200-gpu7/qwen3-8b-lora-sft-2k-mixed-v3-v4-v5blind-v6blindtoolchoice-heldout200_summary.csv
```

Warning: the launcher file was transferred from Windows with CRLF line endings, so the tee log path was created with a trailing carriage return in the filename. The result artifacts above were written correctly and are the authoritative outputs.

## Raw Summary

```csv
model_label,split,total,exact_match_rate,canonical_match_rate,answer_f1_avg,gold_answer_mention_rate,final_answer_rate,tool_call_success_rate,tool_call_coverage_avg,observation_faithfulness_rate,observation_coverage_avg,trajectory_valid_rate,hallucination_rate,correct_rate,canonical_alias_match_rate,missing_final_rate,trajectory_format_error_rate,tool_coverage_gap_rate,supported_but_wrong_answer_rate,unsupported_wrong_answer_rate
qwen3-8b-lora-sft-2k-mixed-v3-v4-v5blind-v6blindtoolchoice-heldout200,overall,200,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.945,0.9725,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
qwen3-8b-lora-sft-2k-mixed-v3-v4-v5blind-v6blindtoolchoice-heldout200,multi_hop_qa,67,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.9403,0.9701,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
qwen3-8b-lora-sft-2k-mixed-v3-v4-v5blind-v6blindtoolchoice-heldout200,noisy_context_retrieval_qa,66,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.9545,0.9773,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
qwen3-8b-lora-sft-2k-mixed-v3-v4-v5blind-v6blindtoolchoice-heldout200,tool_use_qa,67,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.9403,0.9701,1.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0
```

## Metrics

Overall:

```text
total 200
exact_match_rate 1.0
canonical_match_rate 1.0
answer_f1_avg 1.0
gold_answer_mention_rate 1.0
final_answer_rate 1.0
tool_call_success_rate 1.0
tool_call_coverage_avg 1.0
observation_faithfulness_rate 0.945
observation_coverage_avg 0.9725
trajectory_valid_rate 1.0
hallucination_rate 0.0
correct_rate 1.0
```

By task type:

```text
multi_hop_qa: total 67, observation_faithfulness 0.9403, observation_coverage 0.9701, all answer/tool/correct metrics 1.0
noisy_context_retrieval_qa: total 66, observation_faithfulness 0.9545, observation_coverage 0.9773, all answer/tool/correct metrics 1.0
tool_use_qa: total 67, observation_faithfulness 0.9403, observation_coverage 0.9701, all answer/tool/correct metrics 1.0
```

## Error Audit

Audit command:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
PYTHONNOUSERSITE=1 python - <audit_script>
```

Result:

```text
total 200
observation_faithfulness_failed 11
failed_by_task_type {'multi_hop_qa': 4, 'tool_use_qa': 4, 'noisy_context_retrieval_qa': 3}
faithfulness_rate 0.945
coverage_avg 0.9725
```

Failed observations:

```text
wikidata-carl-friedrich-gauss-multi-hop-46: expected ['Braunschweig', 'Germany'], observed ['Brunswick', 'Germany']
wikidata-richard-feynman-tool-50: expected ['New York City', 'United States'], observed ['New York', 'United States']
wikidata-richard-feynman-noisy-51: expected ['New York City', 'United States'], observed ['New York', 'United States']
wikidata-yukihiro-matsumoto-multi-hop-118: expected ['Osaka', 'Japan'], observed ['Tokyo', 'Japan']
wikidata-yukihiro-matsumoto-tool-119: expected ['Osaka', 'Japan'], observed ['Tokyo', 'Japan']
wikidata-yukihiro-matsumoto-noisy-120: expected ['Osaka', 'Japan'], observed ['Tokyo', 'Japan']
wikidata-carl-friedrich-gauss-multi-hop-166: expected ['Braunschweig', 'Germany'], observed ['Brunswick', 'Germany']
wikidata-carl-friedrich-gauss-tool-167: expected ['Braunschweig', 'Germany'], observed ['Brunswick', 'Germany']
wikidata-richard-feynman-multi-hop-169: expected ['New York City', 'United States'], observed ['New York', 'United States']
wikidata-richard-feynman-tool-170: expected ['New York City', 'United States'], observed ['New York', 'United States']
wikidata-richard-feynman-noisy-171: expected ['New York City', 'United States'], observed ['New York', 'United States']
```

Failure pattern:

- `Braunschweig` was normalized by the model as `Brunswick`; final country remained correct.
- `New York City` was shortened to `New York`; final country remained correct.
- `Yukihiro Matsumoto` birthplace was predicted as `Tokyo` instead of the gold `Osaka`; final country remained correct because both resolve to Japan.

## Analysis

The v6 heldout achieved its purpose: it no longer fully saturates every metric. The mixed v3/v4/v5blind adapter still gets every final answer, canonical answer, tool call, and trajectory format correct, but v6 exposes a weaker observation-level grounding contract.

This is a meaningful distinction for the project. The model can solve the final country task under blind tool-choice phrasing, but it is not always faithful to the exact intermediate evidence value. The observed failures are mostly alias-level or same-country substitutions, so the answer-level benchmark alone would hide them.

For the resume project, this is useful evidence that the data factory is not only generating easy QA labels. It now produces a harder heldout where verifier metrics can reveal trajectory/evidence weaknesses even when final-answer metrics are saturated.

## Next Steps

1. Add v6 examples into the training mix and run a targeted SFT or short continued SFT, then re-evaluate whether observation faithfulness improves without regressing v4/v5.
2. Add an alias-aware observation verifier for acceptable aliases such as `Braunschweig` / `Brunswick`, but keep strict checks for true wrong intermediate facts such as `Osaka` / `Tokyo`.
3. Create a v7 split with relation diversity beyond birthplace-to-country, so the benchmark tests more than the current P19/P17 reasoning family.
4. Update README with a compact experiment table:
   - mixed v3/v4/v5blind on v4: all core metrics 1.0
   - mixed v3/v4/v5blind on v5 blind-hard: all core metrics 1.0
   - mixed v3/v4/v5blind on v6 blind tool-choice: answer/tool metrics 1.0, observation faithfulness 0.945
