# DeepSeek Teacher 10 Failed Launch

## Metadata

- Experiment name: deepseek-teacher-10-20260610
- Date: 2026-06-10
- Goal: Run the first real LLM-backed teacher generation using the official DeepSeek OpenAI-compatible API.
- Status: failed before sample generation
- Operator: Codex
- Remote host: `ssh user@ssh-22.e6.luyouxia.net -p 29509`
- Repo path: `/data/wzl/OpenSeeker-AgentDataFactory/repo`
- Branch: `main`
- Commit at launch: `c672f89`
- Commit after fix: `b9b51ce`
- Conda env: `/data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory`
- GPU selection: none
- Number of GPUs: 0
- tmux session: `openseeker-20260610-deepseek-teacher-10`
- Model: `deepseek-v4-pro`
- Base URL: `https://api.deepseek.com`

## Commands

Intended launch shape:

```bash
tmux new-session -d -s openseeker-20260610-deepseek-teacher-10 \
  "bash -lc 'cd /data/wzl/OpenSeeker-AgentDataFactory/repo && source /home/user/anaconda3/etc/profile.d/conda.sh && conda activate /data/wzl/OpenSeeker-AgentDataFactory/.conda-envs/openseeker-datafactory && PYTHONNOUSERSITE=1 python -m openseeker_factory.cli generate --count 10 --seed-file data/seeds/wikidata_seed_sample.jsonl --out-dir /data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-10-20260610 --teacher-backend openai-compatible --teacher-base-url https://api.deepseek.com --teacher-model deepseek-v4-pro --teacher-api-key-env DEEPSEEK_API_KEY 2>&1 | tee /data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-10-20260610.log'"
```

The API key was intended to be passed as a one-time environment variable and not written to repo files, docs, or experiment records.

## Paths

- Log path: `/data/wzl/OpenSeeker-AgentDataFactory/logs/deepseek-teacher-10-20260610.log`
- Results path: `/data/wzl/OpenSeeker-AgentDataFactory/results/deepseek-teacher-10-20260610`
- Checkpoint path: not applicable
- Run path: not applicable

## Raw Result Summary

No samples were produced.

First launch failed with HTTP 401 because the remote process did not receive the intended API key.

Second launch failed before the HTTP request was sent because the key passed through PowerShell stdin carried a trailing CRLF. Python rejected the Authorization header:

```text
ValueError: Invalid header value b'Bearer [REDACTED-DEEPSEEK-KEY]\r'
```

The remote log was redacted after the failure. Current remote log contains `[REDACTED-DEEPSEEK-KEY]` instead of the secret.

## Fix Applied

- Added a failing regression test for API keys with CRLF endings.
- Updated `OpenAICompatibleChatBackend` to strip API key line endings in `__post_init__`.
- Wrapped invalid header errors with a sanitized message that does not include the raw Authorization header.
- Verified local tests: `14 passed`.
- Verified remote tests in the approved env: `14 passed`.

## Notes and Analysis

- The failure was caused by secret transport, not by DeepSeek model behavior or generation quality.
- The remote pre-existing `DEEPSEEK_API_KEY` was intentionally not used after the user asked to use the newly provided key.
- No GPU was used.
- The run should not be counted as a successful LLM-backed synthesis experiment.

## Next Step Thoughts

- Retry only after explicit user approval because the automatic retry budget has been exhausted.
- Use the fixed `b9b51ce` commit for the next attempt.
- Pass the API key in a way that strips CRLF before tmux launch, or set it in the remote process environment with a sanitized one-time export.
- Keep the sample count at 10 for the next attempt to limit cost while validating the real DeepSeek path.
