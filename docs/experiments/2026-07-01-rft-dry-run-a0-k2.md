# RFT Dry Run From Restored A0

## Metadata

- Experiment name: rft-dry-run-a0-k2
- Date: 2026-07-01
- Goal: Verify that restored A0 can sample RFT candidates and that deterministic verifier filtering exports accepted RFT SFT data.
- Status: success
- Operator: Codex
- Remote host: `user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Local branch: `codex/rft-rejection-sampling`
- Local commits: `0eaf540`, `8079abf`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: `CUDA_VISIBLE_DEVICES=0`
- Number of GPUs: 1

## Commands

Build the RFT sample file from the 2.4k mixed SFT components:

```bash
/data/wzl/OpenSeeker-AgentDataFactory/data/rft/openseeker_agent_samples_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice.jsonl
```

Composition after rewriting duplicate ids:

```text
rows 2400
unique_ids 2400
duplicates 0
versions {'canonical-v3': 800, 'canonical-v4': 800, 'canonical-v5-blind-hard': 400, 'canonical-v6-blind-tool-choice-hard': 400}
task_types {'multi_hop_qa': 800, 'tool_use_qa': 800, 'noisy_context_retrieval_qa': 800}
components {'v3': 800, 'v4': 800, 'v5blind': 400, 'v6blindtoolchoice': 400}
```

Dry-run launcher:

```bash
/data/wzl/OpenSeeker-AgentDataFactory/repo/runs/launch_rft_dry_run_a0_k2_20260701.sh
```

Effective sampling command:

```bash
CUDA_VISIBLE_DEVICES=0 PYTHONNOUSERSITE=1 python -m openseeker_factory.cli sample-rft-candidates \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/data/rft/openseeker_agent_samples_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/rft-dry-run-a0-k2-20260701 \
  --model-label qwen3-8b-a0-restore-rft-dry-run \
  --model-name-or-path /data/wzl/OpenSeeker-AgentDataFactory/.cache/huggingface/transformers/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218 \
  --adapter-path /data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice-a0-restore-20260701 \
  --num-return-sequences 2 \
  --temperature 0.7 \
  --top-p 0.95 \
  --limit 2 \
  --batch-size 1 \
  --max-new-tokens 160 \
  --local-files-only \
  --disable-thinking \
  --seed 20260701
```

Effective filter command:

```bash
PYTHONNOUSERSITE=1 python -m openseeker_factory.cli rft-filter \
  --samples /data/wzl/OpenSeeker-AgentDataFactory/data/rft/openseeker_agent_samples_2p4k_mixed_v3_v4_v5blind_v6blindtoolchoice.jsonl \
  --prediction-file /data/wzl/OpenSeeker-AgentDataFactory/results/rft-dry-run-a0-k2-20260701/candidate_predictions.jsonl \
  --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/rft-dry-run-a0-k2-20260701 \
  --model-label qwen3-8b-a0-restore-rft-dry-run \
  --iteration 1
```

## Paths

- Sample log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/rft-dry-run-a0-k2-20260701-sample.log`
- Filter log: `/data/wzl/OpenSeeker-AgentDataFactory/logs/rft-dry-run-a0-k2-20260701-filter.log`
- Results path: `/data/wzl/OpenSeeker-AgentDataFactory/results/rft-dry-run-a0-k2-20260701`
- Candidate predictions: `/data/wzl/OpenSeeker-AgentDataFactory/results/rft-dry-run-a0-k2-20260701/candidate_predictions.jsonl`
- Accepted RFT SFT: `/data/wzl/OpenSeeker-AgentDataFactory/results/rft-dry-run-a0-k2-20260701/rft_sft_conversations.jsonl`

## Raw Result Summary

Sampling:

```text
sampled 1 sample_id=rftmix-0001-v3-wikidata-ada-lovelace-multi-hop-1 candidate_index=0
sampled 2 sample_id=rftmix-0001-v3-wikidata-ada-lovelace-multi-hop-1 candidate_index=1
sampled 3 sample_id=rftmix-0002-v3-wikidata-ada-lovelace-tool-2 candidate_index=0
sampled 4 sample_id=rftmix-0002-v3-wikidata-ada-lovelace-tool-2 candidate_index=1
OpenSeeker RFT sampling complete: candidates=4 predictions=/data/wzl/OpenSeeker-AgentDataFactory/results/rft-dry-run-a0-k2-20260701/candidate_predictions.jsonl
```

Filtering:

```text
OpenSeeker RFT filter complete: sampled=4 accepted=4 rejected=0 pass_rate=1.0 out_dir=/data/wzl/OpenSeeker-AgentDataFactory/results/rft-dry-run-a0-k2-20260701
```

Summary:

```json
{
  "sampled_total": 4,
  "accepted_total": 4,
  "rejected_total": 0,
  "verifier_pass_rate": 1.0,
  "unique_trajectory_rate": 0.25,
  "unique_action_sequence_rate": 0.25,
  "per_task_type": {
    "multi_hop_qa": {
      "sampled_total": 2,
      "accepted_total": 2,
      "rejected_total": 0,
      "pass_rate": 1.0
    },
    "tool_use_qa": {
      "sampled_total": 2,
      "accepted_total": 2,
      "rejected_total": 0,
      "pass_rate": 1.0
    }
  }
}
```

## Metrics

| Metric | Value | Notes |
| --- | --- | --- |
| sampled_total | 4 | 2 prompts x K=2 |
| accepted_total | 4 | all candidates passed |
| rejected_total | 0 | none |
| verifier_pass_rate | 1.0 | deterministic checks all passed |
| unique_trajectory_rate | 0.25 | low diversity |
| unique_action_sequence_rate | 0.25 | low action diversity |

## Failures / Warnings

- The first direct SSH dry-run command closed with `Connection closed by 58.253.68.15 port 29509` before producing output. The dry run was then launched through a narrow synced tmux launcher.
- RFT sample file initially had only 800 unique ids because v3/v4/v5/v6 reused seed ids. The file was rebuilt with unique ids and original ids preserved in `source.rft_original_id`.

## Analysis

The restored A0 adapter is usable for RFT candidate generation, and the verifier/filter/export path works end to end.

The important warning is diversity: at `temperature=0.7`, the small dry run accepted everything but produced essentially one trajectory/action pattern. Full RFT should use a higher sampling temperature such as `1.0` and `top_p=0.98`, then decide whether the filtered data is useful based on pass rate plus diversity rather than pass rate alone.

## Next Steps

- Run RFT Round 1 sampling on the full 2.4k prompt set with `K=4`, `temperature=1.0`, `top_p=0.98`.
- Filter candidates and record pass rate plus diversity.
- Only train the RFT adapter if accepted trajectories are both numerous and non-trivially diverse.
