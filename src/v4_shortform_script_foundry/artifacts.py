"""Stable envelopes for explicit packet handoff across repository boundaries."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

from .canonical import canonical_json


@dataclass(frozen=True, slots=True)
class ArtifactEnvelope:
    schema_version: str
    artifact_type: str
    artifact_id: str
    payload_json: str
    payload_sha256: str

    @classmethod
    def create(
        cls,
        *,
        artifact_type: str,
        artifact_id: str,
        payload: Any,
        schema_version: str = "1",
    ) -> "ArtifactEnvelope":
        if not artifact_type.strip() or not artifact_id.strip():
            raise ValueError("artifact type and id must not be empty")
        payload_json = canonical_json(payload)
        payload_sha256 = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
        return cls(
            schema_version=schema_version,
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            payload_json=payload_json,
            payload_sha256=payload_sha256,
        )

    @property
    def payload(self) -> Any:
        return json.loads(self.payload_json)

    def verify(self) -> bool:
        actual = hashlib.sha256(self.payload_json.encode("utf-8")).hexdigest()
        return actual == self.payload_sha256

    def to_json(self) -> str:
        return canonical_json(
            {
                "schema_version": self.schema_version,
                "artifact_type": self.artifact_type,
                "artifact_id": self.artifact_id,
                "payload": self.payload,
                "payload_sha256": self.payload_sha256,
            }
        )
