"""HIL 2 dynamic state-transition arc contracts and revision proposals."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

from .beat_patterns import BeatPatternKind, validate_pattern_choice
from .canonical import canonical_sha256
from .canonical_package import CanonicalPackage
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


class StoryStateAxis(StrEnum):
    KNOWLEDGE = "knowledge"
    AUDIENCE_KNOWLEDGE = "audience_knowledge"
    RELATION = "relation"
    STATUS = "status"
    BELONGING = "belonging"
    SAFETY = "safety"
    PROOF_OR_EQUIVALENT = "proof_or_equivalent"


@dataclass(frozen=True, slots=True)
class StoryStateEntry:
    axis: StoryStateAxis
    subject_id: str
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.axis, StoryStateAxis):
            raise TypeError("axis must be a StoryStateAxis")
        _require_text(self.subject_id, "subject_id")
        _require_text(self.value, "value")


@dataclass(frozen=True, slots=True)
class StoryState:
    entries: tuple[StoryStateEntry, ...]
    open_questions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.entries:
            raise ValueError("story state entries must not be empty")
        keys = [(entry.axis, entry.subject_id) for entry in self.entries]
        if len(keys) != len(set(keys)):
            raise ValueError("story state axis and subject pairs must be unique")
        if any(not question.strip() for question in self.open_questions):
            raise ValueError("open questions must not be empty")
        if len(self.open_questions) != len(set(self.open_questions)):
            raise ValueError("open questions must be unique")


@dataclass(frozen=True, slots=True)
class AttemptBlockerMove:
    attempt: str
    blocker: str
    consequence: str

    def __post_init__(self) -> None:
        _require_text(self.attempt, "attempt")
        _require_text(self.blocker, "blocker")
        _require_text(self.consequence, "consequence")


@dataclass(frozen=True, slots=True)
class ArcAcceptanceCriterion:
    criterion_id: str
    description: str

    def __post_init__(self) -> None:
        _require_text(self.criterion_id, "criterion_id")
        _require_text(self.description, "description")


@dataclass(frozen=True, slots=True)
class ArcContract:
    work_id: str
    arc_id: str
    revision: int
    parent_canonical_content_sha256: str
    parent_canonical_approval_receipt_sha256: str
    state_before: StoryState
    state_after: StoryState
    dramatic_question: str
    core_pressure: str
    core_choice: str
    consequence: str
    attempt_blocker_chain: tuple[AttemptBlockerMove, ...]
    rewards_paid: tuple[str, ...]
    rewards_deferred: tuple[str, ...]
    irreversible_change: str
    acceptance_criteria: tuple[ArcAcceptanceCriterion, ...]
    episode_count_min: int
    episode_count_max: int
    continuity_invariants: tuple[str, ...]
    renderer_mix: tuple[RendererKind, ...]
    allowed_beat_patterns: tuple[BeatPatternKind, ...]
    original_contributions: tuple[str, ...]
    causal_chain_distance_receipt_sha256: str

    def __post_init__(self) -> None:
        for field_name in (
            "work_id",
            "arc_id",
            "dramatic_question",
            "core_pressure",
            "core_choice",
            "consequence",
            "irreversible_change",
        ):
            _require_text(getattr(self, field_name), field_name)
        if self.revision < 1:
            raise ValueError("revision must be positive")
        for field_name in (
            "parent_canonical_content_sha256",
            "parent_canonical_approval_receipt_sha256",
            "causal_chain_distance_receipt_sha256",
        ):
            if not _SHA256_RE.fullmatch(getattr(self, field_name)):
                raise ValueError(f"{field_name} must be a lowercase SHA-256")
        if self.state_before == self.state_after:
            raise ValueError("arc state_after must differ from state_before")
        if not self.rewards_paid and not self.rewards_deferred:
            raise ValueError("arc must pay or explicitly defer a reward")
        _require_text_tuple(
            self.continuity_invariants,
            "continuity_invariants",
        )
        _require_text_tuple(
            self.original_contributions,
            "original_contributions",
        )
        if not self.acceptance_criteria:
            raise ValueError("acceptance_criteria must not be empty")
        criterion_ids = [
            criterion.criterion_id for criterion in self.acceptance_criteria
        ]
        if len(criterion_ids) != len(set(criterion_ids)):
            raise ValueError("acceptance criterion ids must be unique")
        if self.episode_count_min < 1:
            raise ValueError("episode_count_min must be positive")
        if self.episode_count_max < self.episode_count_min:
            raise ValueError("episode_count_max must be at least episode_count_min")
        if not self.renderer_mix:
            raise ValueError("renderer_mix must not be empty")
        if len(self.renderer_mix) != len(set(self.renderer_mix)):
            raise ValueError("renderer_mix must be unique")
        if any(
            not isinstance(renderer, RendererKind) for renderer in self.renderer_mix
        ):
            raise TypeError("renderer_mix values must be RendererKind")
        if not self.allowed_beat_patterns:
            raise ValueError("allowed_beat_patterns must not be empty")
        if len(self.allowed_beat_patterns) != len(set(self.allowed_beat_patterns)):
            raise ValueError("allowed_beat_patterns must be unique")
        for pattern in self.allowed_beat_patterns:
            if not isinstance(pattern, BeatPatternKind):
                raise TypeError("allowed_beat_patterns values must be BeatPatternKind")
            validate_pattern_choice(pattern, self.renderer_mix)

    @property
    def artifact_id(self) -> str:
        return self.arc_id

    @property
    def content_sha256(self) -> str:
        return canonical_sha256(self)


@dataclass(frozen=True, slots=True)
class ArcRevisionProposal:
    work_id: str
    arc_id: str
    proposed_revision: int
    parent_arc_content_sha256: str
    reason: str
    affected_nodes: tuple[str, ...]
    continuity_risks: tuple[str, ...]
    reward_impact: str
    closure_or_cliff_impact: str

    def __post_init__(self) -> None:
        for field_name in (
            "work_id",
            "arc_id",
            "reason",
            "reward_impact",
            "closure_or_cliff_impact",
        ):
            _require_text(getattr(self, field_name), field_name)
        if self.proposed_revision < 2:
            raise ValueError("proposed_revision must be at least two")
        if not _SHA256_RE.fullmatch(self.parent_arc_content_sha256):
            raise ValueError("parent_arc_content_sha256 must be a lowercase SHA-256")
        _require_text_tuple(self.affected_nodes, "affected_nodes")
        _require_text_tuple(self.continuity_risks, "continuity_risks")

    @property
    def content_sha256(self) -> str:
        return canonical_sha256(self)


@dataclass(frozen=True, slots=True)
class ArcFinding:
    code: str
    location: str
    message: str


@dataclass(frozen=True, slots=True)
class ArcVerificationReport:
    arc_id: str
    findings: tuple[ArcFinding, ...]

    @property
    def passed(self) -> bool:
        return not self.findings


class ArcContractVerifier:
    def verify(
        self,
        contract: ArcContract,
        canonical: CanonicalPackage,
    ) -> ArcVerificationReport:
        findings: list[ArcFinding] = []

        def hard(code: str, location: str, message: str) -> None:
            findings.append(ArcFinding(code, location, message))

        if contract.work_id != canonical.work_id:
            hard(
                "WORK_BINDING_MISMATCH",
                "work_id",
                "arc and canonical package must belong to the same work",
            )
        if contract.parent_canonical_content_sha256 != canonical.content_sha256:
            hard(
                "CANONICAL_HASH_MISMATCH",
                "parent_canonical_content_sha256",
                "arc must bind the exact canonical package",
            )
        disallowed_renderers = set(contract.renderer_mix) - set(
            canonical.allowed_renderers
        )
        if disallowed_renderers:
            hard(
                "RENDERER_OUTSIDE_CANONICAL_RANGE",
                "renderer_mix",
                "arc renderer mix must stay within the HIL 1 range",
            )
        if not set(contract.renderer_mix).intersection(canonical.reward_hierarchy):
            hard(
                "REWARD_HIERARCHY_NOT_REALIZED",
                "renderer_mix",
                "arc must realize at least one HIL 1 reward priority",
            )
        if (
            contract.episode_count_min == contract.episode_count_max
            and contract.episode_count_min > 1
        ):
            hard(
                "FIXED_EPISODE_COUNT",
                "episode_count_min",
                "multi-episode arcs must preserve an episode count band",
            )
        return ArcVerificationReport(
            arc_id=contract.arc_id,
            findings=tuple(findings),
        )
