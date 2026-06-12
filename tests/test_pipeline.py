import json
from pathlib import Path
from threading import Lock
from time import sleep

from openseeker_factory.pipeline import AgentDataFactory
from openseeker_factory.schema import AgentDataSample


class FakeTeacherBackend:
    name = "fake-teacher"

    def complete_json(self, messages):
        return {
            "question": "Teacher: which country contains Ada Lovelace's birthplace?",
            "difficulty": "hard",
            "trajectory": [
                "Thought: Use the teacher-provided tool plan.",
                "Action: wikidata_lookup[Ada Lovelace, P19]",
                "Observation: London",
                "Thought: Resolve London to its country.",
                "Action: wikidata_lookup[London, P17]",
                "Observation: United Kingdom",
                "Final: United Kingdom",
            ],
        }


class FakeInvalidTrajectoryTeacherBackend:
    name = "fake-invalid-trajectory"

    def complete_json(self, messages):
        return {
            "question": "Teacher drafted Ada Lovelace question with invalid trajectory?",
            "difficulty": "hard",
            "trajectory": [
                "Find Ada Lovelace's birthplace: London.",
                "Find the country: United Kingdom.",
            ],
        }


class FakeUnfaithfulTrajectoryTeacherBackend:
    name = "fake-unfaithful-trajectory"

    def complete_json(self, messages):
        return {
            "question": "Teacher drafted Ada Lovelace question with plausible but unfaithful evidence?",
            "difficulty": "hard",
            "trajectory": [
                "Thought: Find Ada Lovelace's birthplace.",
                "Action: wikidata_lookup[Ada Lovelace, P19]",
                "Observation: Cambridge",
                "Thought: Resolve Cambridge to its country.",
                "Action: wikidata_lookup[Cambridge, P17]",
                "Observation: United Kingdom",
                "Final: United Kingdom",
            ],
        }


class FakeNaturalPropertyTrajectoryTeacherBackend:
    name = "fake-natural-property-trajectory"

    def complete_json(self, messages):
        return {
            "question": "Teacher drafted Ada Lovelace question with natural tool keys?",
            "difficulty": "hard",
            "trajectory": [
                "Thought: Find Ada Lovelace's birthplace.",
                "Action: wikidata_lookup[Ada Lovelace birthplace]",
                "Observation: London",
                "Thought: Resolve London to its country.",
                "Action: wikidata_lookup[London country]",
                "Observation: United Kingdom",
                "Final: United Kingdom",
            ],
        }


class FakeFailingTeacherBackend:
    name = "fake-failing-teacher"

    def complete_json(self, messages):
        raise RuntimeError("teacher timed out")


class FakeInvalidDifficultyTeacherBackend:
    name = "fake-invalid-difficulty"

    def complete_json(self, messages):
        return {
            "question": "Teacher drafted question with invalid difficulty?",
            "difficulty": "intermediate",
            "trajectory": [
                "Thought: Use the teacher-provided tool plan.",
                "Action: wikidata_lookup[Ada Lovelace, P19]",
                "Observation: London",
                "Thought: Resolve London to its country.",
                "Action: wikidata_lookup[London, P17]",
                "Observation: United Kingdom",
                "Final: United Kingdom",
            ],
        }


class FakeWrongEntityQuestionTeacherBackend:
    name = "fake-wrong-entity-question"

    def complete_json(self, messages):
        return {
            "question": "What country was Albert Einstein born in?",
            "difficulty": "medium",
            "trajectory": [
                "Thought: Use the seed entity, not the drafted question.",
                "Action: wikidata_lookup[Ada Lovelace, P19]",
                "Observation: London",
                "Thought: Resolve London to its country.",
                "Action: wikidata_lookup[London, P17]",
                "Observation: United Kingdom",
                "Final: United Kingdom",
            ],
        }


