import json
import subprocess
import sys
from pathlib import Path


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
    assert (out_dir / "sft_conversations.jsonl").exists()
    assert (out_dir / "rl_rewards.jsonl").exists()
    assert (out_dir / "trace.jsonl").exists()
    assert "5,5,0" in (out_dir / "summary.csv").read_text(encoding="utf-8")
