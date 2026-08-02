from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from tools.build_afterlife_restaurant_ep001_candidate import (  # noqa: E402
    OUTPUT_ROOT,
    SOURCE_SCAFFOLD_PATH,
    build_episode,
)
from tools.build_afterlife_restaurant_hil2_arc01_approved import (  # noqa: E402
    build_approval,
)
from v4_shortform_script_foundry.episode_script import (  # noqa: E402
    EpisodeObligationKind,
    EpisodeScriptStatus,
    EpisodeScriptVerifier,
)


class AfterlifeRestaurantEp001CandidateTests(unittest.TestCase):
    def test_checked_in_episode_is_current(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / "tools"
                    / "build_afterlife_restaurant_ep001_candidate.py"
                ),
                "--check",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_episode_binds_approved_arc_and_passes_hard_checks(self) -> None:
        episode = build_episode()
        arc, receipt, _ = build_approval()

        report = EpisodeScriptVerifier().verify(episode, arc)

        self.assertTrue(report.passed, report.findings)
        self.assertEqual(EpisodeScriptStatus.CANDIDATE, episode.status)
        self.assertEqual(270, episode.runtime_seconds)
        self.assertEqual(6, len(episode.scenes))
        self.assertEqual(arc.content_sha256, episode.parent_arc_content_sha256)
        self.assertEqual(
            receipt.receipt_sha256,
            episode.parent_arc_approval_receipt_sha256,
        )
        self.assertEqual(
            EpisodeObligationKind.CONTINUATION,
            episode.obligation_kind,
        )
        self.assertTrue(
            all(len(scene.principal_character_ids) <= 3 for scene in episode.scenes)
        )
        self.assertTrue(all(len(scene.dialogue) <= 6 for scene in episode.scenes))

    def test_manifest_keeps_review_and_promotion_closed(self) -> None:
        manifest = json.loads(
            (OUTPUT_ROOT / "manifest.json").read_text(encoding="utf-8")
        )
        storyboard = (
            OUTPUT_ROOT / "episode_001_storyboard_candidate.md"
        ).read_text(encoding="utf-8")

        self.assertEqual("candidate", manifest["status"])
        self.assertEqual("not_started", manifest["br0_status"])
        self.assertEqual("not_started", manifest["br1_status"])
        self.assertEqual("not_started", manifest["owner_approval"])
        self.assertFalse(manifest["external_promotion_allowed"])
        self.assertEqual(
            hashlib.sha256(SOURCE_SCAFFOLD_PATH.read_bytes()).hexdigest(),
            manifest["source_scaffold_sha256"],
        )
        self.assertEqual(
            hashlib.sha256(storyboard.encode("utf-8")).hexdigest(),
            manifest["storyboard_sha256"],
        )

    def test_storyboard_preserves_undefeated_opening_and_human_prose(self) -> None:
        storyboard = (
            OUTPUT_ROOT / "episode_001_storyboard_candidate.md"
        ).read_text(encoding="utf-8")

        self.assertIn("장면 1 0:00-0:08", storyboard)
        self.assertIn("- 김문성: 아무거나 주시오", storyboard)
        self.assertIn("- 소녀: 삼도식당에 아무거나는 없느니라", storyboard)
        self.assertIn("- 도윤: 고르지 못하면, 반응부터 보죠", storyboard)
        self.assertIn("도윤은 처음 보는 저승 재료로 망각어 불향 맑은국을", storyboard)
        self.assertIn("화면에 '망각어 불향 맑은국'이 뜬다", storyboard)
        self.assertNotIn("망각어가 도마 위에서 몸을 꺾을 때", storyboard)
        self.assertIn("첫 코스가 명백히 맛있고", SOURCE_SCAFFOLD_PATH.read_text())
        self.assertNotIn("맛없", storyboard)
        self.assertNotIn("실패", storyboard)
        self.assertNotIn("—", storyboard)
        self.assertIsNone(re.search(r"[A-Za-z_]", storyboard))
        self.assertIn("1차 구조 감리: 시작 전", storyboard)
        self.assertIn("책임자 승인: 시작 전", storyboard)


if __name__ == "__main__":
    unittest.main()