class FakeRepeatedQuestionTeacherBackend:
    name = "fake-repeated-question"

    def complete_json(self, messages):
        import json

        payload = json.loads(messages[-1]["content"])
        entity = payload["entity"]
        intermediate = payload["intermediate"]
        answer = payload["answer"]
        return {
            "question": f"Which country is tied to {entity}'s birthplace?",
            "difficulty": "medium",
            "trajectory": [
                "Thought: Use the lookup trajectory.",
                f"Action: wikidata_lookup[{entity}, P19]",
                f"Observation: {intermediate}",
                "Thought: Resolve country.",
                f"Action: wikidata_lookup[{intermediate}, P17]",
                f"Observation: {answer}",
                f"Final: {answer}",
            ],
        }


class FakeSlowTeacherBackend:
    name = "fake-slow-teacher"

    def __init__(self) -> None:
        self.active = 0
        self.max_active = 0
        self.lock = Lock()

    def complete_json(self, messages):
        import json

        with self.lock:
            self.active += 1
            self.max_active = max(self.max_active, self.active)
        try:
            payload = json.loads(messages[-1]["content"])
            variant_index = int(str(payload["seed_id"]).rsplit("-", 1)[1])
            sleep(0.01 * (7 - variant_index))
            entity = payload["entity"]
            intermediate = payload["intermediate"]
            answer = payload["answer"]
            return {
                "question": f"Which country is tied to {entity}'s birthplace?",
                "difficulty": "medium",
                "trajectory": [
                    "Thought: Use the lookup trajectory.",
                    f"Action: wikidata_lookup[{entity}, P19]",
                    f"Observation: {intermediate}",
                    "Thought: Resolve country.",
                    f"Action: wikidata_lookup[{intermediate}, P17]",
                    f"Observation: {answer}",
                    f"Final: {answer}",
                ],
            }
        finally:
            with self.lock:
                self.active -= 1


def test_factory_generates_verified_samples_for_three_task_types():
    factory = AgentDataFactory.from_demo_knowledge_graph()

    seeds = factory.seed_expand(count=3)
    evolved = [factory.evolve_task(seed, strategy="evol_instruct") for seed in seeds]
    samples = [factory.generate_trajectory(task) for task in evolved]
    accepted, rejected, metrics = factory.verify_and_filter(samples)

    assert len(accepted) == 3
    assert rejected == []
    assert {sample.task_type for sample in accepted} == {
        "multi_hop_qa",
        "tool_use_qa",
        "noisy_context_retrieval_qa",
    }
    assert metrics.total == 3
    assert metrics.accepted == 3
    assert metrics.solvability_rate == 1.0
    assert metrics.evidence_hit_rate == 1.0
    assert metrics.tool_success_rate == 1.0
    assert metrics.trajectory_valid_rate == 1.0


def test_factory_rejects_samples_with_unsupported_answer():
    factory = AgentDataFactory.from_demo_knowledge_graph()
    seed = factory.seed_expand(count=1)[0]
    task = factory.evolve_task(seed)
    sample = factory.generate_trajectory(task)
    bad = AgentDataSample.from_json_dict(sample.to_json_dict())
    bad.answer = "Mars"

    accepted, rejected, metrics = factory.verify_and_filter([bad])

    assert accepted == []
    assert len(rejected) == 1
    assert rejected[0].verifier_result.passed is False
    assert "answer_supported" in rejected[0].verifier_result.reasons
    assert metrics.accepted == 0
    assert metrics.rejected == 1


def test_factory_rejects_samples_with_unfaithful_intermediate_observation():
    factory = AgentDataFactory.from_demo_knowledge_graph()
    seed = factory.seed_expand(count=1)[0]
    task = factory.evolve_task(seed)
    sample = factory.generate_trajectory(task)
    bad = AgentDataSample.from_json_dict(sample.to_json_dict())
    bad.trajectory = [
        "Thought: Identify the entity's birthplace.",
        "Action: wikidata_lookup[Ada Lovelace, P19]",
        "Observation: Cambridge",
        "Thought: Resolve the country from the intermediate location.",
        "Action: wikidata_lookup[Cambridge country]",
        "Observation: United Kingdom",
        "Final: United Kingdom",
    ]

    accepted, rejected, metrics = factory.verify_and_filter([bad])

    assert accepted == []
    assert len(rejected) == 1
    assert rejected[0].verifier_result.checks["evidence_faithfulness"] is False
    assert "evidence_faithfulness" in rejected[0].verifier_result.reasons
    assert metrics.evidence_faithfulness_rate == 0.0


