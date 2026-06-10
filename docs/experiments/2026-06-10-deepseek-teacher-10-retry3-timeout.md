# DeepSeek Teacher 10 Retry3 Timeout

## Metadata

- Experiment name: deepseek-teacher-10-retry3-20260610
- Date: 2026-06-10
- Goal: Retry DeepSeek-backed teacher generation after deterministic ReAct trajectory repair.
- Status: failed before artifact export
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Branch: `main`
- Commit: `c1144ff`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- Number of GPUs: 0
- tmux session: `openseeker-20260610-deepseek-teacher-10-retry3`
- Model: `deepseek-v4-pro`
- Base URL: `https://api.deepseek.com`

## Paths

- Log path: `/data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-10-retry3-20260610.log`
- Results path: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-10-retry3-20260610`
- Checkpoint path: not applicable
- Run path: not applicable

## Raw Result Summary

No sample artifacts were exported.

The run failed while reading a chunked HTTPS response:

```text
TimeoutError: The read operation timed out
```

No API key appeared in the process command line for this retry. The key was passed through the parent shell environment inherited by tmux rather than `tmux -e`.

## Notes and Analysis

- The previous trajectory-format issue was not reached because the API call timed out before export.
- The current pipeline builds all evolved tasks before export; one teacher API timeout aborts the whole run and discards completed drafts.
- The backend should wrap timeout errors with a sanitized message.
- The pipeline should tolerate teacher backend failures by falling back to deterministic task evolution and recording the error in sample `source`.

## Next Step Thoughts

- Add teacher backend failure fallback before retrying.
- Increase `--teacher-timeout-s` for DeepSeek runs after fallback is in place.
- Keep the next retry small and recorded as an API robustness validation, not a quality benchmark.
