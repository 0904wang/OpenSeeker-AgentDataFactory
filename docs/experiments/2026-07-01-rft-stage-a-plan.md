# RFT Stage A Plan

## Metadata

- Experiment name: rft-stage-a-rest-em
- Date: 2026-07-01
- Goal: Restore the deleted best SFT checkpoint, then run one verifier-filtered RFT/ReST-EM round from that checkpoint.
- Status: planned
- Operator: Codex
- Remote host: `user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`

## Baseline To Restore

The previous best SFT-only run used the 2.4k mixed v3/v4/v5blind/v6blindtoolchoice dataset.

Known metrics before checkpoint cleanup:

| Run | Data | Heldout | Failure Count | Key Metric |
| --- | --- | --- | --- | --- |
| SFT-only A0 | 2.4k mixed | v6 blind tool-choice heldout200 | 3/200 | observation faithfulness `0.985` |
| SFT-only A0 | 2.4k mixed | v4 heldout200 | 0/200 | all core metrics `1.0` |
| SFT-only A0 | 2.4k mixed | v5 blind-hard heldout200 | 0/200 | all core metrics `1.0` |

The remote checkpoint directory was cleaned, so A0 must be restored before RFT sampling.

## Restore A0 Command

Launcher:

```bash
/data/wzl/OpenSeeker-AgentDataFactory/repo/runs/launch_sft_mixed_v3_v4_v5blind_v6blindtoolchoice_2p4k_restore_a0_gpu0125.sh
```

Expected checkpoint:

```bash
/data/wzl/OpenSeeker-AgentDataFactory/checkpoints/qwen3-8b-openseeker-sft-2p4k-mixed-v3-v4-v5blind-v6blindtoolchoice-a0-restore-20260701
```

Expected log:

```bash
/data/wzl/OpenSeeker-AgentDataFactory/logs/20260701-restore-a0-qwen3-8b-sft-2p4k-gpu0125.log
```

## RFT Round 1 Plan

1. Sample `K=4` trajectories per training prompt from restored A0.
2. Use deterministic verifier checks:
   - `answer_supported`
   - `tool_success`
   - `evidence_faithfulness`
   - `trajectory_valid`
3. Export accepted trajectories as new SFT data.
4. Record verifier pass rate and diversity:
   - sampled total
   - accepted total
   - verifier pass rate
   - unique trajectory rate
   - unique action sequence rate
   - per task-type pass rate
5. Train one continued SFT adapter from A0 + accepted RFT trajectories.
6. Evaluate v6 first, then v4/v5 regression.

## Approval Gates

No real remote training, sampling, or RFT SFT launch should start until the exact session, command, GPU list, log path, results path, and checkpoint path have been reported and approved.
