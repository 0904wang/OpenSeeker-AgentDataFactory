from __future__ import annotations

import argparse
from pathlib import Path

from openseeker_factory.pipeline import AgentDataFactory


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
    return parser


def export_artifacts(factory: AgentDataFactory, accepted, rejected, metrics, out_dir: Path) -> None:
    factory.export_jsonl(accepted, out_dir / "samples.jsonl")
    factory.export_sft(accepted, out_dir / "sft_conversations.jsonl")
    factory.export_rl(accepted, out_dir / "rl_rewards.jsonl")
    factory.export_trace(accepted + rejected, out_dir / "trace.jsonl")
    factory.export_summary(metrics, out_dir / "summary.csv")


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


def run_generate(count: int, seed_file: Path, out_dir: Path, strategy: str) -> int:
    factory = AgentDataFactory.from_seed_file(seed_file)
    accepted, rejected, metrics = factory.generate_verified(
        count=count, strategy=strategy
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
        return run_generate(args.count, args.seed_file, args.out_dir, args.strategy)
    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
