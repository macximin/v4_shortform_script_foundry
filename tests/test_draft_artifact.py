from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from build_loop04_canary import build_bundle  # noqa: E402
from v4_shortform_script_foundry.canonical import (  # noqa: E402
    canonical_json,
    canonical_sha256,
)


ARTIFACT_PATH = (
    ROOT
    / "artifacts"
    / "canaries"
    / "loop04"
    / "functional_draft_bundle.json"
)


class DraftArtifactTests(unittest.TestCase):
    def test_checked_in_artifact_is_current_and_deterministic(self) -> None:
        checked_in = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

        self.assertEqual(build_bundle(), checked_in)
        self.assertEqual(canonical_json(checked_in), canonical_json(build_bundle()))

    def test_bundle_and_each_draft_hash_verify(self) -> None:
        bundle = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

        self.assertEqual(
            bundle["payload_sha256"],
            canonical_sha256(bundle["payload"]),
        )
        drafts = bundle["payload"]["drafts"]
        self.assertEqual(3, len(drafts))
        for draft in drafts:
            self.assertEqual(
                draft["payload_sha256"],
                canonical_sha256(draft["payload"]),
            )

    def test_artifact_is_candidate_only_and_source_distant(self) -> None:
        bundle = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        text = canonical_json(bundle)
        forbidden = (
            "한강그룹",
            "회장님 서명",
            "3천만 원",
            "수표",
            "은행",
            "백수 이모부",
        )

        self.assertTrue(all(token not in text for token in forbidden))
        for envelope in bundle["payload"]["drafts"]:
            self.assertEqual("candidate", envelope["payload"]["status"])
            self.assertEqual(
                "approved_grammar_only_no_reference_content",
                envelope["payload"]["source_distance"],
            )


if __name__ == "__main__":
    unittest.main()
