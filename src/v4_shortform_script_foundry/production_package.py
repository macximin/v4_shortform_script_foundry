"""Candidate production-text handoff package for downstream visual work."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

from .canonical import canonical_sha256
from .episode_script_text import EpisodeScriptText, EpisodeScriptTextStatus
from .production_annotation import (
    ProductionAnnotationSet,
    ProductionAnnotationVerifier,
)
from .production_gate import (
    ProductionApprovalReceipt,
    ProductionGate,
    require_exact_approval,
)
from .production_surface import (
    HumanProductionSurface,
    ProductionSurfaceRenderer,
    ProductionSurfaceVerifier,
)


_SHA256_RE = re.compile(r"[0-9a-f]{64}")


class ProductionPackageStatus(StrEnum):
    CANDIDATE = "candidate_production_text_package"
    STALE = "stale"


@dataclass(frozen=True, slots=True)
class ProductionTextPackage:
    package_id: str
    source_episode_text_sha256: str
    surface_sha256: str
    annotation_set_sha256: str
    p0_receipt_sha256: str
    p1_receipt_sha256: str
    status: ProductionPackageStatus
    external_delivery_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.package_id.strip():
            raise ValueError("package_id must not be empty")
        for field_name in (
            "source_episode_text_sha256",
            "surface_sha256",
            "annotation_set_sha256",
            "p0_receipt_sha256",
            "p1_receipt_sha256",
        ):
            if not _SHA256_RE.fullmatch(getattr(self, field_name)):
                raise ValueError(f"{field_name} must be a lowercase SHA-256")
        if not isinstance(self.status, ProductionPackageStatus):
            raise TypeError("status must be a ProductionPackageStatus")
        if self.external_delivery_allowed:
            raise ValueError(
                "package construction cannot auto-approve external delivery"
            )

    @property
    def content_sha256(self) -> str:
        return canonical_sha256(
            {
                "package_id": self.package_id,
                "source_episode_text_sha256": self.source_episode_text_sha256,
                "surface_sha256": self.surface_sha256,
                "annotation_set_sha256": self.annotation_set_sha256,
                "p0_receipt_sha256": self.p0_receipt_sha256,
                "p1_receipt_sha256": self.p1_receipt_sha256,
            }
        )


def build_production_text_package(
    *,
    package_id: str,
    source: EpisodeScriptText,
    surface: HumanProductionSurface,
    renderer: ProductionSurfaceRenderer,
    annotation_set: ProductionAnnotationSet,
    p0_receipt: ProductionApprovalReceipt,
    p1_receipt: ProductionApprovalReceipt,
) -> ProductionTextPackage:
    if source.status is not EpisodeScriptTextStatus.APPROVED:
        raise ValueError("production packages require owner-approved story text")

    surface_report = ProductionSurfaceVerifier().verify(
        surface,
        source,
        renderer,
    )
    if not surface_report.passed:
        raise ValueError("production surface verification failed")

    annotation_report = ProductionAnnotationVerifier().verify(
        annotation_set,
        source,
        surface,
    )
    if not annotation_report.passed:
        raise ValueError("production annotation verification failed")

    require_exact_approval(
        p0_receipt,
        gate=ProductionGate.P0_SURFACE_EQUIVALENCE,
        artifact_id=surface.surface_id,
        artifact_sha256=surface.content_sha256,
    )
    require_exact_approval(
        p1_receipt,
        gate=ProductionGate.P1_ANNOTATION_REVIEW,
        artifact_id=annotation_set.annotation_set_id,
        artifact_sha256=annotation_set.content_sha256,
    )

    return ProductionTextPackage(
        package_id=package_id,
        source_episode_text_sha256=source.content_sha256,
        surface_sha256=surface.content_sha256,
        annotation_set_sha256=annotation_set.content_sha256,
        p0_receipt_sha256=p0_receipt.receipt_sha256,
        p1_receipt_sha256=p1_receipt.receipt_sha256,
        status=ProductionPackageStatus.CANDIDATE,
        external_delivery_allowed=False,
    )
