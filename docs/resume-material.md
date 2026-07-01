# Resume Material

Use this file to keep resume wording honest. Only use claims backed by local records under `docs/experiments/`.

## Verified Project Summary

OpenSeeker AgentDataFactory is now a verified synthetic-data, SFT, and RFT loop for tool-use / retrieval agents:

- The data factory covers multi-hop QA, tool-use QA, noisy-context retrieval QA, ReAct trajectory export, verifier filtering, and LLaMA-Factory SFT export.
- The remote workflow is reproducible on the lab GPU server with preflight checks, narrow file sync, project-local conda env, tmux launches, logs, checkpoints, and local experiment records.
- The strongest SFT baseline uses Qwen3-8B + LoRA on 2.4k mixed synthetic rows and reaches v6 observation faithfulness `0.985`.
- RFT / ReST-EM Round 1 samples 9.6k trajectories from the SFT checkpoint, verifier-filters 9,429 all-pass candidates, retains 1,095 changed trajectories, and continues SFT on a 3.5k mixed dataset.
- Main measured result: v6 blind tool-choice heldout failures drop from `3/200` to `0/200` after RFT Round 1, while v4/v5 heldouts remain at all core metrics `1.0`.
- A harder v7 relation-diverse heldout is now implemented and evaluated; it exposes remaining generalization gaps beyond the birthplace-to-country path, with current strict correct rate `0.605`.

## Resume Bullets: Chinese

Long version:

```text
OpenSeeker AgentDataFactory                                      Agent SFT / 数据合成
个人项目
- 构建面向多跳检索、工具调用与 noisy-context QA 的可验证 Agent 数据合成流水线，统一输出 ReAct 轨迹、tool calls、gold evidence、verifier result、SFT conversation、RL reward format 与评测 trace/summary。
- 设计 canonical-v4/v5/v6 数据版本与 deterministic verifier，覆盖答案可解性、工具调用覆盖率、Observation 证据忠实度、轨迹格式有效性和幻觉代理指标；通过 harder heldout 暴露“最终答案正确但中间证据漂移”的失败模式。
- 使用远程 GPU 服务器完成 Qwen3-8B LoRA SFT：从 2k mixed v3/v4/v5blind 基线出发，针对 v6 blind tool-choice 失败模式补充 400 条定向合成数据，形成 2.4k mixed SFT 数据集。
- 实现 verifier-filtered RFT/ReST-EM：从 SFT checkpoint 采样 9.6k 条轨迹，过滤得到 9,429 条四项检查全过样本，仅保留 1,095 条非重复 changed trajectories 进行继续 SFT，避免重复轨迹灌入造成的数据坍塌。
- 在 v6 blind tool-choice heldout200 上将失败样本从 11/200 降至 3/200，并在 RFT Round 1 后进一步降至 0/200；同时 v4 heldout200 与 v5 blind-hard heldout200 的 exact/tool/trajectory/correct 等核心指标保持 1.0。
- 制定共享 GPU 远程实验规范，固化 preflight、dry run、tmux 启动、日志监控、checkpoint 管理和本地实验记录流程，保证数据生成、训练和评测结果可复现、可审计。
```

Shorter 3-bullet version:

```text
- 构建 OpenSeeker AgentDataFactory，面向多跳检索、工具调用与 noisy-context QA 生成可验证 ReAct SFT 数据，统一导出 samples、SFT conversations、RL reward format、trace JSONL 与 summary CSV。
- 设计 v4/v5/v6 harder heldout 与 evidence/tool/trajectory verifier，定位“最终答案正确但 Observation 中间证据漂移”的失败模式，并用定向 v6 合成数据和 RFT/ReST-EM 闭环修复。
- 使用远程 GPU 完成 Qwen3-8B LoRA SFT 与 verifier-filtered RFT：从 9.6k 自采样轨迹中过滤 9,429 条全过候选，仅保留 1,095 条 changed trajectories 继续训练，将 v6 heldout 失败数从 3/200 降至 0/200，且 v4/v5 核心指标保持 1.0。
```

## Resume Bullets: English

```text
OpenSeeker AgentDataFactory                                      Agent SFT / Synthetic Data
Personal Project
- Built a verifiable synthetic-data pipeline for multi-hop retrieval, tool-use QA, and noisy-context QA agents, exporting ReAct trajectories, tool calls, gold evidence, verifier results, SFT conversations, reward-format rows, and evaluation traces.
- Designed canonical-v4/v5/v6 data versions and deterministic verifiers for answer support, tool-call coverage, observation faithfulness, trajectory validity, and hallucination proxy metrics.
- Ran Qwen3-8B LoRA SFT on a remote GPU server with a 2.4k mixed synthetic dataset; targeted v6 data improved blind tool-choice heldout observation faithfulness from 0.945 to 0.985.
- Implemented verifier-filtered RFT/ReST-EM from the SFT checkpoint, sampling 9.6k trajectories, filtering 9,429 all-pass candidates, retaining 1,095 changed trajectories for continued SFT, and reducing v6 heldout failures from 3/200 to 0/200 without v4/v5 regression.
- Established a reproducible remote experiment workflow with preflight checks, dry runs, tmux launches, log monitoring, checkpoint paths, and local experiment records.
```