def test_factory_accepts_samples_with_faithful_intermediate_and_answer_observations():
    factory = AgentDataFactory.from_demo_knowledge_graph()
    sample = factory.generate_trajectory(factory.evolve_task(factory.seed_expand(count=1)[0]))

    accepted, rejected, metrics = factory.verify_and_filter([sample])

    assert len(accepted) == 1
    assert rejected == []
    assert accepted[0].verifier_result.checks["evidence_faithfulness"] is True
    assert metrics.evidence_faithfulness_rate == 1.0


def test_factory_marks_canonical_v3_observation_grounding_metadata():
    factory = AgentDataFactory.from_demo_knowledge_graph()

    accepted, rejected, _ = factory.generate_verified(count=1)

    assert rejected == []
    sample = accepted[0]
    assert sample.source["data_version"] == "canonical-v3"
    assert sample.source["observation_grounding"] == "gold_tool_results"
    assert sample.verifier_result.checks["observation_faithfulness"] is True


def test_factory_uses_canonical_wikidata_property_ids_in_default_tool_plan():
    factory = AgentDataFactory.from_demo_knowledge_graph()
    task = factory.evolve_task(factory.seed_expand(count=1)[0])

    assert [tool_call.query for tool_call in task.tool_plan] == [
        "Ada Lovelace, P19",
        "London, P17",
    ]
    sample = factory.generate_trajectory(task)
    assert "Action: wikidata_lookup[Ada Lovelace, P19]" in sample.trajectory
    assert "Action: wikidata_lookup[London, P17]" in sample.trajectory


def test_factory_exports_jsonl_sft_rl_and_summary(tmp_path: Path):
    factory = AgentDataFactory.from_demo_knowledge_graph()
    samples = [
        factory.generate_trajectory(factory.evolve_task(seed))
        for seed in factory.seed_expand(count=2)
    ]
    accepted, _, metrics = factory.verify_and_filter(samples)

    jsonl_path = tmp_path / "samples.jsonl"
    sft_path = tmp_path / "sft.jsonl"
    rl_path = tmp_path / "rl.jsonl"
    summary_path = tmp_path / "summary.csv"
    trace_path = tmp_path / "trace.jsonl"

    factory.export_jsonl(accepted, jsonl_path)
    factory.export_sft(accepted, sft_path)
    factory.export_rl(accepted, rl_path)
    factory.export_summary(metrics, summary_path)
    factory.export_trace(accepted, trace_path)

    restored = factory.load_jsonl(jsonl_path)
    assert restored == accepted
    sft_row = json.loads(sft_path.read_text(encoding="utf-8").splitlines()[0])
    assert sft_row["id"] == accepted[0].id
    assert "match lookup observations" in sft_row["messages"][0]["content"]
    rl_row = json.loads(rl_path.read_text(encoding="utf-8").splitlines()[0])
    assert "prompt" in rl_row
    assert rl_row["verifier_checks"]["observation_faithfulness"] is True
    assert "total,accepted,rejected" in summary_path.read_text(encoding="utf-8")
    assert '"verifier_result"' in trace_path.read_text(encoding="utf-8")


