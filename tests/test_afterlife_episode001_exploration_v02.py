from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_ROOT = ROOT / "artifacts" / "candidates" / "afterlife_restaurant"
STORYBOARD_PATH = CANDIDATE_ROOT / "episode_001_storyboard_exploration_v0.2.md"
STATUS_PATH = CANDIDATE_ROOT / "replanning_status_v0.2.md"
REFERENCE_PATH = CANDIDATE_ROOT / "reference_01_nobu_episode1_analysis_v0.1.md"


class AfterlifeEpisode001ExplorationV02Tests(unittest.TestCase):
    def test_replanning_stays_open(self) -> None:
        status = STATUS_PATH.read_text(encoding="utf-8")

        self.assertIn("상태: 열림", status)
        self.assertIn("개업한 지 시간이 지났다", status)
        self.assertIn("저승 식재료의 맛과 손질법을 이미 안다", status)
        self.assertIn("기존 1화 글콘티 후보: 폐기 대기", status)
        self.assertIn("외부 전달과 승인본 승격은 별도 결정 전까지 금지", status)

    def test_storyboard_removes_learning_and_diagnostic_dialogue(self) -> None:
        storyboard = STORYBOARD_PATH.read_text(encoding="utf-8")

        self.assertIn("오늘 망각어가 좋습니다", storyboard)
        self.assertIn("두 번째 국물입니다", storyboard)
        self.assertIn("한 그릇 더 주시오", storyboard)
        self.assertIn("개업한 지 시간이 지남", storyboard)
        self.assertIn("저승 식재료에 익숙한 완성형 셰프", storyboard)
        self.assertNotIn("산 자의 혀", storyboard)
        self.assertNotIn("고르지 못하면", storyboard)
        self.assertNotIn("손님을 시험", storyboard)
        self.assertNotIn("처음 먹는 음식 아니더냐", storyboard)
        self.assertNotIn("실패", storyboard)
        self.assertNotIn("—", storyboard)
        self.assertIsNone(re.search(r"[A-Za-z_]", storyboard))

    def test_reference_analysis_marks_evidence_limit_and_copy_boundary(self) -> None:
        reference = REFERENCE_PATH.read_text(encoding="utf-8")

        self.assertIn("한국 지역에서 재생이 제한", reference)
        self.assertIn("정확한 분초 기록이 아니라", reference)
        self.assertIn("삼도식당에 옮길 것", reference)
        self.assertIn("옮기지 않을 것", reference)


if __name__ == "__main__":
    unittest.main()
