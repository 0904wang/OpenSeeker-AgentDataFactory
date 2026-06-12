import csv
import json
from pathlib import Path

from openseeker_factory.evaluation import (
    _format_prompt,
    evaluate_prediction,
    extract_final_answer,
    summarize_prediction_rows,
    tool_call_coverage,
    write_evaluation_outputs,
)
from openseeker_factory.schema import AgentDataSample, ToolCall, VerifierResult


def _sample(task_type: str = "tool_use_qa") -> AgentDataSample:
    return AgentDataSample(
        id="sample-1",
        task_type=task_type,
        question="Use the lookup tool to find Ada Lovelace's birthplace country.",
        answer="United Kingdom",
        gold_evidence=[
            "Ada Lovelace was born in London.",
            "London is located in United Kingdom.",
        ],
        tool_calls=[
            ToolCall(
                tool="wikidata_lookup",
                query="Ada Lovelace birthplace",
                result="London",
            ),
            ToolCall(
                tool="wikidata_lookup",
                query="London country",
                result="United Kingdom",
            ),
        ],
        trajectory=[
            "Thought: Identify birthplace.",
            "Action: wikidata_lookup[Ada Lovelace birthplace]",
            "Observation: London",
            "Thought: Resolve country.",
            "Action: wikidata_lookup[London country]",
            "Observation: United Kingdom",
            "Final: United Kingdom",
        ],
        verifier_result=VerifierResult(
            passed=True,
            checks={
                "not_duplicate": True,
                "answer_supported": True,
                "evidence_coverage": True,
                "tool_success": True,
                "trajectory_valid": True,
            },
            reasons=[],
        ),
        difficulty="medium",
        source={"seed_id": "sample-1"},
        quality_score=1.0,
    )


def test_extract_final_answer_takes_last_final_line():
    prediction = "\n".join(
        [
            "Thought: draft.",
            "Final: London",
            "Thought: correction.",
            "Final: United Kingdom.",
        ]
    )

    assert extract_final_answer(prediction) == "United Kingdom"


def test_evaluate_prediction_scores_react_answer_and_tool_calls():
    prediction = "\n".join(
        [
            "Thought: I need the birthplace.",
            "Action: wikidata_lookup[Ada Lovelace birthplace]",
            "Observation: London",
            "Thought: I need the country.",
            "Action: wikidata_lookup[London country]",
            "Observation: United Kingdom",
            "Final: United Kingdom.",
        ]
    )

    row = evaluate_prediction(_sample(), "qwen3-8b-lora", prediction)

    assert row["model_label"] == "qwen3-8b-lora"
    assert row["predicted_answer"] == "United Kingdom"
    assert row["exact_match"] is True
    assert row["answer_f1"] == 1.0
    assert row["gold_answer_mentioned"] is True
    assert row["tool_call_success"] is True
    assert row["tool_call_coverage"] == 1.0
    assert row["observation_faithfulness"] is True
    assert row["observation_coverage"] == 1.0
    assert row["trajectory_valid"] is True
    assert row["hallucination_proxy"] is False


def test_evaluate_prediction_flags_wrong_observation_despite_canonical_action():
    sample = _sample()
    sample.tool_calls = [
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
    ]
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

    row = evaluate_prediction(sample, "qwen3-8b-lora", prediction)

    assert row["exact_match"] is True
    assert row["tool_call_coverage"] == 1.0
    assert row["observation_coverage"] == 0.5
    assert row["observation_faithfulness"] is False


def test_evaluate_prediction_flags_wrong_unsupported_final_answer():
    prediction = "Thought: Guess.\nFinal: France"

    row = evaluate_prediction(_sample(task_type="multi_hop_qa"), "base", prediction)

    assert row["exact_match"] is False
    assert row["answer_f1"] == 0.0
    assert row["gold_answer_mentioned"] is False
    assert row["tool_call_success"] is False
    assert row["trajectory_valid"] is False
    assert row["hallucination_proxy"] is True
    assert row["error_bucket"] == "unsupported_wrong_answer"


def test_evaluate_prediction_tracks_canonical_country_alias_separately():
    prediction = "\n".join(
        [
            "Thought: I need the birthplace.",
            "Action: wikidata_lookup[Ada Lovelace birthplace]",
            "Observation: London",
            "Thought: I need the country.",
            "Action: wikidata_lookup[London country]",
            "Observation: United Kingdom",
            "Final: England",
        ]
    )

    row = evaluate_prediction(_sample(), "qwen3-8b-lora", prediction)

    assert row["exact_match"] is False
    assert row["canonical_match"] is True
    assert row["error_bucket"] == "canonical_alias_match"
    assert row["hallucination_proxy"] is False


def test_evaluate_prediction_tracks_answer_mention_without_final_format():
    prediction = "Ada Lovelace was born in London, which is in the United Kingdom."

    row = evaluate_prediction(_sample(), "base", prediction)

    assert row["predicted_answer"] == ""
    assert row["exact_match"] is False
    assert row["gold_answer_mentioned"] is True
    assert row["final_answer_present"] is False
    assert row["trajectory_valid"] is False
    assert row["error_bucket"] == "missing_final"