def test_factory_loads_seed_file_and_repeats_it_to_requested_count():
    factory = AgentDataFactory.from_seed_file(Path("tests/fixtures/seeds.jsonl"))

    accepted, rejected, metrics = factory.generate_verified(count=5)

    assert len(accepted) == 5
    assert rejected == []
    assert metrics.total == 5
    assert metrics.accepted == 5
    assert {sample.source["seed_source"] for sample in accepted} == {
        "tests/fixtures/seeds.jsonl"
    }
    assert [sample.source["seed_id"] for sample in accepted][:3] == [
        "wikidata-ada-1",
        "wikidata-curie-2",
        "wikidata-ada-3",
    ]


def test_factory_seed_expand_can_start_after_completed_variants():
    factory = AgentDataFactory.from_seed_file(Path("tests/fixtures/seeds.jsonl"))

    seeds = factory.seed_expand(count=3, start_index=2)

    assert [seed.id for seed in seeds] == [
        "wikidata-ada-3",
        "wikidata-curie-4",
        "wikidata-ada-5",
    ]
    assert [seed.variant_index for seed in seeds] == [2, 2, 3]


def test_factory_uses_per_seed_variant_index_for_unique_seed_rows(tmp_path: Path):
    seed_path = tmp_path / "unique-seeds.jsonl"
    rows = []
    for index in range(5):
        rows.append(
            {
                "id": f"unique-{index}",
                "task_type": "multi_hop_qa",
                "entity": f"Person {index}",
                "relation": "birthplace_country",
                "intermediate": f"City {index}",
                "answer": f"Country {index}",
                "evidence": [
                    f"Person {index} was born in City {index}.",
                    f"City {index} is located in Country {index}.",
                ],
                "noisy_context": [f"Person {index} is known for unrelated work."],
            }
    )
    seed_path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )
    factory = AgentDataFactory.from_seed_file(seed_path)

    expanded = factory.seed_expand(count=5)
    accepted, rejected, metrics = factory.generate_verified(count=5)

    assert [seed.variant_index for seed in expanded] == [1, 1, 1, 1, 1]
    assert rejected == []
    assert metrics.accepted == 5
    assert metrics.question_repaired == 0
    assert all("Use synthesis round" not in sample.question for sample in accepted)
    assert all("question_repaired" not in sample.source for sample in accepted)


def test_factory_uses_teacher_backend_draft_when_provided():
    factory = AgentDataFactory.from_demo_knowledge_graph(
        teacher_backend=FakeTeacherBackend()
    )

    accepted, rejected, metrics = factory.generate_verified(count=1)

    assert rejected == []
    assert metrics.accepted == 1
    assert accepted[0].question == (
        "Teacher: which country contains Ada Lovelace's birthplace?"
    )
    assert accepted[0].difficulty == "hard"
    assert accepted[0].trajectory[0] == "Thought: Use the teacher-provided tool plan."
    assert accepted[0].source["teacher_backend"] == "fake-teacher"


def test_factory_repairs_invalid_teacher_trajectory_with_deterministic_react():
    factory = AgentDataFactory.from_demo_knowledge_graph(
        teacher_backend=FakeInvalidTrajectoryTeacherBackend()
    )

    accepted, rejected, metrics = factory.generate_verified(count=1)

    assert rejected == []
    assert metrics.accepted == 1
    assert accepted[0].question == (
        "Teacher drafted Ada Lovelace question with invalid trajectory?"
    )
    assert accepted[0].trajectory == [
        "Thought: Identify the entity's birthplace.",
        "Action: wikidata_lookup[Ada Lovelace, P19]",
        "Observation: London",
        "Thought: Resolve the country from the intermediate location.",
        "Action: wikidata_lookup[London, P17]",
        "Observation: United Kingdom",
        "Final: United Kingdom",
    ]
    assert accepted[0].source["teacher_trajectory_repaired"] is True


