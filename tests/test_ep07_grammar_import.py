from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from v4_shortform_script_foundry.canonical import canonical_sha256  # noqa: E402
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


def make_abstract_ledger() -> FactLedger:
    return FactLedger(
        premise_id="synthetic-external-proof-reading",
        sources=(
            SourceBinding(
                source_id="owner-original-premise-v1",
                source_kind="synthetic_fixture",
                locator="tests:synthetic-external-proof-reading",
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


def write_document(root: Path, document: dict) -> Path:
    path = root / "import.json"
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


class Ep07GrammarImportTests(unittest.TestCase):
    def test_approved_import_runs_deterministic_vertical_slice(self) -> None:
        imported = load_approved_grammar_import(IMPORT_PATH)

        first = V4ShortformPipeline().run(make_abstract_ledger(), imported.grammar)
        second = V4ShortformPipeline().run(make_abstract_ledger(), imported.grammar)

        self.assertTrue(first.passed)
        self.assertEqual(first, second)
        self.assertEqual(
            "shortform_reverse_lab",
            imported.source_repo,
        )

    def test_import_contains_no_source_specific_tokens(self) -> None:
        text = IMPORT_PATH.read_text(encoding="utf-8")
        forbidden = (
            "한강그룹",
            "회장님 서명",
            "3천만 원",
            "수표",
            "은행",
            "백수 이모부",
        )

        self.assertTrue(all(token not in text for token in forbidden))

    def test_payload_tamper_is_rejected(self) -> None:
        document = json.loads(IMPORT_PATH.read_text(encoding="utf-8"))
        document["payload"]["grammar"]["primary_reward"] = "tampered"
        with tempfile.TemporaryDirectory() as tmp:
            path = write_document(Path(tmp), document)
            with self.assertRaisesRegex(ValueError, "payload hash mismatch"):
                load_approved_grammar_import(path)

    def test_direct_source_distance_is_rejected_even_with_fresh_hash(self) -> None:
        document = json.loads(IMPORT_PATH.read_text(encoding="utf-8"))
        document["payload"]["source"]["distance"] = "direct_source_content"
        document["payload_sha256"] = canonical_sha256(document["payload"])
        with tempfile.TemporaryDirectory() as tmp:
            path = write_document(Path(tmp), document)
            with self.assertRaisesRegex(ValueError, "abstract functional"):
                load_approved_grammar_import(path)

    def test_stale_owner_approval_hash_is_rejected(self) -> None:
        document = json.loads(IMPORT_PATH.read_text(encoding="utf-8"))
        document["payload"]["grammar"]["owner_approval_sha256"] = "0" * 64
        document["payload_sha256"] = canonical_sha256(document["payload"])
        with tempfile.TemporaryDirectory() as tmp:
            path = write_document(Path(tmp), document)
            with self.assertRaisesRegex(ValueError, "approval hash mismatch"):
                load_approved_grammar_import(path)

    def test_artifact_id_must_bind_grammar_packet(self) -> None:
        document = json.loads(IMPORT_PATH.read_text(encoding="utf-8"))
        document["artifact_id"] = "wrong@0.1.0"
        with tempfile.TemporaryDirectory() as tmp:
            path = write_document(Path(tmp), document)
            with self.assertRaisesRegex(ValueError, "artifact id"):
                load_approved_grammar_import(path)


if __name__ == "__main__":
    unittest.main()
