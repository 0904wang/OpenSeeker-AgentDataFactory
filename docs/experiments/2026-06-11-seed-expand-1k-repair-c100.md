# 2026-06-11 Seed Expand 1k Repair C100

## Goal

Generate 1,000 teacher-drafted OpenSeeker AgentDataFactory samples after adding the teacher trajectory repair gate. The run tests whether high-concurrency DeepSeek teacher generation can produce a full SFT-ready batch while preserving verifier metrics and recording repair/fallback behavior.

## Remote Setup

- Remote entrypoint: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Remote repo: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Remote branch: `main`
- Remote commit before local narrow sync: `7b64c03`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- Secret file: `/data/wzl/OpenSeeker-AgentDataFactory/.secrets/deepseek.env`
- Launcher: `/data/wzl/OpenSeeker-AgentDataFactory/runs/launch-seed1k-repair-20260611.sh`
- Tmux session: `openseeker-20260611-seed1k-repair`
- Log path: `/data/wzl/OpenSeeker-AgentDataFactory/logs/seed-expand-1k-repair-20260611.log`
- Results dir: `/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611`

The run did not use GPUs. `CUDA_VISIBLE_DEVICES` was set to empty.

## Preflight

Remote smoke and dry run passed before launch:

```text
python -m pytest: 45 passed in 4.22s
demo --count 3: accepted=3 rejected=0
teacher API smoke --count 1: accepted=1 rejected=0
```

Teacher API smoke summary:

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,evidence_faithfulness_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
1,1,0,1.0,1.0,1.0,1.0,1.0,1.0,1,1,0,0.0,0,0,
```

## Launch Command

The run used this launcher through tmux:

```bash
cd /data/wzl/OpenSeeker-AgentDataFactory/repo
source /home/user/anaconda3/etc/profile.d/conda.sh
conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory
source /data/wzl/OpenSeeker-AgentDataFactory/.secrets/deepseek.env
export CUDA_VISIBLE_DEVICES=
export PYTHONNOUSERSITE=1
python -m openseeker_factory.cli generate \
  --count 1000 \
  --seed-file /data/wzl/OpenSeeker-AgentDataFactory/data/seeds/wikidata_seed_expanded.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611 \
  --strategy magpie_self_instruct \
  --teacher-backend openai-compatible \
  --teacher-base-url https://api.deepseek.com \
  --teacher-model deepseek-v4-pro \
  --teacher-api-key-env DEEPSEEK_API_KEY \
  --teacher-timeout-s 60 \
  --teacher-concurrency 100 \
  --batch-size 100 \
  --resume
```

## Final Results

Raw summary:

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,evidence_faithfulness_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
1000,1000,0,1.0,1.0,1.0,1.0,1.0,1.0,1000,978,22,0.022,11,34,
```

Output line counts:

```text
1000 raw_generations.jsonl
1000 samples.jsonl
1000 sft_conversations.jsonl
1000 rl_rewards.jsonl
1000 trace.jsonl
```

Additional distribution checks:

```text
task_type:
  multi_hop_qa: 334
  tool_use_qa: 333
  noisy_context_retrieval_qa: 333

difficulty:
  easy: 272
  medium: 651
  hard: 77

teacher_status:
  teacher: 978
  fallback: 22

repair_reason:
  none: 989
  react_format: 11

quality_score:
  1.0: 1000

verifier_failed:
  0
```

Final log excerpt:

```text
progress 991/1000 id=wikidata-jane-goodall-noisy-918 teacher_status=teacher accepted=pending
progress 992/1000 id=wikidata-leonardo-da-vinci-multi-hop-991 teacher_status=teacher accepted=pending
progress 993/1000 id=wikidata-yukihiro-matsumoto-multi-hop-958 teacher_status=teacher accepted=pending
progress 994/1000 id=wikidata-leonardo-da-vinci-noisy-993 teacher_status=teacher accepted=pending
progress 995/1000 id=wikidata-rosalind-franklin-tool-998 teacher_status=teacher accepted=pending
progress 996/1000 id=wikidata-tu-youyou-noisy-915 teacher_status=teacher accepted=pending
progress 997/1000 id=wikidata-dorothy-hodgkin-noisy-927 teacher_status=teacher accepted=pending
progress 998/1000 id=wikidata-hedy-lamarr-multi-hop-931 teacher_status=teacher accepted=pending
progress 999/1000 id=wikidata-claude-shannon-multi-hop-934 teacher_status=teacher accepted=pending
progress 1000/1000 id=wikidata-claude-shannon-tool-935 teacher_status=teacher accepted=pending
batch complete: completed=1000/1000 accepted=1000 rejected=0
OpenSeeker AgentDataFactory generation complete: accepted=1000 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/seed-expand-1k-repair-20260611
```

Final GPU memory snapshot:

```text
0, 3506 MiB, 32607 MiB
1, 3505 MiB, 32607 MiB
2, 3507 MiB, 32607 MiB
3, 25985 MiB, 32607 MiB
4, 26101 MiB, 32607 MiB
5, 3493 MiB, 32607 MiB
6, 3505 MiB, 32607 MiB
7, 18 MiB, 32607 MiB
```

## Notes and Issues

- The run completed successfully with 1,000 accepted samples and 0 verifier failures.
- Teacher success rate was 97.8%. The 22 fallback samples came from API/backend failures or timeouts and were filled by deterministic seed-derived generation.
- `teacher_trajectory_repaired=11`, all observed repair reasons were `react_format`. No `evidence_faithfulness` repair appeared in this 1k batch.
- Batch 8 showed a cluster of fallbacks, which suggests concurrency 100 may trigger tail latency or transient rate limiting even though the final run completed.
- The initial launcher file was written from PowerShell with CRLF line endings, which produced a log filename ending in hidden `\r`. After completion, the log was renamed to the canonical path and the launcher was converted to Unix line endings.

## Analysis

This is a usable SFT batch for the next training step. The verifier layer is strict enough to produce 100% accepted/faithful exported data on this seed setting, while repair and fallback metrics give concrete engineering evidence for resume reporting.

The main operational tradeoff is concurrency. `--teacher-concurrency 100` finished the run, but it increased tail latency and caused a visible fallback cluster. For larger 5k or 20k generation, concurrency 50 with batch size 100 is likely a safer default unless throughput is the main priority.

## Next Steps

- Run a quick sample audit over 50 to 100 rows from `samples.jsonl`, including teacher fallback and repaired examples.
- Use this 1k dataset as an SFT candidate or combine it with the earlier 1k set after deduplication.
- For the next generation scale-up, prefer `--teacher-concurrency 50` and keep `--batch-size 100 --resume`.
- Update README or experiment plan with observed 1k generation metrics and the concurrency recommendation.
