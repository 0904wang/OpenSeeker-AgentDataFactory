from __future__ import annotations

from dataclasses import dataclass
from typing import Any

TASK_TYPES = {
    "multi_hop_qa",
    "tool_use_qa",
    "noisy_context_retrieval_qa",
}

DIFFICULTIES = {"easy", "medium", "hard"}


@dataclass(eq=True)
class ToolCall:
    tool: str
    query: str
    result: str

    def to_json_dict(self) -> dict[str, str]:
        return {
            "tool": self.tool,
            "query": self.query,
            "result": self.result,
        }

    @classmethod
    def from_json_dict(cls, row: dict[str, Any]) -> "ToolCall":
        return cls(
            tool=str(row["tool"]),
            query=str(row["query"]),
            result=str(row["result"]),
        )


@dataclass(eq=True)
class VerifierResult:
    passed: bool
    checks: dict[str, bool]
    reasons: list[str]

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "checks": dict(self.checks),
            "reasons": list(self.reasons),
        }

    @classmethod
    def from_json_dict(cls, row: dict[str, Any]) -> "VerifierResult":
        return cls(
            passed=bool(row["passed"]),
            checks={str(key): bool(value) for key, value in row["checks"].items()},
            reasons=[str(reason) for reason in row["reasons"]],
        )


@dataclass(eq=True)
class AgentDataSample:
    id: str
    task_type: str
    question: str
    answer: str
    gold_evidence: list[str]
    tool_calls: list[ToolCall]
    trajectory: list[str]
    verifier_result: VerifierResult
    difficulty: str
    source: dict[str, Any]
    quality_score: float

    def __post_init__(self) -> None:
        if self.task_type not in TASK_TYPES:
            raise ValueError(f"task_type must be one of {sorted(TASK_TYPES)}")
        if self.difficulty not in DIFFICULTIES:
            raise ValueError(f"difficulty must be one of {sorted(DIFFICULTIES)}")
        if not 0.0 <= self.quality_score <= 1.0:
            raise ValueError("quality_score must be between 0 and 1")
        if not self.id:
            raise ValueError("id is required")
        if not self.question:
            raise ValueError("question is required")
        if not self.answer:
            raise ValueError("answer is required")
        if not self.gold_evidence:
            raise ValueError("gold_evidence is required")
        if not self.trajectory:
            raise ValueError("trajectory is required")

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "task_type": self.task_type,
            "question": self.question,
            "answer": self.answer,
            "gold_evidence": list(self.gold_evidence),
            "tool_calls": [tool_call.to_json_dict() for tool_call in self.tool_calls],
            "trajectory": list(self.trajectory),
            "verifier_result": self.verifier_result.to_json_dict(),
            "difficulty": self.difficulty,
            "source": dict(self.source),
            "quality_score": self.quality_score,
        }

    @classmethod
    def from_json_dict(cls, row: dict[str, Any]) -> "AgentDataSample":
        return cls(
            id=str(row["id"]),
            task_type=str(row["task_type"]),
            question=str(row["question"]),
            answer=str(row["answer"]),
            gold_evidence=[str(item) for item in row["gold_evidence"]],
            tool_calls=[
                ToolCall.from_json_dict(tool_call) for tool_call in row["tool_calls"]
            ],
            trajectory=[str(item) for item in row["trajectory"]],
            verifier_result=VerifierResult.from_json_dict(row["verifier_result"]),
            difficulty=str(row["difficulty"]),
            source=dict(row["source"]),
            quality_score=float(row["quality_score"]),
        )

