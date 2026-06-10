from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from openseeker_factory.backends import ChatBackend
from openseeker_factory.schema import AgentDataSample, ToolCall, VerifierResult


@dataclass(eq=True)
class SeedTask:
    id: str
    task_type: str
    entity: str
    relation: str
    intermediate: str
    answer: str
    evidence: list[str]
    noisy_context: list[str]
    variant_index: int = 0


@dataclass(eq=True)
class EvolvedTask:
    id: str
    task_type: str
    question: str
    answer: str
    evidence: list[str]
    noisy_context: list[str]
    tool_plan: list[ToolCall]
    difficulty: str
    source: dict[str, Any]
    trajectory_draft: list[str] | None = None


@dataclass(eq=True)
class QualityMetrics:
    total: int
    accepted: int
    rejected: int
    dedup_rate: float
    solvability_rate: float
    evidence_hit_rate: float
    tool_success_rate: float
    trajectory_valid_rate: float
    manual_sample_pass_rate: float | None = None

    def to_row(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "accepted": self.accepted,
            "rejected": self.rejected,
            "dedup_rate": self.dedup_rate,
            "solvability_rate": self.solvability_rate,
            "evidence_hit_rate": self.evidence_hit_rate,
            "tool_success_rate": self.tool_success_rate,
            "trajectory_valid_rate": self.trajectory_valid_rate,
            "manual_sample_pass_rate": self.manual_sample_pass_rate,
        }


