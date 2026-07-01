from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence

from openseeker_factory.evaluation import (
    _format_prompt,
    evaluate_prediction,
    extract_tool_actions,
    load_samples,
)
from openseeker_factory.schema import AgentDataSample, VerifierResult


RFT_REQUIRED_CHECKS = (
    "answer_supported",
    "tool_success",
    "evidence_faithfulness",
    "trajectory_valid",
)


def validate_sampling_args(
    *,
    num_return_sequences: int,
    temperature: float,
    top_p: float,
    batch_size: int,
) -> None:
    if num_return_sequences < 1:
        raise ValueError("num_return_sequences must be positive")
    if temperature <= 0:
        raise ValueError("temperature must be positive for RFT sampling")
    if not 0 < top_p <= 1:
        raise ValueError("top_p must be in (0, 1]")
    if batch_size < 1:
        raise ValueError("batch_size must be positive")


def build_candidate_prediction_row(
    *,
    sample_id: str,
    candidate_index: int,
    prediction: str,
    model_label: str,
) -> dict[str, Any]:
    return {
        "id": sample_id,
        "candidate_id": f"{sample_id}-rft-cand-{candidate_index:04d}",
        "candidate_index": candidate_index,
        "model_label": model_label,
        "prediction": prediction,
    }


def run_sample_rft_candidates(
    *,
    samples_path: Path,
    out_dir: Path,
    model_label: str,
    model_name_or_path: str,
    adapter_path: str | None,
    num_return_sequences: int,
    temperature: float,
    top_p: float,
    limit: int | None,
    offset: int,
    batch_size: int,
    max_new_tokens: int,
    device: str | None,
    local_files_only: bool,
    disable_thinking: bool,
    seed: int | None,
) -> tuple[Path, int]:
    validate_sampling_args(
        num_return_sequences=num_return_sequences,
        temperature=temperature,
        top_p=top_p,
        batch_size=batch_size,
    )
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise RuntimeError(
            "RFT sampling requires torch and transformers in the active environment."
        ) from exc

    samples = load_samples(samples_path, limit=limit, offset=offset)
    out_dir.mkdir(parents=True, exist_ok=True)
    predictions_path = out_dir / "candidate_predictions.jsonl"
    if seed is not None:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

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
            raise RuntimeError("RFT sampling with adapters requires peft.") from exc
        model = PeftModel.from_pretrained(
            model, adapter_path, local_files_only=local_files_only
        )
    model.to(resolved_device)
    model.eval()

    total_rows = 0
    with predictions_path.open("w", encoding="utf-8") as handle, torch.inference_mode():
        for batch in _batched(samples, batch_size):
            prompts = [
                _format_prompt(
                    tokenizer,
                    sample,
                    enable_thinking=False if disable_thinking else None,
                )
                for sample in batch
            ]
            encoded = tokenizer(
                prompts,
                return_tensors="pt",
                padding=True,
                truncation=True,
            )
            encoded = {key: value.to(resolved_device) for key, value in encoded.items()}
            prompt_length = encoded["input_ids"].shape[1]
            outputs = model.generate(
                **encoded,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                num_return_sequences=num_return_sequences,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
            decoded = tokenizer.batch_decode(
                outputs[:, prompt_length:],
                skip_special_tokens=True,
            )
            for output_index, prediction in enumerate(decoded):
                sample = batch[output_index // num_return_sequences]
                candidate_index = output_index % num_return_sequences
                row = build_candidate_prediction_row(
                    sample_id=sample.id,
                    candidate_index=candidate_index,
                    prediction=prediction.strip(),
                    model_label=model_label,
                )
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                total_rows += 1
                print(
                    f"sampled {total_rows} sample_id={sample.id} "
                    f"candidate_index={candidate_index}",
                    flush=True,
                )
    return predictions_path, total_rows


def run_rft_filter(
    *,
    samples_path: Path,
    prediction_file: Path,
    out_dir: Path,
    model_label: str,
    iteration: int,
    max_per_prompt: int | None = None,
) -> dict[str, Any]:
    if iteration < 1:
        raise ValueError("iteration must be positive")
    if max_per_prompt is not None and max_per_prompt < 1:
        raise ValueError("max_per_prompt must be positive")

    samples = load_samples(samples_path)
    samples_by_id = {sample.id: sample for sample in samples}
    prediction_rows = load_candidate_prediction_rows(prediction_file)
    scored_rows: list[dict[str, Any]] = []
    accepted_samples: list[AgentDataSample] = []
    accepted_by_prompt: dict[str, int] = defaultdict(int)

    for row in prediction_rows:
        sample_id = str(row["id"])
        if sample_id not in samples_by_id:
            raise ValueError(f"Prediction references unknown sample id {sample_id!r}")
        sample = samples_by_id[sample_id]
        scored = score_rft_candidate(sample, row, model_label=model_label)
        if scored["accepted"] and max_per_prompt is not None:
            if accepted_by_prompt[sample_id] >= max_per_prompt:
                scored["accepted"] = False
                scored["rejection_reasons"] = ["max_per_prompt"]
            else:
                accepted_by_prompt[sample_id] += 1
        elif scored["accepted"]:
            accepted_by_prompt[sample_id] += 1
        scored_rows.append(scored)

    accepted_ordinals: dict[str, int] = defaultdict(int)
    for scored in scored_rows:
        if not scored["accepted"]:
            continue
        sample = samples_by_id[str(scored["id"])]
        accepted_ordinals[sample.id] += 1
        accepted_samples.append(
            build_rft_sample(
                sample=sample,
                scored_row=scored,
                model_label=model_label,
                iteration=iteration,
                accepted_ordinal=accepted_ordinals[sample.id],
            )
        )

    summary = summarize_rft(scored_rows)
    write_rft_outputs(
        out_dir=out_dir,
        scored_rows=scored_rows,
        accepted_samples=accepted_samples,
        summary=summary,
    )
    return summary


def load_candidate_prediction_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    next_index_by_id: dict[str, int] = defaultdict(int)
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            raw = json.loads(line)
            sample_id = str(raw.get("id", raw.get("sample_id", "")))
            prediction = raw.get("prediction", raw.get("response", raw.get("text", "")))
            if not sample_id:
                raise ValueError(f"Missing id in prediction file line {line_number}")
            if not prediction:
                raise ValueError(
                    f"Missing prediction/response/text in prediction file line {line_number}"
                )
            candidate_index = int(
                raw.get("candidate_index", next_index_by_id[sample_id])
            )
            next_index_by_id[sample_id] = max(
                next_index_by_id[sample_id], candidate_index + 1
            )
            rows.append(
                {
                    "id": sample_id,
                    "candidate_id": str(
                        raw.get(
                            "candidate_id",
                            f"{sample_id}-rft-cand-{candidate_index:04d}",
                        )
                    ),
                    "candidate_index": candidate_index,
                    "model_label": str(raw.get("model_label", "")),
                    "prediction": str(prediction),
                }
            )
    return rows


def score_rft_candidate(
    sample: AgentDataSample, candidate_row: dict[str, Any], model_label: str
) -> dict[str, Any]:
    evaluation = evaluate_prediction(
        sample,
        model_label=model_label,
        prediction=str(candidate_row["prediction"]),
    )
    checks = {
        "answer_supported": bool(evaluation["exact_match"] or evaluation["canonical_match"]),
        "tool_success": bool(evaluation["tool_call_success"]),
        "evidence_faithfulness": bool(evaluation["observation_faithfulness"]),
        "trajectory_valid": bool(evaluation["trajectory_valid"]),
    }
    rejection_reasons = [name for name in RFT_REQUIRED_CHECKS if not checks[name]]
    return {
        "id": candidate_row["id"],
        "candidate_id": candidate_row["candidate_id"],
        "candidate_index": candidate_row["candidate_index"],
        "model_label": model_label,
        "task_type": sample.task_type,
        "difficulty": sample.difficulty,
        "prediction": candidate_row["prediction"],
        "accepted": not rejection_reasons,
        "rft_checks": checks,
        "rejection_reasons": rejection_reasons,
        "predicted_answer": evaluation["predicted_answer"],
        "exact_match": evaluation["exact_match"],
        "canonical_match": evaluation["canonical_match"],
        "tool_call_coverage": evaluation["tool_call_coverage"],
        "observation_coverage": evaluation["observation_coverage"],
        "trajectory_valid": evaluation["trajectory_valid"],
    }


def build_rft_sample(
    *,
    sample: AgentDataSample,
    scored_row: dict[str, Any],
    model_label: str,
    iteration: int,
    accepted_ordinal: int,
) -> AgentDataSample:
    checks = {
        key: bool(value)
        for key, value in scored_row["rft_checks"].items()
    }
    trajectory = [
        line.strip()
        for line in str(scored_row["prediction"]).splitlines()
        if line.strip()
    ]
    row = sample.to_json_dict()
    row["id"] = f"{sample.id}-rft-{accepted_ordinal:04d}"
    row["trajectory"] = trajectory
    row["verifier_result"] = VerifierResult(
        passed=True,
        checks=checks,
        reasons=[],
    ).to_json_dict()
    row["quality_score"] = round(sum(checks.values()) / len(checks), 4)
    row["source"] = {
        **dict(sample.source),
        "rft_parent_id": sample.id,
        "rft_candidate_id": scored_row["candidate_id"],
        "rft_candidate_index": scored_row["candidate_index"],
        "rft_iteration": iteration,
        "rft_model_label": model_label,
        "rft_filter": "deterministic_verifier",
    }
    return AgentDataSample.from_json_dict(row)


def summarize_rft(scored_rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    sampled_total = len(scored_rows)
    accepted_rows = [row for row in scored_rows if row["accepted"]]
    accepted_total = len(accepted_rows)
    rejected_total = sampled_total - accepted_total
    per_task_type: dict[str, Any] = {}
    for task_type in sorted({str(row["task_type"]) for row in scored_rows}):
        task_rows = [row for row in scored_rows if row["task_type"] == task_type]
        task_accepted = [row for row in task_rows if row["accepted"]]
        per_task_type[task_type] = {
            "sampled_total": len(task_rows),
            "accepted_total": len(task_accepted),
            "rejected_total": len(task_rows) - len(task_accepted),
            "pass_rate": _rate(len(task_accepted), len(task_rows)),
        }

    return {
        "sampled_total": sampled_total,
        "accepted_total": accepted_total,
        "rejected_total": rejected_total,
        "verifier_pass_rate": _rate(accepted_total, sampled_total),
        "unique_trajectory_rate": _unique_rate(
            _normalize_prediction(row["prediction"]) for row in accepted_rows
        ),
        "unique_action_sequence_rate": _unique_rate(
            _action_signature(str(row["prediction"])) for row in accepted_rows
        ),
        "per_task_type": per_task_type,
    }


def write_rft_outputs(
    *,
    out_dir: Path,
    scored_rows: Sequence[dict[str, Any]],
    accepted_samples: Sequence[AgentDataSample],
    summary: dict[str, Any],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl(scored_rows, out_dir / "candidates_scored.jsonl")
    _write_jsonl(
        (sample.to_json_dict() for sample in accepted_samples),
        out_dir / "accepted_samples.jsonl",
    )
    _write_jsonl(
        (_sample_to_sft_row(sample) for sample in accepted_samples),
        out_dir / "rft_sft_conversations.jsonl",
    )
    _write_jsonl(
        (_sample_to_rl_row(sample) for sample in accepted_samples),
        out_dir / "rft_rl_rewards.jsonl",
    )
    (out_dir / "rft_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    flat_summary = {
        key: value
        for key, value in summary.items()
        if key != "per_task_type"
    }
    with (out_dir / "rft_summary.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(flat_summary.keys()))
        writer.writeheader()
        writer.writerow(flat_summary)


def _sample_to_sft_row(sample: AgentDataSample) -> dict[str, Any]:
    return {
        "id": sample.id,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a ReAct agent that must cite tool observations. "
                    "Actions must use the provided lookup schema, and Observation "
                    "lines must match lookup observations from the evidence."
                ),
            },
            {"role": "user", "content": sample.question},
            {"role": "assistant", "content": "\n".join(sample.trajectory)},
        ],
    }


def _sample_to_rl_row(sample: AgentDataSample) -> dict[str, Any]:
    return {
        "id": sample.id,
        "prompt": sample.question,
        "answer": sample.answer,
        "reward": sample.quality_score,
        "verifier_checks": sample.verifier_result.checks,
        "rft_parent_id": sample.source.get("rft_parent_id"),
    }


def _write_jsonl(rows: Iterable[dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _normalize_prediction(prediction: str) -> str:
    return " ".join(prediction.lower().split())


def _action_signature(prediction: str) -> str:
    actions = extract_tool_actions(prediction)
    return " | ".join(
        f"{action['tool'].lower()}[{action['query'].lower()}]" for action in actions
    )


def _unique_rate(values: Iterable[str]) -> float:
    value_list = [value for value in values if value]
    if not value_list:
        return 0.0
    return round(len(set(value_list)) / len(value_list), 4)


def _rate(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, 4)


def _batched(items: Sequence[AgentDataSample], batch_size: int) -> Iterable[list[AgentDataSample]]:
    for start in range(0, len(items), batch_size):
        yield list(items[start : start + batch_size])
