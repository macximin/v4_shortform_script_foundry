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
)


ARTIFACT_ROOT = (
    ROOT / "artifacts" / "candidates" / "afterlife_restaurant" / "hil1"
)


class AfterlifePlanningCanaryTests(unittest.TestCase):
    def test_checked_in_candidate_set_is_current(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / "tools"
                    / "build_afterlife_restaurant_hil1_candidates.py"
                ),
                "--check",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_three_candidates_share_facts_but_have_distinct_primary_rewards(
        self,
    ) -> None:
        manifest = json.loads(
            (ARTIFACT_ROOT / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(3, manifest["candidate_count"])
        self.assertEqual("candidate_set_unapproved", manifest["status"])

        primary_rewards: set[str] = set()
        for entry in manifest["candidates"]:
            payload = json.loads(
                (ARTIFACT_ROOT / entry["json"]).read_text(encoding="utf-8")
            )
            self.assertEqual(
                entry["canonical_content_sha256"],
                canonical_sha256(payload),
            )
            self.assertEqual(
                manifest["source_fact_ledger_sha256"],
                payload["source_fact_ledger_sha256"],
            )
            self.assertEqual(
                ["doyun", "underworld_girl"],
                [
                    character["character_id"]
                    for character in payload["core_characters"]
                ],
            )
            self.assertIn(
                "do_not_reframe_doyun_and_the_girl_as_father_and_daughter",
                payload["forbidden_contradictions"],
            )
            self.assertIn(
                "do_not_add_romance_between_doyun_and_the_girl",
                payload["forbidden_contradictions"],
            )
            self.assertEqual(
                3,
                payload["production_constraints"][
                    "max_principal_characters_per_scene"
                ],
            )
            future_layers = [
                layer
                for layer in payload["payoff_layers"]
                if layer["cadence"] == "future_seed"
            ]
            self.assertEqual(
                ["doyun_return_to_daughter"],
                [layer["payoff_id"] for layer in future_layers],
            )
            primary_rewards.add(payload["primary_reward"])

        self.assertEqual(3, len(primary_rewards))

    def test_pending_distance_receipts_never_claim_promotion_readiness(
        self,
    ) -> None:
        research_inputs = json.loads(
            (ARTIFACT_ROOT / "research_inputs.json").read_text(
                encoding="utf-8"
            )
        )
        receipts = research_inputs["premise_distance_receipts"].values()

        self.assertTrue(
            all(
                receipt["status"] == "pending_not_evaluated"
                and receipt["promotion_allowed"] is False
                for receipt in receipts
            )
        )


if __name__ == "__main__":
    unittest.main()
