from __future__ import annotations

import csv
import json
import re
import string
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence

from openseeker_factory.schema import AgentDataSample, ToolCall


FINAL_RE = re.compile(r"final\s*:\s*(.+)", re.IGNORECASE)
ACTION_RE = re.compile(r"action\s*:\s*([A-Za-z0-9_./-]+)\s*\[([^\]]+)\]", re.IGNORECASE)
OBSERVATION_RE = re.compile(r"observation\s*:\s*(.+)", re.IGNORECASE)

QUERY_INTENT_TOKENS = {
    "birth",
    "birthplace",
    "born",
    "country",
    "current",
    "located",
    "location",
    "present",
    "today",
    "where",
}

CANONICAL_ANSWER_ALIASES = {
    "america": "united states",
    "czechia": "czech republic",
    "england": "united kingdom",
    "northern ireland": "united kingdom",
    "prc": "china",
    "peoples republic of china": "china",
    "scotland": "united kingdom",
    "uk": "united kingdom",
    "united states of america": "united states",
    "us": "united states",
    "usa": "united states",
    "wales": "united kingdom",
}

ERROR_BUCKETS = (
    "correct",
    "canonical_alias_match",
    "missing_final",
    "trajectory_format_error",
    "tool_coverage_gap",
    "supported_but_wrong_answer",
    "unsupported_wrong_answer",
)