def test_factory_repairs_unfaithful_teacher_trajectory_with_deterministic_react():
    factory = AgentDataFactory.from_demo_knowledge_graph(
        teacher_backend=FakeUnfaithfulTrajectoryTeacherBackend()
    )

    accepted, rejected, metrics = factory.generate_verified(count=1)

    assert rejected == []
    assert metrics.accepted == 1
    assert metrics.evidence_faithfulness_rate == 1.0
    assert metrics.teacher_trajectory_repaired == 1
    assert accepted[0].question == (
        "Teacher drafted Ada Lovelace question with plausible but unfaithful evidence?"
    )
    assert accepted[0].trajectory == [
        "Thought: Identify the entity's birthplace.",
        "Action: wikidata_lookup[Ada Lovelace, P19]",
        "Observation: London",
        "Thought: Resolve the country from the intermediate location.",
        "Action: wikidata_lookup[London, P17]",
        "Observation: United Kingdom",
        "Final: United Kingdom",
    ]
    assert accepted[0].source["teacher_trajectory_repaired"] is True
    assert accepted[0].source["teacher_trajectory_repair_reason"] == (
        "evidence_faithfulness"
    )
    assert accepted[0].verifier_result.checks["evidence_faithfulness"] is True


def test_factory_repairs_teacher_trajectory_without_canonical_tool_calls():
    factory = AgentDataFactory.from_demo_knowledge_graph(
        teacher_backend=FakeNaturalPropertyTrajectoryTeacherBackend()
    )

    accepted, rejected, metrics = factory.generate_verified(count=1)

    assert rejected == []
    assert metrics.accepted == 1
    assert metrics.teacher_trajectory_repaired == 1
    assert accepted[0].trajectory == [
        "Thought: Identify the entity's birthplace.",
        "Action: wikidata_lookup[Ada Lovelace, P19]",
        "Observation: London",
        "Thought: Resolve the country from the intermediate location.",
        "Action: wikidata_lookup[London, P17]",
        "Observation: United Kingdom",
        "Final: United Kingdom",
    ]
    assert accepted[0].source["teacher_trajectory_repaired"] is True
    assert accepted[0].source["teacher_trajectory_repair_reason"] == (
        "tool_call_coverage"
    )


def test_factory_falls_back_when_teacher_backend_fails():
    factory = AgentDataFactory.from_demo_knowledge_graph(
        teacher_backend=FakeFailingTeacherBackend()
    )

    accepted, rejected, metrics = factory.generate_verified(count=1)

    assert rejected == []
    assert metrics.accepted == 1
    assert accepted[0].question.startswith("Answer by chaining facts")
    assert accepted[0].source["teacher_backend"] == "fake-failing-teacher"
    assert accepted[0].source["teacher_backend_error"] == "teacher timed out"


def test_factory_metrics_include_teacher_fallback_counts():
    factory = AgentDataFactory.from_demo_knowledge_graph(
        teacher_backend=FakeFailingTeacherBackend()
    )

    accepted, rejected, metrics = factory.generate_verified(count=2)
    row = metrics.to_row()

    assert len(accepted) == 2
    assert rejected == []
    assert row["teacher_attempted"] == 2
    assert row["teacher_succeeded"] == 0
    assert row["teacher_failed"] == 2
    assert row["teacher_fallback_rate"] == 1.0
    assert row["teacher_trajectory_repaired"] == 0
    assert row["teacher_difficulty_normalized"] == 0


def test_factory_normalizes_invalid_teacher_difficulty():
    factory = AgentDataFactory.from_demo_knowledge_graph(
        teacher_backend=FakeInvalidDifficultyTeacherBackend()
    )

    accepted, rejected, metrics = factory.generate_verified(count=1)

    assert rejected == []
    assert metrics.accepted == 1
    assert accepted[0].difficulty == "medium"
    assert accepted[0].source["teacher_difficulty_raw"] == "intermediate"


def test_factory_repairs_teacher_question_with_foreign_entity_before_export():
    factory = AgentDataFactory.from_demo_knowledge_graph(
        teacher_backend=FakeWrongEntityQuestionTeacherBackend()
    )

    accepted, rejected, metrics = factory.generate_verified(count=1)

    assert rejected == []
    assert metrics.accepted == 1
    assert accepted[0].question == "What country was Ada Lovelace born in?"
    assert accepted[0].source["question_repaired"] is True
    assert accepted[0].source["question_repair_reason"] == "entity_alignment"
    assert accepted[0].source["original_question"] == (
        "What country was Albert Einstein born in?"
    )
    assert accepted[0].verifier_result.checks["question_entity_alignment"] is True


