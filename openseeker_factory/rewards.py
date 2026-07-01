from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any, Sequence

from openseeker_factory.evaluation import (
    evaluate_prediction,
    extract_action_observation_pairs,
    extract_tool_actions,
    load_samples,
)
from openseeker_factory.schema import AgentDataSample


@dataclass(frozen=True)
class VerifierRewardWeights:
    answer: float = 0.25
    tool: float = 0.30
    evidence: float = 0.35
    format: float = 0.10


DEFAULT_REWARD_WEIGHTS = VerifierRewardWeights()
REWARD_MODES = {"binary", "weighted"}


def binary_all_pass_reward(evaluation: dict[str, Any]) -> float:
    return float(
        bool(evaluation["exact_match"] or evaluation["canonical_match"])
        and bool(evaluation["tool_call_success"])
        and bool(evaluation["observation_faithfulness"])
        and bool(evaluation["trajectory_valid"])
    )


def score_weighted_verifier_reward(
    evaluation: dict[str, Any],
    *,
    weights: VerifierRewardWeights = DEFAULT_REWARD_WEIGHTS,
) -> dict[str, Any]:
    answer_score = _answer_score(evaluation)
    tool_score = _clamp01(float(evaluation["tool_call_coverage"]))
    evidence_score = _clamp01(float(evaluation["observation_coverage"]))
    format_score = _format_score(evaluation)
    raw_reward = (
        weights.answer * answer_score
        + weights.tool * tool_score
        + weights.evidence * evidence_score
        + weights.format * format_score
    )
    reward, caps = _apply_reward_caps(
        raw_reward=raw_reward,
        answer_score=answer_score,
        tool_score=tool_score,
        format_score=format_score,
        hallucination_proxy=bool(evaluation["hallucination_proxy"]),
    )
    return {
        "reward": round(reward, 4),
        "raw_reward": round(raw_reward, 4),
        "components": {
            "answer": round(answer_score, 4),
            "tool": round(tool_score, 4),
            "evidence": round(evidence_score, 4),
            "format": round(format_score, 4),
        },
        "weights": {
            "answer": weights.answer,
            "tool": weights.tool,
            "evidence": weights.evidence,
            "format": weights.format,
        },
        "applied_caps": caps,
    }


def build_verifier_reward_row(
    *,
    sample: AgentDataSample,
    prediction_row: dict[str, Any],
    model_label: str,
    reward_mode: str = "weighted",
) -> dict[str, Any]:
    if reward_mode not in REWARD_MODES:
        raise ValueError(f"reward_mode must be one of {sorted(REWARD_MODES)}")
    prediction = str(prediction_row["prediction"])
    evaluation = evaluate_prediction(sample, model_label, prediction)
    weighted = score_weighted_verifier_reward(evaluation)
    binary = binary_all_pass_reward(evaluation)
    primary_reward = binary if reward_mode == "binary" else float(weighted["reward"])
    return {
        "id": prediction_row["id"],
        "candidate_id": prediction_row["candidate_id"],
        "candidate_index": prediction_row["candidate_index"],
        "model_label": model_label,
        "reward_mode": reward_mode,
        "reward": round(primary_reward, 4),
        "binary_all_pass_reward": binary,
        "weighted_verifier_reward": weighted["reward"],
        "raw_weighted_reward": weighted["raw_reward"],
        "reward_components": weighted["components"],
        "reward_weights": weighted["weights"],
        "applied_caps": weighted["applied_caps"],
        "verifier_checks": {
            "answer_supported": bool(evaluation["exact_match"] or evaluation["canonical_match"]),
            "tool_success": bool(evaluation["tool_call_success"]),
            "evidence_faithfulness": bool(evaluation["observation_faithfulness"]),
            "trajectory_valid": bool(evaluation["trajectory_valid"]),
        },
        "task_type": sample.task_type,
        "difficulty": sample.difficulty,
        "prompt": sample.question,
        "answer": sample.answer,
        "prediction": prediction,
        "predicted_answer": evaluation["predicted_answer"],
        "exact_match": evaluation["exact_match"],
        "canonical_match": evaluation["canonical_match"],
        "answer_f1": evaluation["answer_f1"],
        "tool_call_coverage": evaluation["tool_call_coverage"],
        "observation_coverage": evaluation["observation_coverage"],
        "trajectory_valid": evaluation["trajectory_valid"],
        "hallucination_proxy": evaluation["hallucination_proxy"],
        "error_bucket": evaluation["error_bucket"],
    }


