import subprocess
import sys


def test_project_builds_wheel_with_data_directory_present(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--wheel-dir",
            str(tmp_path),
            ".",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert any(tmp_path.glob("openseeker_agent_data_factory-*.whl"))

