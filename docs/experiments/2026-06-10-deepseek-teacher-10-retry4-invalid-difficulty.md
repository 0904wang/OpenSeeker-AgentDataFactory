# DeepSeek Teacher 10 Retry4 Invalid Difficulty

## Metadata

- Experiment name: deepseek-teacher-10-retry4-20260610
- Date: 2026-06-10
- Goal: Retry DeepSeek-backed teacher generation after timeout fallback.
- Status: failed before artifact export
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Branch: `main`
- Commit: `e8ae22b`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- Number of GPUs: 0
- tmux session: `openseeker-20260610-deepseek-teacher-10-retry4`
- Model: `deepseek-v4-pro`
- Base URL: `https://api.deepseek.com`

## Paths

- Log path: `/data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-10-retry4-20260610.log`
- Results path: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-10-retry4-20260610`
- Checkpoint path: not applicable
- Run path: not applicable

## Raw Result Summary

No sample artifacts were exported.

The run reached sample construction but failed schema validation:

```text
ValueError: difficulty must be one of ['easy', 'hard', 'medium']
```

## Notes and Analysis

- The timeout fallback fix moved the pipeline further, but teacher-provided `difficulty` is still an untrusted LLM field.
- `difficulty` should be normalized to `medium` when it is outside the allowed enum.
- The original teacher difficulty should be recorded in `source` for auditability.

## Next Step Thoughts

- Add difficulty normalization with a regression test.
- Retry again with a fresh result directory after the fix.
