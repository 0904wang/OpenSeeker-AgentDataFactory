# Resume Material

Use this file to keep resume wording honest. Only use claims that are backed by local records under `docs/experiments/`.

## Verified Project Summary

OpenSeeker AgentDataFactory is now a verified synthetic-data and SFT loop for tool-use / retrieval agents:

- Data factory covers multi-hop QA, tool-use QA, noisy-context retrieval QA, ReAct trajectory export, verifier filtering, and LLaMA-Factory SFT export.
- Remote workflow is reproducible on the lab GPU server with preflight checks, narrow file sync, project-local conda env, tmux launches, logs, checkpoints, and local experiment records.
- Current best SFT run uses Qwen3-8B + LoRA on 2.4k mixed synthetic rows.
- Main measured improvement: v6 heldout observation faithfulness improved from `0.945` to `0.985` while v4/v5 heldouts stayed at all core metrics `1.0`.

## Resume Bullets: Chinese

Use these bullets for a resume project entry:

```text
OpenSeeker AgentDataFactory                                      Agent SFT / 数据合成
个人项目
- 构建面向多跳检索、工具调用与 noisy-context QA 的可验证 Agent 数据合成流水线，统一输出 ReAct 轨迹、tool calls、gold evidence、verifier result、SFT conversation 与评测 trace/summary。
- 设计 canonical-v4/v5/v6 数据版本与 deterministic verifier，覆盖答案可解性、工具调用覆盖率、Observation 证据忠实度、轨迹格式有效性和幻觉代理指标；通过 harder heldout 暴露最终答案正确但中间证据漂移的问题。
- 使用远程 4 卡 GPU 完成 Qwen3-8B LoRA SFT：先在 2k mixed v3/v4/v5blind 数据上训练，再针对 v6 blind tool-choice 失败模式补充 400 条定向合成数据，形成 2.4k mixed SFT 数据集。
- 在 v6 blind tool-choice heldout200 上将 Observation faithfulness 从 0.945 提升到 0.985，失败样本从 11/200 降至 3/200；同时 v4 heldout200 与 v5 blind-hard heldout200 的 exact/tool/trajectory/correct 等核心指标保持 1.0。
- 制定共享 GPU 远程实验规范，固化 preflight、dry run、tmux 启动、日志监控、checkpoint 管理和本地实验记录流程，保证数据生成、训练和评测结果可复现、可审计。
```

Shorter 3-bullet version:

```text
- 构建 OpenSeeker AgentDataFactory，面向多跳检索、工具调用与 noisy-context QA 生成可验证 ReAct SFT 数据，统一导出 samples、SFT conversations、RL reward format、trace JSONL 与 summary CSV。
- 设计 v4/v5/v6 harder heldout 与 evidence/tool/trajectory verifier，定位“最终答案正确但 Observation 中间证据漂移”的失败模式，并用定向 v6 合成数据进行闭环修复。
- 使用远程 4 卡完成 Qwen3-8B LoRA SFT；2.4k mixed 数据相比 2k mixed 基线将 v6 Observation faithfulness 从 0.945 提升到 0.985，且 v4/v5 heldout 核心指标保持 1.0。
```

## Resume Bullets: English

```text
OpenSeeker AgentDataFactory                                      Agent SFT / Synthetic Data
Personal Project
- Built a verifiable synthetic-data pipeline for multi-hop retrieval, tool-use QA, and noisy-context QA agents, exporting ReAct trajectories, tool calls, gold evidence, verifier results, SFT conversations, and evaluation traces.
- Designed canonical-v4/v5/v6 data versions and deterministic verifiers for answer support, tool-call coverage, observation faithfulness, trajectory validity, and hallucination proxy metrics.
- Ran Qwen3-8B LoRA SFT on a remote 4-GPU server with a 2.4k mixed synthetic dataset; targeted v6 data improved blind tool-choice heldout observation faithfulness from 0.945 to 0.985 while v4/v5 heldout core metrics remained 1.0.
- Established a reproducible remote experiment workflow with preflight checks, dry runs, tmux launches, log monitoring, checkpoint paths, and local experiment records.
```

## Interview Talking Points

Use this structure when explaining the project:

1. The original project only had simple multi-hop QA synthesis, so I reframed it as an Agentic Synthetic Data Factory.
2. I did not just generate more data; I built verifiers and harder heldouts to find where the model was wrong.
3. The key failure was evidence drift: the final country answer was correct, but the `Observation:` line sometimes used an unsupported intermediate location.
4. I generated targeted v6 blind tool-choice data and retrained Qwen3-8B LoRA.
5. The fix improved observation faithfulness from 0.945 to 0.985 and did not regress previous v4/v5 heldouts.

Concrete example:

```text
Before v6-targeted training, the model sometimes wrote `Observation: New York` instead of `New York City`, or `Observation: Tokyo` instead of `Osaka`, while still answering `United States` or `Japan` correctly. The v6 verifier made this visible because it scores intermediate tool observations, not just final answer accuracy.
```

## Verified Numbers

| Run | Heldout | Exact | Tool success | Observation faithfulness | Trajectory valid | Hallucination |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 2k mixed v3/v4/v5blind | v4 heldout200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| 2k mixed v3/v4/v5blind | v5 blind-hard heldout200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| 2k mixed v3/v4/v5blind | v6 blind tool-choice heldout200 | 1.000 | 1.000 | 0.945 | 1.000 | 0.000 |
| 2.4k mixed v3/v4/v5blind/v6 | v4 heldout200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| 2.4k mixed v3/v4/v5blind/v6 | v5 blind-hard heldout200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| 2.4k mixed v3/v4/v5blind/v6 | v6 blind tool-choice heldout200 | 1.000 | 1.000 | 0.985 | 1.000 | 0.000 |

Training record:

```text
Model: Qwen3-8B
Method: LoRA SFT
Data: 2.4k mixed synthetic rows
GPU: 4 remote GPUs
Epochs: 1
Optimization steps: 72
Runtime: 134.378s
Train loss: 0.3729
```

## Evidence Records

Key local records:

```text
docs/experiments/2026-06-13-canonical-v6-blind-tool-choice-hard-heldout.md
docs/experiments/2026-06-13-qwen3-8b-mixed-v6-blind-tool-choice-heldout200-eval.md
docs/experiments/2026-06-13-qwen3-8b-mixed-v3-v4-v5blind-v6-data-smoke.md
docs/experiments/2026-06-13-qwen3-8b-mixed-v3-v4-v5blind-v6-sft-gpu0125.md
docs/experiments/2026-06-13-qwen3-8b-mixed-v6trained-v6-heldout200-eval.md
docs/experiments/2026-06-13-qwen3-8b-mixed-v6trained-v4-v5-regression-eval.md
```

## Do Not Claim Yet

Do not claim:

- 20k or 50k data scale
- GRPO / verl / RL gains
- broad public benchmark improvements
- Qwen 14B or 32B training results
- production-grade general tool-use ability

Accurate limitation:

```text
The verified loop is currently strongest on a controlled Wikidata birthplace-to-country reasoning family. The next planned step is a relation-diverse v7 split with more tool-choice paths.
```
