"""Synthetic entity-resolution data with a controlled corruption rate.

We invent a population of *true* entities (people), then emit noisy *records*
for them spread across two source systems ("A" and "B"). Each record is a
corrupted view of its entity: fields may be mistyped, reformatted, or dropped.
The ground-truth entity id travels with every record so downstream clustering
can be scored exactly.
"""

from __future__ import annotations

import random
import string
from dataclasses import dataclass, field
from typing import Optional


# Small, deliberately clash-prone name pools so that corruption produces the
# genuinely ambiguous pairs that make the reconciliation problem interesting.
_FIRST_NAMES = [
    "James", "Jamie", "John", "Jon", "Mary", "Maria", "Robert", "Bob",
    "Patricia", "Patrick", "Michael", "Michelle", "Linda", "Lynda",
    "William", "Will", "Elizabeth", "Beth", "David", "Dave", "Sarah", "Sara",
    "Richard", "Rick", "Susan", "Suzanne", "Thomas", "Tom", "Karen", "Karin",
]

_LAST_NAMES = [
    "Smith", "Smyth", "Johnson", "Jonson", "Williams", "Williamson",
    "Brown", "Browne", "Jones", "Joans", "Garcia", "Gracia", "Miller",
    "Millar", "Davis", "Davies", "Rodriguez", "Rodrigues", "Martinez",
    "Martines", "Wilson", "Willson", "Anderson", "Andersen", "Taylor",
    "Tailor", "Thomas", "Thompson", "Moore", "Moor",
]

_STREETS = [
    "Main St", "Oak Ave", "Maple Dr", "Cedar Ln", "Pine Rd", "Elm St",
    "Washington Ave", "Lake Dr", "Hill Rd", "Park Ave", "Church St",
    "High St", "Sunset Blvd", "River Rd", "Union St",
]

_CITIES = [
    ("Springfield", "IL", "62701"),
    ("Riverside", "CA", "92501"),
    ("Franklin", "TN", "37064"),
    ("Clinton", "NY", "13323"),
    ("Georgetown", "TX", "78626"),
    ("Madison", "WI", "53703"),
    ("Arlington", "VA", "22201"),
    ("Salem", "OR", "97301"),
]


@dataclass(frozen=True)
class Record:
    """A single observed record in one of the source systems.

    ``entity_id`` is ground truth and must never be shown to the matcher; it is
    retained only so results can be scored.
    """

    record_id: int
    entity_id: int
    source: str  # "A" or "B"
    first_name: str
    last_name: str
    dob: Optional[str]  # ISO-ish YYYY-MM-DD, or None if dropped
    street: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    email: Optional[str]


def _random_dob(rng: random.Random) -> str:
    year = rng.randint(1940, 2005)
    month = rng.randint(1, 12)
    day = rng.randint(1, 28)
    return f"{year:04d}-{month:02d}-{day:02d}"


def _make_entity(rng: random.Random) -> dict:
    """A clean, canonical attribute set for one true entity."""
    first = rng.choice(_FIRST_NAMES)
    last = rng.choice(_LAST_NAMES)
    city, state, zip_code = rng.choice(_CITIES)
    number = rng.randint(1, 9999)
    street = f"{number} {rng.choice(_STREETS)}"
    email = f"{first.lower()}.{last.lower()}@example.com"
    return {
        "first_name": first,
        "last_name": last,
        "dob": _random_dob(rng),
        "street": street,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "email": email,
    }


def _typo(text: str, rng: random.Random) -> str:
    """Apply one random character-level edit (insert / delete / substitute /
    transpose) to simulate keying error."""
    if not text:
        return text
    op = rng.choice(["sub", "del", "ins", "transpose"])
    i = rng.randrange(len(text))
    if op == "sub":
        return text[:i] + rng.choice(string.ascii_lowercase) + text[i + 1:]
    if op == "del":
        return text[:i] + text[i + 1:]
    if op == "ins":
        return text[:i] + rng.choice(string.ascii_lowercase) + text[i:]
    # transpose
    if i < len(text) - 1:
        return text[:i] + text[i + 1] + text[i] + text[i + 2:]
    return text


