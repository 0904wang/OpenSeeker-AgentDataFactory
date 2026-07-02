from openseeker_factory.rlvr import (
    RLVRRollout,
    _with_group_advantages,
    extract_observation_branch_prefix,
    summarize_rlvr,
)
from openseeker_factory.schema import AgentDataSample, ToolCall, VerifierResult


def _sample(sample_id: str = "sample-1") -> AgentDataSample:
    return AgentDataSample(
        id=sample_id,
        task_type="tool_use_qa",
        question="Use the lookup tool to find Ada Lovelace's birthplace country.",
        answer="United Kingdom",
        gold_evidence=[
            "Ada Lovelace was born in London.",
            "London is located in United Kingdom.",
        ],
        tool_calls=[
            ToolCall("wikidata_lookup", "Ada Lovelace, P19", "London"),
            ToolCall("wikidata_lookup", "London, P17", "United Kingdom"),
        ],
        trajectory=[
            "Thought: Identify birthplace.",
            "Action: wikidata_lookup[Ada Lovelace, P19]",
            "Observation: London",
            "Final: United Kingdom",
        ],
        verifier_result=VerifierResult(passed=True, checks={}, reasons=[]),
        difficulty="hard",
        source={},
        quality_score=1.0,
    )


def _rollout(sample_id: str, reward: float) -> RLVRRollout:
    sample = _sample(sample_id)
    return RLVRRollout(
        sample=sample,
        prompt="prompt",
        prediction="Final: United Kingdom",
        candidate_id=f"{sample_id}-{reward}",
        candidate_index=0,
        reward_row={
            "reward": reward,
            "binary_all_pass_reward": 1.0 if reward == 1.0 else 0.0,
        },
    )


def test_extract_observation_branch_prefix_stops_after_first_observation():
    prediction = "\n".join(
        [
            "Thought: choose relation.",
            "Action: wikidata_lookup[Ada Lovelace, P19]",
            "Observation: London",
            "Thought: resolve country.",
            "Action: wikidata_lookup[London, P17]",
        ]
    )

    assert extract_observation_branch_prefix(prediction) == (
        "Thought: choose relation.\n"
        "Action: wikidata_lookup[Ada Lovelace, P19]\n"
        "Observation: London\n"
    )


def test_extract_observation_branch_prefix_requires_action_before_observation():
    assert extract_observation_branch_prefix("Thought: x\nObservation: London") == ""


def test_group_advantages_are_normalized_per_prompt():
    rollouts = [
        _rollout("sample-1", 1.0),
        _rollout("sample-1", 0.0),
        _rollout("sample-2", 0.5),
        _rollout("sample-2", 0.5),
    ]

    scored = _with_group_advantages(rollouts)

    assert [row.advantage for row in scored] == [1.0, -1.0, 0.0, 0.0]


def test_summarize_rlvr_reports_reward_and_training_stats():
    rollouts = _with_group_advantages([_rollout("sample-1", 1.0), _rollout("sample-1", 0.0)])
    summary = summarize_rlvr(
        rollouts,
        [{"loss": 0.2}, {"loss": -0.1}],
        algorithm="grpo",
        reward_mode="weighted",
    )

    assert summary["algorithm"] == "grpo"
    assert summary["rollouts"] == 2
    assert summary["reward_avg"] == 0.5
    assert summary["binary_pass_rate"] == 0.5
    assert summary["advantage_abs_avg"] == 1.0
    assert summary["train_steps"] == 2
    assert summary["train_loss_avg"] == 0.05
