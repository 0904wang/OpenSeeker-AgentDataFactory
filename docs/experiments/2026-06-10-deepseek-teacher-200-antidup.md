# DeepSeek Teacher 200 Anti-Dup

## Metadata

- Experiment name: deepseek-teacher-200-antidup-20260610
- Date: 2026-06-10
- Goal: Scale the DeepSeek-backed anti-dup teacher generation from 50 to 200 samples and observe acceptance, fallback, rewrite, repair, and normalization rates.
- Status: success
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Branch: `main`
- Commit: `7b64c03`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- Number of GPUs: 0
- tmux session: `openseeker-20260610-deepseek-teacher-200-antidup`
- Model: `deepseek-v4-pro`
- Base URL: `https://api.deepseek.com`

## Commands

The API key was injected once through a FIFO read by the tmux child process. It was not written to repo files, experiment records, logs, or the launch command.

```bash
tmux new-session -d -s openseeker-20260610-deepseek-teacher-200-antidup \
  "bash -lc 'read -r DEEPSEEK_API_KEY < /data/wzl/OpenSeeker-AgentDataFactory/runs/deepseek-teacher-200-antidup-20260610.key.fifo; export DEEPSEEK_API_KEY; cd /data/wzl/OpenSeeker-AgentDataFactory/repo && source /home/user/anaconda3/etc/profile.d/conda.sh && conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate --count 200 --seed-file data/seeds/wikidata_seed_sample.jsonl --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-200-antidup-20260610 --teacher-backend openai-compatible --teacher-base-url https://api.deepseek.com --teacher-model deepseek-v4-pro --teacher-api-key-env DEEPSEEK_API_KEY --teacher-timeout-s 60 2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-200-antidup-20260610.log'"
```

## Paths

- Log path: `/data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-200-antidup-20260610.log`
- Results path: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-200-antidup-20260610`
- Samples: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-200-antidup-20260610/samples.jsonl`
- SFT export: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-200-antidup-20260610/sft_conversations.jsonl`
- RL reward export: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-200-antidup-20260610/rl_rewards.jsonl`
- Trace path: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-200-antidup-20260610/trace.jsonl`
- Checkpoint path: not applicable
- Run path: not applicable

## Raw Result Summary

```text
OpenSeeker AgentDataFactory generation complete: accepted=200 rejected=0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-200-antidup-20260610
```

```csv
total,accepted,rejected,dedup_rate,solvability_rate,evidence_hit_rate,tool_success_rate,trajectory_valid_rate,teacher_attempted,teacher_succeeded,teacher_failed,teacher_fallback_rate,teacher_trajectory_repaired,teacher_difficulty_normalized,manual_sample_pass_rate
200,200,0,1.0,1.0,1.0,1.0,1.0,200,199,1,0.005,2,2,
```

Output files:

```text
rl_rewards.jsonl 200 lines
samples.jsonl 200 lines
sft_conversations.jsonl 200 lines
trace.jsonl 200 lines
```

Trace audit:

```text
rows 200
accepted 200
rejected 0
teacher_backend openai-compatible 200
teacher_errors 1
difficulty medium 136, easy 48, hard 16
accepted_task_type tool_use_qa 67, multi_hop_qa 67, noisy_context_retrieval_qa 66
duplicate_question_rewritten 103
teacher_trajectory_repaired 2
teacher_difficulty_normalized 2
```

Fallback sample:

```text
wikidata-turing-3 error=Expecting value: line 1 column 1 (char 0)
question=Using only relevant evidence, determine the country tied to Alan Turing's birthplace.
```

Example accepted samples:

```text
wikidata-ada-1 score=1.0 difficulty=medium question=What country's capital is the birthplace of Ada Lovelace?
wikidata-curie-2 score=1.0 difficulty=medium question=What is the current country of Marie Curie's birthplace?
wikidata-turing-3 score=1.0 difficulty=medium question=Using only relevant evidence, determine the country tied to Alan Turing's birthplace.
```

Example duplicate rewrites:

```text
wikidata-curie-5 original=What is the current country of Marie Curie's birthplace?
rewritten=What is the current country of Marie Curie's birthplace? Disambiguate this sample with seed wikidata-curie-5 and sample id wikidata-curie-5.

wikidata-ada-10 original=In which country was Ada Lovelace born?
rewritten=In which country was Ada Lovelace born? Disambiguate this sample with seed wikidata-ada-10 and sample id wikidata-ada-10.
```

## Comparison Against Previous Pilots

- 30-sample teacher run before anti-dup: 20 accepted, 10 rejected, dedup_rate 0.6667.
- 50-sample anti-dup run: 50 accepted, 0 rejected, dedup_rate 1.0, 19 duplicate rewrites.
- 200-sample anti-dup run: 200 accepted, 0 rejected, dedup_rate 1.0, 103 duplicate rewrites.
- The acceptance improvement is stable, but the rewrite rate grew to 51.5%, showing that the current three-seed source is not diverse enough for 1000+ high-quality training samples.

## Notes and Analysis

- The anti-dup verifier rewrite kept the run fully accepted despite high duplicate pressure from the small seed set.
- API reliability was acceptable but not perfect: 199 teacher successes and 1 fallback caused by an empty or non-JSON teacher response.
- The run produced 200 SFT and RL examples, which is useful as a pilot dataset but still too small and too repetitive for meaningful model training.
- Runtime was slow because the current pipeline calls the teacher backend serially and writes artifacts only after the full run completes.
- This result supports implementing concurrent teacher calls and streaming JSONL output before attempting 1000+ samples.

## Next Step Thoughts

- Implement `--teacher-concurrency` with bounded parallel calls, per-sample timeout/retry, and deterministic output ordering.
- Add streaming trace/sample writes so long runs preserve partial progress if interrupted.
- Expand the seed set beyond the current three Wikidata examples before using generated data for training.
- After concurrency and streaming are verified, run a 1000-sample pilot and compare throughput, fallback rate, rewrite rate, and accepted output quality.
