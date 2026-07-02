from __future__ import annotations

import csv
import json
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any, Iterable, Sequence

from openseeker_factory.evaluation import _format_prompt, load_samples
from openseeker_factory.rewards import build_verifier_reward_row
from openseeker_factory.schema import AgentDataSample


RLVR_ALGORITHMS = {"grpo", "arpo"}
RLVR_REWARD_MODES = {"binary", "weighted"}


@dataclass(frozen=True)
class RLVRRollout:
    sample: AgentDataSample
    prompt: str
    prediction: str
    candidate_id: str
    candidate_index: int
    reward_row: dict[str, Any]
    advantage: float = 0.0
    rollout_type: str = "global"


def run_rlvr_smoke(
    *,
    samples_path: Path,
    out_dir: Path,
    model_label: str,
    model_name_or_path: str,
    adapter_path: str | None,
    algorithm: str,
    reward_mode: str,
    limit: int | None,
    offset: int,
    num_generations: int,
    max_new_tokens: int,
    learning_rate: float,
    num_train_epochs: float,
    max_train_rollouts: int | None,
    device: str | None,
    local_files_only: bool,
    disable_thinking: bool,
    seed: int,
) -> dict[str, Any]:
    if algorithm not in RLVR_ALGORITHMS:
        raise ValueError(f"algorithm must be one of {sorted(RLVR_ALGORITHMS)}")
    if reward_mode not in RLVR_REWARD_MODES:
        raise ValueError(f"reward_mode must be one of {sorted(RLVR_REWARD_MODES)}")
    if num_generations < 2:
        raise ValueError("num_generations must be at least 2 for group advantages")
    if learning_rate <= 0:
        raise ValueError("learning_rate must be positive")
    if num_train_epochs <= 0:
        raise ValueError("num_train_epochs must be positive")

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise RuntimeError("RLVR smoke training requires torch and transformers.") from exc

    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    samples = load_samples(samples_path, limit=limit, offset=offset)
    if not samples:
        raise ValueError("No samples selected for RLVR smoke training")
    out_dir.mkdir(parents=True, exist_ok=True)

    resolved_device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.bfloat16 if resolved_device.startswith("cuda") else torch.float32
    tokenizer = AutoTokenizer.from_pretrained(
        model_name_or_path,
        trust_remote_code=True,
        local_files_only=local_files_only,
    )
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"

    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        trust_remote_code=True,
        torch_dtype=dtype,
        local_files_only=local_files_only,
    )
    if adapter_path:
        try:
            from peft import PeftModel
        except ImportError as exc:
            raise RuntimeError("RLVR smoke training with adapters requires peft.") from exc
        model = PeftModel.from_pretrained(
            model,
            adapter_path,
            local_files_only=local_files_only,
            is_trainable=True,
        )
    model.config.use_cache = False
    if hasattr(model, "gradient_checkpointing_enable"):
        model.gradient_checkpointing_enable()
    model.to(resolved_device)

    prompts = {
        sample.id: _format_prompt(
            tokenizer,
            sample,
            enable_thinking=False if disable_thinking else None,
        )
        for sample in samples
    }
    rollouts = _collect_rollouts(
        model=model,
        tokenizer=tokenizer,
        samples=samples,
        prompts=prompts,
        model_label=model_label,
        algorithm=algorithm,
        reward_mode=reward_mode,
        num_generations=num_generations,
        max_new_tokens=max_new_tokens,
        device=resolved_device,
    )
    rollouts = _with_group_advantages(rollouts)
    train_rollouts = list(rollouts)
    if max_train_rollouts is not None:
        train_rollouts = train_rollouts[:max_train_rollouts]

    optimizer = torch.optim.AdamW(
        [param for param in model.parameters() if param.requires_grad],
        lr=learning_rate,
    )
    loss_rows = _train_policy_on_rollouts(
        model=model,
        tokenizer=tokenizer,
        optimizer=optimizer,
        rollouts=train_rollouts,
        epochs=num_train_epochs,
        device=resolved_device,
        seed=seed,
    )

    model.save_pretrained(out_dir)
    tokenizer.save_pretrained(out_dir)
    _write_rollouts(rollouts, out_dir / "rlvr_rollouts.jsonl")
    _write_jsonl(loss_rows, out_dir / "rlvr_train_log.jsonl")
    summary = summarize_rlvr(rollouts, loss_rows, algorithm=algorithm, reward_mode=reward_mode)
    (out_dir / "rlvr_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_summary_csv(summary, out_dir / "rlvr_summary.csv")
    return summary


def extract_observation_branch_prefix(prediction: str) -> str:
    lines: list[str] = []
    saw_action = False
    for raw_line in prediction.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lines.append(line)
        lowered = line.lower()
        if lowered.startswith("action:"):
            saw_action = True
        if saw_action and lowered.startswith("observation:"):
            return "\n".join(lines) + "\n"
    return ""


def summarize_rlvr(
    rollouts: Sequence[RLVRRollout],
    loss_rows: Sequence[dict[str, Any]],
    *,
    algorithm: str,
    reward_mode: str,
) -> dict[str, Any]:
    rewards = [float(rollout.reward_row["reward"]) for rollout in rollouts]
    binary_passes = [
        float(rollout.reward_row["binary_all_pass_reward"]) for rollout in rollouts
    ]
    advantages = [float(rollout.advantage) for rollout in rollouts]
    by_task: dict[str, Any] = {}
    for task_type in sorted({rollout.sample.task_type for rollout in rollouts}):
        task_rollouts = [rollout for rollout in rollouts if rollout.sample.task_type == task_type]
        task_rewards = [float(rollout.reward_row["reward"]) for rollout in task_rollouts]
        by_task[task_type] = {
            "rollouts": len(task_rollouts),
            "reward_avg": round(mean(task_rewards), 4),
            "binary_pass_rate": _rate(
                sum(
                    1
                    for rollout in task_rollouts
                    if float(rollout.reward_row["binary_all_pass_reward"]) == 1.0
                ),
                len(task_rollouts),
            ),
        }
    loss_values = [float(row["loss"]) for row in loss_rows]
    return {
        "algorithm": algorithm,
        "reward_mode": reward_mode,
        "samples": len({rollout.sample.id for rollout in rollouts}),
        "rollouts": len(rollouts),
        "reward_avg": round(mean(rewards), 4),
        "reward_min": round(min(rewards), 4),
        "reward_max": round(max(rewards), 4),
        "binary_pass_rate": _rate(sum(1 for value in binary_passes if value == 1.0), len(binary_passes)),
        "advantage_avg": round(mean(advantages), 4),
        "advantage_abs_avg": round(mean(abs(value) for value in advantages), 4),
        "train_steps": len(loss_rows),
        "train_loss_avg": round(mean(loss_values), 6) if loss_values else 0.0,
        "per_task_type": by_task,
    }


def _collect_rollouts(
    *,
    model: Any,
    tokenizer: Any,
    samples: Sequence[AgentDataSample],
    prompts: dict[str, str],
    model_label: str,
    algorithm: str,
    reward_mode: str,
    num_generations: int,
    max_new_tokens: int,
    device: str,
) -> list[RLVRRollout]:
    rollouts: list[RLVRRollout] = []
    model.eval()
    for sample in samples:
        prompt = prompts[sample.id]
        if algorithm == "grpo":
            predictions = _generate_predictions(
                model=model,
                tokenizer=tokenizer,
                prompt=prompt,
                num_return_sequences=num_generations,
                max_new_tokens=max_new_tokens,
                device=device,
            )
            for index, prediction in enumerate(predictions):
                rollouts.append(
                    _build_rollout(
                        sample=sample,
                        prompt=prompt,
                        prediction=prediction,
                        candidate_index=index,
                        model_label=model_label,
                        reward_mode=reward_mode,
                        rollout_type="global",
                    )
                )
            continue

        global_count = max(1, num_generations // 2)
        branch_count = num_generations - global_count
        global_predictions = _generate_predictions(
            model=model,
            tokenizer=tokenizer,
            prompt=prompt,
            num_return_sequences=global_count,
            max_new_tokens=max_new_tokens,
            device=device,
        )
        sample_rollouts = [
            _build_rollout(
                sample=sample,
                prompt=prompt,
                prediction=prediction,
                candidate_index=index,
                model_label=model_label,
                reward_mode=reward_mode,
                rollout_type="global",
            )
            for index, prediction in enumerate(global_predictions)
        ]
        rollouts.extend(sample_rollouts)
        if branch_count <= 0:
            continue
        branch_source = min(
            sample_rollouts,
            key=lambda rollout: float(rollout.reward_row["reward"]),
        )
        branch_prefix = extract_observation_branch_prefix(branch_source.prediction)
        if not branch_prefix:
            continue
        branch_predictions = _generate_predictions(
            model=model,
            tokenizer=tokenizer,
            prompt=prompt + branch_prefix,
            num_return_sequences=branch_count,
            max_new_tokens=max_new_tokens,
            device=device,
        )
        for offset, continuation in enumerate(branch_predictions, start=global_count):
            rollouts.append(
                _build_rollout(
                    sample=sample,
                    prompt=prompt,
                    prediction=branch_prefix + continuation,
                    candidate_index=offset,
                    model_label=model_label,
                    reward_mode=reward_mode,
                    rollout_type="branch",
                )
            )
    return rollouts


def _generate_predictions(
    *,
    model: Any,
    tokenizer: Any,
    prompt: str,
    num_return_sequences: int,
    max_new_tokens: int,
    device: str,
) -> list[str]:
    import torch

    encoded = tokenizer(prompt, return_tensors="pt", truncation=True)
    encoded = {key: value.to(device) for key, value in encoded.items()}
    prompt_length = encoded["input_ids"].shape[1]
    with torch.inference_mode():
        outputs = model.generate(
            **encoded,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=1.0,
            top_p=0.98,
            num_return_sequences=num_return_sequences,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    decoded = tokenizer.batch_decode(outputs[:, prompt_length:], skip_special_tokens=True)
    return [prediction.strip() for prediction in decoded]


def _build_rollout(
    *,
    sample: AgentDataSample,
    prompt: str,
    prediction: str,
    candidate_index: int,
    model_label: str,
    reward_mode: str,
    rollout_type: str,
) -> RLVRRollout:
    candidate_id = f"{sample.id}-rlvr-cand-{candidate_index:04d}"
    reward_row = build_verifier_reward_row(
        sample=sample,
        prediction_row={
            "id": sample.id,
            "candidate_id": candidate_id,
            "candidate_index": candidate_index,
            "prediction": prediction,
        },
        model_label=model_label,
        reward_mode=reward_mode,
    )
    return RLVRRollout(
        sample=sample,
        prompt=prompt,
        prediction=prediction,
        candidate_id=candidate_id,
        candidate_index=candidate_index,
        reward_row=reward_row,
        rollout_type=rollout_type,
    )


def _with_group_advantages(rollouts: Sequence[RLVRRollout]) -> list[RLVRRollout]:
    grouped: dict[str, list[RLVRRollout]] = defaultdict(list)
    for rollout in rollouts:
        grouped[rollout.sample.id].append(rollout)
    output: list[RLVRRollout] = []
    for sample_rollouts in grouped.values():
        rewards = [float(rollout.reward_row["reward"]) for rollout in sample_rollouts]
        reward_mean = mean(rewards)
        variance = mean((reward - reward_mean) ** 2 for reward in rewards)
        std = variance**0.5
        for rollout, reward in zip(sample_rollouts, rewards):
            advantage = 0.0 if std < 1e-6 else (reward - reward_mean) / std
            advantage = max(-2.0, min(2.0, advantage))
            output.append(
                RLVRRollout(
                    sample=rollout.sample,
                    prompt=rollout.prompt,
                    prediction=rollout.prediction,
                    candidate_id=rollout.candidate_id,
                    candidate_index=rollout.candidate_index,
                    reward_row=rollout.reward_row,
                    advantage=round(advantage, 6),
                    rollout_type=rollout.rollout_type,
                )
            )
    return output


def _train_policy_on_rollouts(
    *,
    model: Any,
    tokenizer: Any,
    optimizer: Any,
    rollouts: Sequence[RLVRRollout],
    epochs: float,
    device: str,
    seed: int,
) -> list[dict[str, Any]]:
    import torch

    model.train()
    loss_rows: list[dict[str, Any]] = []
    epoch_count = max(1, int(round(epochs)))
    train_rows = list(rollouts)
    rng = random.Random(seed)
    step = 0
    for epoch in range(epoch_count):
        rng.shuffle(train_rows)
        for rollout in train_rows:
            if abs(rollout.advantage) < 1e-8:
                continue
            optimizer.zero_grad(set_to_none=True)
            loss = _policy_gradient_loss(
                model=model,
                tokenizer=tokenizer,
                prompt=rollout.prompt,
                completion=rollout.prediction,
                advantage=rollout.advantage,
                device=device,
            )
            if loss is None:
                continue
            loss.backward()
            torch.nn.utils.clip_grad_norm_(
                [param for param in model.parameters() if param.requires_grad],
                max_norm=1.0,
            )
            optimizer.step()
            step += 1
            loss_rows.append(
                {
                    "step": step,
                    "epoch": epoch + 1,
                    "id": rollout.sample.id,
                    "candidate_id": rollout.candidate_id,
                    "reward": rollout.reward_row["reward"],
                    "advantage": rollout.advantage,
                    "loss": round(float(loss.detach().cpu()), 6),
                }
            )
    return loss_rows


def _policy_gradient_loss(
    *,
    model: Any,
    tokenizer: Any,
    prompt: str,
    completion: str,
    advantage: float,
    device: str,
) -> Any | None:
    import torch

    prompt_ids = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)[
        "input_ids"
    ].to(device)
    full = tokenizer(
        prompt + completion,
        return_tensors="pt",
        add_special_tokens=False,
        truncation=True,
    )
    full = {key: value.to(device) for key, value in full.items()}
    input_ids = full["input_ids"]
    if input_ids.shape[1] <= prompt_ids.shape[1] + 1:
        return None
    labels = input_ids.clone()
    prompt_length = min(prompt_ids.shape[1], labels.shape[1])
    labels[:, :prompt_length] = -100
    outputs = model(**full)
    logits = outputs.logits[:, :-1, :].float()
    shifted_labels = labels[:, 1:]
    mask = shifted_labels.ne(-100)
    if not bool(mask.any()):
        return None
    token_logprobs = torch.log_softmax(logits, dim=-1)
    safe_labels = shifted_labels.masked_fill(~mask, 0)
    selected = token_logprobs.gather(-1, safe_labels.unsqueeze(-1)).squeeze(-1)
    completion_logprob = selected[mask].mean()
    return -float(advantage) * completion_logprob


def _write_rollouts(rollouts: Sequence[RLVRRollout], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for rollout in rollouts:
            row = {
                **rollout.reward_row,
                "advantage": rollout.advantage,
                "rollout_type": rollout.rollout_type,
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_jsonl(rows: Iterable[dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_summary_csv(summary: dict[str, Any], path: Path) -> None:
    rows = [
        {
            "split": "overall",
            "rollouts": summary["rollouts"],
            "reward_avg": summary["reward_avg"],
            "binary_pass_rate": summary["binary_pass_rate"],
            "advantage_abs_avg": summary["advantage_abs_avg"],
            "train_steps": summary["train_steps"],
            "train_loss_avg": summary["train_loss_avg"],
        }
    ]
    for task_type, task_summary in summary["per_task_type"].items():
        rows.append(
            {
                "split": task_type,
                "rollouts": task_summary["rollouts"],
                "reward_avg": task_summary["reward_avg"],
                "binary_pass_rate": task_summary["binary_pass_rate"],
                "advantage_abs_avg": "",
                "train_steps": "",
                "train_loss_avg": "",
            }
        )
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)
