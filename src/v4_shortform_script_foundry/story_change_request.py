"""Explicit route from production review back to a new HIL 3 revision."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

from .canonical import canonical_sha256
from .episode_script_text import EpisodeScriptText


_SHA256_RE = re.compile(r"[0-9a-f]{64}")


class StoryChangeType(StrEnum):
    DIALOGUE = "dialogue"
    ACTION = "action"
    ORDER = "order"
    CONTINUITY = "continuity"


class StoryChangeDecision(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class StoryChangeRequest:
    request_id: str
    source_episode_text_sha256: str
    affected_atom_ids: tuple[str, ...]
    change_type: StoryChangeType
    before: str
    after: str
    reason: str
    owner_decision: StoryChangeDecision = StoryChangeDecision.PENDING

    def __post_init__(self) -> None:
        for field_name in ("request_id", "before", "after", "reason"):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must not be empty")
        if not _SHA256_RE.fullmatch(self.source_episode_text_sha256):
            raise ValueError("source_episode_text_sha256 must be a lowercase SHA-256")
        if not self.affected_atom_ids:
            raise ValueError("affected_atom_ids must not be empty")
        if len(self.affected_atom_ids) != len(set(self.affected_atom_ids)):
            raise ValueError("affected_atom_ids must be unique")
        if not isinstance(self.change_type, StoryChangeType):
            raise TypeError("change_type must be a StoryChangeType")
        if not isinstance(self.owner_decision, StoryChangeDecision):
            raise TypeError("owner_decision must be a StoryChangeDecision")
        if self.before == self.after:
            raise ValueError("before and after must differ")

    @property
    def content_sha256(self) -> str:
        return canonical_sha256(
            {
                "request_id": self.request_id,
                "source_episode_text_sha256": self.source_episode_text_sha256,
                "affected_atom_ids": self.affected_atom_ids,
                "change_type": self.change_type,
                "before": self.before,
                "after": self.after,
                "reason": self.reason,
            }
        )

    @property
    def can_create_revision(self) -> bool:
        return self.owner_decision is StoryChangeDecision.APPROVED


@dataclass(frozen=True, slots=True)
class StoryChangeFinding:
    code: str
    location: str
    message: str


@dataclass(frozen=True, slots=True)
class StoryChangeVerificationReport:
    request_id: str
    findings: tuple[StoryChangeFinding, ...]

    @property
    def passed(self) -> bool:
        return not self.findings


class StoryChangeRequestVerifier:
    def verify(
        self,
        request: StoryChangeRequest,
        source: EpisodeScriptText,
    ) -> StoryChangeVerificationReport:
        findings: list[StoryChangeFinding] = []

        def hard(code: str, location: str, message: str) -> None:
            findings.append(StoryChangeFinding(code, location, message))

        if request.source_episode_text_sha256 != source.content_sha256:
            hard(
                "SOURCE_TEXT_HASH_MISMATCH",
                "source_episode_text_sha256",
                "change request must bind the exact story revision",
            )
        source_ids = {atom.atom_id for atom in source.atoms}
        unknown_ids = set(request.affected_atom_ids) - source_ids
        if unknown_ids:
            hard(
                "UNKNOWN_AFFECTED_ATOM",
                "affected_atom_ids",
                "every affected atom must exist in the source revision",
            )
        source_text = "\n".join(
            source.atom(atom_id).text
            for atom_id in request.affected_atom_ids
            if atom_id in source_ids
        )
        if request.before != source_text:
            hard(
                "BEFORE_TEXT_MISMATCH",
                "before",
                "before text must exactly match the affected source atoms",
            )
        return StoryChangeVerificationReport(request.request_id, tuple(findings))
