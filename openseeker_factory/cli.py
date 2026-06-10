from __future__ import annotations

import argparse
from pathlib import Path

from openseeker_factory.backends import build_chat_backend
from openseeker_factory.pipeline import AgentDataFactory
from openseeker_factory.schema import AgentDataSample


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="openseeker-factory",
        description="Run the OpenSeeker Agent Data Factory demo pipeline.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    demo = subparsers.add_parser("demo", help="Generate verified demo artifacts.")
    demo.add_argument("--count", type=int, default=3, help="Number of seed tasks.")
    demo.add_argument(
        "--out-dir",
        type=Path,
        default=Path("outputs/demo"),
        help="Directory for JSONL and CSV artifacts.",
    )
    generate = subparsers.add_parser(
        "generate", help="Generate verified artifacts from a seed JSONL file."
    )
    generate.add_argument("--count", type=int, required=True, help="Number of tasks.")
    generate.add_argument(
        "--seed-file",
        type=Path,
        required=True,
        help="JSONL seed file with Wikidata-derived task seeds.",
    )
    generate.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Directory for JSONL and CSV artifacts.",
    )
    generate.add_argument(
        "--strategy",
        choices=["evol_instruct", "magpie_self_instruct"],
        default="evol_instruct",
        help="Task expansion strategy label.",
    )
    generate.add_argument(
        "--teacher-backend",
        choices=["none", "openai-compatible"],
        default="none",
        help="Optional teacher backend for drafting evolved tasks.",
    )
    generate.add_argument(
        "--teacher-base-url",
        default=None,
        help="Base URL for the OpenAI-compatible backend, such as http://127.0.0.1:8000/v1.",
    )
    generate.add_argument(
        "--teacher-model",
        default=None,
        help="Model name for the OpenAI-compatible backend.",
    )
    generate.add_argument(
        "--teacher-api-key-env",
        default="OPENAI_API_KEY",
        help="Environment variable name holding the API key.",
    )
    generate.add_argument(
        "--teacher-timeout-s",
        type=float,
        default=30.0,
        help="Request timeout for the teacher backend.",
    )
    return parser


def export_artifacts(factory: AgentDataFactory, accepted, rejected, metrics, out_dir: Path) -> None:
    factory.export_jsonl(accepted, out_dir / "samples.jsonl")
    factory.export_sft(accepted, out_dir / "sft_conversations.jsonl")
    factory.export_rl(accepted, out_dir / "rl_rewards.jsonl")
    factory.export_trace(accepted + rejected, out_dir / "trace.jsonl")
    factory.export_summary(metrics, out_dir / "summary.csv")


def print_progress(index: int, total: int, sample: AgentDataSample) -> None:
    if "teacher_backend_error" in sample.source:
        teacher_status = "fallback"
    elif "teacher_backend" in sample.source:
        teacher_status = "teacher"
    else:
        teacher_status = "deterministic"
    print(
        f"progress {index}/{total} id={sample.id} "
        f"teacher_status={teacher_status} accepted=pending",
        flush=True,
    )


def run_demo(count: int, out_dir: Path) -> int:
    factory = AgentDataFactory.from_demo_knowledge_graph()
    accepted, rejected, metrics = factory.generate_verified(count=count)
    export_artifacts(factory, accepted, rejected, metrics, out_dir)

    print(
        f"OpenSeeker AgentDataFactory demo complete: "
        f"accepted={metrics.accepted} rejected={metrics.rejected} "
        f"out_dir={out_dir}"
    )
    return 0


def run_generate(
    count: int,
    seed_file: Path,
    out_dir: Path,
    strategy: str,
    teacher_backend,
):
    factory = AgentDataFactory.from_seed_file(seed_file, teacher_backend=teacher_backend)
    accepted, rejected, metrics = factory.generate_verified(
        count=count, strategy=strategy, progress_callback=print_progress
    )
    export_artifacts(factory, accepted, rejected, metrics, out_dir)
    print(
        f"OpenSeeker AgentDataFactory generation complete: "
        f"accepted={metrics.accepted} rejected={metrics.rejected} "
        f"out_dir={out_dir}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "demo":
        return run_demo(args.count, args.out_dir)
    if args.command == "generate":
        teacher_backend = build_chat_backend(
            backend=args.teacher_backend,
            base_url=args.teacher_base_url,
            model=args.teacher_model,
            api_key_env=args.teacher_api_key_env,
            timeout_s=args.teacher_timeout_s,
        )
        return run_generate(
            args.count,
            args.seed_file,
            args.out_dir,
            args.strategy,
            teacher_backend,
        )
    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
