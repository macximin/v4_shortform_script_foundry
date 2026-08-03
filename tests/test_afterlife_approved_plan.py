from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from v4_shortform_script_foundry.canonical import (  # noqa: E402
    canonical_sha256,
    canonical_text_sha256,
)


ARTIFACT_ROOT = (
    ROOT / "artifacts" / "approved" / "afterlife_restaurant" / "hil1"
)


class AfterlifeApprovedPlanTests(unittest.TestCase):
    def test_checked_in_approved_plan_is_current(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / "tools"
                    / "build_afterlife_restaurant_hil1_approved_plan.py"
                ),
                "--check",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_manifest_binds_canonical_receipt_and_companion_plan(self) -> None:
        manifest = json.loads(
            (ARTIFACT_ROOT / "manifest.json").read_text(encoding="utf-8")
        )
        canonical = json.loads(
            (ARTIFACT_ROOT / "canonical.json").read_text(encoding="utf-8")
        )
        receipt = json.loads(
            (ARTIFACT_ROOT / "approval_receipt.json").read_text(
                encoding="utf-8"
            )
        )
        review_payload = json.loads(
            (ARTIFACT_ROOT / "review_payload.json").read_text(encoding="utf-8")
        )
        plan_path = ARTIFACT_ROOT / manifest["series_plan"]

        self.assertEqual("owner_approved_hil1", manifest["status"])
        self.assertEqual("not_started", manifest["hil2_status"])
        self.assertFalse(manifest["external_promotion_allowed"])
        self.assertEqual(
            "pending_not_evaluated",
            manifest["premise_distance_status"],
        )
        self.assertEqual(
            manifest["canonical_content_sha256"],
            canonical_sha256(canonical),
        )
        self.assertEqual(
            manifest["canonical_content_sha256"],
            receipt["artifact_content_sha256"],
        )
        self.assertEqual(
            manifest["review_payload_sha256"],
            canonical_sha256(review_payload),
        )

        receipt_payload = {
            key: value
            for key, value in receipt.items()
            if key != "receipt_sha256"
        }
        self.assertEqual(
            manifest["approval_receipt_sha256"],
            canonical_sha256(receipt_payload),
        )
        self.assertEqual(
            manifest["series_plan_sha256"],
            canonical_text_sha256(plan_path.read_text(encoding="utf-8")),
        )

    def test_hil1_lock_does_not_claim_hil2_or_external_clearance(self) -> None:
        canonical = json.loads(
            (ARTIFACT_ROOT / "canonical.json").read_text(encoding="utf-8")
        )
        planning = (ARTIFACT_ROOT / "canonical_planning.md").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "hil1_does_not_lock_the_exact_episode_event_order",
            canonical["world_constraints"],
        )
        self.assertIn("owner approved HIL 1", planning)
        self.assertIn("premise_distance: `pending_not_evaluated`", planning)
        self.assertIn("external_promotion_allowed: `false`", planning)


if __name__ == "__main__":
    unittest.main()
