"""Pluggable structured-output adapter for Creative Writer backends."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import unicodedata
from typing import Mapping, Protocol, Sequence

from .approval import ApprovalReceipt, HilGate, ReviewDecision
from .arc_contract import ArcContract, ArcContractVerifier
from .beat_patterns import BeatPatternKind, pattern_spec
from .canonical import canonical_sha256
from .canonical_package import CanonicalPackage
from .episode_script import (
    CausalRole,
    DialogueLine,
    EpisodeObligationKind,
    EpisodeScene,
    EpisodeScriptCandidate,
    EpisodeScriptStatus,
    EpisodeScriptVerifier,
)
from .genre_grammar import RendererKind


def _normalize_text(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def _require_exact_keys(
    value: Mapping[str, object],
    expected: frozenset[str],
    location: str,
) -> None:
    actual = frozenset(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(
            f"{location} keys mismatch; missing={missing}, extra={extra}"
        )


def _require_str(value: object, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{location} must be a non-empty string")
    return value


def _require_int(value: object, location: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{location} must be an integer")
    return value


def _require_sequence(value: object, location: str) -> Sequence[object]:
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{location} must be an array")
    return value


def _text_tuple(value: object, location: str) -> tuple[str, ...]:
    return tuple(
        _require_str(item, f"{location}[{index}]")
        for index, item in enumerate(_require_sequence(value, location))
    )


def _enum_value[T: Enum](
    enum_type: type[T],
    value: object,
    location: str,
) -> T:
    raw = _require_str(value, location)
    try:
        return enum_type(raw)
    except ValueError as error:
        raise ValueError(f"{location} has unsupported value {raw!r}") from error


@dataclass(frozen=True, slots=True)
class WriterRequest:
    candidate_id: str
    work_id: str
    arc_id: str
    episode_id: str
    revision: int
    producer_id: str
    canonical_content_sha256: str
    canonical_approval_receipt_sha256: str
    arc_content_sha256: str
    arc_approval_receipt_sha256: str
    source_scaffold_sha256: str
    target_runtime_seconds: int
    beat_pattern: BeatPatternKind
    beat_functions: tuple[str, ...]
    hard_invariants: tuple[str, ...]
    creative_latitude: tuple[str, ...]
    allowed_renderers: tuple[RendererKind, ...]
    core_character_ids: tuple[str, ...]
    max_principal_characters_per_scene: int
    action_driven: bool
    dialogue_policy: str
    max_dialogue_lines_per_scene: int | None
    dramatic_question: str
    core_pressure: str
    core_choice: str
    consequence: str
    rewards_paid: tuple[str, ...]
    rewards_deferred: tuple[str, ...]

    @classmethod
    def build(
        cls,
        *,
        canonical: CanonicalPackage,
        canonical_approval: ApprovalReceipt,
        arc: ArcContract,
        arc_approval: ApprovalReceipt,
        candidate_id: str,
        episode_id: str,
        revision: int,
        producer_id: str,
        source_scaffold_sha256: str,
        target_runtime_seconds: int,
        beat_pattern: BeatPatternKind,
    ) -> "WriterRequest":
        arc_report = ArcContractVerifier().verify(arc, canonical)
        if not arc_report.passed:
            raise ValueError("arc fails hard verification against canonical package")
        for receipt, gate, artifact_hash in (
            (
                canonical_approval,
                HilGate.HIL1_CANONICAL,
                canonical.content_sha256,
            ),
            (arc_approval, HilGate.HIL2_ARC, arc.content_sha256),
        ):
            if (
                receipt.gate_id is not gate
                or receipt.decision is not ReviewDecision.APPROVE
                or receipt.artifact_content_sha256 != artifact_hash
                or not receipt.verify()
            ):
                raise ValueError(f"{gate.value} requires an exact approval receipt")
        if arc.parent_canonical_approval_receipt_sha256 != (
            canonical_approval.receipt_sha256
        ):
            raise ValueError("arc does not bind the supplied canonical approval")
        if arc_approval.parent_approval_receipt_sha256s != (
            canonical_approval.receipt_sha256,
        ):
            raise ValueError("arc approval does not bind canonical approval")
        if beat_pattern not in arc.allowed_beat_patterns:
            raise ValueError("beat_pattern is outside the approved arc")
        if not candidate_id.strip() or not episode_id.strip() or not producer_id.strip():
            raise ValueError(
                "candidate_id, episode_id and producer_id must not be empty"
            )
        if revision < 1:
            raise ValueError("revision must be positive")
        constraints = canonical.production_constraints
        if not (
            constraints.target_runtime_seconds_min
            <= target_runtime_seconds
            <= constraints.target_runtime_seconds_max
        ):
            raise ValueError(
                "target_runtime_seconds is outside the HIL 1 production range"
            )
        return cls(
            candidate_id=candidate_id,
            work_id=canonical.work_id,
            arc_id=arc.arc_id,
            episode_id=episode_id,
            revision=revision,
            producer_id=producer_id,
            canonical_content_sha256=canonical.content_sha256,
            canonical_approval_receipt_sha256=(
                canonical_approval.receipt_sha256
            ),
            arc_content_sha256=arc.content_sha256,
            arc_approval_receipt_sha256=arc_approval.receipt_sha256,
            source_scaffold_sha256=source_scaffold_sha256,
            target_runtime_seconds=target_runtime_seconds,
            beat_pattern=beat_pattern,
            beat_functions=pattern_spec(beat_pattern).functions,
            hard_invariants=(
                *canonical.forbidden_contradictions,
                *canonical.world_constraints,
                *arc.continuity_invariants,
            ),
            creative_latitude=canonical.originality.creative_latitude,
            allowed_renderers=arc.renderer_mix,
            core_character_ids=tuple(
                character.character_id
                for character in canonical.core_characters
            ),
            max_principal_characters_per_scene=(
                canonical.production_constraints.max_principal_characters_per_scene
            ),
            action_driven=canonical.production_constraints.action_driven,
            dialogue_policy=canonical.production_constraints.dialogue_policy,
            max_dialogue_lines_per_scene=(
                canonical.production_constraints.max_dialogue_lines_per_scene
            ),
            dramatic_question=arc.dramatic_question,
            core_pressure=arc.core_pressure,
            core_choice=arc.core_choice,
            consequence=arc.consequence,
            rewards_paid=arc.rewards_paid,
            rewards_deferred=arc.rewards_deferred,
        )

    @property
    def content_sha256(self) -> str:
        return canonical_sha256(self)


@dataclass(frozen=True, slots=True)
class SourceDistanceProjection:
    candidate_id: str
    text: str
    event_sequence: tuple[str, ...]

    @property
    def projection_payload(self) -> dict[str, object]:
        return {
            "candidate_id": self.candidate_id,
            "text": _normalize_text(self.text),
            "event_sequence": self.event_sequence,
        }

    @property
    def projection_sha256(self) -> str:
        return canonical_sha256(self.projection_payload)


@dataclass(frozen=True, slots=True)
class WriterDraft:
    request: WriterRequest
    scenes: tuple[EpisodeScene, ...]
    final_state_delta_codes: tuple[str, ...]
    rewards_paid: tuple[str, ...]
    rewards_deferred: tuple[str, ...]
    obligation_kind: EpisodeObligationKind
    obligation: str
    original_contributions: tuple[str, ...]

    @property
    def content_sha256(self) -> str:
        return canonical_sha256(self)

    @property
    def source_distance_projection(self) -> SourceDistanceProjection:
        text_parts: list[str] = []
        event_sequence: list[str] = []
        for scene in self.scenes:
            text_parts.extend(
                (
                    scene.location,
                    scene.purpose,
                    scene.observable_action,
                    *(line.text for line in scene.dialogue),
                )
            )
            event_sequence.extend(
                (
                    scene.causal_role.value,
                    *scene.state_delta_codes,
                )
            )
        return SourceDistanceProjection(
            candidate_id=self.request.candidate_id,
            text="\n".join(text_parts),
            event_sequence=tuple(event_sequence),
        )

    def to_candidate(
        self,
        *,
        source_distance_receipt_sha256: str,
    ) -> EpisodeScriptCandidate:
        return EpisodeScriptCandidate(
            work_id=self.request.work_id,
            arc_id=self.request.arc_id,
            episode_id=self.request.episode_id,
            revision=self.request.revision,
            producer_id=self.request.producer_id,
            status=EpisodeScriptStatus.CANDIDATE,
            parent_arc_content_sha256=self.request.arc_content_sha256,
            parent_arc_approval_receipt_sha256=(
                self.request.arc_approval_receipt_sha256
            ),
            source_scaffold_sha256=self.request.source_scaffold_sha256,
            source_distance_receipt_sha256=source_distance_receipt_sha256,
            target_runtime_seconds=self.request.target_runtime_seconds,
            beat_pattern=self.request.beat_pattern,
            scenes=self.scenes,
            final_state_delta_codes=self.final_state_delta_codes,
            rewards_paid=self.rewards_paid,
            rewards_deferred=self.rewards_deferred,
            obligation_kind=self.obligation_kind,
            obligation=self.obligation,
            original_contributions=self.original_contributions,
        )


class WriterBackend(Protocol):
    backend_id: str

    def generate(self, request: WriterRequest) -> Mapping[str, object]:
        """Return schema-bound creative output. Network policy is backend-owned."""


class CreativeWriterAdapter:
    """Turns strict backend mappings into unscreened WriterDraft objects."""

    _OUTPUT_KEYS = frozenset(
        {
            "episode_id",
            "scenes",
            "final_state_delta_codes",
            "rewards_paid",
            "rewards_deferred",
            "obligation_kind",
            "obligation",
            "original_contributions",
        }
    )
    _SCENE_KEYS = frozenset(
        {
            "scene_id",
            "location",
            "purpose",
            "observable_action",
            "causal_role",
            "renderer_primary",
            "renderer_secondary",
            "principal_character_ids",
            "duration_seconds",
            "dialogue",
            "information_revealed_ids",
            "information_withheld_ids",
            "state_delta_codes",
            "tension_delta",
        }
    )
    _DIALOGUE_KEYS = frozenset({"speaker_id", "text", "function"})

    def generate(
        self,
        request: WriterRequest,
        backend: WriterBackend,
        arc: ArcContract,
    ) -> WriterDraft:
        if not backend.backend_id.strip():
            raise ValueError("writer backend_id must not be empty")
        if request.arc_content_sha256 != arc.content_sha256:
            raise ValueError("writer request does not bind the supplied arc")
        output = backend.generate(request)
        if not isinstance(output, Mapping):
            raise ValueError("writer backend output must be an object")
        _require_exact_keys(output, self._OUTPUT_KEYS, "output")
        if _require_str(output["episode_id"], "episode_id") != request.episode_id:
            raise ValueError("writer output episode_id does not match request")
        scenes = tuple(
            self._parse_scene(value, index)
            for index, value in enumerate(
                _require_sequence(output["scenes"], "scenes")
            )
        )
        draft = WriterDraft(
            request=request,
            scenes=scenes,
            final_state_delta_codes=_text_tuple(
                output["final_state_delta_codes"],
                "final_state_delta_codes",
            ),
            rewards_paid=_text_tuple(output["rewards_paid"], "rewards_paid"),
            rewards_deferred=_text_tuple(
                output["rewards_deferred"],
                "rewards_deferred",
            ),
            obligation_kind=_enum_value(
                EpisodeObligationKind,
                output["obligation_kind"],
                "obligation_kind",
            ),
            obligation=_require_str(output["obligation"], "obligation"),
            original_contributions=_text_tuple(
                output["original_contributions"],
                "original_contributions",
            ),
        )
        placeholder = draft.to_candidate(
            source_distance_receipt_sha256="0" * 64,
        )
        report = EpisodeScriptVerifier().verify(placeholder, arc)
        if not report.passed:
            codes = ", ".join(finding.code for finding in report.findings)
            raise ValueError(f"writer output failed hard verification: {codes}")
        return draft

    def _parse_scene(self, value: object, index: int) -> EpisodeScene:
        location = f"scenes[{index}]"
        if not isinstance(value, Mapping):
            raise ValueError(f"{location} must be an object")
        _require_exact_keys(value, self._SCENE_KEYS, location)
        dialogue = tuple(
            self._parse_dialogue(item, index, dialogue_index)
            for dialogue_index, item in enumerate(
                _require_sequence(value["dialogue"], f"{location}.dialogue")
            )
        )
        return EpisodeScene(
            scene_id=_require_str(value["scene_id"], f"{location}.scene_id"),
            location=_require_str(value["location"], f"{location}.location"),
            purpose=_require_str(value["purpose"], f"{location}.purpose"),
            observable_action=_require_str(
                value["observable_action"],
                f"{location}.observable_action",
            ),
            causal_role=_enum_value(
                CausalRole,
                value["causal_role"],
                f"{location}.causal_role",
            ),
            renderer_primary=_enum_value(
                RendererKind,
                value["renderer_primary"],
                f"{location}.renderer_primary",
            ),
            renderer_secondary=tuple(
                _enum_value(
                    RendererKind,
                    item,
                    f"{location}.renderer_secondary[{renderer_index}]",
                )
                for renderer_index, item in enumerate(
                    _require_sequence(
                        value["renderer_secondary"],
                        f"{location}.renderer_secondary",
                    )
                )
            ),
            principal_character_ids=_text_tuple(
                value["principal_character_ids"],
                f"{location}.principal_character_ids",
            ),
            duration_seconds=_require_int(
                value["duration_seconds"],
                f"{location}.duration_seconds",
            ),
            dialogue=dialogue,
            information_revealed_ids=_text_tuple(
                value["information_revealed_ids"],
                f"{location}.information_revealed_ids",
            ),
            information_withheld_ids=_text_tuple(
                value["information_withheld_ids"],
                f"{location}.information_withheld_ids",
            ),
            state_delta_codes=_text_tuple(
                value["state_delta_codes"],
                f"{location}.state_delta_codes",
            ),
            tension_delta=_require_str(
                value["tension_delta"],
                f"{location}.tension_delta",
            ),
        )

    def _parse_dialogue(
        self,
        value: object,
        scene_index: int,
        dialogue_index: int,
    ) -> DialogueLine:
        location = f"scenes[{scene_index}].dialogue[{dialogue_index}]"
        if not isinstance(value, Mapping):
            raise ValueError(f"{location} must be an object")
        _require_exact_keys(value, self._DIALOGUE_KEYS, location)
        return DialogueLine(
            speaker_id=_require_str(
                value["speaker_id"],
                f"{location}.speaker_id",
            ),
            text=_require_str(value["text"], f"{location}.text"),
            function=_require_str(
                value["function"],
                f"{location}.function",
            ),
        )
