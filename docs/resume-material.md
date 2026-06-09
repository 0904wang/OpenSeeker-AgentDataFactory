# Resume Material

Use this file to keep resume wording honest. Move bullets from "planned" to "verified" only after a local experiment record proves the result.

## Current Verified Version

Safe to say now:

- Built a local OpenSeeker AgentDataFactory scaffold for multi-hop QA, tool-use QA, and noisy-context retrieval QA, with ReAct-style trajectories and deterministic verifier filtering.
- Defined a unified JSONL schema covering `id`, `task_type`, `question`, `answer`, `gold_evidence`, `tool_calls`, `trajectory`, `verifier_result`, `difficulty`, `source`, and `quality_score`.
- Implemented exports for Agent SFT conversations, reward-format samples, trace JSONL, and summary CSV, with pytest coverage for schema, pipeline, exports, and CLI behavior.
- Added a remote experiment safety contract for a shared 8-GPU lab server, including preflight, dry run, tmux launch, GPU limits, approved paths, and local experiment recording.

## After Remote Smoke Test

Use only after a local record proves the remote run:

- Ported the OpenSeeker AgentDataFactory pipeline to a shared GPU server and validated the end-to-end dry run under a constrained remote workflow with preflight, tmux monitoring, and local experiment records.

## After 5k / 20k Data Runs

Template:

- Generated `<N>` synthetic Agent SFT samples covering multi-hop retrieval, tool-use QA, and noisy-context reasoning; applied verifier-based filtering over answer support, evidence coverage, tool success, trajectory validity, and deduplication.
- Recorded quality metrics including accepted rate `<x>%`, evidence hit rate `<x>%`, tool success rate `<x>%`, trajectory validity `<x>%`, and manual sample pass rate `<x>%` over `<n>` audited samples.

## After SFT / RL Validation

Template:

- Fine-tuned Qwen `<7B/14B>` with verified OpenSeeker synthetic data and compared baseline, old 5k data, and new `<20k/50k>` data on multi-hop completion, tool-call success, and hallucination metrics.
- Improved `<metric>` from `<baseline>` to `<result>` while preserving trace-level evidence and ablation logs for verifier, Evol-Instruct, and noisy-context components.

## Current One-Page Resume Replacement Draft

This can replace the old `OpenSeeker 数据合成` project only if you want to emphasize system construction before remote results:

```text
OpenSeeker AgentDataFactory                                                        Agent SFT / 数据合成
个人项目
• 面向多跳检索、工具调用与 noisy-context reasoning 设计可验证 Agent 数据合成流水线，覆盖 seed_expand、evolve_task、ReAct 轨迹生成、verifier 过滤与 trace 记录。
• 统一 JSONL 数据协议，包含 question、gold_evidence、tool_calls、trajectory、verifier_result 与 quality_score，并支持 Agent SFT conversation、RL reward-format、summary CSV 导出。
• 参考 Self-Instruct/Magpie、WizardLM/Evol-Instruct、ToolBench/AgentTuning 等路线设计数据扩展与质量筛选方案，补充远程 4 卡实验规范、dry-run 门禁与实验记录模板。
```

## Stronger Draft After Experiments

Do not use until metrics are available:

```text
OpenSeeker AgentDataFactory                                                        Agent SFT / 数据合成
个人项目
• 基于 Wikidata 事实图谱与工具调用环境构建可验证 Agent 数据合成流水线，结合 Self-Instruct/Evol-Instruct、ReAct 轨迹生成与 verifier rejection sampling，产出 <N> 条多跳检索/工具调用 SFT 数据。
• 设计 evidence verifier、tool execution verifier 与 trajectory verifier，统计可解率、轨迹有效率、证据命中率与人工抽样通过率，并通过 ablation 分析数据复杂度和过滤策略影响。
• 使用 <GPU 配置> 完成本地/远程批量生成与 Qwen <7B/14B> LoRA SFT；相比原 5k 数据基线，在 <metric> 上从 <baseline> 提升至 <result>。
```

