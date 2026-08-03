"""Hash-bound camera and edit recommendations anchored outside story canon."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

from .canonical import canonical_sha256
from .episode_script_text import EpisodeScriptText
from .production_surface import HumanProductionSurface


_SHA256_RE = re.compile(r"[0-9a-f]{64}")


class ProductionAnnotationKind(StrEnum):
    CAMERA = "camera"
    SHOT = "shot"
    INSERT = "insert"
    EDIT = "edit"


class ProductionAnnotationStatus(StrEnum):
    CANDIDATE = "candidate_annotation"
    REVIEWED = "reviewed_annotation"
    STALE = "stale"


@dataclass(frozen=True, slots=True)
class ProductionAnnotation:
    annotation_id: str
    kind: ProductionAnnotationKind
    anchor_atom_id: str
    intent: str
    instruction: str
    required: bool = False
    reviewer_role: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "annotation_id",
            "anchor_atom_id",
            "intent",
            "instruction",
        ):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must not be empty")
        if not isinstance(self.kind, ProductionAnnotationKind):
            raise TypeError("kind must be a ProductionAnnotationKind")
        if self.reviewer_role is not None and not self.reviewer_role.strip():
            raise ValueError("reviewer_role must not be blank")


@dataclass(frozen=True, slots=True)
class ProductionAnnotationSet:
    annotation_set_id: str
    source_episode_text_sha256: str
    source_surface_sha256: str
    status: ProductionAnnotationStatus
    annotations: tuple[ProductionAnnotation, ...]

    def __post_init__(self) -> None:
        if not self.annotation_set_id.strip():
            raise ValueError("annotation_set_id must not be empty")
        for field_name in (
            "source_episode_text_sha256",
            "source_surface_sha256",
        ):
            if not _SHA256_RE.fullmatch(getattr(self, field_name)):
                raise ValueError(f"{field_name} must be a lowercase SHA-256")
        if not isinstance(self.status, ProductionAnnotationStatus):
            raise TypeError("status must be a ProductionAnnotationStatus")
        if not self.annotations:
            raise ValueError("annotation set requires at least one annotation")
        annotation_ids = [item.annotation_id for item in self.annotations]
        if len(annotation_ids) != len(set(annotation_ids)):
            raise ValueError("annotation ids must be unique")

    @property
    def content_sha256(self) -> str:
        return canonical_sha256(
            {
                "annotation_set_id": self.annotation_set_id,
                "source_episode_text_sha256": self.source_episode_text_sha256,
                "source_surface_sha256": self.source_surface_sha256,
                "annotations": self.annotations,
            }
        )


@dataclass(frozen=True, slots=True)
class AnnotationFinding:
    code: str
    location: str
    message: str


@dataclass(frozen=True, slots=True)
class AnnotationVerificationReport:
    annotation_set_id: str
    findings: tuple[AnnotationFinding, ...]

    @property
    def passed(self) -> bool:
        return not self.findings


class ProductionAnnotationVerifier:
    def verify(
        self,
        annotation_set: ProductionAnnotationSet,
        source: EpisodeScriptText,
        surface: HumanProductionSurface,
    ) -> AnnotationVerificationReport:
        findings: list[AnnotationFinding] = []

        def hard(code: str, location: str, message: str) -> None:
            findings.append(AnnotationFinding(code, location, message))

        if annotation_set.source_episode_text_sha256 != source.content_sha256:
            hard(
                "SOURCE_TEXT_HASH_MISMATCH",
                "source_episode_text_sha256",
                "annotations must bind the exact episode text",
            )
        if annotation_set.source_surface_sha256 != surface.content_sha256:
            hard(
                "SOURCE_SURFACE_HASH_MISMATCH",
                "source_surface_sha256",
                "annotations must bind the exact production surface",
            )
        valid_atom_ids = {atom.atom_id for atom in source.atoms}
        for annotation in annotation_set.annotations:
            if annotation.anchor_atom_id not in valid_atom_ids:
                hard(
                    "UNKNOWN_ATOM_ANCHOR",
                    annotation.annotation_id,
                    "annotation anchor must exist in the source episode text",
                )
            if annotation.required and annotation.reviewer_role is None:
                hard(
                    "REQUIRED_WITHOUT_REVIEWER_ROLE",
                    annotation.annotation_id,
                    "required direction needs an explicit production reviewer role",
                )
        if annotation_set.status is ProductionAnnotationStatus.REVIEWED:
            for annotation in annotation_set.annotations:
                if annotation.reviewer_role is None:
                    hard(
                        "REVIEWED_SET_WITH_UNREVIEWED_ITEM",
                        annotation.annotation_id,
                        "reviewed annotation sets require reviewer roles on every item",
                    )
        if annotation_set.status is ProductionAnnotationStatus.STALE:
            hard("STALE_ANNOTATION_SET", "status", "stale annotations cannot pass")
        return AnnotationVerificationReport(
            annotation_set.annotation_set_id,
            tuple(findings),
        )
