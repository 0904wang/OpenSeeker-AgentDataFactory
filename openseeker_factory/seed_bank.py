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


@dataclass(frozen=True)
class RelationDiverseFact:
    entity: str
    known_for: str
    birthplace: str
    birthplace_country: str
    education: str
    education_country: str
    employer: str
    employer_country: str
    award: str
    award_country: str


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
    SeedFact("James Clerk Maxwell", "Edinburgh", "United Kingdom", "electromagnetism"),
    SeedFact("Max Planck", "Kiel", "Germany", "quantum theory"),
    SeedFact("Erwin Schrodinger", "Vienna", "Austria", "quantum mechanics"),
    SeedFact("Werner Heisenberg", "Wurzburg", "Germany", "uncertainty principle"),
    SeedFact("Paul Dirac", "Bristol", "United Kingdom", "quantum mechanics"),
    SeedFact("Charles Babbage", "London", "United Kingdom", "computing machinery"),
    SeedFact("Mary Anning", "Lyme Regis", "United Kingdom", "paleontology"),
    SeedFact("Maryam Mirzakhani", "Tehran", "Iran", "geometry"),
    SeedFact("C. V. Raman", "Tiruchirappalli", "India", "light scattering"),
    SeedFact("Sophie Germain", "Paris", "France", "number theory"),
    SeedFact("Emilie du Chatelet", "Paris", "France", "physics translation"),
    SeedFact("Florence Nightingale", "Florence", "Italy", "modern nursing"),
    SeedFact("Blaise Pascal", "Clermont-Ferrand", "France", "probability theory"),
    SeedFact("Gottfried Wilhelm Leibniz", "Leipzig", "Germany", "calculus"),
    SeedFact("Rene Descartes", "La Haye en Touraine", "France", "analytic geometry"),
    SeedFact("Dmitri Mendeleev", "Tobolsk", "Russia", "periodic table"),
    SeedFact("Gregor Mendel", "Hyncice", "Czech Republic", "genetics"),
    SeedFact("Louis Pasteur", "Dole", "France", "microbiology"),
    SeedFact("Alexander Fleming", "Lochfield", "United Kingdom", "penicillin"),
    SeedFact("Mae Jemison", "Decatur", "United States", "spaceflight"),
)

RELATION_DIVERSE_FACTS: tuple[RelationDiverseFact, ...] = (
    RelationDiverseFact(
        entity="Alan Turing",
        known_for="computing theory",
        birthplace="London",
        birthplace_country="United Kingdom",
        education="University of Cambridge",
        education_country="United Kingdom",
        employer="Government Code and Cypher School",
        employer_country="United Kingdom",
        award="Smith's Prize",
        award_country="United Kingdom",
    ),
    RelationDiverseFact(
        entity="Grace Hopper",
        known_for="compiler design",
        birthplace="New York City",
        birthplace_country="United States",
        education="Yale University",
        education_country="United States",
        employer="United States Navy",
        employer_country="United States",
        award="National Medal of Technology",
        award_country="United States",
    ),
    RelationDiverseFact(
        entity="Marie Curie",
        known_for="radioactivity research",
        birthplace="Warsaw",
        birthplace_country="Poland",
        education="University of Paris",
        education_country="France",
        employer="Radium Institute",
        employer_country="France",
        award="Nobel Prize in Chemistry",
        award_country="Sweden",
    ),
    RelationDiverseFact(
        entity="Albert Einstein",
        known_for="relativity",
        birthplace="Ulm",
        birthplace_country="Germany",
        education="ETH Zurich",
        education_country="Switzerland",
        employer="Princeton University",
        employer_country="United States",
        award="Nobel Prize in Physics",
        award_country="Sweden",
    ),
    RelationDiverseFact(
        entity="Katherine Johnson",
        known_for="orbital mechanics",
        birthplace="White Sulphur Springs",
        birthplace_country="United States",
        education="West Virginia State College",
        education_country="United States",
        employer="NASA",
        employer_country="United States",
        award="Presidential Medal of Freedom",
        award_country="United States",
    ),
    RelationDiverseFact(
        entity="C. V. Raman",
        known_for="light scattering",
        birthplace="Tiruchirappalli",
        birthplace_country="India",
        education="Presidency College",
        education_country="India",
        employer="Indian Association for the Cultivation of Science",
        employer_country="India",
        award="Nobel Prize in Physics",
        award_country="Sweden",
    ),
    RelationDiverseFact(
        entity="Tu Youyou",
        known_for="artemisinin research",
        birthplace="Ningbo",
        birthplace_country="China",
        education="Peking University",
        education_country="China",
        employer="China Academy of Chinese Medical Sciences",
        employer_country="China",
        award="Nobel Prize in Physiology or Medicine",
        award_country="Sweden",
    ),
)


