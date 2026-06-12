from pathlib import Path

from openseeker_factory.seed_bank import build_wikidata_seed_rows, write_seed_jsonl


def test_build_wikidata_seed_rows_covers_task_types_and_unique_ids():
    rows = build_wikidata_seed_rows()

    assert len(rows) >= 90
    assert len({row["id"] for row in rows}) == len(rows)
    assert {row["task_type"] for row in rows} == {
        "multi_hop_qa",
        "tool_use_qa",
        "noisy_context_retrieval_qa",
    }
    for row in rows:
        assert row["entity"]
        assert row["intermediate"]
        assert row["answer"]
        assert len(row["evidence"]) >= 2
        assert len(row["noisy_context"]) >= 2


def test_build_wikidata_seed_rows_supports_heldout_offset():
    train_rows = build_wikidata_seed_rows(limit=120)
    heldout_rows = build_wikidata_seed_rows(offset=120, limit=60)

    assert len(train_rows) == 120
    assert len(heldout_rows) == 60
    train_entities = {row["entity"] for row in train_rows}
    heldout_entities = {row["entity"] for row in heldout_rows}
    assert train_entities.isdisjoint(heldout_entities)
    assert {row["task_type"] for row in heldout_rows} == {
        "multi_hop_qa",
        "tool_use_qa",
        "noisy_context_retrieval_qa",
    }


def test_write_seed_jsonl_round_trips_rows(tmp_path: Path):
    rows = build_wikidata_seed_rows()[:5]
    path = tmp_path / "seeds.jsonl"

    write_seed_jsonl(rows, path)

    assert path.read_text(encoding="utf-8").count("\n") == 5
    assert '"task_type"' in path.read_text(encoding="utf-8")