## Interview Talking Points

Use this structure when explaining the project:

1. The original project only had simple multi-hop QA synthesis, so I reframed it as an Agentic Synthetic Data Factory.
2. I did not just generate more data; I built verifiers and harder heldouts to find where the model was wrong.
3. The key failure was evidence drift: the final country answer was correct, but the `Observation:` line sometimes used an unsupported intermediate location.
4. I generated targeted v6 blind tool-choice data and retrained Qwen3-8B LoRA, improving observation faithfulness from `0.945` to `0.985`.
5. I then ran RFT/ReST-EM from the SFT checkpoint, but trained only on changed verifier-passing trajectories, which removed the remaining v6 failures without regressing v4/v5.

Concrete example:

```text
Before v6-targeted training, the model sometimes wrote `Observation: New York` instead of `New York City`, or `Observation: Tokyo` instead of `Osaka`, while still answering `United States` or `Japan` correctly. The v6 verifier made this visible because it scores intermediate tool observations, not just final answer accuracy.
```

## Verified Numbers

Heldout evaluation:

| Run | Heldout | Failures | Exact | Tool success | Observation faithfulness | Trajectory valid | Hallucination |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2k mixed v3/v4/v5blind | v4 heldout200 | 0/200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| 2k mixed v3/v4/v5blind | v5 blind-hard heldout200 | 0/200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| 2k mixed v3/v4/v5blind | v6 blind tool-choice heldout200 | 11/200 | 1.000 | 1.000 | 0.945 | 1.000 | 0.000 |
| 2.4k mixed v3/v4/v5blind/v6 A0 | v4 heldout200 | 0/200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| 2.4k mixed v3/v4/v5blind/v6 A0 | v5 blind-hard heldout200 | 0/200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| 2.4k mixed v3/v4/v5blind/v6 A0 | v6 blind tool-choice heldout200 | 3/200 | 1.000 | 1.000 | 0.985 | 1.000 | 0.000 |
| 3.5k SFT + RFT changed round1 | v4 heldout200 | 0/200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| 3.5k SFT + RFT changed round1 | v5 blind-hard heldout200 | 0/200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| 3.5k SFT + RFT changed round1 | v6 blind tool-choice heldout200 | 0/200 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |

RFT Round 1:

| Metric | Value |
| --- | ---: |
| Source checkpoint | 2.4k mixed A0 restore |
| Training prompts | 2,400 |
| Sampling K | 4 |
| Sampled candidates | 9,600 |
| Verifier all-pass candidates | 9,429 |
| Rejected candidates | 171 |
| Verifier pass rate | 0.9822 |
| Accepted exact-gold trajectories | 8,334 |
| Accepted changed trajectories used for continued SFT | 1,095 |

Training records:

```text
SFT A0 restore:
Model: Qwen3-8B
Method: LoRA SFT
Data: 2.4k mixed synthetic rows
GPU: 4 remote GPUs
Runtime: 135.7892s
Train loss: 0.3726

RFT changed-only continued SFT:
Model: Qwen3-8B
Method: LoRA SFT
Data: 3.5k mixed rows = 2.4k base + 1,095 changed RFT rows
GPU: remote GPUs 0,6
Runtime: 388.64s
Train loss: 0.0059
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
docs/experiments/2026-07-01-qwen3-8b-a0-restore-sft.md
docs/experiments/2026-07-01-rft-round1-a0-k4-t1p0.md
docs/experiments/2026-07-01-sft-rft-round1-changed-3p5k-gpu06.md
docs/experiments/2026-07-01-rftchanged-round1-v6-v4-v5-eval.md
```

## Do Not Claim Yet

Do not claim:

- 20k or 50k data scale
- GRPO / verl / RL gains
- broad public benchmark improvements
- Qwen 14B or 32B training results
- production-grade general tool-use ability
- solved relation-diverse tool-use generalization

Accurate limitation:

```text
The verified RFT loop solves the controlled birthplace-to-country heldouts, but the v7 relation-diverse heldout shows remaining gaps on education, employer, and award relation paths. The next step is targeted v7 data plus SFT/RFT and v4/v5/v6 regression checks.
```
