from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class SeedFact:
    entity: str
    birthplace: str
    country: str
    known_for: str


SEED_FACTS: tuple[SeedFact, ...] = (
    SeedFact("Ada Lovelace", "London", "United Kingdom", "early computing"),
    SeedFact("Marie Curie", "Warsaw", "Poland", "radioactivity research"),
    SeedFact("Alan Turing", "London", "United Kingdom", "computing theory"),
    SeedFact("Albert Einstein", "Ulm", "Germany", "relativity"),
    SeedFact("Isaac Newton", "Woolsthorpe-by-Colsterworth", "United Kingdom", "classical mechanics"),
    SeedFact("Niels Bohr", "Copenhagen", "Denmark", "atomic structure"),
    SeedFact("Grace Hopper", "New York City", "United States", "compiler design"),
    SeedFact("Katherine Johnson", "White Sulphur Springs", "United States", "orbital mechanics"),
    SeedFact("Nikola Tesla", "Smiljan", "Croatia", "alternating current systems"),
    SeedFact("Galileo Galilei", "Pisa", "Italy", "observational astronomy"),
    SeedFact("Leonardo da Vinci", "Vinci", "Italy", "Renaissance engineering"),
    SeedFact("Charles Darwin", "Shrewsbury", "United Kingdom", "evolutionary biology"),
    SeedFact("Rosalind Franklin", "London", "United Kingdom", "DNA structure research"),
    SeedFact("Michael Faraday", "Newington Butts", "United Kingdom", "electromagnetism"),
    SeedFact("Emmy Noether", "Erlangen", "Germany", "abstract algebra"),
    SeedFact("Carl Friedrich Gauss", "Braunschweig", "Germany", "number theory"),
    SeedFact("Richard Feynman", "New York City", "United States", "quantum electrodynamics"),
    SeedFact("Enrico Fermi", "Rome", "Italy", "nuclear physics"),
    SeedFact("Srinivasa Ramanujan", "Erode", "India", "number theory"),
    SeedFact("Satyendra Nath Bose", "Kolkata", "India", "quantum statistics"),
    SeedFact("Jagadish Chandra Bose", "Mymensingh", "Bangladesh", "radio science"),
    SeedFact("Subrahmanyan Chandrasekhar", "Lahore", "Pakistan", "stellar structure"),
    SeedFact("Abdus Salam", "Jhang", "Pakistan", "electroweak theory"),
    SeedFact("Chien-Shiung Wu", "Liuhe", "China", "experimental physics"),
    SeedFact("Tu Youyou", "Ningbo", "China", "artemisinin research"),
    SeedFact("Jane Goodall", "London", "United Kingdom", "primatology"),
    SeedFact("Rachel Carson", "Springdale", "United States", "environmental science"),
    SeedFact("Barbara McClintock", "Hartford", "United States", "genetics"),
    SeedFact("Dorothy Hodgkin", "Cairo", "Egypt", "protein crystallography"),
    SeedFact("Lise Meitner", "Vienna", "Austria", "nuclear fission research"),
    SeedFact("Hedy Lamarr", "Vienna", "Austria", "frequency-hopping communication"),
    SeedFact("Claude Shannon", "Petoskey", "United States", "information theory"),
    SeedFact("John von Neumann", "Budapest", "Hungary", "computer architecture"),
    SeedFact("Norbert Wiener", "Columbia", "United States", "cybernetics"),
    SeedFact("Donald Knuth", "Milwaukee", "United States", "algorithm analysis"),
    SeedFact("Tim Berners-Lee", "London", "United Kingdom", "the World Wide Web"),
    SeedFact("Margaret Hamilton", "Paoli", "United States", "Apollo guidance software"),
    SeedFact("Edsger Dijkstra", "Rotterdam", "Netherlands", "shortest path algorithms"),
    SeedFact("Guido van Rossum", "Haarlem", "Netherlands", "Python programming"),
    SeedFact("Yukihiro Matsumoto", "Osaka", "Japan", "Ruby programming"),
)


TASK_VARIANTS: tuple[tuple[str, str, str], ...] = (
    ("multi_hop_qa", "birthplace_country", "multi-hop"),
    ("tool_use_qa", "birthplace_current_country", "tool"),
    ("noisy_context_retrieval_qa", "birthplace_country_noisy", "noisy"),
)


def build_wikidata_seed_rows(limit: int | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fact in SEED_FACTS:
        for task_type, relation, suffix in TASK_VARIANTS:
            rows.append(_build_seed_row(fact, task_type, relation, suffix))
    if limit is not None:
        if limit < 1:
            raise ValueError("limit must be positive")
        return rows[:limit]
    return rows


def write_seed_jsonl(rows: Iterable[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _build_seed_row(
    fact: SeedFact, task_type: str, relation: str, suffix: str
) -> dict[str, Any]:
    return {
        "id": f"wikidata-{_slugify(fact.entity)}-{suffix}",
        "task_type": task_type,
        "entity": fact.entity,
        "relation": relation,
        "intermediate": fact.birthplace,
        "answer": fact.country,
        "evidence": [
            f"{fact.entity} was born in {fact.birthplace}.",
            f"{fact.birthplace} is located in {fact.country}.",
        ],
        "noisy_context": [
            f"{fact.entity} is associated with {fact.known_for}.",
            f"{fact.known_for.capitalize()} is not sufficient by itself to identify {fact.entity}'s birthplace country.",
        ],
    }


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return slug.strip("-")