def test_factory_does_not_emit_synthetic_round_marker_for_repeated_variants():
    factory = AgentDataFactory.from_demo_knowledge_graph(
        teacher_backend=FakeFailingTeacherBackend()
    )

    accepted, rejected, metrics = factory.generate_verified(count=13)

    assert rejected == []
    assert metrics.accepted == 13
    assert metrics.question_repaired == 0
    assert all("Use synthesis round" not in sample.question for sample in accepted)
    assert all("question_repaired" not in sample.source for sample in accepted)
    assert all(
        sample.verifier_result.checks["question_entity_alignment"] is True
        for sample in accepted
    )


def test_verify_and_filter_repairs_loaded_raw_sample_question_alignment():
    factory = AgentDataFactory.from_demo_knowledge_graph()
    sample = factory.generate_trajectory(factory.evolve_task(factory.seed_expand(count=1)[0]))
    raw = AgentDataSample.from_json_dict(sample.to_json_dict())
    raw.question = "What country was Albert Einstein born in?"
    raw.source = dict(raw.source)
    raw.source["teacher_backend"] = "openai-compatible"

    accepted, rejected, metrics = factory.verify_and_filter([raw])

    assert rejected == []
    assert metrics.accepted == 1
    assert accepted[0].question == "What country was Ada Lovelace born in?"
    assert accepted[0].source["question_repaired"] is True
    assert accepted[0].source["question_repair_reason"] == "entity_alignment"
    assert accepted[0].source["original_question"] == (
        "What country was Albert Einstein born in?"
    )
    assert accepted[0].verifier_result.checks["question_entity_alignment"] is True


def test_factory_rewrites_duplicate_teacher_questions_before_filtering():
    factory = AgentDataFactory.from_demo_knowledge_graph(
        teacher_backend=FakeRepeatedQuestionTeacherBackend()
    )

    accepted, rejected, metrics = factory.generate_verified(count=6)

    assert len(accepted) == 6
    assert rejected == []
    assert metrics.accepted == 6
    assert metrics.rejected == 0
    assert metrics.dedup_rate == 1.0
    assert len({sample.question for sample in accepted}) == 6
    rewritten = [
        sample for sample in accepted if sample.source.get("duplicate_question_rewritten")
    ]
    assert len(rewritten) == 3
    assert all(
        sample.source["original_question"].startswith("Which country is tied to ")
        for sample in rewritten
    )
    assert all(
        "question_repaired" not in sample.source
        for sample in accepted
    )
    assert all("Disambiguate this sample" not in sample.question for sample in accepted)
    assert all("sample id" not in sample.question for sample in accepted)
    assert all("seed " not in sample.question.lower() for sample in accepted)
    assert all(
        sample.verifier_result.checks["not_duplicate"] is True
        for sample in accepted
    )


def test_factory_runs_teacher_backend_concurrently_when_requested():
    teacher = FakeSlowTeacherBackend()
    factory = AgentDataFactory.from_demo_knowledge_graph(teacher_backend=teacher)
    progress_indices = []

    accepted, rejected, metrics = factory.generate_verified(
        count=6,
        teacher_concurrency=4,
        progress_callback=lambda index, total, sample: progress_indices.append(index),
    )

    assert len(accepted) == 6
    assert rejected == []
    assert metrics.accepted == 6
    assert teacher.max_active > 1
    assert progress_indices == [1, 2, 3, 4, 5, 6]
    assert [sample.id for sample in accepted] == [
        "task-ada-1",
        "task-curie-2",
        "task-turing-3",
        "task-ada-4",
        "task-curie-5",
        "task-turing-6",
    ]
