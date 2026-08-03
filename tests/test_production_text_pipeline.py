from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from v4_shortform_script_foundry.canonical import canonical_text_sha256
from v4_shortform_script_foundry.artifact_graph import (
    ArtifactGraph,
    ArtifactNode,
    ArtifactNodeKind,
)
from v4_shortform_script_foundry.episode_script_text import (
    EpisodeScriptText,
    EpisodeScriptTextStatus,
    ScriptAtom,
    ScriptAtomKind,
)
from v4_shortform_script_foundry.production_annotation import (
    ProductionAnnotation,
    ProductionAnnotationKind,
    ProductionAnnotationSet,
    ProductionAnnotationStatus,
    ProductionAnnotationVerifier,
)
from v4_shortform_script_foundry.production_gate import (
    ProductionApprovalReceipt,
    ProductionDecision,
    ProductionGate,
    require_exact_approval,
)
from v4_shortform_script_foundry.production_package import (
    ProductionPackageStatus,
    ProductionTextPackage,
    build_production_text_package,
)
from v4_shortform_script_foundry.production_surface import (
    HumanProductionSurface,
    ProductionSurfaceVerifier,
    RenderedAtom,
    SamdoKoreanShootingSurfaceRenderer,
    build_production_surface,
)
from v4_shortform_script_foundry.story_change_request import (
    StoryChangeDecision,
    StoryChangeRequest,
    StoryChangeRequestVerifier,
    StoryChangeType,
)


CONTRACT_SHA = "1" * 64


def build_story(
    status: EpisodeScriptTextStatus = EpisodeScriptTextStatus.APPROVED,
    *,
    revision: int = 1,
    dialogue: str = "개점이니라!",
) -> EpisodeScriptText:
    return EpisodeScriptText(
        work_id="afterlife_restaurant",
        episode_id="afterlife_restaurant:ep001",
        revision=revision,
        parent_episode_contract_sha256=CONTRACT_SHA,
        status=status,
        atoms=(
            ScriptAtom(
                "S01-H",
                "S01",
                1,
                ScriptAtomKind.SCENE_HEADING,
                "1. 삼도식당. 홀 (실내/밤)",
            ),
            ScriptAtom(
                "S01-A01",
                "S01",
                2,
                ScriptAtomKind.ACTION,
                "연화가 영업 목패를 건다.",
            ),
            ScriptAtom(
                "S01-D01",
                "S01",
                3,
                ScriptAtomKind.DIALOGUE,
                dialogue,
                speaker_id="연화",
            ),
            ScriptAtom(
                "S01-S01",
                "S01",
                4,
                ScriptAtomKind.SFX,
                "SFX (화면 안): 탁.",
            ),
        ),
    )


def build_annotation_set(
    story: EpisodeScriptText,
    surface: HumanProductionSurface,
    *,
    anchor_atom_id: str = "S01-A01",
    required: bool = False,
    reviewer_role: str | None = "director",
) -> ProductionAnnotationSet:
    return ProductionAnnotationSet(
        annotation_set_id="afterlife_restaurant:ep001:camera:v1",
        source_episode_text_sha256=story.content_sha256,
        source_surface_sha256=surface.content_sha256,
        status=ProductionAnnotationStatus.CANDIDATE,
        annotations=(
            ProductionAnnotation(
                annotation_id="CAM-001",
                kind=ProductionAnnotationKind.CAMERA,
                anchor_atom_id=anchor_atom_id,
                intent="개점 동작과 영업등 인과를 한 쇼트로 읽힌다",
                instruction="목패를 따라 틸트한 뒤 영업등에서 멈춘다.",
                required=required,
                reviewer_role=reviewer_role,
            ),
        ),
    )