class AgentDataFactory:
    def __init__(
        self,
        seeds: list[SeedTask],
        seed_source_label: str = "wikidata-demo",
        teacher_backend: ChatBackend | None = None,
    ) -> None:
        if not seeds:
            raise ValueError("at least one seed task is required")
        self._seeds = seeds
        self._seed_source_label = seed_source_label
        self._teacher_backend = teacher_backend

    @classmethod
    def from_demo_knowledge_graph(
        cls, teacher_backend: ChatBackend | None = None
    ) -> "AgentDataFactory":
        seeds = [
            SeedTask(
                id="demo-ada",
                task_type="multi_hop_qa",
                entity="Ada Lovelace",
                relation="birthplace_capital_country",
                intermediate="London",
                answer="United Kingdom",
                evidence=[
                    "Ada Lovelace was born in London.",
                    "London is the capital of the United Kingdom.",
                ],
                noisy_context=[
                    "Ada Lovelace collaborated with Charles Babbage.",
                    "The Analytical Engine was never completed in Lovelace's lifetime.",
                ],
            ),
            SeedTask(
                id="demo-curie",
                task_type="tool_use_qa",
                entity="Marie Curie",
                relation="birthplace_current_country",
                intermediate="Warsaw",
                answer="Poland",
                evidence=[
                    "Marie Curie was born in Warsaw.",
                    "Warsaw is the capital of Poland.",
                ],
                noisy_context=[
                    "Marie Curie won Nobel Prizes in Physics and Chemistry.",
                    "Paris was an important city in Curie's research career.",
                ],
            ),
            SeedTask(
                id="demo-turing",
                task_type="noisy_context_retrieval_qa",
                entity="Alan Turing",
                relation="birthplace_country",
                intermediate="London",
                answer="United Kingdom",
                evidence=[
                    "Alan Turing was born in London.",
                    "London is located in the United Kingdom.",
                ],
                noisy_context=[
                    "Alan Turing worked at Bletchley Park.",
                    "The Turing Award is named after Alan Turing.",
                    "Manchester was one of Turing's later workplaces.",
                ],
            ),
        ]
        return cls(
            seeds,
            seed_source_label="wikidata-demo",
            teacher_backend=teacher_backend,
        )

    @classmethod
    def from_seed_file(
        cls, path: Path, teacher_backend: ChatBackend | None = None
    ) -> "AgentDataFactory":
        seeds: list[SeedTask] = []
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                try:
                    seeds.append(
                        SeedTask(
                            id=str(row["id"]),
                            task_type=str(row["task_type"]),
                            entity=str(row["entity"]),
                            relation=str(row["relation"]),
                            intermediate=str(row["intermediate"]),
                            answer=str(row["answer"]),
                            evidence=[str(item) for item in row["evidence"]],
                            noisy_context=[
                                str(item) for item in row.get("noisy_context", [])
                            ],
                            variant_index=0,
                        )
                    )
                except KeyError as exc:
                    raise ValueError(
                        f"Missing required seed field {exc.args[0]!r} on line {line_number}"
                    ) from exc
        return cls(
            seeds,
            seed_source_label=path.as_posix(),
            teacher_backend=teacher_backend,
        )

    def generate_verified(
        self, count: int, strategy: str = "evol_instruct"
    ) -> tuple[list[AgentDataSample], list[AgentDataSample], QualityMetrics]:
        seeds = self.seed_expand(count=count)
        tasks = [self.evolve_task(seed, strategy=strategy) for seed in seeds]
        samples = [self.generate_trajectory(task) for task in tasks]
        return self.verify_and_filter(samples)

    def seed_expand(self, count: int) -> list[SeedTask]:
        if count < 1:
            raise ValueError("count must be positive")
        expanded = []
        for index in range(count):
            base = self._seeds[index % len(self._seeds)]
            expanded.append(
                SeedTask(
                    id=f"{base.id}-{index + 1}",
                    task_type=base.task_type,
                    entity=base.entity,
                    relation=base.relation,
                    intermediate=base.intermediate,
                    answer=base.answer,
                    evidence=list(base.evidence),
                    noisy_context=list(base.noisy_context),
                    variant_index=index + 1,
                )
            )
        return expanded

    def evolve_task(
        self, seed: SeedTask, strategy: str = "evol_instruct"
    ) -> EvolvedTask:
        if strategy not in {"evol_instruct", "magpie_self_instruct"}:
            raise ValueError("strategy must be evol_instruct or magpie_self_instruct")

        question = self._build_question(seed)

        tool_plan = [
            ToolCall(
                tool="wikidata_lookup",
                query=f"{seed.entity} birthplace",
                result=seed.intermediate,
            ),
            ToolCall(
                tool="wikidata_lookup",
                query=f"{seed.intermediate} country",
                result=seed.answer,
            ),
        ]
        task = EvolvedTask(
            id=seed.id.replace("demo-", "task-"),
            task_type=seed.task_type,
            question=question,
            answer=seed.answer,
            evidence=list(seed.evidence),
            noisy_context=list(seed.noisy_context),
            tool_plan=tool_plan,
            difficulty="medium",
            source={
                "seed_id": seed.id,
                "seed_source": self._seed_source_label,
                "variant_index": seed.variant_index,
                "strategy": strategy,
                "references": [
                    "Self-Instruct",
                    "Magpie",
                    "WizardLM/Evol-Instruct",
                    "ToolBench/AgentTuning",
                ],
            },
            trajectory_draft=None,
        )
        if self._teacher_backend is not None:
            draft = self._teacher_backend.complete_json(
                [
                    {
                        "role": "system",
                        "content": (
                            "Return only JSON with question, difficulty, and trajectory. "
                            "The trajectory must be a list of ReAct strings using this exact style: "
                            "Thought: ..., Action: wikidata_lookup[...], Observation: ..., Final: ..."
                        ),
                    },
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "seed_id": seed.id,
                                "task_type": seed.task_type,
                                "entity": seed.entity,
                                "relation": seed.relation,
                                "intermediate": seed.intermediate,
                                "answer": seed.answer,
                                "evidence": seed.evidence,
                                "noisy_context": seed.noisy_context,
                                "strategy": strategy,
                            },
                            ensure_ascii=False,
                        ),
                    },
                ]
            )
            question = str(draft.get("question", question))
            difficulty = str(draft.get("difficulty", "medium"))
            trajectory_draft = [str(item) for item in draft.get("trajectory", []) if str(item)]
            task.question = question
            task.difficulty = difficulty
            task.trajectory_draft = trajectory_draft or None
            task.source = dict(task.source)
            task.source["teacher_backend"] = self._teacher_backend.name
        return task

    def _build_question(self, seed: SeedTask) -> str:
        variant = seed.variant_index or 1
        if seed.task_type == "tool_use_qa":
            templates = [
                "Use the available lookup tool to identify the present-day country associated with {entity}'s birthplace.",
                "Call the lookup tool step by step: where is {entity}'s birthplace located today?",
                "Resolve {entity}'s birthplace with tools, then return the country.",
                "Find {entity}'s birthplace via lookup and map that location to its country.",
            ]
        elif seed.task_type == "noisy_context_retrieval_qa":
            templates = [
                "Ignore distracting context and answer: which country contains {entity}'s birthplace?",
                "Filter the noisy evidence and identify the country of {entity}'s birthplace.",
                "Using only relevant evidence, determine the country tied to {entity}'s birthplace.",
                "Discard unrelated clues and answer the birthplace country for {entity}.",
            ]
        else:
            templates = [
                "Answer by chaining facts: which country is tied to the capital or location of {entity}'s birthplace?",
                "Use multi-hop reasoning to find the country connected to {entity}'s birthplace.",
                "First identify {entity}'s birthplace, then infer the country from that location.",
                "Follow the evidence chain from {entity} to birthplace to country.",
            ]
        template = templates[(variant - 1) % len(templates)]
        round_number = ((variant - 1) // len(templates)) + 1
        question = template.format(entity=seed.entity)
        if round_number > 1:
            question = f"{question} Use synthesis round {round_number}."
        return question

    def generate_trajectory(self, task: EvolvedTask) -> AgentDataSample:
        source = dict(task.source)
        default_trajectory = self._default_trajectory(task)
        if task.trajectory_draft and self._is_react_trajectory(
            task.trajectory_draft, task.answer
        ):
            trajectory = task.trajectory_draft
        else:
            trajectory = default_trajectory
            if task.trajectory_draft:
                source["teacher_trajectory_repaired"] = True

        return AgentDataSample(
            id=task.id,
            task_type=task.task_type,
            question=task.question,
            answer=task.answer,
            gold_evidence=task.evidence + task.noisy_context,
            tool_calls=list(task.tool_plan),
            trajectory=trajectory,
            verifier_result=VerifierResult(passed=False, checks={}, reasons=[]),
            difficulty=task.difficulty,
            source=source,
            quality_score=0.0,
        )

    def _default_trajectory(self, task: EvolvedTask) -> list[str]:
        trajectory = [
            "Thought: Identify the entity's birthplace.",
            f"Action: wikidata_lookup[{task.tool_plan[0].query}]",
            f"Observation: {task.tool_plan[0].result}",
            "Thought: Resolve the country from the intermediate location.",
            f"Action: wikidata_lookup[{task.tool_plan[1].query}]",
            f"Observation: {task.tool_plan[1].result}",
            f"Final: {task.answer}",
        ]
        if task.task_type == "noisy_context_retrieval_qa" and task.trajectory_draft is None:
            trajectory.insert(0, "Thought: Discard context that is not evidence-bearing.")
        return trajectory

    def _is_react_trajectory(self, trajectory: list[str], answer: str) -> bool:
        trajectory_text = " ".join(trajectory).lower()
        return (
            "thought:" in trajectory_text
            and "action:" in trajectory_text
            and "observation:" in trajectory_text
            and f"final: {answer.lower()}" in trajectory_text
        )

    def verify_and_filter(
        self, samples: Iterable[AgentDataSample]
    ) -> tuple[list[AgentDataSample], list[AgentDataSample], QualityMetrics]:
        rows = list(samples)
        accepted: list[AgentDataSample] = []
        rejected: list[AgentDataSample] = []
        seen_questions: set[str] = set()
        duplicate_count = 0

        for sample in rows:
            normalized_question = " ".join(sample.question.lower().split())
            duplicate = normalized_question in seen_questions
            if duplicate:
                duplicate_count += 1
            seen_questions.add(normalized_question)

            verified = self._verify_sample(sample, duplicate=duplicate)
            if verified.verifier_result.passed:
                accepted.append(verified)
            else:
                rejected.append(verified)

        metrics = self._build_metrics(rows, accepted, rejected, duplicate_count)
        return accepted, rejected, metrics

    def export_jsonl(self, samples: Iterable[AgentDataSample], path: Path) -> None:
        self._write_jsonl((sample.to_json_dict() for sample in samples), path)

    def load_jsonl(self, path: Path) -> list[AgentDataSample]:
        with path.open("r", encoding="utf-8") as handle:
            return [
                AgentDataSample.from_json_dict(json.loads(line))
                for line in handle
                if line.strip()
            ]

    def export_sft(self, samples: Iterable[AgentDataSample], path: Path) -> None:
        def rows() -> Iterable[dict[str, Any]]:
            for sample in samples:
                yield {
                    "id": sample.id,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a ReAct agent that must cite tool observations.",
                        },
                        {"role": "user", "content": sample.question},
                        {"role": "assistant", "content": "\n".join(sample.trajectory)},
                    ],
                }

        self._write_jsonl(rows(), path)

    def export_rl(self, samples: Iterable[AgentDataSample], path: Path) -> None:
        def rows() -> Iterable[dict[str, Any]]:
            for sample in samples:
                yield {
                    "id": sample.id,
                    "prompt": sample.question,
                    "answer": sample.answer,
                    "reward": sample.quality_score,
                    "verifier_checks": sample.verifier_result.checks,
                }

        self._write_jsonl(rows(), path)

    def export_trace(self, samples: Iterable[AgentDataSample], path: Path) -> None:
        def rows() -> Iterable[dict[str, Any]]:
            for sample in samples:
                row = sample.to_json_dict()
                row["trace_summary"] = {
                    "steps": len(sample.trajectory),
                    "tool_calls": len(sample.tool_calls),
                    "accepted": sample.verifier_result.passed,
                }
                yield row

        self._write_jsonl(rows(), path)

    def export_summary(self, metrics: QualityMetrics, path: Path) -> None:
        self._ensure_parent(path)
        row = metrics.to_row()
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
            writer.writeheader()
            writer.writerow(row)

    def _verify_sample(
        self, sample: AgentDataSample, duplicate: bool
    ) -> AgentDataSample:
        evidence_text = " ".join(sample.gold_evidence).lower()
        tool_results = {call.result.lower() for call in sample.tool_calls}
        trajectory_text = " ".join(sample.trajectory).lower()

        checks = {
            "not_duplicate": not duplicate,
            "answer_supported": sample.answer.lower() in evidence_text,
            "evidence_coverage": any(
                call.result.lower() in evidence_text for call in sample.tool_calls
            ),
            "tool_success": sample.answer.lower() in tool_results,
            "trajectory_valid": (
                "thought:" in trajectory_text
                and "action:" in trajectory_text
                and f"final: {sample.answer.lower()}" in trajectory_text
            ),
        }
        reasons = [name for name, passed in checks.items() if not passed]
        passed = not reasons
        quality_score = round(sum(checks.values()) / len(checks), 4)
        verified = AgentDataSample.from_json_dict(sample.to_json_dict())
        verified.verifier_result = VerifierResult(
            passed=passed,
            checks=checks,
            reasons=reasons,
        )
        verified.quality_score = quality_score
        return verified

    def _build_metrics(
        self,
        rows: list[AgentDataSample],
        accepted: list[AgentDataSample],
        rejected: list[AgentDataSample],
        duplicate_count: int,
    ) -> QualityMetrics:
        total = len(rows)
        if total == 0:
            return QualityMetrics(
                total=0,
                accepted=0,
                rejected=0,
                dedup_rate=1.0,
                solvability_rate=0.0,
                evidence_hit_rate=0.0,
                tool_success_rate=0.0,
                trajectory_valid_rate=0.0,
            )

        verified = accepted + rejected

        def rate(check_name: str) -> float:
            passed = sum(
                1
                for sample in verified
                if sample.verifier_result.checks.get(check_name, False)
            )
            return round(passed / total, 4)

        return QualityMetrics(
            total=total,
            accepted=len(accepted),
            rejected=len(rejected),
            dedup_rate=round((total - duplicate_count) / total, 4),
            solvability_rate=rate("answer_supported"),
            evidence_hit_rate=rate("evidence_coverage"),
            tool_success_rate=rate("tool_success"),
            trajectory_valid_rate=rate("trajectory_valid"),
        )

    def _write_jsonl(self, rows: Iterable[dict[str, Any]], path: Path) -> None:
        self._ensure_parent(path)
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    def _ensure_parent(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
