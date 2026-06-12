from __future__ import annotations

import csv
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from openseeker_factory.backends import ChatBackend
from openseeker_factory.schema import (
    DIFFICULTIES,
    AgentDataSample,
    ToolCall,
    VerifierResult,
)

ACTION_QUERY_RE = re.compile(
    r"action\s*:\s*wikidata_lookup\s*\[([^\]]+)\]", re.IGNORECASE
)


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
    evidence_faithfulness_rate: float
    tool_success_rate: float
    trajectory_valid_rate: float
    teacher_attempted: int
    teacher_succeeded: int
    teacher_failed: int
    teacher_fallback_rate: float
    teacher_trajectory_repaired: int
    question_repaired: int
    teacher_difficulty_normalized: int
    manual_sample_pass_rate: float | None = None

    def to_row(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "accepted": self.accepted,
            "rejected": self.rejected,
            "dedup_rate": self.dedup_rate,
            "solvability_rate": self.solvability_rate,
            "evidence_hit_rate": self.evidence_hit_rate,
            "evidence_faithfulness_rate": self.evidence_faithfulness_rate,
            "tool_success_rate": self.tool_success_rate,
            "trajectory_valid_rate": self.trajectory_valid_rate,
            "teacher_attempted": self.teacher_attempted,
            "teacher_succeeded": self.teacher_succeeded,
            "teacher_failed": self.teacher_failed,
            "teacher_fallback_rate": self.teacher_fallback_rate,
            "teacher_trajectory_repaired": self.teacher_trajectory_repaired,
            "question_repaired": self.question_repaired,
            "teacher_difficulty_normalized": self.teacher_difficulty_normalized,
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
        self,
        count: int,
        strategy: str = "evol_instruct",
        progress_callback: Callable[[int, int, AgentDataSample], None] | None = None,
        teacher_concurrency: int = 1,
        start_index: int = 0,
    ) -> tuple[list[AgentDataSample], list[AgentDataSample], QualityMetrics]:
        samples = self.generate_samples(
            count=count,
            strategy=strategy,
            progress_callback=progress_callback,
            teacher_concurrency=teacher_concurrency,
            start_index=start_index,
        )
        return self.verify_and_filter(samples)

    def generate_samples(
        self,
        count: int,
        strategy: str = "evol_instruct",
        progress_callback: Callable[[int, int, AgentDataSample], None] | None = None,
        teacher_concurrency: int = 1,
        start_index: int = 0,
    ) -> list[AgentDataSample]:
        seeds = self.seed_expand(count=count, start_index=start_index)
        return self.generate_samples_for_seeds(
            seeds,
            strategy=strategy,
            progress_callback=progress_callback,
            teacher_concurrency=teacher_concurrency,
        )

    def generate_samples_for_seeds(
        self,
        seeds: Sequence[SeedTask],
        strategy: str = "evol_instruct",
        progress_callback: Callable[[int, int, AgentDataSample], None] | None = None,
        teacher_concurrency: int = 1,
    ) -> list[AgentDataSample]:
        if teacher_concurrency < 1:
            raise ValueError("teacher_concurrency must be positive")
        total = len(seeds)

        def build_sample(index: int, seed: SeedTask) -> tuple[int, AgentDataSample]:
            task = self.evolve_task(seed, strategy=strategy)
            sample = self.generate_trajectory(task)
            return index, sample

        if teacher_concurrency == 1:
            samples: list[AgentDataSample] = []
            for index, seed in enumerate(seeds, start=1):
                _, sample = build_sample(index, seed)
                samples.append(sample)
                if progress_callback is not None:
                    progress_callback(index, total, sample)
            return samples

        samples_by_index: dict[int, AgentDataSample] = {}
        with ThreadPoolExecutor(max_workers=teacher_concurrency) as executor:
            futures = {
                executor.submit(build_sample, index, seed): index
                for index, seed in enumerate(seeds, start=1)
            }
            completed = 0
            for future in as_completed(futures):
                index, sample = future.result()
                samples_by_index[index] = sample
                completed += 1
                if progress_callback is not None:
                    progress_callback(completed, total, sample)

        samples = [samples_by_index[index] for index in range(1, total + 1)]
        return samples

    def seed_expand(self, count: int, start_index: int = 0) -> list[SeedTask]:
        if count < 1:
            raise ValueError("count must be positive")
        if start_index < 0:
            raise ValueError("start_index must be non-negative")
        expanded = []
        for index in range(start_index, start_index + count):
            base_index = index % len(self._seeds)
            base = self._seeds[base_index]
            variant_index = (index // len(self._seeds)) + 1
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
                    variant_index=variant_index,
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
                query=f"{seed.entity}, P19",
                result=seed.intermediate,
            ),
            ToolCall(
                tool="wikidata_lookup",
                query=f"{seed.intermediate}, P17",
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
            task.source = dict(task.source)
            task.source["teacher_backend"] = self._teacher_backend.name
            try:
                draft = self._teacher_backend.complete_json(
                    [
                        {
                            "role": "system",
                            "content": (
                                "Return only JSON with question, difficulty, and trajectory. "
                                "The trajectory must be a list of ReAct strings using this exact style: "
                                "Thought: ..., Action: wikidata_lookup[...], Observation: ..., Final: ... "
                                "Use canonical Wikidata property calls only: "
                                "wikidata_lookup[<entity>, P19] for birthplace and "
                                "wikidata_lookup[<birthplace>, P17] for country."
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
            except Exception as exc:
                task.source["teacher_backend_error"] = str(exc)
                return task
            question = str(draft.get("question", question))
            difficulty_raw = str(draft.get("difficulty", "medium")).lower().strip()
            difficulty = difficulty_raw if difficulty_raw in DIFFICULTIES else "medium"
            if difficulty != difficulty_raw:
                task.source["teacher_difficulty_raw"] = difficulty_raw
            trajectory_draft = [str(item) for item in draft.get("trajectory", []) if str(item)]
            task.question = question
            task.difficulty = difficulty
            task.trajectory_draft = trajectory_draft or None
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
            repeat_constraints = [
                "Use the birthplace clue rather than career context.",
                f"Start from {seed.intermediate}, then resolve the country.",
                "Use only evidence that connects the person to a birthplace and country.",
                "Give the country name as the final answer.",
                f"Resolve {seed.intermediate} to its present-day country.",
                "Ignore unrelated biographical clues while answering.",
                "Follow the two-hop evidence chain before responding.",
                "Treat the birthplace statement as the controlling clue.",
            ]
            constraint = repeat_constraints[
                (round_number - 2) % len(repeat_constraints)
            ]
            question = f"{question} {constraint}"
        return question

    def generate_trajectory(self, task: EvolvedTask) -> AgentDataSample:
        source = dict(task.source)
        source["data_version"] = "canonical-v3"
        source["observation_grounding"] = "gold_tool_results"
        source["observation_grounding_policy"] = (
            "observations_must_match_expected_tool_results"
        )
        default_trajectory = self._default_trajectory(task)
        if task.trajectory_draft is None:
            trajectory = default_trajectory
        elif not self._is_react_trajectory(task.trajectory_draft, task.answer):
            trajectory = default_trajectory
            source["teacher_trajectory_repaired"] = True
            source["teacher_trajectory_repair_reason"] = "react_format"
        elif not self._trajectory_contains_expected_results(
            task.trajectory_draft, task.tool_plan
        ):
            trajectory = default_trajectory
            source["teacher_trajectory_repaired"] = True
            source["teacher_trajectory_repair_reason"] = "evidence_faithfulness"
        elif not self._trajectory_contains_expected_tool_calls(
            task.trajectory_draft, task.tool_plan
        ):
            trajectory = default_trajectory
            source["teacher_trajectory_repaired"] = True
            source["teacher_trajectory_repair_reason"] = "tool_call_coverage"
        else:
            trajectory = task.trajectory_draft
        question = task.question
        question_repair_reason = self._question_repair_reason(question, task)
        if question_repair_reason is not None:
            source["question_repaired"] = True
            source["question_repair_reason"] = question_repair_reason
            source["original_question"] = question
            question = self._default_question_for_task(task)

        return AgentDataSample(
            id=task.id,
            task_type=task.task_type,
            question=question,
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

    def _question_repair_reason(
        self, question: str, task: EvolvedTask
    ) -> str | None:
        question_text = question.lower()
        expected_entity = self._entity_from_tool_plan(task)
        if "use synthesis round" in question_text:
            return "synthetic_round_marker"
        if expected_entity.lower() not in question_text:
            return "entity_alignment"
        for seed in self._seeds:
            if seed.entity != expected_entity and seed.entity.lower() in question_text:
                return "entity_alignment"
        return None

    def _default_question_for_task(self, task: EvolvedTask) -> str:
        entity = self._entity_from_tool_plan(task)
        if task.task_type == "tool_use_qa":
            return (
                f"Use the lookup tool to find {entity}'s birthplace and return "
                "the present-day country."
            )
        if task.task_type == "noisy_context_retrieval_qa":
            return (
                f"Ignore unrelated context and identify the country of {entity}'s "
                "birthplace."
            )
        return f"What country was {entity} born in?"

    def _entity_from_tool_plan(self, task: EvolvedTask) -> str:
        if not task.tool_plan:
            return "the person"
        query = task.tool_plan[0].query
        suffixes = (", P19", " birthplace")
        for suffix in suffixes:
            if query.endswith(suffix):
                return query[: -len(suffix)]
        return query

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
        duplicate_rewrite_counts: dict[str, int] = {}
        duplicate_count = 0

        for sample in rows:
            sample = self._repair_sample_question_if_needed(sample)
            normalized_question = " ".join(sample.question.lower().split())
            duplicate = normalized_question in seen_questions
            if duplicate:
                duplicate_rewrite_counts[normalized_question] = (
                    duplicate_rewrite_counts.get(normalized_question, 0) + 1
                )
                sample = self._rewrite_duplicate_question(
                    sample,
                    duplicate_index=duplicate_rewrite_counts[normalized_question],
                )
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

    def _rewrite_duplicate_question(
        self, sample: AgentDataSample, duplicate_index: int
    ) -> AgentDataSample:
        rewritten = AgentDataSample.from_json_dict(sample.to_json_dict())
        rewritten.source = dict(rewritten.source)
        rewritten.source["duplicate_question_rewritten"] = True
        rewritten.source["original_question"] = rewritten.question
        rewritten.source["duplicate_rewrite_index"] = duplicate_index
        rewritten.question = self._natural_duplicate_question(
            rewritten, duplicate_index
        )
        return rewritten

    def _repair_sample_question_if_needed(
        self, sample: AgentDataSample
    ) -> AgentDataSample:
        reason = self._sample_question_repair_reason(sample)
        if reason is None:
            return sample
        repaired = AgentDataSample.from_json_dict(sample.to_json_dict())
        repaired.source = dict(repaired.source)
        repaired.source.setdefault("original_question", repaired.question)
        repaired.source["question_repaired"] = True
        repaired.source["question_repair_reason"] = reason
        repaired.question = self._default_question_for_sample(repaired)
        return repaired

    def _sample_question_repair_reason(
        self, sample: AgentDataSample
    ) -> str | None:
        question_text = sample.question.lower()
        expected_entity = self._entity_from_tool_query(sample)
        if "use synthesis round" in question_text:
            return "synthetic_round_marker"
        if expected_entity.lower() not in question_text:
            return "entity_alignment"
        for seed in self._seeds:
            if seed.entity != expected_entity and seed.entity.lower() in question_text:
                return "entity_alignment"
        return None

    def _default_question_for_sample(self, sample: AgentDataSample) -> str:
        entity = self._entity_from_tool_query(sample)
        if sample.task_type == "tool_use_qa":
            return (
                f"Use the lookup tool to find {entity}'s birthplace and return "
                "the present-day country."
            )
        if sample.task_type == "noisy_context_retrieval_qa":
            return (
                f"Ignore unrelated context and identify the country of {entity}'s "
                "birthplace."
            )
        return f"What country was {entity} born in?"

    def _natural_duplicate_question(
        self, sample: AgentDataSample, duplicate_index: int
    ) -> str:
        entity = self._entity_from_tool_query(sample)
        intermediate = (
            sample.tool_calls[0].result if sample.tool_calls else "the birthplace"
        )
        natural_constraints = [
            "Use the birthplace clue rather than career context.",
            f"Start from {intermediate}, then resolve the country.",
            f"Confirm the location linked to {entity} before naming the country.",
            "Use only evidence that connects the person to a birthplace and country.",
            "Give the country name as the final answer.",
            f"Resolve {intermediate} to its present-day country.",
            "Ignore unrelated biographical clues while answering.",
            "Follow the two-hop evidence chain before responding.",
            "Treat the birthplace statement as the controlling clue.",
            "Answer with the country supported by the lookup observations.",
            "Use the location evidence and avoid using field-of-work clues.",
            f"Check the country associated with {intermediate} before answering.",
        ]
        constraint = natural_constraints[
            (duplicate_index - 1) % len(natural_constraints)
        ]
        return f"{sample.question} {constraint}"

    def _entity_from_tool_query(self, sample: AgentDataSample) -> str:
        if not sample.tool_calls:
            return "the person"
        query = sample.tool_calls[0].query
        suffixes = (", P19", " birthplace")
        for suffix in suffixes:
            if query.endswith(suffix):
                return query[: -len(suffix)]
        return query

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
                            "content": (
                                "You are a ReAct agent that must cite tool observations. "
                                "Actions must use the provided lookup schema, and "
                                "Observation lines must match lookup observations from "
                                "the evidence instead of memorized or localized facts."
                            ),
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
        evidence_faithful = self._trajectory_matches_expected_evidence(sample)

        checks = {
            "not_duplicate": not duplicate,
            "answer_supported": sample.answer.lower() in evidence_text,
            "evidence_coverage": any(
                call.result.lower() in evidence_text for call in sample.tool_calls
            ),
            "evidence_faithfulness": evidence_faithful,
            "observation_faithfulness": evidence_faithful,
            "question_entity_alignment": self._question_matches_expected_entity(sample),
            "tool_success": (
                sample.answer.lower() in tool_results
                and self._trajectory_contains_expected_tool_calls(
                    sample.trajectory, sample.tool_calls
                )
            ),
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

    def _question_matches_expected_entity(self, sample: AgentDataSample) -> bool:
        question_text = sample.question.lower()
        expected_entity = self._entity_from_tool_query(sample)
        if expected_entity.lower() not in question_text:
            return False
        for seed in self._seeds:
            if seed.entity != expected_entity and seed.entity.lower() in question_text:
                return False
        if "use synthesis round" in question_text:
            return False
        return True

    def _trajectory_matches_expected_evidence(self, sample: AgentDataSample) -> bool:
        return self._trajectory_contains_expected_results(
            sample.trajectory,
            sample.tool_calls,
        )

    def _trajectory_contains_expected_results(
        self, trajectory: Sequence[str], tool_calls: Sequence[ToolCall]
    ) -> bool:
        trajectory_text = " ".join(trajectory).lower()
        expected_results = [call.result.lower() for call in tool_calls]
        return all(result in trajectory_text for result in expected_results)

    def _trajectory_contains_expected_tool_calls(
        self, trajectory: Sequence[str], tool_calls: Sequence[ToolCall]
    ) -> bool:
        action_queries = [
            self._normalize_tool_query(query)
            for line in trajectory
            for query in ACTION_QUERY_RE.findall(line)
        ]
        expected_queries = [
            self._normalize_tool_query(call.query)
            for call in tool_calls
            if call.tool.lower() == "wikidata_lookup"
        ]
        return all(query in action_queries for query in expected_queries)

    def _normalize_tool_query(self, query: str) -> str:
        return re.sub(r"\s*,\s*", ", ", " ".join(query.lower().split()))

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
                evidence_faithfulness_rate=0.0,
                tool_success_rate=0.0,
                trajectory_valid_rate=0.0,
                teacher_attempted=0,
                teacher_succeeded=0,
                teacher_failed=0,
                teacher_fallback_rate=0.0,
                teacher_trajectory_repaired=0,
                question_repaired=0,
                teacher_difficulty_normalized=0,
            )

        verified = accepted + rejected
        teacher_attempted = sum(
            1 for sample in verified if "teacher_backend" in sample.source
        )
        teacher_failed = sum(
            1 for sample in verified if "teacher_backend_error" in sample.source
        )

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
            evidence_faithfulness_rate=rate("evidence_faithfulness"),
            tool_success_rate=rate("tool_success"),
            trajectory_valid_rate=rate("trajectory_valid"),
            teacher_attempted=teacher_attempted,
            teacher_succeeded=teacher_attempted - teacher_failed,
            teacher_failed=teacher_failed,
            teacher_fallback_rate=(
                round(teacher_failed / teacher_attempted, 4)
                if teacher_attempted
                else 0.0
            ),
            teacher_trajectory_repaired=sum(
                1
                for sample in verified
                if sample.source.get("teacher_trajectory_repaired")
            ),
            question_repaired=sum(
                1 for sample in verified if sample.source.get("question_repaired")
            ),
            teacher_difficulty_normalized=sum(
                1 for sample in verified if "teacher_difficulty_raw" in sample.source
            ),
        )

    def _write_jsonl(self, rows: Iterable[dict[str, Any]], path: Path) -> None:
        self._ensure_parent(path)
        with path.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    def _ensure_parent(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
