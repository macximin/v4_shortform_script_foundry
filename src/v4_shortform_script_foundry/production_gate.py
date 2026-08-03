"""Independent production-text approvals after HIL 3 story approval."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import re

from .canonical import canonical_sha256


_SHA256_RE = re.compile(r"[0-9a-f]{64}")


class ProductionGate(StrEnum):
    P0_SURFACE_EQUIVALENCE = "p0_surface_equivalence"
    P1_ANNOTATION_REVIEW = "p1_annotation_review"
    P2_TEXT_PACKAGE = "p2_text_package"
    EXTERNAL_DELIVERY = "external_delivery"


class ProductionDecision(StrEnum):
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"
    REJECT = "reject"


_APPROVER_ROLES: dict[ProductionGate, frozenset[str]] = {
    ProductionGate.P0_SURFACE_EQUIVALENCE: frozenset(
        {"system_verifier", "owner"}
    ),
    ProductionGate.P1_ANNOTATION_REVIEW: frozenset(
        {"director", "cinematographer", "editor", "producer", "owner"}
    ),
    ProductionGate.P2_TEXT_PACKAGE: frozenset({"producer", "owner"}),
    ProductionGate.EXTERNAL_DELIVERY: frozenset({"owner"}),
}


@dataclass(frozen=True, slots=True)
class ProductionApprovalReceipt:
    gate: ProductionGate
    artifact_id: str
    artifact_sha256: str
    decision: ProductionDecision
    actor_id: str
    actor_role: str
    decided_at: str
    note: str

    def __post_init__(self) -> None:
        for field_name in (
            "artifact_id",
            "actor_id",
            "actor_role",
            "decided_at",
            "note",
        ):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} must not be empty")
        if not isinstance(self.gate, ProductionGate):
            raise TypeError("gate must be a ProductionGate")
        if not isinstance(self.decision, ProductionDecision):
            raise TypeError("decision must be a ProductionDecision")
        if not _SHA256_RE.fullmatch(self.artifact_sha256):
            raise ValueError("artifact_sha256 must be a lowercase SHA-256")
        if (
            self.decision is ProductionDecision.APPROVE
            and self.actor_role not in _APPROVER_ROLES[self.gate]
        ):
            raise ValueError(
                f"{self.actor_role} cannot approve {self.gate.value}"
            )

    @property
    def receipt_sha256(self) -> str:
        return canonical_sha256(self)

    def approves(self, artifact_id: str, artifact_sha256: str) -> bool:
        return (
            self.decision is ProductionDecision.APPROVE
            and self.artifact_id == artifact_id
            and self.artifact_sha256 == artifact_sha256
        )


def require_exact_approval(
    receipt: ProductionApprovalReceipt,
    *,
    gate: ProductionGate,
    artifact_id: str,
    artifact_sha256: str,
) -> None:
    if receipt.gate is not gate:
        raise ValueError(f"receipt must approve {gate.value}")
    if not receipt.approves(artifact_id, artifact_sha256):
        raise ValueError("receipt does not approve the exact artifact hash")
