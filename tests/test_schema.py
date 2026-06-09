import pytest

from openseeker_factory.schema import AgentDataSample, ToolCall, VerifierResult


def test_sample_round_trip_preserves_required_jsonl_fields():
    sample = AgentDataSample(
        id="sample-1",
        task_type="multi_hop_qa",
        question="Which country is the capital city of the birthplace of Ada Lovelace in?",
        answer="United Kingdom",
        gold_evidence=[
            "Ada Lovelace was born in London.",
            "London is the capital of the United Kingdom.",
        ],
        tool_calls=[
            ToolCall(tool="wikidata_lookup", query="Ada Lovelace birthplace", result="London")
        ],
        trajectory=[
            "Thought: Find Ada Lovelace's birthplace.",
            "Action: wikidata_lookup[Ada Lovelace birthplace]",
            "Observation: London",
            "Thought: Find the country whose capital is London.",
            "Final: United Kingdom",
        ],
        verifier_result=VerifierResult(
            passed=True,
            checks={
                "answer_supported": True,
                "evidence_coverage": True,
                "tool_success": True,
                "trajectory_valid": True,
            },
            reasons=[],
        ),
        difficulty="medium",
        source={"seed": "wikidata-demo"},
        quality_score=0.93,
    )

    row = sample.to_json_dict()
    assert list(row.keys()) == [
        "id",
        "task_type",
        "question",
        "answer",
        "gold_evidence",
        "tool_calls",
        "trajectory",
        "verifier_result",
        "difficulty",
        "source",
        "quality_score",
    ]

    restored = AgentDataSample.from_json_dict(row)
    assert restored == sample


def test_sample_validation_rejects_unknown_task_type():
    with pytest.raises(ValueError, match="task_type"):
        AgentDataSample(
            id="bad",
            task_type="unsupported",
            question="q",
            answer="a",
            gold_evidence=["a"],
            tool_calls=[],
            trajectory=["Final: a"],
            verifier_result=VerifierResult(passed=True, checks={}, reasons=[]),
            difficulty="easy",
            source={},
            quality_score=0.5,
        )


def test_sample_validation_rejects_quality_score_outside_unit_interval():
    with pytest.raises(ValueError, match="quality_score"):
        AgentDataSample(
            id="bad-score",
            task_type="multi_hop_qa",
            question="q",
            answer="a",
            gold_evidence=["a"],
            tool_calls=[],
            trajectory=["Final: a"],
            verifier_result=VerifierResult(passed=True, checks={}, reasons=[]),
            difficulty="easy",
            source={},
            quality_score=1.5,
        )

