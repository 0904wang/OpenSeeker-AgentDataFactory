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
    return parser


def run_demo(count: int, out_dir: Path) -> int:
    factory = AgentDataFactory.from_demo_knowledge_graph()
    seeds = factory.seed_expand(count=count)
    tasks = [factory.evolve_task(seed) for seed in seeds]
    samples = [factory.generate_trajectory(task) for task in tasks]
    accepted, rejected, metrics = factory.verify_and_filter(samples)

    factory.export_jsonl(accepted, out_dir / "samples.jsonl")
    factory.export_sft(accepted, out_dir / "sft_conversations.jsonl")
    factory.export_rl(accepted, out_dir / "rl_rewards.jsonl")
    factory.export_trace(accepted + rejected, out_dir / "trace.jsonl")
    factory.export_summary(metrics, out_dir / "summary.csv")

    print(
        f"OpenSeeker AgentDataFactory demo complete: "
        f"accepted={metrics.accepted} rejected={metrics.rejected} "
        f"out_dir={out_dir}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "demo":
        return run_demo(args.count, args.out_dir)
    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())

