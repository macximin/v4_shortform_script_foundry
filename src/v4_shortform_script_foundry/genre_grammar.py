"""Versioned genre grammar packets accepted by the renderer router."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

from .canonical import canonical_sha256


class GrammarStatus(StrEnum):
    CANDIDATE = "candidate"
    APPROVED = "approved"
    REJECTED = "rejected"


class RendererKind(StrEnum):
    RESOURCE = "resource"
    COMPETENCE = "competence"
    STATUS = "status"
    SCARCITY = "scarcity"
    SELECTION = "selection"
    ATTACHMENT_SAFETY = "attachment_safety"
    SOCIAL_RECOGNITION = "social_recognition"
    NORM = "norm"


@dataclass(frozen=True, slots=True)
class RendererPreference:
    renderer: RendererKind
    weight: int
    threat: str
    proof_mode: str
    reward_target: str
    required_fact_tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.renderer, RendererKind):
            raise TypeError("renderer must be a RendererKind")
        if not 1 <= self.weight <= 100:
            raise ValueError("renderer weight must be between 1 and 100")
        for field_name in ("threat", "proof_mode", "reward_target"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must not be empty")
        if any(not tag.strip() for tag in self.required_fact_tags):
            raise ValueError("required fact tags must not be empty")
        if len(self.required_fact_tags) != len(set(self.required_fact_tags)):
            raise ValueError("required fact tags must be unique")


@dataclass(frozen=True, slots=True)
class GenreGrammarPacket:
    grammar_id: str
    version: str
    target_profile: str
    entry_pressure: str
    primary_reward: str
    preferences: tuple[RendererPreference, ...]
    evidence_ids: tuple[str, ...]
    status: GrammarStatus = GrammarStatus.CANDIDATE
    owner_approval_sha256: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.status, GrammarStatus):
            raise TypeError("status must be a GrammarStatus")
        for field_name in (
            "grammar_id",
            "version",
            "target_profile",
            "entry_pressure",
            "primary_reward",
        ):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must not be empty")
        if not self.preferences:
            raise ValueError("at least one renderer preference is required")
        renderers = [preference.renderer for preference in self.preferences]
        if len(renderers) != len(set(renderers)):
            raise ValueError("renderer preferences must be unique")
        if self.status is GrammarStatus.APPROVED:
            if not self.evidence_ids:
                raise ValueError("approved grammar requires evidence ids")
            if not self.owner_approval_sha256 or not re.fullmatch(
                r"[0-9a-f]{64}", self.owner_approval_sha256
            ):
                raise ValueError(
                    "approved grammar requires a lowercase SHA-256 approval hash"
                )
            if self.owner_approval_sha256 != self.content_sha256:
                raise ValueError(
                    "approved grammar hash must equal the canonical content hash"
                )

    @property
    def packet_id(self) -> str:
        return f"{self.grammar_id}@{self.version}"

    @property
    def approval_payload(self) -> dict[str, object]:
        return {
            "grammar_id": self.grammar_id,
            "version": self.version,
            "target_profile": self.target_profile,
            "entry_pressure": self.entry_pressure,
            "primary_reward": self.primary_reward,
            "preferences": self.preferences,
            "evidence_ids": self.evidence_ids,
        }

    @property
    def content_sha256(self) -> str:
        return canonical_sha256(self.approval_payload)

    def preference_for(self, renderer: RendererKind) -> RendererPreference:
        for preference in self.preferences:
            if preference.renderer is renderer:
                return preference
        raise KeyError(renderer)
