import csv
import json
import subprocess
import sys
from pathlib import Path

from openseeker_factory.evaluation import evaluate_prediction
from openseeker_factory.rewards import (
    binary_all_pass_reward,
    build_verifier_reward_row,
    run_score_verifier_rewards,
    score_weighted_verifier_reward,
)
from openseeker_factory.schema import AgentDataSample, ToolCall, VerifierResult


def _sample() -> AgentDataSample:
    return AgentDataSample(
        id="sample-1",
        task_type="tool_use_qa",
        question="Use the lookup tool to find Ada Lovelace's birthplace country.",
        answer="United Kingdom",
        gold_evidence=[
            "Ada Lovelace was born in London.",
            "London is located in United Kingdom.",
        ],
        tool_calls=[
            ToolCall(
                tool="wikidata_lookup",
                query="Ada Lovelace, P19",
                result="London",
            ),
            ToolCall(
                tool="wikidata_lookup",
                query="London, P17",
                result="United Kingdom",
            ),
        ],
        trajectory=[
            "Thought: Identify birthplace.",
            "Action: wikidata_lookup[Ada Lovelace, P19]",
            "Observation: London",
            "Thought: Resolve country.",
            "Action: wikidata_lookup[London, P17]",
            "Observation: United Kingdom",
            "Final: United Kingdom",
        ],
        verifier_result=VerifierResult(passed=True, checks={}, reasons=[]),
        difficulty="hard",
        source={"seed_id": "sample-1"},
        quality_score=1.0,
    )


def _good_prediction() -> str:
    return "\n".join(
        [
            "Thought: I need the birthplace.",
            "Action: wikidata_lookup[Ada Lovelace, P19]",
            "Observation: London",
            "Thought: I need the country.",
            "Action: wikidata_lookup[London, P17]",
            "Observation: United Kingdom",
            "Final: United Kingdom",
        ]
    )


def test_weighted_reward_scores_all_pass_prediction_as_one():
    evaluation = evaluate_prediction(_sample(), "model", _good_prediction())

    weighted = score_weighted_verifier_reward(evaluation)

    assert binary_all_pass_reward(evaluation) == 1.0
    assert weighted["reward"] == 1.0
    assert weighted["components"] == {
        "answer": 1.0,
        "tool": 1.0,
        "evidence": 1.0,
        "format": 1.0,
    }
    assert weighted["applied_caps"] == []


def test_weighted_reward_keeps_evidence_faithfulness_continuous():
    prediction = "\n".join(
        [
            "Thought: I need the birthplace.",
            "Action: wikidata_lookup[Ada Lovelace, P19]",
            "Observation: Cambridge",
            "Thought: I need the country.",
            "Action: wikidata_lookup[Cambridge, P17]",
            "Observation: United Kingdom",
            "Final: United Kingdom",
        ]
    )
    evaluation = evaluate_prediction(_sample(), "model", prediction)

    weighted = score_weighted_verifier_reward(evaluation)

    assert binary_all_pass_reward(evaluation) == 0.0
    assert weighted["components"]["answer"] == 1.0
    assert weighted["components"]["tool"] == 1.0
    assert weighted["components"]["evidence"] == 0.5
    assert weighted["components"]["format"] == 1.0
    assert weighted["reward"] == 0.825


def test_weighted_reward_caps_right_answer_with_tool_gap():
    prediction = "\n".join(
        [
            "Thought: I need the birthplace.",
            "Action: wikidata_lookup[Ada Lovelace, P19]",
            "Observation: London",
            "Final: United Kingdom",
        ]
    )
    evaluation = evaluate_prediction(_sample(), "model", prediction)

    weighted = score_weighted_verifier_reward(evaluation)

    assert weighted["raw_reward"] == 0.675
    assert weighted["reward"] == 0.65
    assert weighted["applied_caps"] == ["right_answer_tool_gap_cap_0.65"]


def test_build_verifier_reward_row_uses_selected_reward_mode():
    row = build_verifier_reward_row(
        sample=_sample(),
        prediction_row={
            "id": "sample-1",
            "candidate_id": "sample-1-cand-0000",
            "candidate_index": 0,
            "prediction": _good_prediction(),
        },
        model_label="model",
        reward_mode="binary",
    )

    assert row["reward"] == 1.0
    assert row["binary_all_pass_reward"] == 1.0
    assert row["weighted_verifier_reward"] == 1.0
    assert row["verifier_checks"] == {
        "answer_supported": True,
        "tool_success": True,
        "evidence_faithfulness": True,
        "trajectory_valid": True,
    }


def test_score_verifier_rewards_writes_jsonl_and_summary(tmp_path: Path):
    samples_path = tmp_path / "samples.jsonl"
    samples_path.write_text(
        json.dumps(_sample().to_json_dict()) + "\n",
        encoding="utf-8",
    )
    predictions_path = tmp_path / "predictions.jsonl"
    predictions_path.write_text(
        "\n".join(
            [
                json.dumps({"id": "sample-1", "prediction": _good_prediction()}),
                json.dumps({"id": "sample-1", "prediction": "Thought: Guess.\nFinal: France"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    rewards_path, summary = run_score_verifier_rewards(
        samples_path=samples_path,
        prediction_file=predictions_path,
        out_dir=tmp_path / "rewards",
        model_label="model",
        reward_mode="weighted",
    )

    rows = [json.loads(line) for line in rewards_path.read_text(encoding="utf-8").splitlines()]
    assert [row["reward"] for row in rows] == [1.0, 0.05]
    assert summary["total"] == 2
    assert summary["reward_avg"] == 0.525
    assert summary["binary_pass_rate"] == 0.5
    with (tmp_path / "rewards" / "verifier_reward_summary.csv").open(
        "r", encoding="utf-8", newline=""
    ) as handle:
        csv_rows = list(csv.DictReader(handle))
    assert csv_rows[0]["split"] == "overall"
    assert csv_rows[0]["reward_avg"] == "0.525"


def test_score_verifier_rewards_cli(tmp_path: Path):
    samples_path = tmp_path / "samples.jsonl"
    samples_path.write_text(
        json.dumps(_sample().to_json_dict()) + "\n",
        encoding="utf-8",
    )
    predictions_path = tmp_path / "predictions.jsonl"
    predictions_path.write_text(
        json.dumps({"id": "sample-1", "prediction": _good_prediction()}) + "\n",
        encoding="utf-8",
    )
    out_dir = tmp_path / "rewards-cli"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "openseeker_factory.cli",
            "score-verifier-rewards",
            "--samples",
            str(samples_path),
            "--prediction-file",
            str(predictions_path),
            "--out-dir",
            str(out_dir),
            "--model-label",
            "model",
            "--reward-mode",
            "binary",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "OpenSeeker verifier reward scoring complete" in result.stdout
    assert "binary_pass_rate=1.0" in result.stdout
    reward_row = json.loads((out_dir / "verifier_rewards.jsonl").read_text(encoding="utf-8"))
    assert reward_row["reward_mode"] == "binary"
    assert reward_row["reward"] == 1.0
