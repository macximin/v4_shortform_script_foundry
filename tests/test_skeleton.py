from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class SkeletonTests(unittest.TestCase):
    def test_core_boundaries_are_importable(self) -> None:
        modules = (
            "approval",
            "arc_contract",
            "beat_patterns",
            "canonical_package",
            "creative_review",
            "episode_script",
            "fact_ledger",
            "planning_artifact",
            "renderer_router",
            "episode_state",
            "script_packet",
            "verification",
        )

        for module in modules:
            with self.subTest(module=module):
                importlib.import_module(f"v4_shortform_script_foundry.{module}")

    def test_legacy_foundry_assets_are_not_present(self) -> None:
        forbidden_paths = (
            ROOT / "40_works",
            ROOT / "45_screenworks",
            ROOT / "tools" / "draft_relay",
        )

        self.assertFalse(any(path.exists() for path in forbidden_paths))


if __name__ == "__main__":
    unittest.main()
