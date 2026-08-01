"""HIL 1 contract for a work's creative north star and protected latitude."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

from .canonical import canonical_sha256
from .genre_grammar import RendererKind


_SHA256_RE = re.compile(r"[0-9a-f]{64}")


def _require_text(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")


def _require_text_tuple(
    values: tuple[str, ...],
    field_name: str,
    *,
    minimum: int = 1,
) -> None:
    if len(values) < minimum:
        raise ValueError(f"{field_name} requires at least {minimum} value(s)")
    if any(not value.strip() for value in values):
        raise ValueError(f"{field_name} values must not be empty")
    if len(values) != len(set(values)):
        raise ValueError(f"{field_name} values must be unique")


@dataclass(frozen=True, slots=True)
class CoreCharacterContract:
    character_id: str
    narrative_role: str
    goal: str
    failure_cost: str
    operating_identity_invariant_kernel: str
    initial_agency_state: str
    allowed_agency_transitions: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "character_id",
            "narrative_role",
            "goal",
            "failure_cost",
            "operating_identity_invariant_kernel",
            "initial_agency_state",
        ):
            _require_text(getattr(self, field_name), field_name)
        _require_text_tuple(
            self.allowed_agency_transitions,
            "allowed_agency_transitions",
        )


ProtagonistContract = CoreCharacterContract


class PayoffCadence(StrEnum):
    EPISODE = "episode"
    ARC = "arc"
    SEASON = "season"
    FUTURE_SEED = "future_seed"


@dataclass(frozen=True, slots=True)
class PayoffLayer:
    payoff_id: str
    cadence: PayoffCadence
    subject_id: str
    promise: str
    delivery_policy: str

    def __post_init__(self) -> None:
        for field_name in (
            "payoff_id",
            "subject_id",
            "promise",
            "delivery_policy",
        ):
            _require_text(getattr(self, field_name), field_name)
        if not isinstance(self.cadence, PayoffCadence):
            raise TypeError("cadence must be a PayoffCadence")


@dataclass(frozen=True, slots=True)
class ProductionConstraints:
    target_runtime_seconds_min: int
    target_runtime_seconds_max: int
    max_principal_characters_per_scene: int
    action_driven: bool
    dialogue_policy: str
    max_dialogue_lines_per_scene: int | None = None

    def __post_init__(self) -> None:
        if not 40 <= self.target_runtime_seconds_min <= 300:
            raise ValueError(
                "target_runtime_seconds_min must be between 40 and 300"
            )
        if not 40 <= self.target_runtime_seconds_max <= 300:
            raise ValueError(
                "target_runtime_seconds_max must be between 40 and 300"
            )
        if self.target_runtime_seconds_max < self.target_runtime_seconds_min:
            raise ValueError(
                "target_runtime_seconds_max must be at least the minimum"
            )
        if not 1 <= self.max_principal_characters_per_scene <= 8:
            raise ValueError(
                "max_principal_characters_per_scene must be between 1 and 8"
            )
        if not isinstance(self.action_driven, bool):
            raise TypeError("action_driven must be a bool")
        _require_text(self.dialogue_policy, "dialogue_policy")
        if (
            self.max_dialogue_lines_per_scene is not None
            and self.max_dialogue_lines_per_scene < 1
        ):
            raise ValueError("max_dialogue_lines_per_scene must be positive")


@dataclass(frozen=True, slots=True)
class AudienceInformationContract:
    objective_fact_policy: str
    character_perception_policy: str
    asymmetry_principles: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_text(
            self.objective_fact_policy,
            "objective_fact_policy",
        )
        _require_text(
            self.character_perception_policy,
            "character_perception_policy",
        )
        _require_text_tuple(
            self.asymmetry_principles,
            "asymmetry_principles",
        )


@dataclass(frozen=True, slots=True)
class OriginalityContract:
    originality_axes: tuple[str, ...]
    anti_goals: tuple[str, ...]
    creative_latitude: tuple[str, ...]
    source_rights_policy: str
    premise_distance_receipt_sha256: str
    original_contributions: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_text_tuple(self.originality_axes, "originality_axes")
        _require_text_tuple(self.anti_goals, "anti_goals")
        _require_text_tuple(
            self.creative_latitude,
            "creative_latitude",
        )
        _require_text(self.source_rights_policy, "source_rights_policy")
        if not _SHA256_RE.fullmatch(self.premise_distance_receipt_sha256):
            raise ValueError(
                "premise_distance_receipt_sha256 must be a lowercase SHA-256"
            )
        _require_text_tuple(
            self.original_contributions,
            "original_contributions",
        )


@dataclass(frozen=True, slots=True)
class CanonicalPackage:
    work_id: str
    canonical_id: str
    revision: int
    target_and_platform_hypothesis: str
    premise: str
    core_characters: tuple[CoreCharacterContract, ...]
    audience_information: AudienceInformationContract
    primary_reward: str
    payoff_layers: tuple[PayoffLayer, ...]
    ending_direction: str
    initial_relation_facts: tuple[str, ...]
    forbidden_contradictions: tuple[str, ...]
    world_constraints: tuple[str, ...]
    production_constraints: ProductionConstraints
    reward_hierarchy: tuple[RendererKind, ...]
    allowed_renderers: tuple[RendererKind, ...]
    originality: OriginalityContract
    source_fact_ledger_sha256: str
    source_genre_grammar_sha256: str

    def __post_init__(self) -> None:
        for field_name in (
            "work_id",
            "canonical_id",
            "target_and_platform_hypothesis",
            "premise",
            "primary_reward",
            "ending_direction",
        ):
            _require_text(getattr(self, field_name), field_name)
        if self.revision < 1:
            raise ValueError("revision must be positive")
        if not 1 <= len(self.core_characters) <= 3:
            raise ValueError("HIL 1 requires between one and three core characters")
        character_ids = [
            character.character_id for character in self.core_characters
        ]
        if len(character_ids) != len(set(character_ids)):
            raise ValueError("core character ids must be unique")
        if any(
            not isinstance(character, CoreCharacterContract)
            for character in self.core_characters
        ):
            raise TypeError(
                "core_characters values must be CoreCharacterContract"
            )
        if not self.payoff_layers:
            raise ValueError("payoff_layers must not be empty")
        if any(
            not isinstance(layer, PayoffLayer) for layer in self.payoff_layers
        ):
            raise TypeError("payoff_layers values must be PayoffLayer")
        payoff_ids = [layer.payoff_id for layer in self.payoff_layers]
        if len(payoff_ids) != len(set(payoff_ids)):
            raise ValueError("payoff layer ids must be unique")
        if self.primary_reward not in payoff_ids:
            raise ValueError("primary_reward must identify a payoff layer")
        if not any(
            layer.cadence is PayoffCadence.EPISODE
            for layer in self.payoff_layers
        ):
            raise ValueError("HIL 1 requires an episode-cadence payoff")
        if not isinstance(self.production_constraints, ProductionConstraints):
            raise TypeError(
                "production_constraints must be ProductionConstraints"
            )
        for field_name in (
            "initial_relation_facts",
            "forbidden_contradictions",
            "world_constraints",
        ):
            _require_text_tuple(getattr(self, field_name), field_name)
        if len(self.allowed_renderers) < 2:
            raise ValueError("HIL 1 must preserve a range of at least two renderers")
        if len(self.allowed_renderers) != len(set(self.allowed_renderers)):
            raise ValueError("allowed_renderers must be unique")
        if any(
            not isinstance(renderer, RendererKind)
            for renderer in self.allowed_renderers
        ):
            raise TypeError("allowed_renderers values must be RendererKind")
        if not self.reward_hierarchy:
            raise ValueError("reward_hierarchy must not be empty")
        if len(self.reward_hierarchy) != len(set(self.reward_hierarchy)):
            raise ValueError("reward_hierarchy must be unique")
        if any(
            not isinstance(renderer, RendererKind) for renderer in self.reward_hierarchy
        ):
            raise TypeError("reward_hierarchy values must be RendererKind")
        if not set(self.reward_hierarchy).issubset(self.allowed_renderers):
            raise ValueError("reward_hierarchy must be within allowed_renderers")
        for field_name in (
            "source_fact_ledger_sha256",
            "source_genre_grammar_sha256",
        ):
            if not _SHA256_RE.fullmatch(getattr(self, field_name)):
                raise ValueError(f"{field_name} must be a lowercase SHA-256")

    @property
    def artifact_id(self) -> str:
        return self.canonical_id

    @property
    def protagonist(self) -> CoreCharacterContract:
        """Compatibility view for older single-lead consumers."""

        return self.core_characters[0]

    @property
    def payoff_promises(self) -> tuple[str, ...]:
        """Compatibility view of layered promises without cadence metadata."""

        return tuple(layer.promise for layer in self.payoff_layers)

    @property
    def content_sha256(self) -> str:
        return canonical_sha256(self)