def run_score_verifier_rewards(
    *,
    samples_path: Path,
    prediction_file: Path,
    out_dir: Path,
    model_label: str,
    reward_mode: str,
) -> tuple[Path, dict[str, Any]]:
    samples = load_samples(samples_path)
    samples_by_id = {sample.id: sample for sample in samples}
    prediction_rows = load_reward_prediction_rows(prediction_file)
    scored_rows: list[dict[str, Any]] = []
    for prediction_row in prediction_rows:
        sample_id = str(prediction_row["id"])
        if sample_id not in samples_by_id:
            raise ValueError(f"Prediction references unknown sample id {sample_id!r}")
        scored_rows.append(
            build_verifier_reward_row(
                sample=samples_by_id[sample_id],
                prediction_row=prediction_row,
                model_label=model_label,
                reward_mode=reward_mode,
            )
        )
    out_dir.mkdir(parents=True, exist_ok=True)
    rewards_path = out_dir / "verifier_rewards.jsonl"
    with rewards_path.open("w", encoding="utf-8") as handle:
        for row in scored_rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    summary = summarize_reward_rows(scored_rows)
    (out_dir / "verifier_reward_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    _write_summary_csv(summary, out_dir / "verifier_reward_summary.csv")
    return rewards_path, summary


def load_reward_prediction_rows(path: Path) -> list[dict[str, Any]]:
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
            candidate_index = int(raw.get("candidate_index", next_index_by_id[sample_id]))
            next_index_by_id[sample_id] = max(
                next_index_by_id[sample_id], candidate_index + 1
            )
            rows.append(
                {
                    "id": sample_id,
                    "candidate_id": str(
                        raw.get(
                            "candidate_id",
                            f"{sample_id}-reward-cand-{candidate_index:04d}",
                        )
                    ),
                    "candidate_index": candidate_index,
                    "prediction": str(prediction),
                }
            )
    return rows


def summarize_reward_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "total": 0,
            "reward_mode": "",
            "reward_avg": 0.0,
            "binary_pass_rate": 0.0,
            "per_task_type": {},
        }

    def summarize_subset(subset: Sequence[dict[str, Any]]) -> dict[str, Any]:
        rewards = [float(row["reward"]) for row in subset]
        return {
            "total": len(subset),
            "reward_avg": round(mean(rewards), 4),
            "reward_min": round(min(rewards), 4),
            "reward_max": round(max(rewards), 4),
            "binary_pass_rate": _rate(
                sum(1 for row in subset if float(row["binary_all_pass_reward"]) == 1.0),
                len(subset),
            ),
            "answer_avg": _component_avg(subset, "answer"),
            "tool_avg": _component_avg(subset, "tool"),
            "evidence_avg": _component_avg(subset, "evidence"),
            "format_avg": _component_avg(subset, "format"),
            "error_buckets": dict(Counter(str(row["error_bucket"]) for row in subset)),
        }

    per_task_type = {
        task_type: summarize_subset([row for row in rows if row["task_type"] == task_type])
        for task_type in sorted({str(row["task_type"]) for row in rows})
    }
    return {
        "total": len(rows),
        "reward_mode": str(rows[0]["reward_mode"]),
        **summarize_subset(rows),
        "per_task_type": per_task_type,
    }


def _answer_score(evaluation: dict[str, Any]) -> float:
    if evaluation["exact_match"] or evaluation["canonical_match"]:
        return 1.0
    if evaluation["final_answer_present"]:
        return round(0.5 * float(evaluation["answer_f1"]), 4)
    return 0.0


def _format_score(evaluation: dict[str, Any]) -> float:
    if evaluation["trajectory_valid"]:
        return 1.0
    prediction = str(evaluation.get("prediction", ""))
    if evaluation["final_answer_present"] or (
        extract_tool_actions(prediction) and extract_action_observation_pairs(prediction)
    ):
        return 0.5
    return 0.0


def _apply_reward_caps(
    *,
    raw_reward: float,
    answer_score: float,
    tool_score: float,
    format_score: float,
    hallucination_proxy: bool,
) -> tuple[float, list[str]]:
    reward = raw_reward
    caps: list[str] = []

    def cap(name: str, value: float) -> None:
        nonlocal reward
        if reward > value:
            reward = value
            caps.append(name)

    if format_score == 0.0:
        cap("format_zero_cap_0.20", 0.20)
    if tool_score == 0.0:
        cap("tool_zero_cap_0.45", 0.45)
    if answer_score == 1.0 and tool_score < 1.0:
        cap("right_answer_tool_gap_cap_0.65", 0.65)
    if answer_score == 0.0:
        cap("wrong_answer_cap_0.45", 0.45)
    if hallucination_proxy:
        cap("hallucination_cap_0.35", 0.35)
    return _clamp01(reward), caps


def _component_avg(rows: Sequence[dict[str, Any]], component: str) -> float:
    return round(
        mean(float(row["reward_components"][component]) for row in rows),
        4,
    )


def _write_summary_csv(summary: dict[str, Any], path: Path) -> None:
    rows = [
        {
            "split": "overall",
            "total": summary["total"],
            "reward_avg": summary["reward_avg"],
            "binary_pass_rate": summary["binary_pass_rate"],
            "answer_avg": summary["answer_avg"],
            "tool_avg": summary["tool_avg"],
            "evidence_avg": summary["evidence_avg"],
            "format_avg": summary["format_avg"],
        }
    ]
    for task_type, task_summary in summary["per_task_type"].items():
        rows.append(
            {
                "split": task_type,
                "total": task_summary["total"],
                "reward_avg": task_summary["reward_avg"],
                "binary_pass_rate": task_summary["binary_pass_rate"],
                "answer_avg": task_summary["answer_avg"],
                "tool_avg": task_summary["tool_avg"],
                "evidence_avg": task_summary["evidence_avg"],
                "format_avg": task_summary["format_avg"],
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


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
