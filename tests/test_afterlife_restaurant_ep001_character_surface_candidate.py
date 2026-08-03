from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from tools.build_afterlife_restaurant_ep001_character_surface_candidate import (  # noqa: E402
    OUTPUT_ROOT,
    PREVIOUS_OUTPUT_ROOT,
    SOURCE_SCAFFOLD_PATH,
    build_episode,
    build_format_receipt,
)
from tools.build_afterlife_restaurant_ep001_established_service_candidate import (  # noqa: E402
    build_episode as build_previous_episode,
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


class CharacterSurfaceEpisodeOneTests(unittest.TestCase):
    def test_checked_in_outputs_are_current(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / "tools"
                    / "build_afterlife_restaurant_ep001_character_surface_candidate.py"
                ),
                "--check",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_episode_stays_bound_to_approved_hil2(self) -> None:
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
        self.assertEqual(36, episode.scenes[0].duration_seconds)
        self.assertEqual(100, episode.scenes[2].duration_seconds)
        self.assertEqual(12, episode.scenes[-1].duration_seconds)
        self.assertTrue(all(len(scene.dialogue) <= 6 for scene in episode.scenes))
        self.assertTrue(
            all(len(scene.principal_character_ids) <= 3 for scene in episode.scenes)
        )

    def test_first_scene_proves_both_leads_before_guest_arrives(self) -> None:
        episode = build_episode()
        first = episode.scenes[0]
        action = first.observable_action
        dialogue = "\n".join(line.text for line in first.dialogue)

        self.assertNotIn("guest_kim_munseong", first.principal_character_ids)
        self.assertIn("돌아보지 않고 칼자루로", action)
        self.assertIn("칼이 한 번 지나간다", action)
        self.assertIn("굵은 소금 두 알", action)
        self.assertIn("개점이다! 오늘 첫 그릇은 내 것이다!", dialogue)
        self.assertIn("맛보기는 끼니가 아니니라", dialogue)
        self.assertIn("오늘도 간신히 합격이다", dialogue)
        self.assertIn("접시를 꼭 끌어안고", action)
        self.assertIn("doyun_overwhelming_established_skill", first.information_revealed_ids)
        self.assertIn("girl_bright_royal_appetite", first.information_revealed_ids)

    def test_girl_has_playfulness_and_professional_judgment(self) -> None:
        episode = build_episode()
        cooking = episode.scenes[2]
        dialogue = "\n".join(line.text for line in cooking.dialogue)
        action = cooking.observable_action

        self.assertIn("한 숟갈만.", dialogue)
        self.assertIn("검은 주전자는 내가 맡겠다.", dialogue)
        self.assertIn("손님이 불에서 눈을 못 떼니라.", dialogue)
        self.assertIn("국자를 내려놓고", action)
        self.assertIn("보온 화로에 올리고", action)
        self.assertIn("girl_role:playful_taster->necessary_service_observer", cooking.state_delta_codes)

    def test_doyun_never_fails_and_guest_closes(self) -> None:
        episode = build_episode()
        prose = "\n".join(scene.observable_action for scene in episode.scenes)
        dialogue = "\n".join(
            line.text for scene in episode.scenes for line in scene.dialogue
        )

        self.assertNotIn("실패", prose + dialogue)
        self.assertNotIn("맛없", prose + dialogue)
        self.assertIn("국물이 바닥까지 비칠 만큼 맑아진다", prose)
        self.assertIn("맛보고 고개를 끄덕인다", prose)
        self.assertIn("건더기와 국물을 모두 비운다", prose)
        self.assertIn("이번에도 국물 한 방울 남기지 않는다", prose)
        self.assertIn("검은 엽전을 놓는다", prose)
        self.assertIn("문을 나간다", prose)
        self.assertIn("한 그릇 더 주시오.", dialogue)
        self.assertEqual(
            (
                "dish_and_guest_action_payoff",
                "story_unit_closure",
                "restaurant_operational_accumulation",
            ),
            episode.rewards_paid,
        )

    def test_human_surface_contains_only_readable_screenplay_layers(self) -> None:
        script = (OUTPUT_ROOT / "episode_001_human_screenplay.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("# 제1화 오늘 망각어가 좋습니다", script)
        self.assertIn("## 1. 삼도식당 주방 / 실내 / 밤", script)
        self.assertIn("    소녀      개점이다!", script)
        self.assertIn("    도윤      공주님께선", script)
        self.assertIn("끝.", script)
        for forbidden in (
            "장면 목적",
            "컷 설계",
            "소리와 편집",
            "회차 약속",
            "이번 화에서 닫히는 것",
            "승격 경계",
            "HIL",
            "BR0",
            "guest_kim_munseong",
            "underworld_girl",
            "samdo_open_kitchen",
            "두 번째 맛도 손님이 고르기 전에 완성된다",
        ):
            self.assertNotIn(forbidden, script)

    def test_rejected_old_lines_and_exposition_do_not_return(self) -> None:
        script = (OUTPUT_ROOT / "episode_001_human_screenplay.md").read_text(
            encoding="utf-8"
        )
        for phrase in (
            "아무거나 주시오",
            "삼도식당에 아무거나는 없느니라",
            "손님을 시험",
            "명경초다",
            "산 자의 혀",
            "처음 먹는 음식 아니더냐",
            "현실의 딸",
            "계약",
            "개업 과정",
        ):
            self.assertNotIn(phrase, script)

    def test_production_and_review_layers_are_separate(self) -> None:
        script = (OUTPUT_ROOT / "episode_001_human_screenplay.md").read_text(
            encoding="utf-8"
        )
        breakdown = (OUTPUT_ROOT / "production_scene_breakdown.md").read_text(
            encoding="utf-8"
        )
        review = (OUTPUT_ROOT / "author_self_review.md").read_text(encoding="utf-8")

        self.assertNotIn("0:00-0:36", script)
        self.assertIn("0:00-0:36", breakdown)
        self.assertIn("승격 경계", breakdown)
        self.assertIn("독립 BR0·BR1이 아니다", review)
        self.assertIn("45/50", review)
        self.assertIn("남은 연출 위험", review)

    def test_manifest_supersedes_old_candidate_without_promotion(self) -> None:
        manifest = json.loads(
            (OUTPUT_ROOT / "manifest.json").read_text(encoding="utf-8")
        )
        previous_episode = build_previous_episode()
        format_receipt = build_format_receipt()

        self.assertEqual("candidate", manifest["status"])
        self.assertEqual("ep001_only", manifest["episode_scope"])
        self.assertEqual(
            previous_episode.content_sha256,
            manifest["supersedes_candidate_content_sha256"],
        )
        self.assertEqual(
            PREVIOUS_OUTPUT_ROOT.relative_to(ROOT).as_posix(),
            manifest["supersedes_candidate_path"],
        )
        self.assertEqual("pending_not_evaluated", manifest["scene_distance_status"])
        self.assertEqual("not_started", manifest["br0_status"])
        self.assertEqual("not_started", manifest["br1_status"])
        self.assertEqual("not_started", manifest["owner_approval"])
        self.assertFalse(manifest["external_promotion_allowed"])
        self.assertFalse(format_receipt["raw_reference_dialogue_ingested"])
        self.assertFalse(format_receipt["raw_reference_event_order_ingested"])
        self.assertFalse(format_receipt["generator_ingest_allowed"])
        self.assertEqual(
            canonical_text_sha256(
                SOURCE_SCAFFOLD_PATH.read_text(encoding="utf-8")
            ),
            manifest["source_scaffold_sha256"],
        )
        self.assertFalse(any("002" in path.name for path in OUTPUT_ROOT.iterdir()))


if __name__ == "__main__":
    unittest.main()
