"""Selectable episode beat patterns; none is a universal story formula."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .genre_grammar import RendererKind


class BeatPatternKind(StrEnum):
    EVIDENCE_REVERSAL = "evidence_reversal"
    SUSPENSE_INFORMATION_GAP = "suspense_information_gap"
    COMPETENCE_RECOGNITION = "competence_recognition"
    SELECTION_SAFETY = "selection_safety"


@dataclass(frozen=True, slots=True)
class BeatPatternSpec:
    pattern: BeatPatternKind
    functions: tuple[str, ...]
    compatible_renderers: tuple[RendererKind, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.pattern, BeatPatternKind):
            raise TypeError("pattern must be a BeatPatternKind")
        if not self.functions:
            raise ValueError("beat pattern functions must not be empty")
        if any(not function.strip() for function in self.functions):
            raise ValueError("beat pattern functions must not be empty")
        if len(self.functions) != len(set(self.functions)):
            raise ValueError("beat pattern functions must be unique")
        if not self.compatible_renderers:
            raise ValueError("compatible_renderers must not be empty")
        if any(
            not isinstance(renderer, RendererKind)
            for renderer in self.compatible_renderers
        ):
            raise TypeError("compatible_renderers values must be RendererKind")


PATTERN_SPECS: tuple[BeatPatternSpec, ...] = (
    BeatPatternSpec(
        pattern=BeatPatternKind.EVIDENCE_REVERSAL,
        functions=(
            "attention_trigger",
            "pressure",
            "proof",
            "reclassification",
            "reward_or_obligation",
        ),
        compatible_renderers=(
            RendererKind.RESOURCE,
            RendererKind.STATUS,
            RendererKind.SCARCITY,
            RendererKind.SOCIAL_RECOGNITION,
        ),
    ),
    BeatPatternSpec(
        pattern=BeatPatternKind.SUSPENSE_INFORMATION_GAP,
        functions=(
            "goal_and_loss",
            "attempt",
            "blocker",
            "clue",
            "narrowed_options",
            "information_gap",
        ),
        compatible_renderers=tuple(RendererKind),
    ),
    BeatPatternSpec(
        pattern=BeatPatternKind.COMPETENCE_RECOGNITION,
        functions=(
            "exclusion",
            "task",
            "execution",
            "witness_update",
            "belonging_cost",
        ),
        compatible_renderers=(
            RendererKind.COMPETENCE,
            RendererKind.SOCIAL_RECOGNITION,
            RendererKind.NORM,
        ),
    ),
    BeatPatternSpec(
        pattern=BeatPatternKind.SELECTION_SAFETY,
        functions=(
            "rupture",
            "bid_or_choice",
            "boundary",
            "earned_safety_or_withhold",
        ),
        compatible_renderers=(
            RendererKind.SELECTION,
            RendererKind.ATTACHMENT_SAFETY,
            RendererKind.SOCIAL_RECOGNITION,
        ),
    ),
)


def pattern_spec(pattern: BeatPatternKind) -> BeatPatternSpec:
    if not isinstance(pattern, BeatPatternKind):
        raise TypeError("pattern must be a BeatPatternKind")
    for spec in PATTERN_SPECS:
        if spec.pattern is pattern:
            return spec
    raise KeyError(pattern)


def allowed_patterns(
    renderers: tuple[RendererKind, ...],
) -> tuple[BeatPatternKind, ...]:
    if not renderers:
        raise ValueError("at least one renderer is required")
    if any(not isinstance(renderer, RendererKind) for renderer in renderers):
        raise TypeError("renderers values must be RendererKind")
    renderer_set = set(renderers)
    return tuple(
        spec.pattern
        for spec in PATTERN_SPECS
        if renderer_set.intersection(spec.compatible_renderers)
    )


def validate_pattern_choice(
    pattern: BeatPatternKind,
    renderers: tuple[RendererKind, ...],
) -> None:
    if pattern not in allowed_patterns(renderers):
        raise ValueError(f"{pattern.value} is incompatible with the active renderers")