def approval(
    gate: ProductionGate,
    artifact_id: str,
    artifact_sha256: str,
    *,
    actor_role: str,
) -> ProductionApprovalReceipt:
    return ProductionApprovalReceipt(
        gate=gate,
        artifact_id=artifact_id,
        artifact_sha256=artifact_sha256,
        decision=ProductionDecision.APPROVE,
        actor_id=f"test_{actor_role}",
        actor_role=actor_role,
        decided_at="2026-08-03T12:00:00+09:00",
        note="contract test approval",
    )


class ProductionTextPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.renderer = SamdoKoreanShootingSurfaceRenderer()
        self.story = build_story()
        self.surface = build_production_surface(
            self.story,
            surface_id="afterlife_restaurant:ep001:surface:v1",
            renderer=self.renderer,
        )
        self.annotations = build_annotation_set(self.story, self.surface)

    def test_text_hash_is_stable_across_line_endings(self) -> None:
        self.assertEqual(
            canonical_text_sha256("첫 줄\n둘째 줄\n"),
            canonical_text_sha256("첫 줄\r\n둘째 줄\r\n"),
        )

    def test_story_status_does_not_change_story_content_hash(self) -> None:
        candidate = replace(self.story, status=EpisodeScriptTextStatus.CANDIDATE)
        self.assertEqual(candidate.content_sha256, self.story.content_sha256)

    def test_scene_atoms_cannot_reopen_a_closed_scene(self) -> None:
        atoms = list(self.story.atoms)
        atoms.extend(
            (
                ScriptAtom(
                    "S02-H",
                    "S02",
                    5,
                    ScriptAtomKind.SCENE_HEADING,
                    "2. 삼도식당. 주방 (실내/밤)",
                ),
                ScriptAtom(
                    "S01-A02",
                    "S01",
                    6,
                    ScriptAtomKind.ACTION,
                    "도윤이 불을 켠다.",
                ),
            )
        )
        with self.assertRaisesRegex(ValueError, "contiguous block"):
            replace(self.story, atoms=tuple(atoms))

    def test_surface_source_hash_requires_lowercase_hex(self) -> None:
        with self.assertRaisesRegex(ValueError, "lowercase SHA-256"):
            replace(self.surface, source_episode_text_sha256="Z" * 64)

    def test_surface_is_deterministic_and_preserves_atom_order(self) -> None:
        again = build_production_surface(
            self.story,
            surface_id=self.surface.surface_id,
            renderer=self.renderer,
        )
        report = ProductionSurfaceVerifier().verify(
            self.surface,
            self.story,
            self.renderer,
        )
        self.assertTrue(report.passed)
        self.assertEqual(self.surface.content_sha256, again.content_sha256)
        self.assertIn("    연화    개점이니라!", self.surface.rendered_text)

    def test_surface_tamper_is_rejected(self) -> None:
        rendered = list(self.surface.rendered_atoms)
        rendered[1] = RenderedAtom("S01-A01", "연화가 목패를 던진다.")
        tampered = replace(self.surface, rendered_atoms=tuple(rendered))
        report = ProductionSurfaceVerifier().verify(
            tampered,
            self.story,
            self.renderer,
        )
        self.assertFalse(report.passed)
        self.assertIn(
            "RENDERED_ATOM_MISMATCH",
            {finding.code for finding in report.findings},
        )

    def test_annotation_is_separate_from_story_content_hash(self) -> None:
        original_hash = self.story.content_sha256
        report = ProductionAnnotationVerifier().verify(
            self.annotations,
            self.story,
            self.surface,
        )
        self.assertTrue(report.passed)
        self.assertEqual(original_hash, self.story.content_sha256)

    def test_annotation_rejects_unknown_anchor(self) -> None:
        annotations = build_annotation_set(
            self.story,
            self.surface,
            anchor_atom_id="missing",
        )
        report = ProductionAnnotationVerifier().verify(
            annotations,
            self.story,
            self.surface,
        )
        self.assertIn(
            "UNKNOWN_ATOM_ANCHOR",
            {finding.code for finding in report.findings},
        )

    def test_required_annotation_needs_reviewer_role(self) -> None:
        annotations = build_annotation_set(
            self.story,
            self.surface,
            required=True,
            reviewer_role=None,
        )
        report = ProductionAnnotationVerifier().verify(
            annotations,
            self.story,
            self.surface,
        )
        self.assertIn(
            "REQUIRED_WITHOUT_REVIEWER_ROLE",
            {finding.code for finding in report.findings},
        )

    def test_package_requires_owner_approved_story(self) -> None:
        story = replace(self.story, status=EpisodeScriptTextStatus.CANDIDATE)
        surface = build_production_surface(
            story,
            surface_id=self.surface.surface_id,
            renderer=self.renderer,
        )
        annotations = build_annotation_set(story, surface)
        p0 = approval(
            ProductionGate.P0_SURFACE_EQUIVALENCE,
            surface.surface_id,
            surface.content_sha256,
            actor_role="system_verifier",
        )
        p1 = approval(
            ProductionGate.P1_ANNOTATION_REVIEW,
            annotations.annotation_set_id,
            annotations.content_sha256,
            actor_role="director",
        )
        with self.assertRaisesRegex(ValueError, "owner-approved story"):
            build_production_text_package(
                package_id="afterlife_restaurant:ep001:production:v1",
                source=story,
                surface=surface,
                renderer=self.renderer,
                annotation_set=annotations,
                p0_receipt=p0,
                p1_receipt=p1,
            )

    def test_package_binds_exact_surface_and_annotation_receipts(self) -> None:
        p0 = approval(
            ProductionGate.P0_SURFACE_EQUIVALENCE,
            self.surface.surface_id,
            self.surface.content_sha256,
            actor_role="system_verifier",
        )
        p1 = approval(
            ProductionGate.P1_ANNOTATION_REVIEW,
            self.annotations.annotation_set_id,
            self.annotations.content_sha256,
            actor_role="director",
        )
        package = build_production_text_package(
            package_id="afterlife_restaurant:ep001:production:v1",
            source=self.story,
            surface=self.surface,
            renderer=self.renderer,
            annotation_set=self.annotations,
            p0_receipt=p0,
            p1_receipt=p1,
        )
        self.assertIs(package.status, ProductionPackageStatus.CANDIDATE)
        self.assertFalse(package.external_delivery_allowed)
        self.assertEqual(self.story.content_sha256, package.source_episode_text_sha256)

    def test_package_rejects_stale_receipt_hash(self) -> None:
        p0 = approval(
            ProductionGate.P0_SURFACE_EQUIVALENCE,
            self.surface.surface_id,
            "0" * 64,
            actor_role="system_verifier",
        )
        p1 = approval(
            ProductionGate.P1_ANNOTATION_REVIEW,
            self.annotations.annotation_set_id,
            self.annotations.content_sha256,
            actor_role="director",
        )
        with self.assertRaisesRegex(ValueError, "exact artifact hash"):
            build_production_text_package(
                package_id="afterlife_restaurant:ep001:production:v1",
                source=self.story,
                surface=self.surface,
                renderer=self.renderer,
                annotation_set=self.annotations,
                p0_receipt=p0,
                p1_receipt=p1,
            )

    def test_external_delivery_cannot_be_auto_enabled(self) -> None:
        with self.assertRaisesRegex(ValueError, "auto-approve external delivery"):
            ProductionTextPackage(
                package_id="afterlife_restaurant:ep001:production:v1",
                source_episode_text_sha256="1" * 64,
                surface_sha256="2" * 64,
                annotation_set_sha256="3" * 64,
                p0_receipt_sha256="4" * 64,
                p1_receipt_sha256="5" * 64,
                status=ProductionPackageStatus.CANDIDATE,
                external_delivery_allowed=True,
            )

    def test_only_owner_can_approve_external_delivery(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot approve"):
            approval(
                ProductionGate.EXTERNAL_DELIVERY,
                "package",
                "1" * 64,
                actor_role="producer",
            )

    def test_p2_receipt_approves_exact_candidate_package(self) -> None:
        p0 = approval(
            ProductionGate.P0_SURFACE_EQUIVALENCE,
            self.surface.surface_id,
            self.surface.content_sha256,
            actor_role="system_verifier",
        )
        p1 = approval(
            ProductionGate.P1_ANNOTATION_REVIEW,
            self.annotations.annotation_set_id,
            self.annotations.content_sha256,
            actor_role="director",
        )
        package = build_production_text_package(
            package_id="afterlife_restaurant:ep001:production:v1",
            source=self.story,
            surface=self.surface,
            renderer=self.renderer,
            annotation_set=self.annotations,
            p0_receipt=p0,
            p1_receipt=p1,
        )
        p2 = approval(
            ProductionGate.P2_TEXT_PACKAGE,
            package.package_id,
            package.content_sha256,
            actor_role="producer",
        )
        require_exact_approval(
            p2,
            gate=ProductionGate.P2_TEXT_PACKAGE,
            artifact_id=package.package_id,
            artifact_sha256=package.content_sha256,
        )

    def test_story_change_request_is_the_explicit_revision_route(self) -> None:
        request = StoryChangeRequest(
            request_id="afterlife_restaurant:ep001:scr:phone-handoff",
            source_episode_text_sha256=self.story.content_sha256,
            affected_atom_ids=("S01-A01",),
            change_type=StoryChangeType.ACTION,
            before="연화가 영업 목패를 건다.",
            after="연화가 영업 목패를 고리에 건다.",
            reason="행동 연결을 명시한다",
            owner_decision=StoryChangeDecision.PENDING,
        )
        report = StoryChangeRequestVerifier().verify(request, self.story)
        self.assertTrue(report.passed)
        self.assertFalse(request.can_create_revision)
        self.assertTrue(
            replace(
                request,
                owner_decision=StoryChangeDecision.APPROVED,
            ).can_create_revision
        )

    def test_new_story_revision_invalidates_old_surface_binding(self) -> None:
        revised = build_story(revision=2, dialogue="이제 개점이니라!")
        report = ProductionSurfaceVerifier().verify(
            self.surface,
            revised,
            self.renderer,
        )
        self.assertIn(
            "SOURCE_TEXT_HASH_MISMATCH",
            {finding.code for finding in report.findings},
        )

    def test_artifact_graph_orders_dependencies_and_propagates_stale(self) -> None:
        graph = ArtifactGraph(
            graph_id="afterlife_restaurant:ep001:production",
            nodes=(
                ArtifactNode(
                    "text",
                    ArtifactNodeKind.EPISODE_TEXT,
                    "1" * 64,
                ),
                ArtifactNode(
                    "surface",
                    ArtifactNodeKind.HUMAN_SURFACE,
                    "2" * 64,
                    ("text",),
                ),
                ArtifactNode(
                    "annotations",
                    ArtifactNodeKind.PRODUCTION_ANNOTATION,
                    "3" * 64,
                    ("text", "surface"),
                ),
                ArtifactNode(
                    "package",
                    ArtifactNodeKind.PRODUCTION_PACKAGE,
                    "4" * 64,
                    ("surface", "annotations"),
                ),
            ),
        )
        self.assertEqual(
            graph.topological_order(),
            ("text", "surface", "annotations", "package"),
        )
        self.assertEqual(
            graph.invalidated_descendants("text"),
            ("surface", "annotations", "package"),
        )

    def test_artifact_graph_rejects_cycles(self) -> None:
        with self.assertRaisesRegex(ValueError, "acyclic"):
            ArtifactGraph(
                graph_id="cycle",
                nodes=(
                    ArtifactNode(
                        "a",
                        ArtifactNodeKind.EPISODE_TEXT,
                        "1" * 64,
                        ("b",),
                    ),
                    ArtifactNode(
                        "b",
                        ArtifactNodeKind.HUMAN_SURFACE,
                        "2" * 64,
                        ("a",),
                    ),
                ),
            )


if __name__ == "__main__":
    unittest.main()
