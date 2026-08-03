from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from tools.build_afterlife_restaurant_hil2_arc01_candidate import (  # noqa: E402
    ADAPTATION_MAP_PATH,
    EP001_ROUGH_PATH,
    OUTPUT_ROOT,
    build_arc,
    build_distance_status,
    build_hil1_context,
)
from v4_shortform_script_foundry.arc_contract import (  # noqa: E402
    ArcContractVerifier,
)
from v4_shortform_script_foundry.canonical import (  # noqa: E402
    canonical_text_sha256,
)
from v4_shortform_script_foundry.canonical import (  # noqa: E402
    canonical_sha256,
)


class AfterlifeHil2Arc01CandidateTests(unittest.TestCase):
    def test_checked_in_candidate_is_current(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / "tools"
                    / "build_afterlife_restaurant_hil2_arc01_candidate.py"
                ),
                "--check",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_arc_binds_and_verifies_against_approved_hil1(self) -> None:
        arc = build_arc()
        canonical, _ = build_hil1_context()

        report = ArcContractVerifier().verify(arc, canonical)

        self.assertTrue(report.passed, report.findings)
        self.assertEqual(2, arc.episode_count_min)
        self.assertEqual(3, arc.episode_count_max)
        self.assertIn(
            "dish_and_guest_action_payoff",
            arc.rewards_paid,
        )
        self.assertIn(
            "doyun_return_to_daughter",
            arc.rewards_deferred,
        )

    def test_manifest_keeps_hil2_unapproved_and_hil3_blocked(self) -> None:
        manifest = json.loads(
            (OUTPUT_ROOT / "manifest.json").read_text(encoding="utf-8")
        )

        self.assertEqual("candidate", manifest["status"])
        self.assertEqual("not_started", manifest["owner_approval"])
        self.assertFalse(manifest["external_promotion_allowed"])
        self.assertEqual(
            "blocked_until_hil2_owner_approval",
            manifest["hil3_status"],
        )
        self.assertEqual(
            "pending_not_evaluated",
            manifest["causal_chain_distance_status"],
        )
        self.assertEqual(
            canonical_sha256(build_distance_status()),
            manifest["causal_chain_distance_status_sha256"],
        )
        self.assertEqual(
            canonical_text_sha256(
                ADAPTATION_MAP_PATH.read_text(encoding="utf-8")
            ),
            manifest["adaptation_map_sha256"],
        )
        self.assertEqual(
            "working_sketch_not_hil3",
            manifest["episode_001_rough_status"],
        )
        self.assertEqual(
            canonical_text_sha256(
                EP001_ROUGH_PATH.read_text(encoding="utf-8")
            ),
            manifest["episode_001_rough_beat_sheet_sha256"],
        )

    def test_adaptation_map_closes_the_premiere_payoff_gap(self) -> None:
        adaptation_map = ADAPTATION_MAP_PATH.read_text(encoding="utf-8")

        self.assertIn("성공하는 첫 코스", adaptation_map)
        self.assertIn("속도를 올려 완식", adaptation_map)
        self.assertIn("첫 8초에 도윤이 왜 죽었고", adaptation_map)
        self.assertNotIn("그릇을 돌려준다", adaptation_map)
        self.assertIn("한 그릇을 수명·점수·레벨로 환산하지 않는다", adaptation_map)
        self.assertIn("명계시장·군중 판매·다수 상인", adaptation_map)
        self.assertIn("부녀 관계, 대체 가족, 로맨스", adaptation_map)
        self.assertIn("1~3화 캐릭터 어필 비트", adaptation_map)
        self.assertIn("왕실식 말투", adaptation_map)
        self.assertIn("캐릭터 어필을 점수화", adaptation_map)

    def test_episode_one_rough_sheet_is_bounded_but_not_hil3(self) -> None:
        rough = EP001_ROUGH_PATH.read_text(encoding="utf-8")

        self.assertIn("상태: `working_sketch`", rough)
        self.assertIn("HIL 3 대본: `아님`", rough)
        self.assertIn("목표 러닝타임: `270초`", rough)
        self.assertIn("S01", rough)
        self.assertIn("S06", rough)
        self.assertIn("120초 조리 하이라이트", rough)
        self.assertIn("도윤 무패 원칙", rough)
        self.assertIn("8초 안에 사고·딸·계약을 설명하지 않는다", rough)
        self.assertIn("첫 코스가 명백히 맛있고", rough)
        self.assertIn("소녀의 귀여운 반응 뒤에 규칙 판단", rough)


if __name__ == "__main__":
    unittest.main()
