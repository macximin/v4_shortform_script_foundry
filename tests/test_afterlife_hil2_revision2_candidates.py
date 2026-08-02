from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from tools.build_afterlife_restaurant_hil2_revision2_candidates import (  # noqa: E402
    APPROVED_HIL2_ROOT,
    CANDIDATE_A_ROOT,
    CANDIDATE_B_ROOT,
    OUTPUT_ROOT,
    build_candidate_a,
    build_candidate_b,
    build_hil1_context,
    build_research_receipt,
    build_revision_proposal,
)
from v4_shortform_script_foundry.arc_contract import (  # noqa: E402
    ArcContractVerifier,
)
from v4_shortform_script_foundry.canonical import (  # noqa: E402
    canonical_sha256,
)


PARENT_ARC_SHA256 = (
    "3eb172f699b6f331befdf66090293ffdbbb2e3a33fbf55652444fe1032363816"
)


class AfterlifeHil2Revision2CandidateTests(unittest.TestCase):
    def test_checked_in_candidate_set_is_current(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / "tools"
                    / "build_afterlife_restaurant_hil2_revision2_candidates.py"
                ),
                "--check",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_both_candidates_verify_against_approved_hil1(self) -> None:
        canonical, _ = build_hil1_context()
        verifier = ArcContractVerifier()
        candidate_a = build_candidate_a()
        candidate_b = build_candidate_b()

        self.assertTrue(verifier.verify(candidate_a, canonical).passed)
        self.assertTrue(verifier.verify(candidate_b, canonical).passed)
        self.assertEqual(2, candidate_a.revision)
        self.assertEqual(2, candidate_b.revision)
        self.assertEqual((1, 2), (candidate_a.episode_count_min, candidate_a.episode_count_max))
        self.assertEqual((2, 3), (candidate_b.episode_count_min, candidate_b.episode_count_max))

    def test_revision_proposals_bind_exact_approved_parent(self) -> None:
        parent_manifest = json.loads(
            (APPROVED_HIL2_ROOT / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual("owner_approved_hil2", parent_manifest["status"])
        self.assertEqual(PARENT_ARC_SHA256, parent_manifest["arc_content_sha256"])

        for candidate in (build_candidate_a(), build_candidate_b()):
            proposal = build_revision_proposal(candidate)
            self.assertEqual(PARENT_ARC_SHA256, proposal.parent_arc_content_sha256)
            self.assertEqual(2, proposal.proposed_revision)
            self.assertEqual(64, len(canonical_sha256(proposal)))

    def test_manifests_keep_parent_authoritative_and_hil3_blocked(self) -> None:
        for root in (CANDIDATE_A_ROOT, CANDIDATE_B_ROOT):
            manifest = json.loads(
                (root / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual("candidate", manifest["status"])
            self.assertEqual("not_started", manifest["owner_approval"])
            self.assertFalse(manifest["external_promotion_allowed"])
            self.assertTrue(manifest["supersedes_parent_only_if_owner_approved"])
            self.assertEqual(PARENT_ARC_SHA256, manifest["parent_hil2_content_sha256"])
            self.assertEqual(
                "blocked_until_hil2_revision_owner_approval",
                manifest["hil3_status"],
            )
            self.assertEqual(
                "pending_not_evaluated",
                manifest["causal_chain_distance_status"],
            )

        candidate_set = json.loads(
            (OUTPUT_ROOT / "manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual("candidate_set", candidate_set["status"])
        self.assertFalse(candidate_set["recommendation_is_approval"])
        self.assertFalse(candidate_set["external_promotion_allowed"])

    def test_candidate_a_closes_and_candidate_b_reopens_only_new_desire(self) -> None:
        allocation_a = (CANDIDATE_A_ROOT / "episode_allocation.md").read_text(
            encoding="utf-8"
        )
        allocation_b = (CANDIDATE_B_ROOT / "episode_allocation.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("1화만으로", allocation_a)
        self.assertIn("김문성의 감정 문제를 다시 열", allocation_a)
        self.assertIn("새 욕망과 구체적 주문", allocation_b)
        self.assertIn("1화는 독립 완결", allocation_b)
        self.assertIn("마지막 식사", allocation_b)

    def test_common_direction_rejects_origin_and_failure_pressure(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in OUTPUT_ROOT.rglob("*")
            if path.is_file()
        )
        self.assertIn("이미 영업 중", combined)
        self.assertIn("완성형 셰프", combined)
        self.assertIn("실패·오답·맛없음", combined)
        self.assertIn("처음부터 완성", combined)
        self.assertIn("손님 퇴장 뒤 8~12초", combined)
        self.assertIn("다음 영업 행동", combined)
        self.assertNotIn("guest_kim_munseong", combined)
        self.assertNotIn("삼도식당에 아무거나는 없느니라", combined)
        self.assertNotIn("손님을 시험하겠다는 것이냐", combined)
        self.assertNotIn("산 자의 혀로는 끝맛을 못 느끼느니라", combined)

    def test_research_is_hypothesis_only_and_never_generator_input(self) -> None:
        receipt = build_research_receipt()
        checked_in = json.loads(
            (OUTPUT_ROOT / "research_input_receipt.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(receipt, checked_in)
        self.assertEqual(
            "human_reviewed_structural_hypotheses_only",
            receipt["use_scope"],
        )
        self.assertFalse(receipt["source_specific_copy_allowed"])
        self.assertFalse(receipt["generator_ingest_allowed"])
        self.assertFalse(receipt["writeback_to_reverse_lab_allowed"])

    def test_comparison_recommends_a_without_approving_it(self) -> None:
        comparison = (OUTPUT_ROOT / "comparison.md").read_text(encoding="utf-8")

        self.assertIn("후보 A를 HIL 2 소유자 검토 1순위로 추천", comparison)
        self.assertIn("이 추천은 승인이 아니다", comparison)
        self.assertIn("revision 1 승인본이 계속 권위본", comparison)


if __name__ == "__main__":
    unittest.main()
