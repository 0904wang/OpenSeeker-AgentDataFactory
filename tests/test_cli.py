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
                                "question": "CLI teacher generated question?",
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
    assert first["question"] == "CLI teacher generated question?"
    assert first["difficulty"] == "hard"
