"""Immutable HIL approval receipts, revisions, invalidation, and resume rules."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
import re

from .canonical import canonical_sha256


_SHA256_RE = re.compile(r"[0-9a-f]{64}")


def _require_text(value: str, field_name: str) -> None:
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")


def _require_sha256(value: str, field_name: str) -> None:
    if not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{field_name} must be a lowercase SHA-256")


def _require_unique(values: tuple[str, ...], field_name: str) -> None:
    if any(not value.strip() for value in values):
        raise ValueError(f"{field_name} values must not be empty")
    if len(values) != len(set(values)):
        raise ValueError(f"{field_name} values must be unique")


class HilGate(StrEnum):
    HIL1_CANONICAL = "hil1_canonical"
    HIL2_ARC = "hil2_arc"
    HIL3_EPISODE_SCRIPT = "hil3_episode_script"


class ReviewDecision(StrEnum):
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"
    REJECT = "reject"


class ArtifactStatus(StrEnum):
    CANDIDATE = "candidate"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    STALE = "stale"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class ApprovalReceipt:
    gate_id: HilGate
    work_id: str
    artifact_id: str
    revision: int
    artifact_content_sha256: str
    parent_content_sha256s: tuple[str, ...]
    parent_approval_receipt_sha256s: tuple[str, ...]
    decision: ReviewDecision
    reviewer_id: str
    reviewer_role: str
    rubric_version: str
    review_payload_sha256: str
    decided_at: str
    receipt_sha256: str

    def __post_init__(self) -> None:
        if not isinstance(self.gate_id, HilGate):
            raise TypeError("gate_id must be a HilGate")
        if not isinstance(self.decision, ReviewDecision):
            raise TypeError("decision must be a ReviewDecision")
        for field_name in (
            "work_id",
            "artifact_id",
            "reviewer_id",
            "reviewer_role",
            "rubric_version",
            "decided_at",
        ):
            _require_text(getattr(self, field_name), field_name)
        if self.revision < 1:
            raise ValueError("revision must be positive")
        _require_sha256(
            self.artifact_content_sha256,
            "artifact_content_sha256",
        )
        _require_sha256(
            self.review_payload_sha256,
            "review_payload_sha256",
        )
        _require_sha256(self.receipt_sha256, "receipt_sha256")
        _require_unique(
            self.parent_content_sha256s,
            "parent_content_sha256s",
        )
        _require_unique(
            self.parent_approval_receipt_sha256s,
            "parent_approval_receipt_sha256s",
        )
        for value in self.parent_content_sha256s:
            _require_sha256(value, "parent_content_sha256s")
        for value in self.parent_approval_receipt_sha256s:
            _require_sha256(
                value,
                "parent_approval_receipt_sha256s",
            )
        if len(self.parent_content_sha256s) != len(
            self.parent_approval_receipt_sha256s
        ):
            raise ValueError(
                "parent content and approval hashes must have equal counts"
            )
        try:
            decided_at = datetime.fromisoformat(self.decided_at)
        except ValueError as error:
            raise ValueError("decided_at must be ISO-8601") from error
        if decided_at.tzinfo is None:
            raise ValueError("decided_at must include a timezone")
        if self.receipt_sha256 != canonical_sha256(self.receipt_payload):
            raise ValueError("receipt_sha256 must bind the receipt payload")

    @property
    def receipt_payload(self) -> dict[str, object]:
        return {
            "gate_id": self.gate_id,
            "work_id": self.work_id,
            "artifact_id": self.artifact_id,
            "revision": self.revision,
            "artifact_content_sha256": self.artifact_content_sha256,
            "parent_content_sha256s": self.parent_content_sha256s,
            "parent_approval_receipt_sha256s": (self.parent_approval_receipt_sha256s),
            "decision": self.decision,
            "reviewer_id": self.reviewer_id,
            "reviewer_role": self.reviewer_role,
            "rubric_version": self.rubric_version,
            "review_payload_sha256": self.review_payload_sha256,
            "decided_at": self.decided_at,
        }

    @classmethod
    def issue(
        cls,
        *,
        gate_id: HilGate,
        work_id: str,
        artifact_id: str,
        revision: int,
        artifact_content_sha256: str,
        parent_content_sha256s: tuple[str, ...] = (),
        parent_approval_receipt_sha256s: tuple[str, ...] = (),
        decision: ReviewDecision,
        reviewer_id: str,
        reviewer_role: str,
        rubric_version: str,
        review_payload_sha256: str,
        decided_at: str,
    ) -> "ApprovalReceipt":
        payload = {
            "gate_id": gate_id,
            "work_id": work_id,
            "artifact_id": artifact_id,
            "revision": revision,
            "artifact_content_sha256": artifact_content_sha256,
            "parent_content_sha256s": parent_content_sha256s,
            "parent_approval_receipt_sha256s": (parent_approval_receipt_sha256s),
            "decision": decision,
            "reviewer_id": reviewer_id,
            "reviewer_role": reviewer_role,
            "rubric_version": rubric_version,
            "review_payload_sha256": review_payload_sha256,
            "decided_at": decided_at,
        }
        return cls(
            gate_id=gate_id,
            work_id=work_id,
            artifact_id=artifact_id,
            revision=revision,
            artifact_content_sha256=artifact_content_sha256,
            parent_content_sha256s=parent_content_sha256s,
            parent_approval_receipt_sha256s=(parent_approval_receipt_sha256s),
            decision=decision,
            reviewer_id=reviewer_id,
            reviewer_role=reviewer_role,
            rubric_version=rubric_version,
            review_payload_sha256=review_payload_sha256,
            decided_at=decided_at,
            receipt_sha256=canonical_sha256(payload),
        )

    def verify(self) -> bool:
        return self.receipt_sha256 == canonical_sha256(self.receipt_payload)


@dataclass(frozen=True, slots=True)
class ArtifactRevision:
    work_id: str
    artifact_id: str
    gate_id: HilGate
    revision: int
    content_sha256: str
    parent_content_sha256s: tuple[str, ...] = ()
    parent_approval_receipt_sha256s: tuple[str, ...] = ()
    status: ArtifactStatus = ArtifactStatus.CANDIDATE
    latest_review_receipt_sha256: str | None = None
    approval_receipt_sha256: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.gate_id, HilGate):
            raise TypeError("gate_id must be a HilGate")
        if not isinstance(self.status, ArtifactStatus):
            raise TypeError("status must be an ArtifactStatus")
        _require_text(self.work_id, "work_id")
        _require_text(self.artifact_id, "artifact_id")
        if self.revision < 1:
            raise ValueError("revision must be positive")
        _require_sha256(self.content_sha256, "content_sha256")
        _require_unique(
            self.parent_content_sha256s,
            "parent_content_sha256s",
        )
        _require_unique(
            self.parent_approval_receipt_sha256s,
            "parent_approval_receipt_sha256s",
        )
        for value in self.parent_content_sha256s:
            _require_sha256(value, "parent_content_sha256s")
        for value in self.parent_approval_receipt_sha256s:
            _require_sha256(
                value,
                "parent_approval_receipt_sha256s",
            )
        if len(self.parent_content_sha256s) != len(
            self.parent_approval_receipt_sha256s
        ):
            raise ValueError(
                "parent content and approval hashes must have equal counts"
            )
        for field_name in (
            "latest_review_receipt_sha256",
            "approval_receipt_sha256",
        ):
            value = getattr(self, field_name)
            if value is not None:
                _require_sha256(value, field_name)
        if (
            self.status is ArtifactStatus.APPROVED
            and self.approval_receipt_sha256 is None
        ):
            raise ValueError("approved artifacts require an approval receipt")
        if self.gate_id is HilGate.HIL1_CANONICAL:
            if self.parent_content_sha256s or self.parent_approval_receipt_sha256s:
                raise ValueError("HIL 1 artifacts cannot have HIL parents")
        elif (
            not self.parent_content_sha256s or not self.parent_approval_receipt_sha256s
        ):
            raise ValueError(
                "HIL 2 and HIL 3 artifacts require parent content and approval hashes"
            )


@dataclass(frozen=True, slots=True)
class ApprovalRequirement:
    step_id: str
    gate_id: HilGate
    artifact_id: str
    parent_content_sha256s: tuple[str, ...] = ()
    parent_approval_receipt_sha256s: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.gate_id, HilGate):
            raise TypeError("gate_id must be a HilGate")
        _require_text(self.step_id, "step_id")
        _require_text(self.artifact_id, "artifact_id")
        _require_unique(
            self.parent_content_sha256s,
            "parent_content_sha256s",
        )
        _require_unique(
            self.parent_approval_receipt_sha256s,
            "parent_approval_receipt_sha256s",
        )
        for value in self.parent_content_sha256s:
            _require_sha256(value, "parent_content_sha256s")
        for value in self.parent_approval_receipt_sha256s:
            _require_sha256(
                value,
                "parent_approval_receipt_sha256s",
            )
        if len(self.parent_content_sha256s) != len(
            self.parent_approval_receipt_sha256s
        ):
            raise ValueError(
                "parent content and approval hashes must have equal counts"
            )
        if self.gate_id is HilGate.HIL1_CANONICAL:
            if self.parent_content_sha256s or self.parent_approval_receipt_sha256s:
                raise ValueError("HIL 1 requirements cannot have parents")
        elif (
            not self.parent_content_sha256s or not self.parent_approval_receipt_sha256s
        ):
            raise ValueError("HIL 2 and HIL 3 requirements need parent hashes")


@dataclass(frozen=True, slots=True)
class ResumeBoundary:
    complete: bool
    step_id: str | None
    gate_id: HilGate | None
    reason: str


@dataclass(frozen=True, slots=True)
class ApprovalLedger:
    records: tuple[ArtifactRevision, ...] = ()

    def __post_init__(self) -> None:
        keys = [
            (record.work_id, record.artifact_id, record.revision)
            for record in self.records
        ]
        if len(keys) != len(set(keys)):
            raise ValueError("artifact revisions must be unique")

    def add_candidate(self, candidate: ArtifactRevision) -> "ApprovalLedger":
        if candidate.status is not ArtifactStatus.CANDIDATE:
            raise ValueError("new revisions must start as candidates")
        matching = [
            record
            for record in self.records
            if record.work_id == candidate.work_id
            and record.artifact_id == candidate.artifact_id
        ]
        expected_revision = 1 + max(
            (record.revision for record in matching),
            default=0,
        )
        if candidate.revision != expected_revision:
            raise ValueError(f"revision must be the next value: {expected_revision}")
        return ApprovalLedger(self.records + (candidate,))

    def begin_review(
        self,
        *,
        work_id: str,
        artifact_id: str,
        revision: int,
    ) -> "ApprovalLedger":
        index = self._index_of(work_id, artifact_id, revision)
        record = self.records[index]
        if record.status is not ArtifactStatus.CANDIDATE:
            raise ValueError("only candidates can enter review")
        return self._replace_at(
            index,
            replace(record, status=ArtifactStatus.IN_REVIEW),
        )

    def apply_receipt(self, receipt: ApprovalReceipt) -> "ApprovalLedger":
        index = self._index_of(
            receipt.work_id,
            receipt.artifact_id,
            receipt.revision,
        )
        record = self.records[index]
        if record.status is not ArtifactStatus.IN_REVIEW:
            raise ValueError("review receipts require an artifact in review")
        if record.gate_id is not receipt.gate_id:
            raise ValueError("receipt gate does not match artifact gate")
        if record.content_sha256 != receipt.artifact_content_sha256:
            raise ValueError("receipt content hash does not match artifact")
        if record.parent_content_sha256s != receipt.parent_content_sha256s:
            raise ValueError("receipt parent content hashes do not match")
        if (
            record.parent_approval_receipt_sha256s
            != receipt.parent_approval_receipt_sha256s
        ):
            raise ValueError("receipt parent approval hashes do not match")

        if receipt.decision is ReviewDecision.APPROVE:
            if receipt.reviewer_role != "owner":
                raise ValueError("only the owner role may approve HIL artifacts")
            updated = replace(
                record,
                status=ArtifactStatus.APPROVED,
                latest_review_receipt_sha256=receipt.receipt_sha256,
                approval_receipt_sha256=receipt.receipt_sha256,
            )
            ledger = self._replace_at(index, updated)
            return ledger._supersede_prior_approved(updated)
        if receipt.decision is ReviewDecision.REJECT:
            status = ArtifactStatus.REJECTED
        else:
            status = ArtifactStatus.CANDIDATE
        return self._replace_at(
            index,
            replace(
                record,
                status=status,
                latest_review_receipt_sha256=receipt.receipt_sha256,
            ),
        )

    def latest_approved(
        self,
        *,
        work_id: str,
        artifact_id: str,
    ) -> ArtifactRevision | None:
        matching = [
            record
            for record in self.records
            if record.work_id == work_id
            and record.artifact_id == artifact_id
            and record.status is ArtifactStatus.APPROVED
        ]
        if not matching:
            return None
        return max(matching, key=lambda record: record.revision)

    def resume_boundary(
        self,
        *,
        work_id: str,
        requirements: tuple[ApprovalRequirement, ...],
    ) -> ResumeBoundary:
        step_ids = [requirement.step_id for requirement in requirements]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError("resume requirement step ids must be unique")
        for requirement in requirements:
            approved = self.latest_approved(
                work_id=work_id,
                artifact_id=requirement.artifact_id,
            )
            if approved is None:
                return ResumeBoundary(
                    complete=False,
                    step_id=requirement.step_id,
                    gate_id=requirement.gate_id,
                    reason="missing_approved_artifact",
                )
            if approved.gate_id is not requirement.gate_id:
                return ResumeBoundary(
                    complete=False,
                    step_id=requirement.step_id,
                    gate_id=requirement.gate_id,
                    reason="gate_mismatch",
                )
            if approved.parent_content_sha256s != requirement.parent_content_sha256s:
                return ResumeBoundary(
                    complete=False,
                    step_id=requirement.step_id,
                    gate_id=requirement.gate_id,
                    reason="parent_content_mismatch",
                )
            if (
                approved.parent_approval_receipt_sha256s
                != requirement.parent_approval_receipt_sha256s
            ):
                return ResumeBoundary(
                    complete=False,
                    step_id=requirement.step_id,
                    gate_id=requirement.gate_id,
                    reason="parent_approval_mismatch",
                )
        return ResumeBoundary(
            complete=True,
            step_id=None,
            gate_id=None,
            reason="all_requirements_approved",
        )

    def _supersede_prior_approved(
        self,
        approved: ArtifactRevision,
    ) -> "ApprovalLedger":
        records = list(self.records)
        invalidated_content: set[str] = set()
        invalidated_receipts: set[str] = set()
        for index, record in enumerate(records):
            if (
                record.work_id == approved.work_id
                and record.artifact_id == approved.artifact_id
                and record.revision < approved.revision
                and record.status is ArtifactStatus.APPROVED
            ):
                records[index] = replace(
                    record,
                    status=ArtifactStatus.SUPERSEDED,
                )
                invalidated_content.add(record.content_sha256)
                if record.approval_receipt_sha256:
                    invalidated_receipts.add(record.approval_receipt_sha256)

        changed = True
        while changed:
            changed = False
            for index, record in enumerate(records):
                if record.status not in {
                    ArtifactStatus.CANDIDATE,
                    ArtifactStatus.IN_REVIEW,
                    ArtifactStatus.APPROVED,
                }:
                    continue
                if invalidated_content.intersection(
                    record.parent_content_sha256s
                ) or invalidated_receipts.intersection(
                    record.parent_approval_receipt_sha256s
                ):
                    records[index] = replace(
                        record,
                        status=ArtifactStatus.STALE,
                    )
                    if record.content_sha256 not in invalidated_content:
                        invalidated_content.add(record.content_sha256)
                        changed = True
                    if (
                        record.approval_receipt_sha256
                        and record.approval_receipt_sha256 not in invalidated_receipts
                    ):
                        invalidated_receipts.add(record.approval_receipt_sha256)
                        changed = True
        return ApprovalLedger(tuple(records))

    def _index_of(
        self,
        work_id: str,
        artifact_id: str,
        revision: int,
    ) -> int:
        for index, record in enumerate(self.records):
            if (
                record.work_id == work_id
                and record.artifact_id == artifact_id
                and record.revision == revision
            ):
                return index
        raise KeyError((work_id, artifact_id, revision))

    def _replace_at(
        self,
        index: int,
        record: ArtifactRevision,
    ) -> "ApprovalLedger":
        records = list(self.records)
        records[index] = record
        return ApprovalLedger(tuple(records))
