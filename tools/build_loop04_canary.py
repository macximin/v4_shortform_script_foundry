"""Build the deterministic Loop 04 functional-draft canary artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from v4_shortform_script_foundry.artifacts import ArtifactEnvelope  # noqa: E402
from v4_shortform_script_foundry.canonical import canonical_json  # noqa: E402
from v4_shortform_script_foundry.fact_ledger import (  # noqa: E402
    Certainty,
    FactLedger,
    FactRecord,
    SourceBinding,
)
from v4_shortform_script_foundry.grammar_import import (  # noqa: E402
    load_approved_grammar_import,
)
from v4_shortform_script_foundry.pipeline import V4ShortformPipeline  # noqa: E402


IMPORT_PATH = (
    ROOT
    / "imports"
    / "approved_genre_grammar"
    / "ep07_external_proof_reading_v1.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "artifacts"
    / "canaries"
    / "loop04"
    / "functional_draft_bundle.json"
)


def build_original_ledger() -> FactLedger:
    return FactLedger(
        premise_id="synthetic-external-proof-reading",
        sources=(
            SourceBinding(
                source_id="owner-original-premise-v1",
                source_kind="synthetic_fixture",
                locator="loop04:owner-original-premise",
            ),
        ),
        facts=(
            FactRecord(
                fact_id="f-proof",
                subject="portable_evidence",
                predicate="is_disputed",
                value="true",
                certainty=Certainty.CONFIRMED,
                source_ids=("owner-original-premise-v1",),
                tags=(
                    "disputed_portable_proof",
                    "resource_value",
                    "misperception",
                ),
            ),
            FactRecord(
                fact_id="f-validator",
                subject="validator",
                predicate="can_read_marker",
                value="true",
                certainty=Certainty.CONFIRMED,
                source_ids=("owner-original-premise-v1",),
                tags=("external_validator", "authority"),
            ),
        ),
    )


def build_bundle() -> dict[str, object]:
    imported = load_approved_grammar_import(IMPORT_PATH)
    ledger = build_original_ledger()
    result = V4ShortformPipeline().run(ledger, imported.grammar)
    if not result.passed:
        raise RuntimeError("Loop 04 canary pipeline failed verification")

    draft_envelopes = [
        json.loads(
            ArtifactEnvelope.create(
                artifact_type="functional_draft_script",
                artifact_id=(
                    f"{ledger.premise_id}:ep{draft.episode_number:03d}"
                ),
                payload=draft,
            ).to_json()
        )
        for draft in result.drafts
    ]
    payload = {
        "canary_id": "loop04-external-proof-reading",
        "premise_kind": "synthetic_original_fixture",
        "grammar_packet_id": imported.grammar.packet_id,
        "grammar_import_payload_sha256": imported.envelope_payload_sha256,
        "source_distance": "approved_grammar_only_no_reference_content",
        "episode_count": len(result.drafts),
        "all_hard_verification_passed": result.passed,
        "drafts": draft_envelopes,
    }
    return json.loads(
        ArtifactEnvelope.create(
            artifact_type="functional_draft_bundle",
            artifact_id="loop04-external-proof-reading",
            payload=payload,
        ).to_json()
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        canonical_json(build_bundle()) + "\n",
        encoding="utf-8",
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
