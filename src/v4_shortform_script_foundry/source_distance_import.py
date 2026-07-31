"""Manual, hash-bound import of source-distance receipts from Eval."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import json
from pathlib import Path
from typing import Mapping

from .canonical import canonical_sha256
from .episode_script import EpisodeScriptCandidate
from .writer_adapter import WriterDraft


class ImportedDistanceDecision(StrEnum):
    PASS = "pass"
    REVIEW_REQUIRED = "review_required"
    FAIL = "fail"


_RECEIPT_KEYS = frozenset(
    {
        "receipt_version",
        "evaluator_version",
        "candidate_id",
        "candidate_projection_sha256",
        "reference_manifest_sha256",
        "policy_id",
        "policy_version",
        "policy_tier",
        "policy_content_sha256",
        "calibration_receipt_sha256",
        "decision",
        "metrics",
        "evaluated_at",
        "receipt_sha256",
    }
)
_FORBIDDEN_RAW_KEYS = frozenset(
    {
        "text",
        "source_text",
        "source_uri",
        "locator",
        "protected_phrases",
    }
)


def _reject_raw_source_fields(value: object) -> None:
    if isinstance(value, Mapping):
        forbidden = _FORBIDDEN_RAW_KEYS.intersection(
            str(key) for key in value
        )
        if forbidden:
            raise ValueError(
                "distance receipt must not contain raw source fields: "
                + ", ".join(sorted(forbidden))
            )
        for nested in value.values():
            _reject_raw_source_fields(nested)
    elif isinstance(value, (tuple, list)):
        for nested in value:
            _reject_raw_source_fields(nested)


@dataclass(frozen=True, slots=True)
class ImportedSourceDistanceReceipt:
    receipt_payload: dict[str, object]
    receipt_sha256: str

    @classmethod
    def from_mapping(
        cls,
        mapping: Mapping[str, object],
    ) -> "ImportedSourceDistanceReceipt":
        actual = frozenset(mapping)
        if actual != _RECEIPT_KEYS:
            raise ValueError("distance receipt fields do not match version 1")
        _reject_raw_source_fields(mapping)
        payload = {
            key: mapping[key]
            for key in _RECEIPT_KEYS
            if key != "receipt_sha256"
        }
        receipt_sha256 = mapping["receipt_sha256"]
        if not isinstance(receipt_sha256, str):
            raise ValueError("receipt_sha256 must be a string")
        if canonical_sha256(payload) != receipt_sha256:
            raise ValueError("distance receipt hash does not bind payload")
        raw_decision = mapping["decision"]
        if not isinstance(raw_decision, str):
            raise ValueError("distance receipt decision must be a string")
        try:
            decision = ImportedDistanceDecision(raw_decision)
        except (TypeError, ValueError) as error:
            raise ValueError("distance receipt has invalid decision") from error
        if decision is not ImportedDistanceDecision.PASS:
            raise ValueError(
                "only pass receipts can bind a finished script candidate"
            )
        return cls(
            receipt_payload=payload,
            receipt_sha256=receipt_sha256,
        )

    @property
    def candidate_id(self) -> str:
        value = self.receipt_payload["candidate_id"]
        if not isinstance(value, str):
            raise ValueError("candidate_id must be a string")
        return value

    @property
    def candidate_projection_sha256(self) -> str:
        value = self.receipt_payload["candidate_projection_sha256"]
        if not isinstance(value, str):
            raise ValueError("candidate_projection_sha256 must be a string")
        return value

    @property
    def policy_tier(self) -> str:
        value = self.receipt_payload["policy_tier"]
        if not isinstance(value, str):
            raise ValueError("policy_tier must be a string")
        return value


def bind_source_distance_receipt(
    draft: WriterDraft,
    receipt: ImportedSourceDistanceReceipt,
    *,
    allow_synthetic_canary: bool = False,
) -> EpisodeScriptCandidate:
    projection = draft.source_distance_projection
    if receipt.candidate_id != projection.candidate_id:
        raise ValueError("distance receipt candidate_id does not match writer draft")
    if receipt.candidate_projection_sha256 != projection.projection_sha256:
        raise ValueError(
            "distance receipt projection hash does not match writer draft"
        )
    if (
        receipt.policy_tier != "production_approved"
        and not allow_synthetic_canary
    ):
        raise ValueError(
            "only production-approved distance policy can bind a candidate"
        )
    return draft.to_candidate(
        source_distance_receipt_sha256=receipt.receipt_sha256,
    )


def load_source_distance_receipt(
    path: Path,
) -> ImportedSourceDistanceReceipt:
    with path.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, dict):
        raise ValueError("distance receipt JSON must contain an object")
    return ImportedSourceDistanceReceipt.from_mapping(raw)
