"""Manual, hash-bound import of approved abstract genre grammar evidence."""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
from pathlib import Path
import re
from typing import Any

from .canonical import canonical_sha256
from .genre_grammar import (
    GenreGrammarPacket,
    GrammarStatus,
    RendererKind,
    RendererPreference,
)


REQUIRED_USAGE_CONSTRAINTS = {
    "internal_private_analysis_only",
    "no_commercial_use",
    "no_external_publication",
    "no_source_asset_distribution",
}


@dataclass(frozen=True, slots=True)
class ApprovedGrammarImport:
    grammar: GenreGrammarPacket
    source_repo: str
    source_canary_id: str
    source_blueprint_id: str
    source_blueprint_sha256: str
    usage_constraints: tuple[str, ...]
    envelope_payload_sha256: str


def load_approved_grammar_import(path: Path) -> ApprovedGrammarImport:
    document = _load_object(path)
    if document.get("schema_version") != "1":
        raise ValueError("unsupported import schema version")
    if document.get("artifact_type") != "approved_genre_grammar":
        raise ValueError("artifact type must be approved_genre_grammar")

    payload = document.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("import payload must be an object")
    payload_sha256 = document.get("payload_sha256")
    if not _is_sha256(payload_sha256):
        raise ValueError("import payload requires a lowercase SHA-256")
    if canonical_sha256(payload) != payload_sha256:
        raise ValueError("import payload hash mismatch")

    source = payload.get("source")
    if not isinstance(source, dict):
        raise ValueError("import source must be an object")
    source_blueprint_sha256 = source.get("blueprint_sha256")
    if not _is_sha256(source_blueprint_sha256):
        raise ValueError("source blueprint requires a lowercase SHA-256")
    if source.get("distance") != "abstract_functional_blueprint_only":
        raise ValueError("only abstract functional blueprints may be imported")
    if source.get("source_specific_tokens_excluded") is not True:
        raise ValueError("source-specific token exclusion must be attested")

    usage_constraints = payload.get("usage_constraints")
    if not isinstance(usage_constraints, list) or any(
        not isinstance(item, str) for item in usage_constraints
    ):
        raise ValueError("usage constraints must be a string list")
    if len(usage_constraints) != len(set(usage_constraints)):
        raise ValueError("usage constraints must be unique")
    if not REQUIRED_USAGE_CONSTRAINTS.issubset(usage_constraints):
        raise ValueError("required private-research constraints are missing")

    grammar_data = payload.get("grammar")
    if not isinstance(grammar_data, dict):
        raise ValueError("grammar must be an object")
    grammar = _load_approved_grammar(grammar_data)
    if document.get("artifact_id") != grammar.packet_id:
        raise ValueError("artifact id must equal the grammar packet id")

    evidence_binding = (
        f"{source.get('repo')}:{source.get('canary_id')}:"
        f"{source.get('blueprint_id')}@sha256:{source_blueprint_sha256}"
    )
    if evidence_binding not in grammar.evidence_ids:
        raise ValueError("grammar evidence ids do not bind the source blueprint")

    return ApprovedGrammarImport(
        grammar=grammar,
        source_repo=_required_string(source, "repo"),
        source_canary_id=_required_string(source, "canary_id"),
        source_blueprint_id=_required_string(source, "blueprint_id"),
        source_blueprint_sha256=source_blueprint_sha256,
        usage_constraints=tuple(usage_constraints),
        envelope_payload_sha256=payload_sha256,
    )


def _load_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("import document must be an object")
    return value


def _load_approved_grammar(data: dict[str, Any]) -> GenreGrammarPacket:
    if data.get("status") != GrammarStatus.APPROVED.value:
        raise ValueError("imported grammar must be approved")
    preferences_data = data.get("preferences")
    if not isinstance(preferences_data, list):
        raise ValueError("grammar preferences must be a list")
    preferences = tuple(
        RendererPreference(
            renderer=RendererKind(_required_string(item, "renderer")),
            weight=item["weight"],
            threat=_required_string(item, "threat"),
            proof_mode=_required_string(item, "proof_mode"),
            reward_target=_required_string(item, "reward_target"),
            required_fact_tags=_string_tuple(item, "required_fact_tags"),
        )
        for item in preferences_data
        if isinstance(item, dict)
    )
    if len(preferences) != len(preferences_data):
        raise ValueError("each grammar preference must be an object")

    candidate = GenreGrammarPacket(
        grammar_id=_required_string(data, "grammar_id"),
        version=_required_string(data, "version"),
        target_profile=_required_string(data, "target_profile"),
        entry_pressure=_required_string(data, "entry_pressure"),
        primary_reward=_required_string(data, "primary_reward"),
        preferences=preferences,
        evidence_ids=_string_tuple(data, "evidence_ids"),
        status=GrammarStatus.CANDIDATE,
    )
    approval_sha256 = data.get("owner_approval_sha256")
    if not _is_sha256(approval_sha256):
        raise ValueError("imported grammar requires an owner approval SHA-256")
    if approval_sha256 != candidate.content_sha256:
        raise ValueError("imported grammar approval hash mismatch")
    return replace(
        candidate,
        status=GrammarStatus.APPROVED,
        owner_approval_sha256=approval_sha256,
    )


def _required_string(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value


def _string_tuple(data: dict[str, Any], key: str) -> tuple[str, ...]:
    value = data.get(key)
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ValueError(f"{key} must be a non-empty string list")
    if len(value) != len(set(value)):
        raise ValueError(f"{key} must be unique")
    return tuple(value)


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None
