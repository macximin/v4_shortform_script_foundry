from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from test_hil_contracts import (  # noqa: E402
    make_arc,
    make_canonical,
    make_canonical_receipt,
    make_episode,
    make_arc_receipt,
)
from v4_shortform_script_foundry.arc_contract import (  # noqa: E402
    ArcContractVerifier,
    StoryStateAxis,
)
from v4_shortform_script_foundry.canonical_package import (  # noqa: E402
    PayoffCadence,
    PayoffLayer,
)
from v4_shortform_script_foundry.episode_script import (  # noqa: E402
    DialogueLine,
    EpisodeScriptVerifier,
)
from v4_shortform_script_foundry.planning_artifact import (  # noqa: E402
    export_hil1_planning_document,
    export_hil2_planning_document,
)


class PlanningContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.canonical = make_canonical()
        self.hil1 = make_canonical_receipt(self.canonical)
        self.arc = make_arc(self.canonical, self.hil1)
        self.hil2 = make_arc_receipt(
            self.arc,
            self.canonical,
            self.hil1,
        )

    def test_hil_one_preserves_core_pair_and_payoff_cadence(self) -> None:
        self.assertEqual(
            ("protagonist", "field_partner"),
            tuple(
                character.character_id
                for character in self.canonical.core_characters
            ),
        )
        self.assertEqual(
            {
                PayoffCadence.EPISODE,
                PayoffCadence.ARC,
                PayoffCadence.SEASON,
            },
            {layer.cadence for layer in self.canonical.payoff_layers},
        )

    def test_hil_two_carries_world_operation_state(self) -> None:
        before_axes = {entry.axis for entry in self.arc.state_before.entries}
        after_axes = {entry.axis for entry in self.arc.state_after.entries}

        self.assertIn(StoryStateAxis.WORLD_OPERATION, before_axes)
        self.assertIn(StoryStateAxis.WORLD_OPERATION, after_axes)

    def test_owner_readable_hil_documents_bind_exact_payload_hashes(self) -> None:
        hil1_document = export_hil1_planning_document(self.canonical)
        hil2_document = export_hil2_planning_document(self.arc)

        self.assertTrue(hil1_document.verify())
        self.assertTrue(hil2_document.verify())
        self.assertIn("## 핵심 인물", hil1_document.markdown)
        self.assertIn("field_partner", hil1_document.markdown)
        self.assertIn("## 보상 층위", hil1_document.markdown)
        self.assertIn("## 시작 상태", hil2_document.markdown)
        self.assertIn("world_operation", hil2_document.markdown)

    def test_arc_cannot_pay_future_seed_early(self) -> None:
        future_seed = PayoffLayer(
            payoff_id="future_return_question",
            cadence=PayoffCadence.FUTURE_SEED,
            subject_id="protagonist",
            promise="a future return remains possible",
            delivery_policy="seed only; do not resolve in the current arc",
        )
        canonical = replace(
            self.canonical,
            payoff_layers=self.canonical.payoff_layers + (future_seed,),
        )
        receipt = make_canonical_receipt(canonical)
        arc = replace(
            make_arc(canonical, receipt),
            rewards_paid=("future_return_question",),
        )

        report = ArcContractVerifier().verify(arc, canonical)

        self.assertFalse(report.passed)
        self.assertIn(
            "FUTURE_SEED_PAID_EARLY",
            {finding.code for finding in report.findings},
        )

    def test_scene_principal_limit_is_hard_verified(self) -> None:
        candidate = make_episode(self.arc, self.hil2)
        crowded_scene = replace(
            candidate.scenes[0],
            principal_character_ids=("a", "b", "c", "d"),
        )
        crowded = replace(
            candidate,
            scenes=(crowded_scene, candidate.scenes[1]),
        )

        report = EpisodeScriptVerifier().verify(crowded, self.arc)

        self.assertFalse(report.passed)
        self.assertIn(
            "SCENE_PRINCIPAL_LIMIT_EXCEEDED",
            {finding.code for finding in report.findings},
        )

    def test_scene_dialogue_limit_is_hard_verified(self) -> None:
        candidate = make_episode(self.arc, self.hil2)
        extra_dialogue = tuple(
            DialogueLine(
                speaker_id="evaluator",
                text=f"line {index}",
                function="apply_pressure",
            )
            for index in range(5)
        )
        talky_scene = replace(
            candidate.scenes[0],
            dialogue=extra_dialogue,
        )
        talky = replace(
            candidate,
            scenes=(talky_scene, candidate.scenes[1]),
        )

        report = EpisodeScriptVerifier().verify(talky, self.arc)

        self.assertFalse(report.passed)
        self.assertIn(
            "SCENE_DIALOGUE_LIMIT_EXCEEDED",
            {finding.code for finding in report.findings},
        )


if __name__ == "__main__":
    unittest.main()
