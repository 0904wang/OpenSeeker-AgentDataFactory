import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

from openseeker_factory.rft import (
    build_candidate_prediction_row,
    run_rft_filter,
    validate_sampling_args,
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
        verifier_result=VerifierResult(
            passed=True,
            checks={
                "answer_supported": True,
                "tool_success": True,
                "evidence_faithfulness": True,
                "trajectory_valid": True,
            },
            reasons=[],
        ),
        difficulty="hard",
        source={"seed_id": "sample-1", "data_version": "canonical-v6-blind-tool-choice-hard"},
        quality_score=1.0,
    )


def _write_samples(path: Path, samples: list[AgentDataSample]) -> None:
    path.write_text(
        "".join(json.dumps(sample.to_json_dict()) + "\n" for sample in samples),
        encoding="utf-8",
    )


def _write_predictions(path: Path) -> None:
    good_prediction = "\n".join(
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
    bad_observation = "\n".join(
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
    rows = [
        build_candidate_prediction_row(
            sample_id="sample-1",
            candidate_index=0,
            prediction=good_prediction,
            model_label="a0",
        ),
        build_candidate_prediction_row(
            sample_id="sample-1",
            candidate_index=1,
            prediction=bad_observation,
            model_label="a0",
        ),
    ]
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_rft_filter_exports_only_candidates_that_pass_required_checks(tmp_path: Path):
    samples_path = tmp_path / "samples.jsonl"
    predictions_path = tmp_path / "predictions.jsonl"
    out_dir = tmp_path / "rft"
    _write_samples(samples_path, [_sample()])
    _write_predictions(predictions_path)

    summary = run_rft_filter(
        samples_path=samples_path,
        prediction_file=predictions_path,
        out_dir=out_dir,
        model_label="a0",
        iteration=1,
    )

    assert summary["sampled_total"] == 2
    assert summary["accepted_total"] == 1
    assert summary["rejected_total"] == 1
    assert summary["verifier_pass_rate"] == 0.5
    assert summary["unique_trajectory_rate"] == 1.0
    assert summary["unique_action_sequence_rate"] == 1.0
    assert summary["per_task_type"]["tool_use_qa"]["sampled_total"] == 2
    assert summary["per_task_type"]["tool_use_qa"]["accepted_total"] == 1
    assert summary["per_task_type"]["tool_use_qa"]["pass_rate"] == 0.5

    accepted_rows = [
        json.loads(line)
        for line in (out_dir / "accepted_samples.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert len(accepted_rows) == 1
    assert accepted_rows[0]["id"] == "sample-1-rft-0001"
    assert accepted_rows[0]["source"]["rft_parent_id"] == "sample-1"
    assert accepted_rows[0]["source"]["rft_iteration"] == 1
    assert accepted_rows[0]["trajectory"][-1] == "Final: United Kingdom"

    sft_row = json.loads(
        (out_dir / "rft_sft_conversations.jsonl").read_text(encoding="utf-8")
    )
    assert sft_row["id"] == "sample-1-rft-0001"
    assert sft_row["messages"][2]["content"].startswith("Thought:")

    scored_rows = [
        json.loads(line)
        for line in (out_dir / "candidates_scored.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [row["accepted"] for row in scored_rows] == [True, False]
    assert scored_rows[1]["rejection_reasons"] == ["evidence_faithfulness"]

    with (out_dir / "rft_summary.csv").open("r", encoding="utf-8", newline="") as handle:
        summary_rows = list(csv.DictReader(handle))
    assert summary_rows[0]["sampled_total"] == "2"
    assert summary_rows[0]["accepted_total"] == "1"
    assert summary_rows[0]["verifier_pass_rate"] == "0.5"


def test_rft_filter_cli_writes_summary(tmp_path: Path):
    samples_path = tmp_path / "samples.jsonl"
    predictions_path = tmp_path / "predictions.jsonl"
    out_dir = tmp_path / "rft-cli"
    _write_samples(samples_path, [_sample()])
    _write_predictions(predictions_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "openseeker_factory.cli",
            "rft-filter",
            "--samples",
            str(samples_path),
            "--prediction-file",
            str(predictions_path),
            "--out-dir",
            str(out_dir),
            "--model-label",
            "a0",
            "--iteration",
            "1",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "OpenSeeker RFT filter complete" in result.stdout
    assert "accepted=1 rejected=1" in result.stdout
    assert (out_dir / "rft_summary.json").exists()


def test_validate_sampling_args_rejects_non_positive_values():
    with pytest.raises(ValueError, match="num_return_sequences"):
        validate_sampling_args(
            num_return_sequences=0,
            temperature=0.7,
            top_p=0.95,
            batch_size=1,
        )
    with pytest.raises(ValueError, match="temperature"):
        validate_sampling_args(
            num_return_sequences=4,
            temperature=0.0,
            top_p=0.95,
            batch_size=1,
        )
    with pytest.raises(ValueError, match="top_p"):
        validate_sampling_args(
            num_return_sequences=4,
            temperature=0.7,
            top_p=1.5,
            batch_size=1,
        )


def test_build_candidate_prediction_row_has_stable_candidate_id():
    row = build_candidate_prediction_row(
        sample_id="sample-1",
        candidate_index=7,
        prediction="Final: United Kingdom",
        model_label="a0",
    )

    assert row == {
        "id": "sample-1",
        "candidate_id": "sample-1-rft-cand-0007",
        "candidate_index": 7,
        "model_label": "a0",
        "prediction": "Final: United Kingdom",
    }