def _corrupt_field(value: Optional[str], rng: random.Random,
                   corruption_rate: float) -> Optional[str]:
    """Independently decide whether to drop, reformat, or mistype a field."""
    if value is None:
        return None
    if rng.random() >= corruption_rate:
        return value  # left untouched

    roll = rng.random()
    if roll < 0.25:
        return None  # dropped / missing
    if roll < 0.5:
        # formatting drift: strip punctuation and re-case
        reformatted = value.replace("-", "").replace(".", "").lower()
        return reformatted
    # keying error: one or two typos
    corrupted = _typo(value, rng)
    if rng.random() < 0.3:
        corrupted = _typo(corrupted, rng)
    return corrupted


def _emit_record(record_id: int, entity_id: int, source: str,
                 entity: dict, rng: random.Random,
                 corruption_rate: float) -> Record:
    return Record(
        record_id=record_id,
        entity_id=entity_id,
        source=source,
        first_name=_corrupt_field(entity["first_name"], rng, corruption_rate) or "",
        last_name=_corrupt_field(entity["last_name"], rng, corruption_rate) or "",
        dob=_corrupt_field(entity["dob"], rng, corruption_rate),
        street=_corrupt_field(entity["street"], rng, corruption_rate),
        city=_corrupt_field(entity["city"], rng, corruption_rate),
        state=entity["state"],  # state rarely mis-keyed; keep as a stable block key
        zip_code=_corrupt_field(entity["zip_code"], rng, corruption_rate),
        email=_corrupt_field(entity["email"], rng, corruption_rate),
    )


@dataclass
class Dataset:
    """A generated problem instance."""

    records: list[Record]
    n_entities: int
    corruption_rate: float

    def truth(self) -> dict[int, int]:
        """Mapping record_id -> ground-truth entity_id."""
        return {r.record_id: r.entity_id for r in self.records}


def generate_dataset(
    n_entities: int = 40,
    corruption_rate: float = 0.3,
    records_per_entity: tuple[int, int] = (1, 3),
    overlap: float = 0.7,
    seed: Optional[int] = None,
) -> Dataset:
    """Generate a two-system entity-resolution instance.

    Args:
        n_entities: number of distinct true entities in the population.
        corruption_rate: per-field probability that a field is corrupted
            (dropped, reformatted, or mistyped) when a record is emitted.
        records_per_entity: inclusive ``(min, max)`` range for how many
            records an entity contributes *in total* across both systems.
        overlap: probability that an entity appears in *both* systems. When it
            appears in only one, it lands in A or B with equal chance.
        seed: optional RNG seed for reproducibility.

    Returns:
        A :class:`Dataset`. Each record carries its true ``entity_id`` so the
        clustering can be scored.
    """
    if not 0.0 <= corruption_rate <= 1.0:
        raise ValueError("corruption_rate must be in [0, 1]")
    if not 0.0 <= overlap <= 1.0:
        raise ValueError("overlap must be in [0, 1]")
    lo, hi = records_per_entity
    if lo < 1 or hi < lo:
        raise ValueError("records_per_entity must satisfy 1 <= min <= max")

    rng = random.Random(seed)
    records: list[Record] = []
    rid = 0

    for entity_id in range(n_entities):
        entity = _make_entity(rng)
        total = rng.randint(lo, hi)

        if rng.random() < overlap:
            # Split records across both systems, guaranteeing at least one each.
            in_a = rng.randint(1, max(1, total - 1)) if total > 1 else 1
            sources = ["A"] * in_a + ["B"] * (total - in_a)
            if total == 1:
                sources = [rng.choice(["A", "B"])]
        else:
            sources = [rng.choice(["A", "B"])] * total

        rng.shuffle(sources)
        for source in sources:
            records.append(
                _emit_record(rid, entity_id, source, entity, rng, corruption_rate)
            )
            rid += 1

    rng.shuffle(records)
    return Dataset(records=records, n_entities=n_entities,
                   corruption_rate=corruption_rate)
