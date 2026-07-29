"""Deterministic selection of episode-level threat, proof, and reward lenses."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from .fact_ledger import Certainty, FactLedger
from .genre_grammar import (
    GenreGrammarPacket,
    GrammarStatus,
    RendererKind,
    RendererPreference,
)


@dataclass(frozen=True, slots=True)
class RendererDecision:
    episode_number: int
    primary: RendererKind
    secondary: tuple[RendererKind, ...]
    primary_threat: str
    proof_mode: str
    reward_target: str
    bound_fact_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]


class RendererRouter:
    """Selects lenses without writing prose or mutating input facts."""

    def route(
        self,
        ledger: FactLedger,
        grammar: GenreGrammarPacket,
        episode_number: int,
        previously_used: tuple[RendererKind, ...] = (),
    ) -> RendererDecision:
        if grammar.status is not GrammarStatus.APPROVED:
            raise ValueError("renderer router accepts approved genre grammar only")
        if episode_number < 1:
            raise ValueError("episode_number must be positive")
        if not ledger.confirmed_fact_ids:
            raise ValueError("renderer routing requires at least one confirmed fact")

        eligible = [
            preference
            for preference in grammar.preferences
            if set(preference.required_fact_tags).issubset(ledger.confirmed_tags)
        ]
        if not eligible:
            raise ValueError(
                "no renderer is eligible for the confirmed fact tags"
            )

        use_counts = Counter(previously_used)
        ranked = sorted(
            eligible,
            key=lambda preference: self._rank_key(preference, use_counts),
        )
        primary = ranked[0]
        secondary = tuple(preference.renderer for preference in ranked[1:3])
        bound_fact_ids = self._supporting_fact_ids(ledger, primary)
        return RendererDecision(
            episode_number=episode_number,
            primary=primary.renderer,
            secondary=secondary,
            primary_threat=primary.threat,
            proof_mode=primary.proof_mode,
            reward_target=primary.reward_target,
            bound_fact_ids=bound_fact_ids,
            rationale_codes=(
                "approved_genre_grammar",
                "weighted_renderer_selection",
                "confirmed_fact_tag_eligibility",
                "recurrence_penalty",
                "confirmed_fact_boundary",
            ),
        )

    @staticmethod
    def _rank_key(
        preference: RendererPreference,
        use_counts: Counter[RendererKind],
    ) -> tuple[int, str]:
        score = preference.weight - 100 * use_counts[preference.renderer]
        return (-score, preference.renderer.value)

    @staticmethod
    def _supporting_fact_ids(
        ledger: FactLedger,
        preference: RendererPreference,
    ) -> tuple[str, ...]:
        required_tags = set(preference.required_fact_tags)
        if not required_tags:
            return ledger.confirmed_fact_ids[:1]
        return tuple(
            sorted(
                fact.fact_id
                for fact in ledger.facts
                if fact.certainty is Certainty.CONFIRMED
                and required_tags.intersection(fact.tags)
            )
        )