TASK_VARIANTS: tuple[tuple[str, str, str], ...] = (
    ("multi_hop_qa", "birthplace_country", "multi-hop"),
    ("tool_use_qa", "birthplace_current_country", "tool"),
    ("noisy_context_retrieval_qa", "birthplace_country_noisy", "noisy"),
)


def build_wikidata_seed_rows(
    limit: int | None = None, offset: int = 0, relation_diverse: bool = False
) -> list[dict[str, Any]]:
    if offset < 0:
        raise ValueError("offset must be non-negative")
    if relation_diverse:
        rows = _build_relation_diverse_seed_rows()
        rows = rows[offset:]
        if limit is not None:
            if limit < 1:
                raise ValueError("limit must be positive")
            return rows[:limit]
        return rows
    rows: list[dict[str, Any]] = []
    for fact in SEED_FACTS:
        for task_type, relation, suffix in TASK_VARIANTS:
            rows.append(_build_seed_row(fact, task_type, relation, suffix))
    rows = rows[offset:]
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


def _build_relation_diverse_seed_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for fact in RELATION_DIVERSE_FACTS:
        rows.extend(
            [
                _build_relation_seed_row(
                    fact=fact,
                    task_type="multi_hop_qa",
                    relation="birthplace_country",
                    suffix="birthplace",
                    intermediate=fact.birthplace,
                    answer=fact.birthplace_country,
                    evidence=[
                        f"{fact.entity} was born in {fact.birthplace}.",
                        f"{fact.birthplace} is located in {fact.birthplace_country}.",
                    ],
                ),
                _build_relation_seed_row(
                    fact=fact,
                    task_type="tool_use_qa",
                    relation="education_country",
                    suffix="education",
                    intermediate=fact.education,
                    answer=fact.education_country,
                    evidence=[
                        f"{fact.entity} was educated at {fact.education}.",
                        f"{fact.education} is located in {fact.education_country}.",
                    ],
                ),
                _build_relation_seed_row(
                    fact=fact,
                    task_type="multi_hop_qa",
                    relation="employer_country",
                    suffix="employer",
                    intermediate=fact.employer,
                    answer=fact.employer_country,
                    evidence=[
                        f"{fact.entity} worked for {fact.employer}.",
                        f"{fact.employer} is headquartered in {fact.employer_country}.",
                    ],
                ),
                _build_relation_seed_row(
                    fact=fact,
                    task_type="noisy_context_retrieval_qa",
                    relation="award_country",
                    suffix="award",
                    intermediate=fact.award,
                    answer=fact.award_country,
                    evidence=[
                        f"{fact.entity} received {fact.award}.",
                        f"{fact.award} is associated with {fact.award_country}.",
                    ],
                ),
            ]
        )
    return rows


def _build_relation_seed_row(
    fact: RelationDiverseFact,
    task_type: str,
    relation: str,
    suffix: str,
    intermediate: str,
    answer: str,
    evidence: list[str],
) -> dict[str, Any]:
    return {
        "id": f"wikidata-v7-{_slugify(fact.entity)}-{suffix}",
        "task_type": task_type,
        "entity": fact.entity,
        "relation": relation,
        "intermediate": intermediate,
        "answer": answer,
        "evidence": evidence,
        "noisy_context": [
            f"{fact.entity} is associated with {fact.known_for}.",
            f"{fact.known_for.capitalize()} is not sufficient by itself to identify the requested relation-country path.",
        ],
    }


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return slug.strip("-")
