import json
import os
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread


class _TeacherHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        length = int(self.headers["Content-Length"])
        json.loads(self.rfile.read(length))
        payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "question": "CLI teacher generated Ada Lovelace question?",
                                "difficulty": "hard",
                                "trajectory": [
                                    "Thought: Use the lookup trajectory.",
                                    "Action: wikidata_lookup[Ada Lovelace birthplace]",
                                    "Observation: London",
                                    "Thought: Resolve country.",
                                    "Action: wikidata_lookup[London country]",
                                    "Observation: United Kingdom",
                                    "Final: United Kingdom",
                                ],
                            }
                        )
                    }
                }
            ]
        }
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, format: str, *args) -> None:
        return


def test_cli_demo_writes_all_expected_artifacts(tmp_path: Path):
    out_dir = tmp_path / "run"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "openseeker_factory.cli",
            "demo",
            "--count",
            "3",
            "--out-dir",
            str(out_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "accepted=3 rejected=0" in result.stdout
    expected = {
        "samples.jsonl",
        "sft_conversations.jsonl",
        "rl_rewards.jsonl",
        "trace.jsonl",
        "summary.csv",
    }
    assert expected.issubset({path.name for path in out_dir.iterdir()})

    first = json.loads((out_dir / "samples.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert set(first) == {
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
    }


def test_cli_generate_uses_seed_file_and_writes_baseline_artifacts(tmp_path: Path):
    out_dir = tmp_path / "baseline"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "openseeker_factory.cli",
            "generate",
            "--count",
            "5",
            "--seed-file",
            "tests/fixtures/seeds.jsonl",
            "--out-dir",
            str(out_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "accepted=5 rejected=0" in result.stdout
    assert (out_dir / "samples.jsonl").read_text(encoding="utf-8").count("\n") == 5
    assert (out_dir / "raw_generations.jsonl").read_text(encoding="utf-8").count("\n") == 5
    assert (out_dir / "sft_conversations.jsonl").exists()
    assert (out_dir / "rl_rewards.jsonl").exists()
    assert (out_dir / "trace.jsonl").exists()
    assert "5,5,0" in (out_dir / "summary.csv").read_text(encoding="utf-8")


def test_cli_generate_supports_start_index_for_disjoint_variants(tmp_path: Path):
    out_dir = tmp_path / "offset"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "openseeker_factory.cli",
            "generate",
            "--count",
            "2",
            "--seed-file",
            "tests/fixtures/seeds.jsonl",
            "--out-dir",
            str(out_dir),
            "--start-index",
            "4",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "accepted=2 rejected=0" in result.stdout
    samples = [
        json.loads(line)
        for line in (out_dir / "samples.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [sample["source"]["seed_id"] for sample in samples] == [
        "wikidata-ada-5",
        "wikidata-curie-6",
    ]
    assert [sample["source"]["variant_index"] for sample in samples] == [3, 3]


def test_cli_generate_supports_canonical_v4_data_version(tmp_path: Path):
    out_dir = tmp_path / "canonical-v4"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "openseeker_factory.cli",
            "generate",
            "--count",
            "1",
            "--seed-file",
            "tests/fixtures/seeds.jsonl",
            "--out-dir",
            str(out_dir),
            "--data-version",
            "canonical-v4",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "accepted=1 rejected=0" in result.stdout
    sample = json.loads(
        (out_dir / "samples.jsonl").read_text(encoding="utf-8").splitlines()[0]
    )
    assert sample["source"]["data_version"] == "canonical-v4"
    assert "Available lookup observations:" in sample["question"]
    sft = json.loads(
        (out_dir / "sft_conversations.jsonl").read_text(encoding="utf-8").splitlines()[0]
    )
    assert "copy the provided lookup observation values exactly" in sft["messages"][0]["content"]
    assert "Available lookup observations:" in sft["messages"][1]["content"]


def test_cli_generate_supports_canonical_v4_hard_data_version(tmp_path: Path):
    out_dir = tmp_path / "canonical-v4-hard"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "openseeker_factory.cli",
            "generate",
            "--count",
            "1",
            "--seed-file",
            "tests/fixtures/seeds.jsonl",
            "--out-dir",
            str(out_dir),
            "--data-version",
            "canonical-v4-hard",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "accepted=1 rejected=0" in result.stdout
    sample = json.loads(
        (out_dir / "samples.jsonl").read_text(encoding="utf-8").splitlines()[0]
    )
    assert sample["difficulty"] == "hard"
    assert sample["source"]["data_version"] == "canonical-v4-hard"
    assert sample["source"]["heldout_profile"] == "v4-hard"
    assert sample["source"]["distractor_lookup_observation"] is True
    assert "Distractor lookup observations:" in sample["question"]
    assert "Do not copy distractor observations" in sample["question"]
    sft = json.loads(
        (out_dir / "sft_conversations.jsonl").read_text(encoding="utf-8").splitlines()[0]
    )
    assert "copy the provided lookup observation values exactly" in sft["messages"][0]["content"]
    assert "Available lookup observations:" in sft["messages"][1]["content"]


def test_cli_generate_supports_canonical_v5_blind_hard_data_version(tmp_path: Path):
    out_dir = tmp_path / "canonical-v5-blind-hard"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "openseeker_factory.cli",
            "generate",
            "--count",
            "1",
            "--seed-file",
            "tests/fixtures/seeds.jsonl",
            "--out-dir",
            str(out_dir),
            "--data-version",
            "canonical-v5-blind-hard",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "accepted=1 rejected=0" in result.stdout
    sample = json.loads(
        (out_dir / "samples.jsonl").read_text(encoding="utf-8").splitlines()[0]
    )
    assert sample["difficulty"] == "hard"
    assert sample["source"]["data_version"] == "canonical-v5-blind-hard"
    assert sample["source"]["heldout_profile"] == "v5-blind-hard"
    assert sample["source"]["lookup_observation_block"] is False
    assert "Available lookup observations:" not in sample["question"]
    assert "Use ReAct steps with wikidata_lookup[entity, P19]" in sample["question"]
    assert "Alias trap:" in sample["question"]
    sft = json.loads(
        (out_dir / "sft_conversations.jsonl").read_text(encoding="utf-8").splitlines()[0]
    )
    assert "Available lookup observations:" not in sft["messages"][1]["content"]


def test_cli_generate_batches_export_artifacts_after_all_batches(tmp_path: Path):
    out_dir = tmp_path / "batched"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "openseeker_factory.cli",
            "generate",
            "--count",
            "5",
            "--seed-file",
            "tests/fixtures/seeds.jsonl",
            "--out-dir",
            str(out_dir),
            "--batch-size",
            "2",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "accepted=5 rejected=0" in result.stdout
    assert "batch complete: completed=2/5" in result.stdout
    assert "batch complete: completed=4/5" in result.stdout
    assert "batch complete: completed=5/5" in result.stdout
    assert (out_dir / "raw_generations.jsonl").read_text(encoding="utf-8").count("\n") == 5
    assert (out_dir / "samples.jsonl").read_text(encoding="utf-8").count("\n") == 5
    assert (out_dir / "sft_conversations.jsonl").read_text(encoding="utf-8").count("\n") == 5
    assert (out_dir / "rl_rewards.jsonl").read_text(encoding="utf-8").count("\n") == 5
    assert (out_dir / "trace.jsonl").read_text(encoding="utf-8").count("\n") == 5
    assert "5,5,0" in (out_dir / "summary.csv").read_text(encoding="utf-8")


def test_cli_generate_resume_fills_missing_seed_ids_without_duplication(tmp_path: Path):
    out_dir = tmp_path / "resume"
    first = subprocess.run(
        [
            sys.executable,
            "-m",
            "openseeker_factory.cli",
            "generate",
            "--count",
            "3",
            "--seed-file",
            "tests/fixtures/seeds.jsonl",
            "--out-dir",
            str(out_dir),
            "--batch-size",
            "2",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "accepted=3 rejected=0" in first.stdout

    raw_path = out_dir / "raw_generations.jsonl"
    raw_rows = [
        json.loads(line)
        for line in raw_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    raw_path.write_text(
        "\n".join(
            json.dumps(row)
            for row in raw_rows
            if row["source"]["seed_id"] != "wikidata-curie-2"
        )
        + "\n",
        encoding="utf-8",
    )

    resumed = subprocess.run(
        [
            sys.executable,
            "-m",
            "openseeker_factory.cli",
            "generate",
            "--count",
            "3",
            "--seed-file",
            "tests/fixtures/seeds.jsonl",
            "--out-dir",
            str(out_dir),
            "--batch-size",
            "2",
            "--resume",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "resume: loaded=2 remaining=1" in resumed.stdout
    assert "accepted=3 rejected=0" in resumed.stdout
    final_rows = [
        json.loads(line)
        for line in raw_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    seed_ids = [row["source"]["seed_id"] for row in final_rows]
    assert sorted(seed_ids) == [
        "wikidata-ada-1",
        "wikidata-ada-3",
        "wikidata-curie-2",
    ]
    assert len(seed_ids) == len(set(seed_ids))
    assert (out_dir / "samples.jsonl").read_text(encoding="utf-8").count("\n") == 3


def test_cli_build_seeds_writes_expanded_seed_file(tmp_path: Path):
    out_file = tmp_path / "expanded.jsonl"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "openseeker_factory.cli",
            "build-seeds",
            "--out-file",
            str(out_file),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "OpenSeeker seed build complete" in result.stdout
    assert out_file.read_text(encoding="utf-8").count("\n") >= 90


def test_cli_build_seeds_supports_offset_for_heldout_file(tmp_path: Path):
    out_file = tmp_path / "heldout.jsonl"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "openseeker_factory.cli",
            "build-seeds",
            "--out-file",
            str(out_file),
            "--offset",
            "120",
            "--limit",
            "3",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    rows = [
        json.loads(line)
        for line in out_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert "rows=3" in result.stdout
    assert len(rows) == 3
    assert {row["entity"] for row in rows} == {"James Clerk Maxwell"}


def test_cli_evaluate_model_scores_prediction_file(tmp_path: Path):
    samples_dir = tmp_path / "samples"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "openseeker_factory.cli",
            "demo",
            "--count",
            "1",
            "--out-dir",
            str(samples_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    sample = json.loads(
        (samples_dir / "samples.jsonl").read_text(encoding="utf-8").splitlines()[0]
    )
    prediction_file = tmp_path / "predictions.jsonl"
    prediction_file.write_text(
        json.dumps(
            {
                "id": sample["id"],
                "prediction": "Thought: done.\nFinal: United Kingdom",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    out_dir = tmp_path / "eval"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "openseeker_factory.cli",
            "evaluate-model",
            "--samples",
            str(samples_dir / "samples.jsonl"),
            "--prediction-file",
            str(prediction_file),
            "--model-label",
            "fake-model",
            "--out-dir",
            str(out_dir),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "OpenSeeker model evaluation complete" in result.stdout
    assert (out_dir / "fake-model_predictions.jsonl").exists()
    summary = (out_dir / "fake-model_summary.csv").read_text(encoding="utf-8")
    assert "exact_match_rate" in summary
    assert "1.0" in summary


def test_cli_generate_can_use_openai_compatible_teacher_backend(tmp_path: Path):
    server = ThreadingHTTPServer(("127.0.0.1", 0), _TeacherHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    out_dir = tmp_path / "teacher"

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "openseeker_factory.cli",
                "generate",
                "--count",
                "1",
                "--seed-file",
                "tests/fixtures/seeds.jsonl",
                "--out-dir",
                str(out_dir),
                "--teacher-backend",
                "openai-compatible",
                "--teacher-base-url",
                f"http://127.0.0.1:{server.server_port}/v1",
                "--teacher-model",
                "fake-model",
                "--teacher-api-key-env",
                "TEST_TEACHER_API_KEY",
                "--teacher-concurrency",
                "2",
            ],
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "TEST_TEACHER_API_KEY": "test-key"},
        )
    finally:
        server.shutdown()
        thread.join(timeout=2)

    assert "accepted=1 rejected=0" in result.stdout
    assert (
        "progress 1/1 id=wikidata-ada-1 teacher_status=teacher accepted=pending"
        in result.stdout
    )
    first = json.loads((out_dir / "samples.jsonl").read_text(encoding="utf-8"))
    assert first["question"] == "CLI teacher generated Ada Lovelace question?"
    assert first["difficulty"] == "hard"