def test_evaluate_prediction_buckets_correct_answer_with_tool_gap():
    prediction = "\n".join(
        [
            "Thought: I know the answer.",
            "Action: wikidata_lookup[Ada Lovelace birthplace]",
            "Observation: London",
            "Final: United Kingdom",
        ]
    )

    row = evaluate_prediction(_sample(), "qwen3-8b-lora", prediction)

    assert row["exact_match"] is True
    assert row["tool_call_success"] is False
    assert row["trajectory_valid"] is True
    assert row["error_bucket"] == "tool_coverage_gap"


def test_tool_call_coverage_matches_diacritic_location_query():
    prediction = "Action: wikidata_lookup[Würzburg]\nObservation: Würzburg is in Germany."

    coverage = tool_call_coverage(
        prediction,
        [
            ToolCall(
                tool="wikidata_lookup",
                query="Wurzburg country",
                result="Germany",
            )
        ],
    )

    assert coverage == 1.0


def test_tool_call_coverage_matches_initials_without_punctuation():
    prediction = "Action: wikidata_lookup[CV Raman]\nObservation: C. V. Raman was born in Tiruchirappalli."

    coverage = tool_call_coverage(
        prediction,
        [
            ToolCall(
                tool="wikidata_lookup",
                query="C. V. Raman birthplace",
                result="Tiruchirappalli",
            )
        ],
    )

    assert coverage == 1.0


def test_tool_call_coverage_matches_shortened_location_query():
    prediction = "Action: wikidata_lookup[La Haye]\nObservation: La Haye is located in France."

    coverage = tool_call_coverage(
        prediction,
        [
            ToolCall(
                tool="wikidata_lookup",
                query="La Haye en Touraine country",
                result="France",
            )
        ],
    )

    assert coverage == 1.0


def test_format_prompt_requires_bounded_lookup_and_final_line():
    class FakeChatTokenizer:
        chat_template = "fake"

        def __init__(self):
            self.messages = None
            self.kwargs = None

        def apply_chat_template(self, messages, **kwargs):
            self.messages = messages
            self.kwargs = kwargs
            return "rendered prompt"

    tokenizer = FakeChatTokenizer()

    prompt = _format_prompt(tokenizer, _sample(), enable_thinking=False)

    assert prompt == "rendered prompt"
    assert tokenizer.kwargs["enable_thinking"] is False
    system_content = tokenizer.messages[0]["content"]
    user_content = tokenizer.messages[1]["content"]
    assert "at most two" in system_content.lower()
    assert "Final: <country>" in system_content
    assert "Do not output any text after Final" in user_content


def test_summarize_prediction_rows_includes_overall_and_task_rows():
    rows = [
        evaluate_prediction(
            _sample("tool_use_qa"),
            "model-a",
            "\n".join(
                [
                    "Thought: I need the birthplace.",
                    "Action: wikidata_lookup[Ada Lovelace birthplace]",
                    "Observation: London",
                    "Thought: I need the country.",
                    "Action: wikidata_lookup[London country]",
                    "Observation: United Kingdom",
                    "Final: United Kingdom",
                ]
            ),
        ),
        evaluate_prediction(_sample("multi_hop_qa"), "model-a", "Final: France"),
    ]

    summary = summarize_prediction_rows(rows)

    assert summary[0]["split"] == "overall"
    assert summary[0]["total"] == 2
    assert summary[0]["exact_match_rate"] == 0.5
    assert summary[0]["canonical_match_rate"] == 0.5
    assert summary[0]["gold_answer_mention_rate"] == 0.5
    assert summary[0]["observation_faithfulness_rate"] == 0.5
    assert summary[0]["observation_coverage_avg"] == 0.5
    assert summary[0]["hallucination_rate"] == 0.5
    assert summary[0]["correct_rate"] == 0.5
    assert summary[0]["unsupported_wrong_answer_rate"] == 0.5
    assert {row["split"] for row in summary[1:]} == {"multi_hop_qa", "tool_use_qa"}


def test_write_evaluation_outputs_writes_jsonl_and_summary_csv(tmp_path: Path):
    rows = [
        evaluate_prediction(_sample("tool_use_qa"), "model-a", "Final: United Kingdom"),
    ]

    predictions_path, summary_path = write_evaluation_outputs(
        rows, tmp_path, model_label="model-a"
    )

    prediction_row = json.loads(predictions_path.read_text(encoding="utf-8"))
    assert prediction_row["id"] == "sample-1"
    with summary_path.open("r", encoding="utf-8", newline="") as handle:
        summary_rows = list(csv.DictReader(handle))
    assert summary_rows[0]["model_label"] == "model-a"
    assert summary_rows[0]["exact_match_rate"] == "1.0"
