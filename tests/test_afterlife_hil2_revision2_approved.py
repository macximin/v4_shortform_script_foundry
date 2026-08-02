from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from tools.build_afterlife_restaurant_hil2_revision2_approved import (  # noqa: E402
    OUTPUT_ROOT,
    OWNER_INSTRUCTION,
    build_approval,
)
from tools.build_afterlife_restaurant_hil2_revision2_candidates import (  # noqa: E402
    CANDIDATE_B_ROOT,
    build_hil1_context,
)
from v4_shortform_script_foundry.approval import (  # noqa: E402
    HilGate,
    ReviewDecision,
)
from v4_shortform_script_foundry.arc_contract import (  # noqa: E402
    ArcContractVerifier,
)


class AfterlifeHil2Revision2ApprovedTests(unittest.TestCase):
    def test_checked_in_approval_is_current(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / "tools"
                    / "build_afterlife_restaurant_hil2_revision2_approved.py"
                ),
                "--check",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_receipt_approves_exact_candidate_a_and_hil1_parent(self) -> None:
        arc, receipt, review = build_approval()
        canonical, hil1_manifest = build_hil1_context()

        self.assertTrue(ArcContractVerifier().verify(arc, canonical).passed)
        self.assertTrue(receipt.verify())
        self.assertEqual(HilGate.HIL2_ARC, receipt.gate_id)
        self.assertEqual(ReviewDecision.APPROVE, receipt.decision)
        self.assertEqual(arc.content_sha256, receipt.artifact_content_sha256)
        self.assertEqual((canonical.content_sha256,), receipt.parent_content_sha256s)
        self.assertEqual(
            (hil1_manifest["approval_receipt_sha256"],),
            receipt.parent_approval_receipt_sha256s,
        )
        self.assertEqual(OWNER_INSTRUCTION, review["owner_instruction"])
        self.assertIn("eight-to-twelve-second", review["approved_scope"])
        self.assertIn("candidate B", review["excluded_scope"])

    def test_approval_supersedes_revision_one_but_not_candidate_b(self) -> None:
        manifest = json.loads(
            (OUTPUT_ROOT / "manifest.json").read_text(encoding="utf-8")
        )
        candidate_b = json.loads(
            (CANDIDATE_B_ROOT / "manifest.json").read_text(encoding="utf-8")
        )

        self.assertEqual("owner_approved_hil2", manifest["status"])
        self.assertEqual(2, manifest["revision"])
        self.assertEqual("candidate", candidate_b["status"])
        self.assertEqual("not_started", manifest["hil3_status"])
        self.assertFalse(manifest["external_promotion_allowed"])
        self.assertEqual(
            "pending_not_evaluated",
            manifest["causal_chain_distance_status"],
        )


if __name__ == "__main__":
    unittest.main()
