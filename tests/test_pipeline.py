from pathlib import Path

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
                "Action: wikidata_lookup[Ada Lovelace birthplace]",
                "Observation: London",
                "Thought: Resolve London to its country.",
                "Action: wikidata_lookup[London country]",
                "Observation: United Kingdom",
                "Final: United Kingdom",
            ],
        }


class FakeInvalidTrajectoryTeacherBackend:
    name = "fake-invalid-trajectory"

    def complete_json(self, messages):
        return {
            "question": "Teacher drafted question with invalid trajectory?",
            "difficulty": "hard",
            "trajectory": [
                "Find Ada Lovelace's birthplace: London.",
                "Find the country: United Kingdom.",
            ],
        }


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
    assert sft_path.read_text(encoding="utf-8").splitlines()[0].startswith('{"id":')
    assert '"prompt"' in rl_path.read_text(encoding="utf-8")
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
    assert accepted[0].question == "Teacher drafted question with invalid trajectory?"
    assert accepted[0].trajectory == [
        "Thought: Identify the entity's birthplace.",
        "Action: wikidata_lookup[Ada Lovelace birthplace]",
        "Observation: London",
        "Thought: Resolve the country from the intermediate location.",
        "Action: wikidata_lookup[London country]",
        "Observation: United Kingdom",
        "Final: United Kingdom",
    ]
    assert accepted[0].source["teacher_trajectory_repaired"] is True