def normalize_answer(text: str) -> str:
    ascii_text = (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    lowered = ascii_text.lower()
    no_punctuation = lowered.translate(str.maketrans("", "", string.punctuation))
    tokens = [
        token
        for token in no_punctuation.split()
        if token not in {"a", "an", "the"}
    ]
    merged_tokens: list[str] = []
    index = 0
    while index < len(tokens):
        if len(tokens[index]) == 1 and tokens[index].isalpha():
            end = index + 1
            while end < len(tokens) and len(tokens[end]) == 1 and tokens[end].isalpha():
                end += 1
            if end - index > 1:
                merged_tokens.append("".join(tokens[index:end]))
                index = end
                continue
        merged_tokens.append(tokens[index])
        index += 1
    return " ".join(merged_tokens)


def canonicalize_answer(text: str) -> str:
    normalized = normalize_answer(text)
    return CANONICAL_ANSWER_ALIASES.get(normalized, normalized)


def extract_final_answer(prediction: str) -> str:
    matches = FINAL_RE.findall(prediction)
    if not matches:
        return ""
    answer = matches[-1].strip()
    answer = re.split(r"<\|im_end\|>|</s>|<\|endoftext\|>", answer)[0].strip()
    answer = answer.strip(" \t\r\n\"'")
    while answer.endswith((".", ",", ";", ":")):
        answer = answer[:-1].strip()
    return answer


def extract_tool_actions(prediction: str) -> list[dict[str, str]]:
    return [
        {"tool": tool.strip(), "query": query.strip()}
        for tool, query in ACTION_RE.findall(prediction)
    ]


def extract_action_observation_pairs(prediction: str) -> list[dict[str, str]]:
    pairs: list[dict[str, str]] = []
    pending_action: dict[str, str] | None = None
    for line in prediction.splitlines():
        action_match = ACTION_RE.search(line)
        if action_match:
            pending_action = {
                "tool": action_match.group(1).strip(),
                "query": action_match.group(2).strip(),
                "observation": "",
            }
            pairs.append(pending_action)
            continue
        observation_match = OBSERVATION_RE.search(line)
        if observation_match and pending_action is not None:
            pending_action["observation"] = observation_match.group(1).strip()
            pending_action = None
    return pairs


def _content_tokens(text: str) -> set[str]:
    return {
        token
        for token in normalize_answer(text).split()
        if token not in QUERY_INTENT_TOKENS
    }


def token_f1(predicted: str, gold: str) -> float:
    predicted_tokens = normalize_answer(predicted).split()
    gold_tokens = normalize_answer(gold).split()
    if not predicted_tokens or not gold_tokens:
        return 1.0 if predicted_tokens == gold_tokens else 0.0
    common = Counter(predicted_tokens) & Counter(gold_tokens)
    overlap = sum(common.values())
    if overlap == 0:
        return 0.0
    precision = overlap / len(predicted_tokens)
    recall = overlap / len(gold_tokens)
    return round((2 * precision * recall) / (precision + recall), 4)


def _action_matches_tool_call(action: dict[str, str], tool_call: ToolCall) -> bool:
    if action["tool"].lower() != tool_call.tool.lower():
        return False
    expected_tokens = _content_tokens(tool_call.query)
    predicted_tokens = _content_tokens(action["query"])
    if not expected_tokens:
        return False
    if predicted_tokens == expected_tokens:
        return True
    if predicted_tokens and (
        predicted_tokens <= expected_tokens or expected_tokens <= predicted_tokens
    ):
        return True
    overlap = len(expected_tokens & predicted_tokens)
    expected_ratio = overlap / len(expected_tokens)
    predicted_ratio = overlap / len(predicted_tokens) if predicted_tokens else 0.0
    result_tokens = _content_tokens(tool_call.result)
    result_matched = bool(result_tokens and result_tokens <= predicted_tokens)
    return (
        expected_ratio >= 0.5
        or predicted_ratio >= 0.8
        or result_matched
    )


def tool_call_coverage(prediction: str, tool_calls: Sequence[ToolCall]) -> float:
    if not tool_calls:
        return 1.0
    actions = extract_tool_actions(prediction)
    matched = 0
    used_action_indexes: set[int] = set()
    for tool_call in tool_calls:
        for index, action in enumerate(actions):
            if index in used_action_indexes:
                continue
            if _action_matches_tool_call(action, tool_call):
                matched += 1
                used_action_indexes.add(index)
                break
    return round(matched / len(tool_calls), 4)


def observation_coverage(prediction: str, tool_calls: Sequence[ToolCall]) -> float:
    if not tool_calls:
        return 1.0
    pairs = extract_action_observation_pairs(prediction)
    matched = 0
    used_pair_indexes: set[int] = set()
    for tool_call in tool_calls:
        for index, pair in enumerate(pairs):
            if index in used_pair_indexes:
                continue
            if not _action_matches_tool_call(pair, tool_call):
                continue
            expected_result = normalize_answer(tool_call.result)
            observed = normalize_answer(pair["observation"])
            if expected_result and expected_result in observed:
                matched += 1
                used_pair_indexes.add(index)
                break
    return round(matched / len(tool_calls), 4)


def trajectory_is_valid(prediction: str) -> bool:
    lowered = prediction.lower()
    return (
        "thought:" in lowered
        and "action:" in lowered
        and "observation:" in lowered
        and bool(extract_final_answer(prediction))
    )


def _prediction_supported_by_evidence(
    predicted_answer: str, sample: AgentDataSample
) -> bool:
    if not predicted_answer:
        return False
    normalized_prediction = normalize_answer(predicted_answer)
    if not normalized_prediction:
        return False
    normalized_evidence = normalize_answer(" ".join(sample.gold_evidence))
    return normalized_prediction in normalized_evidence


def _gold_answer_mentioned(prediction: str, sample: AgentDataSample) -> bool:
    normalized_gold = normalize_answer(sample.answer)
    normalized_prediction = normalize_answer(prediction)
    return bool(normalized_gold) and normalized_gold in normalized_prediction


def _classify_error_bucket(
    *,
    exact_match: bool,
    canonical_match: bool,
    predicted_answer: str,
    coverage: float,
    trajectory_valid: bool,
    hallucination_proxy: bool,
) -> str:
    if not predicted_answer:
        return "missing_final"
    if exact_match or canonical_match:
        if not trajectory_valid:
            return "trajectory_format_error"
        if coverage < 1.0:
            return "tool_coverage_gap"
        if canonical_match and not exact_match:
            return "canonical_alias_match"
        return "correct"
    if hallucination_proxy:
        return "unsupported_wrong_answer"
    return "supported_but_wrong_answer"


def evaluate_prediction(
    sample: AgentDataSample, model_label: str, prediction: str
) -> dict[str, Any]:
    predicted_answer = extract_final_answer(prediction)
    exact_match = normalize_answer(predicted_answer) == normalize_answer(sample.answer)
    canonical_match = (
        canonicalize_answer(predicted_answer) == canonicalize_answer(sample.answer)
    )
    coverage = tool_call_coverage(prediction, sample.tool_calls)
    observation_match_rate = observation_coverage(prediction, sample.tool_calls)
    trajectory_valid = trajectory_is_valid(prediction)
    hallucination_proxy = (
        bool(predicted_answer)
        and not exact_match
        and not canonical_match
        and not _prediction_supported_by_evidence(predicted_answer, sample)
    )
    error_bucket = _classify_error_bucket(
        exact_match=exact_match,
        canonical_match=canonical_match,
        predicted_answer=predicted_answer,
        coverage=coverage,
        trajectory_valid=trajectory_valid,
        hallucination_proxy=hallucination_proxy,
    )
    return {
        "id": sample.id,
        "model_label": model_label,
        "task_type": sample.task_type,
        "difficulty": sample.difficulty,
        "question": sample.question,
        "gold_answer": sample.answer,
        "predicted_answer": predicted_answer,
        "prediction": prediction,
        "exact_match": exact_match,
        "canonical_match": canonical_match,
        "answer_f1": token_f1(predicted_answer, sample.answer),
        "gold_answer_mentioned": _gold_answer_mentioned(prediction, sample),
        "final_answer_present": bool(predicted_answer),
        "tool_call_coverage": coverage,
        "tool_call_success": coverage == 1.0,
        "observation_coverage": observation_match_rate,
        "observation_faithfulness": observation_match_rate == 1.0,
        "trajectory_valid": trajectory_valid,
        "hallucination_proxy": hallucination_proxy,
        "error_bucket": error_bucket,
    }


def summarize_prediction_rows(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return []

    def summarize(split: str, split_rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
        total = len(split_rows)

        def rate(field: str) -> float:
            return round(sum(1 for row in split_rows if row[field]) / total, 4)

        def bucket_rate(bucket: str) -> float:
            return round(
                sum(1 for row in split_rows if row["error_bucket"] == bucket) / total,
                4,
            )

        return {
            "model_label": split_rows[0]["model_label"],
            "split": split,
            "total": total,
            "exact_match_rate": rate("exact_match"),
            "canonical_match_rate": rate("canonical_match"),
            "answer_f1_avg": round(
                sum(float(row["answer_f1"]) for row in split_rows) / total, 4
            ),
            "gold_answer_mention_rate": rate("gold_answer_mentioned"),
            "final_answer_rate": rate("final_answer_present"),
            "tool_call_success_rate": rate("tool_call_success"),
            "tool_call_coverage_avg": round(
                sum(float(row["tool_call_coverage"]) for row in split_rows) / total, 4
            ),
            "observation_faithfulness_rate": rate("observation_faithfulness"),
            "observation_coverage_avg": round(
                sum(float(row["observation_coverage"]) for row in split_rows) / total,
                4,
            ),
            "trajectory_valid_rate": rate("trajectory_valid"),
            "hallucination_rate": rate("hallucination_proxy"),
            **{
                f"{bucket}_rate": bucket_rate(bucket)
                for bucket in ERROR_BUCKETS
            },
        }

    summary = [summarize("overall", rows)]
    for task_type in sorted({str(row["task_type"]) for row in rows}):
        task_rows = [row for row in rows if row["task_type"] == task_type]
        summary.append(summarize(task_type, task_rows))
    return summary


def write_evaluation_outputs(
    rows: Sequence[dict[str, Any]], out_dir: Path, model_label: str
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_label = safe_filename(model_label)
    predictions_path = out_dir / f"{safe_label}_predictions.jsonl"
    summary_path = out_dir / f"{safe_label}_summary.csv"

    with predictions_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary_rows = summarize_prediction_rows(rows)
    fieldnames = list(summary_rows[0].keys()) if summary_rows else []
    with summary_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summary_rows)

    return predictions_path, summary_path


def safe_filename(label: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", label).strip("-") or "model"


def load_samples(path: Path, limit: int | None = None, offset: int = 0) -> list[AgentDataSample]:
    samples: list[AgentDataSample] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            samples.append(AgentDataSample.from_json_dict(json.loads(line)))
    selected = samples[offset:]
    if limit is not None:
        selected = selected[:limit]
    return selected


def load_prediction_file(path: Path) -> dict[str, str]:
    predictions: dict[str, str] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            sample_id = str(row.get("id", ""))
            prediction = row.get("prediction", row.get("response", row.get("text", "")))
            if not sample_id:
                raise ValueError(f"Missing id in prediction file line {line_number}")
            predictions[sample_id] = str(prediction)
    return predictions


def score_prediction_file(
    samples: Sequence[AgentDataSample], prediction_file: Path, model_label: str
) -> list[dict[str, Any]]:
    predictions = load_prediction_file(prediction_file)
    rows = []
    for sample in samples:
        if sample.id not in predictions:
            raise ValueError(f"Missing prediction for sample id {sample.id!r}")
        rows.append(evaluate_prediction(sample, model_label, predictions[sample.id]))
    return rows


def run_model_predictions(
    samples: Sequence[AgentDataSample],
    model_name_or_path: str,
    model_label: str,
    adapter_path: str | None = None,
    max_new_tokens: int = 160,
    batch_size: int = 1,
    device: str | None = None,
    local_files_only: bool = False,
    enable_thinking: bool | None = None,
) -> list[dict[str, Any]]:
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise RuntimeError(
            "Model evaluation requires torch and transformers in the active environment."
        ) from exc

    if batch_size < 1:
        raise ValueError("batch_size must be positive")

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
            raise RuntimeError(
                "Adapter evaluation requires peft in the active environment."
            ) from exc
        model = PeftModel.from_pretrained(model, adapter_path, local_files_only=local_files_only)
    model.to(resolved_device)
    model.eval()

    rows: list[dict[str, Any]] = []
    with torch.inference_mode():
        for batch in _batched(list(samples), batch_size):
            prompts = [
                _format_prompt(tokenizer, sample, enable_thinking=enable_thinking)
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
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
            decoded = tokenizer.batch_decode(
                outputs[:, prompt_length:],
                skip_special_tokens=True,
            )
            for sample, prediction in zip(batch, decoded):
                rows.append(evaluate_prediction(sample, model_label, prediction.strip()))
    return rows


def _format_prompt(
    tokenizer: Any, sample: AgentDataSample, enable_thinking: bool | None = None
) -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a ReAct agent that must cite tool observations. "
                "Use at most two wikidata_lookup actions: first find the birthplace, "
                "then find that birthplace's country. Stop once the country is known. "
                "The final line must be exactly `Final: <country>`."
            ),
        },
        {
            "role": "user",
            "content": (
                f"{sample.question}\n"
                "Use only Thought, Action, Observation, and Final lines. "
                "Do not output any text after Final."
            ),
        },
    ]
    if getattr(tokenizer, "chat_template", None):
        kwargs = {
            "tokenize": False,
            "add_generation_prompt": True,
        }
        if enable_thinking is not None:
            kwargs["enable_thinking"] = enable_thinking
        try:
            return tokenizer.apply_chat_template(messages, **kwargs)
        except TypeError:
            kwargs.pop("enable_thinking", None)
            return tokenizer.apply_chat_template(messages, **kwargs)
    return (
        f"System: {messages[0]['content']}\n"
        f"User: {messages[1]['content']}\n"
        "Assistant:"
    )


def _batched(items: Sequence[AgentDataSample], batch_size: int) -> Iterable[list[AgentDataSample]]:
    for start in range(0, len(items), batch_size):
        yield list(items[start : start + batch_size])
