"""HIL 3 finished episode-script candidate and hard-contract verification."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

from .arc_contract import ArcContract
from .beat_patterns import BeatPatternKind, validate_pattern_choice
from .canonical import canonical_sha256
from .genre_grammar import RendererKind


_SHA256_RE = re.compile(r"[0-9a-f]{64}")


def _require_text(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")


class EpisodeScriptStatus(StrEnum):
    CANDIDATE = "candidate"
    APPROVED = "approved"


class CausalRole(StrEnum):
    MEANINGFUL_CHOICE = "meaningful_choice"
    MEANINGFUL_ACTION = "meaningful_action"
    PRIOR_CHOICE_CONSEQUENCE = "prior_choice_consequence"
    EXTERNAL_PRESSURE_CONSEQUENCE = "external_pressure_consequence"


class EpisodeObligationKind(StrEnum):
    CONTINUATION = "continuation"
    CLOSURE = "closure"


@dataclass(frozen=True, slots=True)
class DialogueLine:
    speaker_id: str
    text: str
    function: str

    def __post_init__(self) -> None:
        _require_text(self.speaker_id, "speaker_id")
        _require_text(self.text, "text")
        _require_text(self.function, "function")


@dataclass(frozen=True, slots=True)
class EpisodeScene:
    scene_id: str
    location: str
    purpose: str
    observable_action: str
    causal_role: CausalRole
    renderer_primary: RendererKind
    renderer_secondary: tuple[RendererKind, ...]
    duration_seconds: int
    dialogue: tuple[DialogueLine, ...]
    information_revealed_ids: tuple[str, ...]
    information_withheld_ids: tuple[str, ...]
    state_delta_codes: tuple[str, ...]
    tension_delta: str

    def __post_init__(self) -> None:
        for field_name in (
            "scene_id",
            "location",
            "purpose",
            "observable_action",
            "tension_delta",
        ):
            _require_text(getattr(self, field_name), field_name)
        if not isinstance(self.causal_role, CausalRole):
            raise TypeError("causal_role must be a CausalRole")
        if not isinstance(self.renderer_primary, RendererKind):
            raise TypeError("renderer_primary must be a RendererKind")
        if any(
            not isinstance(renderer, RendererKind)
            for renderer in self.renderer_secondary
        ):
            raise TypeError("renderer_secondary values must be RendererKind")
        if self.renderer_primary in self.renderer_secondary:
            raise ValueError("renderer_secondary must not repeat renderer_primary")
        if len(self.renderer_secondary) != len(set(self.renderer_secondary)):
            raise ValueError("renderer_secondary must be unique")
        if self.duration_seconds < 1:
            raise ValueError("scene duration must be positive")
        for field_name in (
            "information_revealed_ids",
            "information_withheld_ids",
            "state_delta_codes",
        ):
            values = getattr(self, field_name)
            if any(not value.strip() for value in values):
                raise ValueError(f"{field_name} values must not be empty")
            if len(values) != len(set(values)):
                raise ValueError(f"{field_name} values must be unique")
        if set(self.information_revealed_ids).intersection(
            self.information_withheld_ids
        ):
            raise ValueError("the same information cannot be revealed and withheld")


@dataclass(frozen=True, slots=True)
class EpisodeScriptCandidate:
    work_id: str
    arc_id: str
    episode_id: str
    revision: int
    producer_id: str
    status: EpisodeScriptStatus
    parent_arc_content_sha256: str
    parent_arc_approval_receipt_sha256: str
    source_scaffold_sha256: str
    source_distance_receipt_sha256: str
    target_runtime_seconds: int
    beat_pattern: BeatPatternKind
    scenes: tuple[EpisodeScene, ...]
    final_state_delta_codes: tuple[str, ...]
    rewards_paid: tuple[str, ...]
    rewards_deferred: tuple[str, ...]
    obligation_kind: EpisodeObligationKind
    obligation: str
    original_contributions: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "work_id",
            "arc_id",
            "episode_id",
            "producer_id",
            "obligation",
        ):
            _require_text(getattr(self, field_name), field_name)
        if self.revision < 1:
            raise ValueError("revision must be positive")
        if not isinstance(self.status, EpisodeScriptStatus):
            raise TypeError("status must be an EpisodeScriptStatus")
        if not isinstance(self.beat_pattern, BeatPatternKind):
            raise TypeError("beat_pattern must be a BeatPatternKind")
        if not isinstance(self.obligation_kind, EpisodeObligationKind):
            raise TypeError("obligation_kind must be an EpisodeObligationKind")
        for field_name in (
            "parent_arc_content_sha256",
            "parent_arc_approval_receipt_sha256",
            "source_scaffold_sha256",
            "source_distance_receipt_sha256",
        ):
            if not _SHA256_RE.fullmatch(getattr(self, field_name)):
                raise ValueError(f"{field_name} must be a lowercase SHA-256")
        if not 40 <= self.target_runtime_seconds <= 300:
            raise ValueError("target runtime must be between 40 and 300 seconds")
        if not self.scenes:
            raise ValueError("finished scripts require at least one scene")
        scene_ids = [scene.scene_id for scene in self.scenes]
        if len(scene_ids) != len(set(scene_ids)):
            raise ValueError("scene ids must be unique")
        if self.runtime_seconds != self.target_runtime_seconds:
            raise ValueError("scene runtime must equal target_runtime_seconds")
        for field_name in (
            "final_state_delta_codes",
            "original_contributions",
        ):
            values = getattr(self, field_name)
            if not values:
                raise ValueError(f"{field_name} must not be empty")
            if any(not value.strip() for value in values):
                raise ValueError(f"{field_name} values must not be empty")
            if len(values) != len(set(values)):
                raise ValueError(f"{field_name} values must be unique")
        if not self.rewards_paid and not self.rewards_deferred:
            raise ValueError("episode must pay or explicitly defer a reward")

    @property
    def runtime_seconds(self) -> int:
        return sum(scene.duration_seconds for scene in self.scenes)

    @property
    def artifact_id(self) -> str:
        return self.episode_id

    @property
    def content_sha256(self) -> str:
        return canonical_sha256(self)

    @property
    def structure_sha256(self) -> str:
        return canonical_sha256(
            {
                "beat_pattern": self.beat_pattern,
                "obligation_kind": self.obligation_kind,
                "scenes": tuple(
                    {
                        "purpose": scene.purpose,
                        "causal_role": scene.causal_role,
                        "renderer_primary": scene.renderer_primary,
                        "renderer_secondary": scene.renderer_secondary,
                        "duration_seconds": scene.duration_seconds,
                        "state_delta_codes": scene.state_delta_codes,
                    }
                    for scene in self.scenes
                ),
            }
        )


@dataclass(frozen=True, slots=True)
class EpisodeScriptFinding:
    code: str
    location: str
    message: str


@dataclass(frozen=True, slots=True)
class EpisodeScriptVerificationReport:
    episode_id: str
    findings: tuple[EpisodeScriptFinding, ...]

    @property
    def passed(self) -> bool:
        return not self.findings


class EpisodeScriptVerifier:
    def verify(
        self,
        script: EpisodeScriptCandidate,
        arc: ArcContract,
    ) -> EpisodeScriptVerificationReport:
        findings: list[EpisodeScriptFinding] = []

        def hard(code: str, location: str, message: str) -> None:
            findings.append(EpisodeScriptFinding(code, location, message))

        if script.status is not EpisodeScriptStatus.CANDIDATE:
            hard(
                "AUTO_PROMOTION_FORBIDDEN",
                "status",
                "generated scripts must remain candidates",
            )
        if script.work_id != arc.work_id or script.arc_id != arc.arc_id:
            hard(
                "ARC_BINDING_MISMATCH",
                "arc_id",
                "episode script must bind the exact work and arc",
            )
        if script.parent_arc_content_sha256 != arc.content_sha256:
            hard(
                "ARC_HASH_MISMATCH",
                "parent_arc_content_sha256",
                "episode script must bind the exact Arc Contract",
            )
        if script.beat_pattern not in arc.allowed_beat_patterns:
            hard(
                "BEAT_PATTERN_OUTSIDE_ARC",
                "beat_pattern",
                "episode beat pattern must be allowed by the Arc Contract",
            )

        active_renderers = tuple(
            dict.fromkeys(
                renderer
                for scene in script.scenes
                for renderer in (
                    scene.renderer_primary,
                    *scene.renderer_secondary,
                )
            )
        )
        disallowed_renderers = set(active_renderers) - set(arc.renderer_mix)
        if disallowed_renderers:
            hard(
                "RENDERER_OUTSIDE_ARC_MIX",
                "scenes",
                "scene renderers must stay within the Arc Contract mix",
            )
        try:
            validate_pattern_choice(
                script.beat_pattern,
                active_renderers,
            )
        except ValueError as error:
            hard(
                "BEAT_PATTERN_RENDERER_MISMATCH",
                "beat_pattern",
                str(error),
            )

        if not any(scene.state_delta_codes for scene in script.scenes):
            hard(
                "MISSING_OBSERVABLE_STATE_DELTA",
                "scenes",
                "at least one scene must carry an observable state delta",
            )
        if not any(
            scene.causal_role
            in {
                CausalRole.MEANINGFUL_CHOICE,
                CausalRole.MEANINGFUL_ACTION,
                CausalRole.PRIOR_CHOICE_CONSEQUENCE,
                CausalRole.EXTERNAL_PRESSURE_CONSEQUENCE,
            }
            for scene in script.scenes
        ):
            hard(
                "MISSING_CAUSAL_FUNCTION",
                "scenes",
                "episode must contain choice, action, or causal consequence",
            )
        if not set(script.rewards_paid).issubset(
            set(arc.rewards_paid).union(arc.rewards_deferred)
        ):
            hard(
                "UNPLANNED_REWARD_PAYMENT",
                "rewards_paid",
                "paid rewards must be authorized by the Arc Contract",
            )
        if not set(script.rewards_deferred).issubset(
            set(arc.rewards_paid).union(arc.rewards_deferred)
        ):
            hard(
                "UNPLANNED_REWARD_DEFERRAL",
                "rewards_deferred",
                "deferred rewards must be authorized by the Arc Contract",
            )
        if (
            script.obligation_kind is EpisodeObligationKind.CLOSURE
            and script.rewards_deferred
        ):
            hard(
                "CLOSURE_DEFERS_REWARD",
                "rewards_deferred",
                "closure episodes cannot silently defer rewards",
            )
        return EpisodeScriptVerificationReport(
            episode_id=script.episode_id,
            findings=tuple(findings),
        )
