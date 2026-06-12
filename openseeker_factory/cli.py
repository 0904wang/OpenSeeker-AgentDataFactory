from __future__ import annotations

import argparse
import json
from pathlib import Path

from openseeker_factory.backends import build_chat_backend
from openseeker_factory.evaluation import (
    load_samples,
    run_model_predictions,
    score_prediction_file,
    write_evaluation_outputs,
)
from openseeker_factory.pipeline import AgentDataFactory
from openseeker_factory.schema import AgentDataSample
from openseeker_factory.seed_bank import build_wikidata_seed_rows, write_seed_jsonl


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
    generate.add_argument(
        "--teacher-concurrency",
        type=int,
        default=1,
        help="Maximum concurrent teacher requests.",
    )
    generate.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Optional generation batch size. Each completed batch refreshes exports.",
    )
    generate.add_argument(
        "--resume",
        action="store_true",
        help="Resume from out-dir/raw_generations.jsonl by missing seed_id.",
    )
    build_seeds = subparsers.add_parser(
        "build-seeds", help="Build a reproducible expanded Wikidata-style seed file."
    )
    build_seeds.add_argument(
        "--out-file",
        type=Path,
        default=Path("data/seeds/wikidata_seed_expanded.jsonl"),
        help="Output JSONL seed path.",
    )
    build_seeds.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional maximum number of seed rows to write.",
    )
    build_seeds.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Number of seed rows to skip before applying --limit.",
    )
    evaluate = subparsers.add_parser(
        "evaluate-model",
        help="Evaluate a base model or LoRA adapter on OpenSeeker samples.",
    )
    evaluate.add_argument(
        "--samples",
        type=Path,
        required=True,
        help="Input samples.jsonl file using the OpenSeeker sample schema.",
    )
    evaluate.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Directory for prediction JSONL and summary CSV artifacts.",
    )
    evaluate.add_argument(
        "--model-label",
        required=True,
        help="Short label used in metrics and output filenames.",
    )
    evaluate.add_argument(
        "--model-name-or-path",
        default=None,
        help="Base Hugging Face model name or local path. Required unless --prediction-file is set.",
    )
    evaluate.add_argument(
        "--adapter-path",
        default=None,
        help="Optional PEFT/LoRA adapter path to load on top of the base model.",
    )
    evaluate.add_argument(
        "--prediction-file",
        type=Path,
        default=None,
        help="Optional JSONL with id and prediction/response/text fields. Skips model inference.",
    )
    evaluate.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of samples to evaluate.",
    )
    evaluate.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Number of samples to skip before applying --limit.",
    )
    evaluate.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="Model generation batch size.",
    )
    evaluate.add_argument(
        "--max-new-tokens",
        type=int,
        default=160,
        help="Maximum new tokens to generate per sample.",
    )
    evaluate.add_argument(
        "--device",
        default=None,
        help="Torch device such as cuda or cpu. Defaults to cuda when available.",
    )
    evaluate.add_argument(
        "--local-files-only",
        action="store_true",
        help="Force Transformers/PEFT to use local files only.",
    )
    evaluate.add_argument(
        "--disable-thinking",
        action="store_true",
        help="Ask compatible chat templates such as Qwen3 to disable thinking mode.",
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


def run_build_seeds(out_file: Path, limit: int | None, offset: int) -> int:
    rows = build_wikidata_seed_rows(limit=limit, offset=offset)
    write_seed_jsonl(rows, out_file)
    print(
        f"OpenSeeker seed build complete: rows={len(rows)} out_file={out_file}"
    )
    return 0


def run_generate(
    count: int,
    seed_file: Path,
    out_dir: Path,
    strategy: str,
    teacher_backend,
    teacher_concurrency: int,
    batch_size: int | None,
    resume: bool,
):
    factory = AgentDataFactory.from_seed_file(seed_file, teacher_backend=teacher_backend)
    if batch_size is not None or resume:
        return run_generate_batched(
            factory=factory,
            count=count,
            out_dir=out_dir,
            strategy=strategy,
            teacher_concurrency=teacher_concurrency,
            batch_size=batch_size or count,
            resume=resume,
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    raw_generations_path = out_dir / "raw_generations.jsonl"

    with raw_generations_path.open("w", encoding="utf-8") as raw_handle:

        def stream_progress(index: int, total: int, sample: AgentDataSample) -> None:
            raw_handle.write(json.dumps(sample.to_json_dict(), ensure_ascii=False) + "\n")
            raw_handle.flush()
            print_progress(index, total, sample)

        accepted, rejected, metrics = factory.generate_verified(
            count=count,
            strategy=strategy,
            progress_callback=stream_progress,
            teacher_concurrency=teacher_concurrency,
        )
    export_artifacts(factory, accepted, rejected, metrics, out_dir)
    print(
        f"OpenSeeker AgentDataFactory generation complete: "
        f"accepted={metrics.accepted} rejected={metrics.rejected} "
        f"out_dir={out_dir}"
    )
    return 0


def _sample_seed_id(sample: AgentDataSample) -> str:
    return str(sample.source.get("seed_id", sample.id))


def _ordered_completed_samples(
    target_seed_ids: list[str],
    samples_by_seed_id: dict[str, AgentDataSample],
) -> list[AgentDataSample]:
    return [
        samples_by_seed_id[seed_id]
        for seed_id in target_seed_ids
        if seed_id in samples_by_seed_id
    ]


def run_generate_batched(
    factory: AgentDataFactory,
    count: int,
    out_dir: Path,
    strategy: str,
    teacher_concurrency: int,
    batch_size: int,
    resume: bool,
):
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_generations_path = out_dir / "raw_generations.jsonl"
    target_seeds = factory.seed_expand(count=count)
    target_seed_ids = [seed.id for seed in target_seeds]
    target_seed_id_set = set(target_seed_ids)

    samples_by_seed_id: dict[str, AgentDataSample] = {}
    if resume and raw_generations_path.exists():
        for sample in factory.load_jsonl(raw_generations_path):
            seed_id = _sample_seed_id(sample)
            if seed_id in target_seed_id_set and seed_id not in samples_by_seed_id:
                samples_by_seed_id[seed_id] = sample
    else:
        raw_generations_path.write_text("", encoding="utf-8")

    remaining_seeds = [
        seed for seed in target_seeds if seed.id not in samples_by_seed_id
    ]
    print(
        f"resume: loaded={len(samples_by_seed_id)} remaining={len(remaining_seeds)}",
        flush=True,
    )

    def export_current() -> tuple[list[AgentDataSample], list[AgentDataSample]]:
        current_samples = _ordered_completed_samples(target_seed_ids, samples_by_seed_id)
        accepted, rejected, metrics = factory.verify_and_filter(current_samples)
        export_artifacts(factory, accepted, rejected, metrics, out_dir)
        return accepted, rejected

    for batch_start in range(0, len(remaining_seeds), batch_size):
        batch_seeds = remaining_seeds[batch_start : batch_start + batch_size]
        seen_this_batch: list[AgentDataSample] = []

        with raw_generations_path.open("a", encoding="utf-8") as raw_handle:

            def stream_progress(index: int, total: int, sample: AgentDataSample) -> None:
                raw_handle.write(
                    json.dumps(sample.to_json_dict(), ensure_ascii=False) + "\n"
                )
                raw_handle.flush()
                seen_this_batch.append(sample)
                print_progress(
                    len(samples_by_seed_id) + len(seen_this_batch),
                    count,
                    sample,
                )

            batch_samples = factory.generate_samples_for_seeds(
                batch_seeds,
                strategy=strategy,
                progress_callback=stream_progress,
                teacher_concurrency=teacher_concurrency,
            )

        for sample in batch_samples:
            samples_by_seed_id[_sample_seed_id(sample)] = sample
        accepted, rejected = export_current()
        print(
            f"batch complete: completed={len(samples_by_seed_id)}/{count} "
            f"accepted={len(accepted)} rejected={len(rejected)}",
            flush=True,
        )

    accepted, rejected = export_current()
    print(
        f"OpenSeeker AgentDataFactory generation complete: "
        f"accepted={len(accepted)} rejected={len(rejected)} "
        f"out_dir={out_dir}"
    )
    return 0


def run_evaluate_model(
    samples_path: Path,
    out_dir: Path,
    model_label: str,
    model_name_or_path: str | None,
    adapter_path: str | None,
    prediction_file: Path | None,
    limit: int | None,
    offset: int,
    batch_size: int,
    max_new_tokens: int,
    device: str | None,
    local_files_only: bool,
    disable_thinking: bool,
) -> int:
    samples = load_samples(samples_path, limit=limit, offset=offset)
    if prediction_file is not None:
        rows = score_prediction_file(samples, prediction_file, model_label)
    else:
        if model_name_or_path is None:
            raise ValueError("--model-name-or-path is required without --prediction-file")
        rows = run_model_predictions(
            samples=samples,
            model_name_or_path=model_name_or_path,
            model_label=model_label,
            adapter_path=adapter_path,
            max_new_tokens=max_new_tokens,
            batch_size=batch_size,
            device=device,
            local_files_only=local_files_only,
            enable_thinking=False if disable_thinking else None,
        )
    predictions_path, summary_path = write_evaluation_outputs(
        rows, out_dir, model_label=model_label
    )
    print(
        f"OpenSeeker model evaluation complete: "
        f"model_label={model_label} samples={len(rows)} "
        f"predictions={predictions_path} summary={summary_path}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "demo":
        return run_demo(args.count, args.out_dir)
    if args.command == "build-seeds":
        return run_build_seeds(args.out_file, args.limit, args.offset)
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
            args.teacher_concurrency,
            args.batch_size,
            args.resume,
        )
    if args.command == "evaluate-model":
        return run_evaluate_model(
            samples_path=args.samples,
            out_dir=args.out_dir,
            model_label=args.model_label,
            model_name_or_path=args.model_name_or_path,
            adapter_path=args.adapter_path,
            prediction_file=args.prediction_file,
            limit=args.limit,
            offset=args.offset,
            batch_size=args.batch_size,
            max_new_tokens=args.max_new_tokens,
            device=args.device,
            local_files_only=args.local_files_only,
            disable_thinking=args.disable_thinking,
        )
    raise ValueError(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
