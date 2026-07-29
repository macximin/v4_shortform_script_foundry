"""Immutable fact ledger that remains authoritative over renderer interpretation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Certainty(StrEnum):
    CONFIRMED = "confirmed"
    CLAIMED = "claimed"
    INFERRED = "inferred"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class SourceBinding:
    source_id: str
    source_kind: str
    locator: str

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("source_id must not be empty")
        if not self.source_kind.strip():
            raise ValueError("source_kind must not be empty")
        if not self.locator.strip():
            raise ValueError("locator must not be empty")


@dataclass(frozen=True, slots=True)
class FactRecord:
    fact_id: str
    subject: str
    predicate: str
    value: str
    certainty: Certainty
    source_ids: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.certainty, Certainty):
            raise TypeError("certainty must be a Certainty")
        for field_name in ("fact_id", "subject", "predicate", "value"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must not be empty")
        if self.certainty is Certainty.CONFIRMED and not self.source_ids:
            raise ValueError("confirmed facts require at least one source binding")
        if any(not tag.strip() for tag in self.tags):
            raise ValueError("fact tags must not be empty")
        if len(self.tags) != len(set(self.tags)):
            raise ValueError("fact tags must be unique")


@dataclass(frozen=True, slots=True)
class FactLedger:
    premise_id: str
    sources: tuple[SourceBinding, ...]
    facts: tuple[FactRecord, ...]

    def __post_init__(self) -> None:
        if not self.premise_id.strip():
            raise ValueError("premise_id must not be empty")
        source_ids = [source.source_id for source in self.sources]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("source ids must be unique")
        fact_ids = [fact.fact_id for fact in self.facts]
        if len(fact_ids) != len(set(fact_ids)):
            raise ValueError("fact ids must be unique")
        known_source_ids = set(source_ids)
        for fact in self.facts:
            missing = set(fact.source_ids) - known_source_ids
            if missing:
                raise ValueError(
                    f"fact {fact.fact_id} references unknown sources: {sorted(missing)}"
                )

    def get(self, fact_id: str) -> FactRecord:
        for fact in self.facts:
            if fact.fact_id == fact_id:
                return fact
        raise KeyError(fact_id)

    @property
    def confirmed_fact_ids(self) -> tuple[str, ...]:
        return tuple(
            sorted(
                fact.fact_id
                for fact in self.facts
                if fact.certainty is Certainty.CONFIRMED
            )
        )

    @property
    def confirmed_tags(self) -> frozenset[str]:
        return frozenset(
            tag
            for fact in self.facts
            if fact.certainty is Certainty.CONFIRMED
            for tag in fact.tags
        )
