from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from tools.build_afterlife_restaurant_ep001_established_service_candidate import (  # noqa: E402
    OUTPUT_ROOT,
    SOURCE_SCAFFOLD_PATH,
    build_episode,
    build_research_receipt,
    export_author_self_review,
)
from tools.build_afterlife_restaurant_hil2_revision2_approved import (  # noqa: E402
    build_approval,
)
from v4_shortform_script_foundry.canonical import (  # noqa: E402
    canonical_text_sha256,
)
from v4_shortform_script_foundry.episode_script import (  # noqa: E402
    EpisodeObligationKind,
    EpisodeScriptStatus,
    EpisodeScriptVerifier,
)


class EstablishedServiceEpisodeOneTests(unittest.TestCase):
    def test_checked_in_outputs_are_current(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / "tools"
                    / "build_afterlife_restaurant_ep001_established_service_candidate.py"
                ),
                "--check",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_episode_binds_exact_approved_hil2_and_passes_contract(self) -> None:
        episode = build_episode()
        arc, receipt, _ = build_approval()
        report = EpisodeScriptVerifier().verify(episode, arc)

        self.assertTrue(report.passed, report.findings)
        self.assertEqual(EpisodeScriptStatus.CANDIDATE, episode.status)
        self.assertEqual(EpisodeObligationKind.CLOSURE, episode.obligation_kind)
        self.assertEqual(arc.content_sha256, episode.parent_arc_content_sha256)
        self.assertEqual(
            receipt.receipt_sha256,
            episode.parent_arc_approval_receipt_sha256,
        )
        self.assertEqual(275, episode.runtime_seconds)
        self.assertEqual(6, len(episode.scenes))
        self.assertEqual(105, episode.scenes[2].duration_seconds)
        self.assertEqual(69, episode.scenes[4].duration_seconds)
        self.assertEqual(12, episode.scenes[5].duration_seconds)
        self.assertLessEqual(sum(len(scene.dialogue) for scene in episode.scenes), 24)
        self.assertTrue(all(len(scene.dialogue) <= 6 for scene in episode.scenes))
        self.assertTrue(
            all(len(scene.principal_character_ids) <= 3 for scene in episode.scenes)
        )

    def test_food_guest_and_girl_actions_close_in_episode_one(self) -> None:
        episode = build_episode()
        prose = "\n".join(scene.observable_action for scene in episode.scenes)
        dialogue = "\n".join(
            line.text for scene in episode.scenes for line in scene.dialogue
        )

        self.assertIn("국물이 바닥까지 비칠 만큼 맑아질", prose)
        self.assertIn("별도 불향 국물", episode.original_contributions[0])
        self.assertIn("검은 주전자를 작은 보온 화로로 옮긴다", prose)
        self.assertIn("불향 진하게, 한 그릇 추가", prose)
        self.assertIn("실제로 먹어 비운다", prose)
        self.assertIn("검은 엽전을 놓고", prose)
        self.assertIn("문을 나간다", prose)
        self.assertIn("한 그릇 더. 불향은 그대로.", dialogue)
        self.assertEqual(
            (
                "dish_and_guest_action_payoff",
                "story_unit_closure",
                "restaurant_operational_accumulation",
            ),
            episode.rewards_paid,
        )
        self.assertEqual(("doyun_return_to_daughter",), episode.rewards_deferred)

    def test_human_script_avoids_rejected_lines_and_machine_ids(self) -> None:
        script = (OUTPUT_ROOT / "episode_001_script_candidate.md").read_text(
            encoding="utf-8"
        )
        rejected = (
            "guest_kim_munseong",
            "underworld_girl",
            "아무거나 주시오",
            "삼도식당에 아무거나는 없느니라",
            "손님을 시험",
            "명경초다",
            "산 자의 혀",
            "처음 먹는 음식 아니더냐",
        )
        for phrase in rejected:
            self.assertNotIn(phrase, script)
        self.assertIn("오늘 망각어 살이 좋습니다", script)
        self.assertIn("첫입부터 22초", script)
        self.assertIn("두 사람의 다음 영업 행동을 12초 코다로 남긴다", script)
        self.assertIn("2화 대본 생성: `이번 범위 아님`", script)

    def test_research_and_promotion_boundaries_remain_closed(self) -> None:
        manifest = json.loads(
            (OUTPUT_ROOT / "manifest.json").read_text(encoding="utf-8")
        )
        research = build_research_receipt()
        self.assertEqual("candidate", manifest["status"])
        self.assertEqual("ep001_only", manifest["episode_scope"])
        self.assertEqual("not_started", manifest["br0_status"])
        self.assertEqual("not_started", manifest["br1_status"])
        self.assertEqual("not_started", manifest["owner_approval"])
        self.assertFalse(manifest["external_promotion_allowed"])
        self.assertEqual("pending_not_evaluated", manifest["scene_distance_status"])
        self.assertFalse(research["generator_ingest_allowed"])
        self.assertFalse(research["raw_reference_dialogue_ingested"])
        self.assertEqual(
            canonical_text_sha256(
                SOURCE_SCAFFOLD_PATH.read_text(encoding="utf-8")
            ),
            manifest["source_scaffold_sha256"],
        )
        self.assertFalse(any("002" in path.name for path in OUTPUT_ROOT.iterdir()))

    def test_author_self_review_is_explicitly_not_independent_review(self) -> None:
        review = export_author_self_review(build_episode())
        self.assertIn("독립 BR0·BR1이 아닌 집필자 자체 점검", review)
        self.assertIn("판정: `통과`", review)
        self.assertIn("남은 실제 위험", review)
        self.assertIn("손 안→바깥주머니", review)


if __name__ == "__main__":
    unittest.main()
