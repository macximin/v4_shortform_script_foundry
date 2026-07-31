from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from test_hil_contracts import (  # noqa: E402
    digest,
    make_arc,
    make_arc_receipt,
    make_canonical,
    make_canonical_receipt,
)
from v4_shortform_script_foundry.beat_patterns import (  # noqa: E402
    BeatPatternKind,
)
from v4_shortform_script_foundry.canonical import (  # noqa: E402
    canonical_sha256,
)
from v4_shortform_script_foundry.source_distance_import import (  # noqa: E402
    ImportedSourceDistanceReceipt,
    bind_source_distance_receipt,
    load_source_distance_receipt,
)
from v4_shortform_script_foundry.writer_adapter import (  # noqa: E402
    CreativeWriterAdapter,
    WriterRequest,
)


class SyntheticBackend:
    backend_id = "synthetic-backend"

    def __init__(self, output: dict[str, object]) -> None:
        self.output = output
        self.seen_request: WriterRequest | None = None

    def generate(self, request: WriterRequest) -> dict[str, object]:
        self.seen_request = request
        return self.output


def valid_output(episode_id: str) -> dict[str, object]:
    return {
        "episode_id": episode_id,
        "scenes": [
            {
                "scene_id": "S01",
                "location": "dispatch_floor",
                "purpose": "make the public test visible",
                "observable_action": (
                    "the analyst freezes one handoff and starts a wall timer"
                ),
                "causal_role": "meaningful_choice",
                "renderer_primary": "competence",
                "renderer_secondary": ["social_recognition"],
                "duration_seconds": 40,
                "dialogue": [
                    {
                        "speaker_id": "lead",
                        "text": "Choose the queue before the timer expires.",
                        "function": "state_public_test",
                    }
                ],
                "information_revealed_ids": ["evaluation_rule"],
                "information_withheld_ids": ["final_assignment"],
                "state_delta_codes": ["test:offered->accepted"],
                "tension_delta": "public_failure_cost_increases",
            },
            {
                "scene_id": "S02",
                "location": "dispatch_floor",
                "purpose": "convert action into provisional authority",
                "observable_action": (
                    "the risky queue stays frozen while the safe queue clears"
                ),
                "causal_role": "meaningful_action",
                "renderer_primary": "competence",
                "renderer_secondary": ["social_recognition"],
                "duration_seconds": 50,
                "dialogue": [
                    {
                        "speaker_id": "lead",
                        "text": "Keep the console. The next decision is yours.",
                        "function": "grant_provisional_authority",
                    }
                ],
                "information_revealed_ids": ["test_result"],
                "information_withheld_ids": ["long_term_trust"],
                "state_delta_codes": [
                    "new_group_status:unknown->provisionally_trusted"
                ],
                "tension_delta": "new_authority_creates_next_cost",
            },
        ],
        "final_state_delta_codes": [
            "belonging:excluded->provisional_new_group"
        ],
        "rewards_paid": ["new_group_professional_trust"],
        "rewards_deferred": ["old_group_public_reclassification"],
        "obligation_kind": "continuation",
        "obligation": "next episode tests the cost of provisional authority",
        "original_contributions": [
            "a visible timeout transfers operational authority"
        ],
    }


class WriterAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.canonical = make_canonical()
        self.hil1 = make_canonical_receipt(self.canonical)
        self.arc = make_arc(self.canonical, self.hil1)
        self.hil2 = make_arc_receipt(self.arc, self.canonical, self.hil1)
        self.request = WriterRequest.build(
            canonical=self.canonical,
            canonical_approval=self.hil1,
            arc=self.arc,
            arc_approval=self.hil2,
            candidate_id="original-work:ep001:variant-a",
            episode_id="original-work:ep001",
            revision=1,
            producer_id="writer-a",
            source_scaffold_sha256=digest("writer-scaffold"),
            target_runtime_seconds=90,
            beat_pattern=BeatPatternKind.COMPETENCE_RECOGNITION,
        )

    def test_adapter_returns_unscreened_draft_without_raw_source(self) -> None:
        backend = SyntheticBackend(valid_output(self.request.episode_id))

        draft = CreativeWriterAdapter().generate(
            self.request,
            backend,
            self.arc,
        )

        self.assertEqual(self.request, backend.seen_request)
        self.assertNotIn("source_text", repr(self.request))
        self.assertNotIn("reference", repr(self.request))
        self.assertEqual(90, sum(scene.duration_seconds for scene in draft.scenes))
        self.assertEqual(
            self.request.candidate_id,
            draft.source_distance_projection.candidate_id,
        )

    def test_adapter_rejects_unexpected_structured_output_field(self) -> None:
        output = valid_output(self.request.episode_id)
        output["raw_source_text"] = "must not cross this boundary"

        with self.assertRaisesRegex(ValueError, "keys mismatch"):
            CreativeWriterAdapter().generate(
                self.request,
                SyntheticBackend(output),
                self.arc,
            )

    def test_adapter_rejects_renderer_outside_arc(self) -> None:
        output = valid_output(self.request.episode_id)
        scenes = output["scenes"]
        assert isinstance(scenes, list)
        first = scenes[0]
        assert isinstance(first, dict)
        first["renderer_primary"] = "resource"

        with self.assertRaisesRegex(ValueError, "RENDERER_OUTSIDE_ARC_MIX"):
            CreativeWriterAdapter().generate(
                self.request,
                SyntheticBackend(output),
                self.arc,
            )

    def test_exact_approval_hash_is_required(self) -> None:
        with self.assertRaisesRegex(ValueError, "exact approval"):
            WriterRequest.build(
                canonical=self.canonical,
                canonical_approval=self.hil1,
                arc=self.arc,
                arc_approval=self.hil1,
                candidate_id="variant",
                episode_id="original-work:ep001",
                revision=1,
                producer_id="writer-a",
                source_scaffold_sha256=digest("writer-scaffold"),
                target_runtime_seconds=90,
                beat_pattern=BeatPatternKind.COMPETENCE_RECOGNITION,
            )

    def test_pass_receipt_binds_draft_and_creates_candidate(self) -> None:
        draft = CreativeWriterAdapter().generate(
            self.request,
            SyntheticBackend(valid_output(self.request.episode_id)),
            self.arc,
        )
        projection = draft.source_distance_projection
        payload = {
            "receipt_version": "1",
            "evaluator_version": "source-distance-v1",
            "candidate_id": projection.candidate_id,
            "candidate_projection_sha256": projection.projection_sha256,
            "reference_manifest_sha256": "1" * 64,
            "policy_id": "calibrated-policy",
            "policy_version": "v1",
            "policy_tier": "production_approved",
            "policy_content_sha256": "2" * 64,
            "calibration_receipt_sha256": "3" * 64,
            "decision": "pass",
            "metrics": [],
            "evaluated_at": "2026-07-30T15:00:00+09:00",
        }
        receipt = ImportedSourceDistanceReceipt.from_mapping(
            {
                **payload,
                "receipt_sha256": canonical_sha256(payload),
            }
        )

        candidate = bind_source_distance_receipt(draft, receipt)

        self.assertEqual(
            receipt.receipt_sha256,
            candidate.source_distance_receipt_sha256,
        )
        self.assertEqual("candidate", candidate.status.value)

    def test_review_required_receipt_cannot_create_candidate(self) -> None:
        draft = CreativeWriterAdapter().generate(
            self.request,
            SyntheticBackend(valid_output(self.request.episode_id)),
            self.arc,
        )
        projection = draft.source_distance_projection
        payload = {
            "receipt_version": "1",
            "evaluator_version": "source-distance-v1",
            "candidate_id": projection.candidate_id,
            "candidate_projection_sha256": projection.projection_sha256,
            "reference_manifest_sha256": "1" * 64,
            "policy_id": "calibrated-policy",
            "policy_version": "v1",
            "policy_tier": "synthetic_canary",
            "policy_content_sha256": "2" * 64,
            "calibration_receipt_sha256": "3" * 64,
            "decision": "review_required",
            "metrics": [],
            "evaluated_at": "2026-07-30T15:00:00+09:00",
        }

        with self.assertRaisesRegex(ValueError, "only pass"):
            ImportedSourceDistanceReceipt.from_mapping(
                {
                    **payload,
                    "receipt_sha256": canonical_sha256(payload),
                }
            )

    def test_checked_in_manual_eval_receipt_binds_exact_projection(self) -> None:
        draft = CreativeWriterAdapter().generate(
            self.request,
            SyntheticBackend(valid_output(self.request.episode_id)),
            self.arc,
        )
        receipt = load_source_distance_receipt(
            ROOT
            / "imports"
            / "source_distance"
            / "synthetic_ep001_variant_a_receipt_v1.json"
        )

        candidate = bind_source_distance_receipt(
            draft,
            receipt,
            allow_synthetic_canary=True,
        )

        self.assertEqual(
            "d5dfc35e063009ff08fe9e46c5e48eeeb6344796b61b7987bf506f1cccbec12c",
            candidate.source_distance_receipt_sha256,
        )

    def test_synthetic_policy_receipt_is_blocked_by_default(self) -> None:
        draft = CreativeWriterAdapter().generate(
            self.request,
            SyntheticBackend(valid_output(self.request.episode_id)),
            self.arc,
        )
        receipt = load_source_distance_receipt(
            ROOT
            / "imports"
            / "source_distance"
            / "synthetic_ep001_variant_a_receipt_v1.json"
        )

        with self.assertRaisesRegex(ValueError, "production-approved"):
            bind_source_distance_receipt(draft, receipt)


if __name__ == "__main__":
    unittest.main()
