from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from v4_shortform_script_foundry.approval import (  # noqa: E402
    ApprovalLedger,
    ApprovalReceipt,
    ApprovalRequirement,
    ArtifactRevision,
    ArtifactStatus,
    HilGate,
    ReviewDecision,
)
from v4_shortform_script_foundry.arc_contract import (  # noqa: E402
    ArcAcceptanceCriterion,
    ArcContract,
    ArcContractVerifier,
    ArcRevisionProposal,
    StoryState,
    StoryStateAxis,
    StoryStateEntry,
)
from v4_shortform_script_foundry.artifacts import (  # noqa: E402
    ArtifactEnvelope,
)
from v4_shortform_script_foundry.beat_patterns import (  # noqa: E402
    BeatPatternKind,
)
from v4_shortform_script_foundry.canonical import (  # noqa: E402
    canonical_sha256,
)
from v4_shortform_script_foundry.canonical_package import (  # noqa: E402
    AudienceInformationContract,
    CanonicalPackage,
    CoreCharacterContract,
    OriginalityContract,
    PayoffCadence,
    PayoffLayer,
    ProductionConstraints,
)
from v4_shortform_script_foundry.creative_review import (  # noqa: E402
    COMMON_FLOOR_AXES,
    CandidateSetVerifier,
    CreativeAxis,
    CreativeQualityGate,
    CreativeReview,
    CreativeScore,
    PairwiseComparison,
    PromotionReadinessVerifier,
    ReviewLane,
)
from v4_shortform_script_foundry.episode_script import (  # noqa: E402
    CausalRole,
    DialogueLine,
    EpisodeObligationKind,
    EpisodeScene,
    EpisodeScriptCandidate,
    EpisodeScriptStatus,
    EpisodeScriptVerifier,
)
from v4_shortform_script_foundry.genre_grammar import (  # noqa: E402
    RendererKind,
)


def digest(label: str) -> str:
    return canonical_sha256({"fixture": label})


def make_canonical(*, revision: int = 1) -> CanonicalPackage:
    return CanonicalPackage(
        work_id="original-work",
        canonical_id="original-work:canonical",
        revision=revision,
        target_and_platform_hypothesis="vertical short-form under five minutes",
        premise=(
            "A dismissed operations analyst earns a new team's trust through "
            "visible decisions while the old team misreads the departure."
        ),
        core_characters=(
            CoreCharacterContract(
                character_id="protagonist",
                narrative_role="lead",
                goal="build a safe professional identity outside the old group",
                failure_cost="remain defined by the old group's accusation",
                operating_identity_invariant_kernel=(
                    "reads systems, tests claims, and acts through demonstrated work"
                ),
                initial_agency_state="defensive_explanation",
                allowed_agency_transitions=(
                    "boundary_setting",
                    "independent_execution",
                    "public_ownership",
                ),
            ),
            CoreCharacterContract(
                character_id="field_partner",
                narrative_role="co_lead",
                goal="protect the new group without repeating its old habits",
                failure_cost="become a passive witness to another unsafe system",
                operating_identity_invariant_kernel=(
                    "tests trust through direct operational collaboration"
                ),
                initial_agency_state="guarded_evaluator",
                allowed_agency_transitions=(
                    "bounded_collaboration",
                    "shared_operational_risk",
                ),
            ),
        ),
        audience_information=AudienceInformationContract(
            objective_fact_policy="facts and perceptions remain separate",
            character_perception_policy=(
                "each group may hold a different interpretation"
            ),
            asymmetry_principles=(
                "audience_sees_the_departure_choice_before_old_group",
                "new_group_validation_precedes_old_group_reclassification",
            ),
        ),
        primary_reward="earned_belonging_through_competence",
        payoff_layers=(
            PayoffLayer(
                payoff_id="new_group_professional_trust",
                cadence=PayoffCadence.EPISODE,
                subject_id="protagonist",
                promise="visible work earns provisional trust",
                delivery_policy="each episode must register a local trust change",
            ),
            PayoffLayer(
                payoff_id="old_group_public_reclassification",
                cadence=PayoffCadence.ARC,
                subject_id="old_group",
                promise="the old group confronts the operational cost",
                delivery_policy="pay only after the new group trust is evidenced",
            ),
            PayoffLayer(
                payoff_id="earned_belonging_through_competence",
                cadence=PayoffCadence.SEASON,
                subject_id="protagonist",
                promise="the lead chooses earned belonging",
                delivery_policy="accumulate through independent choices",
            ),
        ),
        ending_direction="the protagonist chooses earned belonging",
        initial_relation_facts=(
            "old_group_distrusts_protagonist",
            "new_group_has_no_prior_loyalty",
        ),
        forbidden_contradictions=("verbal_explanation_alone_cannot_restore_trust",),
        world_constraints=("professional_actions_must_be_observable",),
        production_constraints=ProductionConstraints(
            target_runtime_seconds_min=60,
            target_runtime_seconds_max=120,
            max_principal_characters_per_scene=3,
            action_driven=True,
            dialogue_policy="state changes must be carried by observable action",
            max_dialogue_lines_per_scene=4,
        ),
        reward_hierarchy=(
            RendererKind.COMPETENCE,
            RendererKind.SOCIAL_RECOGNITION,
        ),
        allowed_renderers=(
            RendererKind.COMPETENCE,
            RendererKind.SOCIAL_RECOGNITION,
            RendererKind.NORM,
        ),
        originality=OriginalityContract(
            originality_axes=(
                "operations_failure_as_social_cost",
                "belonging_earned_by_work",
            ),
            anti_goals=(
                "no_hidden_wealth_reveal",
                "no_reference_event_chain",
            ),
            creative_latitude=(
                "new_professional_arena",
                "new_task_and_witness_design",
            ),
            source_rights_policy="abstract_function_only",
            premise_distance_receipt_sha256=digest("premise-distance"),
            original_contributions=(
                "group-specific knowledge state",
                "choice-led belonging transition",
            ),
        ),
        source_fact_ledger_sha256=digest("fact-ledger"),
        source_genre_grammar_sha256=digest("genre-grammar"),
    )


def make_canonical_receipt(
    canonical: CanonicalPackage,
) -> ApprovalReceipt:
    return ApprovalReceipt.issue(
        gate_id=HilGate.HIL1_CANONICAL,
        work_id=canonical.work_id,
        artifact_id=canonical.artifact_id,
        revision=canonical.revision,
        artifact_content_sha256=canonical.content_sha256,
        decision=ReviewDecision.APPROVE,
        reviewer_id="synthetic-owner",
        reviewer_role="owner",
        rubric_version="hil1-v1",
        review_payload_sha256=digest(f"hil1-review-{canonical.revision}"),
        decided_at="2026-07-30T12:00:00+09:00",
    )


def make_arc(
    canonical: CanonicalPackage,
    canonical_receipt: ApprovalReceipt,
) -> ArcContract:
    before = StoryState(
        entries=(
            StoryStateEntry(
                StoryStateAxis.BELONGING,
                "protagonist",
                "excluded_from_old_group",
            ),
            StoryStateEntry(
                StoryStateAxis.STATUS,
                "new_group",
                "unaware_of_protagonist",
            ),
            StoryStateEntry(
                StoryStateAxis.KNOWLEDGE,
                "old_group",
                "attributes_departure_to_resentment",
            ),
            StoryStateEntry(
                StoryStateAxis.WORLD_OPERATION,
                "new_group_workflow",
                "unsafe_handoff_unresolved",
            ),
        ),
        open_questions=("can_new_group_trust_be_earned",),
    )
    after = StoryState(
        entries=(
            StoryStateEntry(
                StoryStateAxis.BELONGING,
                "protagonist",
                "provisionally_accepted_by_new_group",
            ),
            StoryStateEntry(
                StoryStateAxis.STATUS,
                "new_group",
                "recognizes_operational_value",
            ),
            StoryStateEntry(
                StoryStateAxis.KNOWLEDGE,
                "old_group",
                "sees_operational_gap_but_misreads_cause",
            ),
            StoryStateEntry(
                StoryStateAxis.WORLD_OPERATION,
                "new_group_workflow",
                "safe_handoff_rule_installed",
            ),
        ),
        open_questions=("will_old_group_rewrite_the_departure",),
    )
    return ArcContract(
        work_id=canonical.work_id,
        arc_id="original-work:arc01",
        revision=1,
        parent_canonical_content_sha256=canonical.content_sha256,
        parent_canonical_approval_receipt_sha256=(canonical_receipt.receipt_sha256),
        state_before=before,
        state_after=after,
        dramatic_question=(
            "can demonstrated work create belonging outside the old group"
        ),
        core_pressure="the new group evaluates results without sympathy",
        core_choice="the protagonist accepts a public operational test",
        consequence="success creates new trust and exposes the old gap",
        attempt_blocker_chain=(),
        rewards_paid=("new_group_professional_trust",),
        rewards_deferred=("old_group_public_reclassification",),
        irreversible_change="the protagonist commits to the new group",
        acceptance_criteria=(
            ArcAcceptanceCriterion(
                "AC1",
                "new group recognition follows visible work",
            ),
            ArcAcceptanceCriterion(
                "AC2",
                "old group cost appears without immediate apology",
            ),
        ),
        episode_count_min=2,
        episode_count_max=4,
        production_constraints=canonical.production_constraints,
        continuity_invariants=(
            "old_group_cannot_know_new_group_private_evaluation",
            "trust_requires_observed_work",
        ),
        renderer_mix=(
            RendererKind.COMPETENCE,
            RendererKind.SOCIAL_RECOGNITION,
        ),
        allowed_beat_patterns=(
            BeatPatternKind.COMPETENCE_RECOGNITION,
            BeatPatternKind.SUSPENSE_INFORMATION_GAP,
        ),
        original_contributions=(
            "the decisive proof is a live operations choice",
            "the old group experiences a process failure rather than a loss",
        ),
        causal_chain_distance_receipt_sha256=digest("causal-distance"),
    )


def make_arc_receipt(
    arc: ArcContract,
    canonical: CanonicalPackage,
    canonical_receipt: ApprovalReceipt,
) -> ApprovalReceipt:
    return ApprovalReceipt.issue(
        gate_id=HilGate.HIL2_ARC,
        work_id=arc.work_id,
        artifact_id=arc.artifact_id,
        revision=arc.revision,
        artifact_content_sha256=arc.content_sha256,
        parent_content_sha256s=(canonical.content_sha256,),
        parent_approval_receipt_sha256s=(canonical_receipt.receipt_sha256,),
        decision=ReviewDecision.APPROVE,
        reviewer_id="synthetic-owner",
        reviewer_role="owner",
        rubric_version="hil2-v1",
        review_payload_sha256=digest("hil2-review"),
        decided_at="2026-07-30T12:10:00+09:00",
    )


def make_episode(
    arc: ArcContract,
    arc_receipt: ApprovalReceipt,
    *,
    episode_id: str = "original-work:ep001",
    contribution: str = "a silent timeout makes the choice visible",
) -> EpisodeScriptCandidate:
    return EpisodeScriptCandidate(
        work_id=arc.work_id,
        arc_id=arc.arc_id,
        episode_id=episode_id,
        revision=1,
        producer_id="writer-agent",
        status=EpisodeScriptStatus.CANDIDATE,
        parent_arc_content_sha256=arc.content_sha256,
        parent_arc_approval_receipt_sha256=(arc_receipt.receipt_sha256),
        source_scaffold_sha256=digest(f"scaffold-{episode_id}"),
        source_distance_receipt_sha256=digest(f"scene-distance-{episode_id}"),
        target_runtime_seconds=90,
        beat_pattern=BeatPatternKind.COMPETENCE_RECOGNITION,
        scenes=(
            EpisodeScene(
                scene_id="S01",
                location="new_team_control_room",
                purpose="make the evaluation standard visible",
                observable_action=(
                    "the protagonist stops an unsafe handoff and starts a timer"
                ),
                causal_role=CausalRole.MEANINGFUL_CHOICE,
                renderer_primary=RendererKind.COMPETENCE,
                renderer_secondary=(RendererKind.SOCIAL_RECOGNITION,),
                principal_character_ids=("protagonist", "evaluator"),
                duration_seconds=40,
                dialogue=(
                    DialogueLine(
                        "evaluator",
                        "Show us which queue you would stop.",
                        "state_operational_test",
                    ),
                ),
                information_revealed_ids=("evaluation_rule",),
                information_withheld_ids=("final_hiring_decision",),
                state_delta_codes=("test:offered->accepted",),
                tension_delta="public_failure_cost_increases",
            ),
            EpisodeScene(
                scene_id="S02",
                location="new_team_control_room",
                purpose="turn execution into provisional trust",
                observable_action=(
                    "the delayed queue clears while the risky queue stays frozen"
                ),
                causal_role=CausalRole.MEANINGFUL_ACTION,
                renderer_primary=RendererKind.COMPETENCE,
                renderer_secondary=(RendererKind.SOCIAL_RECOGNITION,),
                principal_character_ids=("protagonist", "evaluator"),
                duration_seconds=50,
                dialogue=(
                    DialogueLine(
                        "evaluator",
                        "Keep the console. The next call is yours.",
                        "grant_provisional_authority",
                    ),
                ),
                information_revealed_ids=("test_result",),
                information_withheld_ids=("long_term_trust",),
                state_delta_codes=("new_group_status:unknown->provisionally_trusted",),
                tension_delta="new_authority_creates_next_decision_cost",
            ),
        ),
        final_state_delta_codes=("belonging:excluded->provisional_new_group",),
        rewards_paid=("new_group_professional_trust",),
        rewards_deferred=("old_group_public_reclassification",),
        obligation_kind=EpisodeObligationKind.CONTINUATION,
        obligation="next episode must test the cost of provisional authority",
        original_contributions=(contribution,),
    )


def make_reviews(
    candidate: EpisodeScriptCandidate,
    *,
    low_axis: CreativeAxis | None = None,
) -> tuple[CreativeReview, ...]:
    reviews: list[CreativeReview] = []
    for lane, reviewer in (
        (ReviewLane.BR0, "reviewer-a"),
        (ReviewLane.BR1, "reviewer-b"),
    ):
        scores = tuple(
            CreativeScore(
                axis=axis,
                score=2 if axis is low_axis else 4,
                rationale=f"{axis.value} is evidenced by scene actions",
            )
            for axis in CreativeAxis
        )
        reviews.append(
            CreativeReview(
                lane=lane,
                reviewer_id=reviewer,
                candidate_content_sha256=candidate.content_sha256,
                rubric_version="creative-v1",
                scores=scores,
            )
        )
    return tuple(reviews)


class HilOneAndTwoContractTests(unittest.TestCase):
    def test_canonical_keeps_renderer_range_and_agency_transition(self) -> None:
        canonical = make_canonical()

        self.assertEqual(3, len(canonical.allowed_renderers))
        self.assertIn(
            "independent_execution",
            canonical.protagonist.allowed_agency_transitions,
        )
        self.assertEqual(
            canonical.content_sha256,
            canonical_sha256(canonical),
        )

    def test_hil_one_rejects_single_renderer_lock(self) -> None:
        canonical = make_canonical()

        with self.assertRaisesRegex(ValueError, "range"):
            replace(
                canonical,
                reward_hierarchy=(RendererKind.COMPETENCE,),
                allowed_renderers=(RendererKind.COMPETENCE,),
            )

    def test_arc_binds_canonical_and_uses_episode_band(self) -> None:
        canonical = make_canonical()
        receipt = make_canonical_receipt(canonical)
        arc = make_arc(canonical, receipt)

        report = ArcContractVerifier().verify(arc, canonical)

        self.assertTrue(report.passed, report.findings)
        self.assertEqual(
            (2, 4),
            (
                arc.episode_count_min,
                arc.episode_count_max,
            ),
        )

    def test_hil_artifacts_export_with_canonical_hashes(self) -> None:
        canonical = make_canonical()
        receipt = make_canonical_receipt(canonical)
        arc = make_arc(canonical, receipt)

        canonical_envelope = ArtifactEnvelope.create(
            artifact_type="hil1_canonical_package",
            artifact_id=canonical.artifact_id,
            payload=canonical,
        )
        arc_envelope = ArtifactEnvelope.create(
            artifact_type="hil2_arc_contract",
            artifact_id=arc.artifact_id,
            payload=arc,
        )

        self.assertTrue(canonical_envelope.verify())
        self.assertTrue(arc_envelope.verify())
        self.assertEqual(
            canonical.content_sha256,
            canonical_envelope.payload_sha256,
        )
        self.assertEqual(
            arc.content_sha256,
            arc_envelope.payload_sha256,
        )

    def test_arc_rejects_renderer_outside_hil_one(self) -> None:
        canonical = make_canonical()
        receipt = make_canonical_receipt(canonical)
        arc = replace(
            make_arc(canonical, receipt),
            renderer_mix=(RendererKind.RESOURCE,),
            allowed_beat_patterns=(BeatPatternKind.EVIDENCE_REVERSAL,),
        )

        report = ArcContractVerifier().verify(arc, canonical)

        self.assertFalse(report.passed)
        self.assertIn(
            "RENDERER_OUTSIDE_CANONICAL_RANGE",
            {finding.code for finding in report.findings},
        )

    def test_multi_episode_arc_rejects_fixed_episode_count(self) -> None:
        canonical = make_canonical()
        receipt = make_canonical_receipt(canonical)
        arc = replace(
            make_arc(canonical, receipt),
            episode_count_min=3,
            episode_count_max=3,
        )

        report = ArcContractVerifier().verify(arc, canonical)

        self.assertFalse(report.passed)
        self.assertIn(
            "FIXED_EPISODE_COUNT",
            {finding.code for finding in report.findings},
        )

    def test_arc_change_is_a_new_revision_proposal(self) -> None:
        canonical = make_canonical()
        receipt = make_canonical_receipt(canonical)
        arc = make_arc(canonical, receipt)
        proposal = ArcRevisionProposal(
            work_id=arc.work_id,
            arc_id=arc.arc_id,
            proposed_revision=2,
            parent_arc_content_sha256=arc.content_sha256,
            reason="a stronger operational choice emerged",
            affected_nodes=("arc01-node02",),
            continuity_risks=("new_group_trust_timing",),
            reward_impact="trust is paid one episode later",
            closure_or_cliff_impact="episode one closes on authority cost",
        )

        self.assertNotEqual(arc.content_sha256, proposal.content_sha256)


class ApprovalLedgerTests(unittest.TestCase):
    def approve_record(
        self,
        ledger: ApprovalLedger,
        record: ArtifactRevision,
        *,
        reviewer: str = "synthetic-owner",
    ) -> tuple[ApprovalLedger, ApprovalReceipt]:
        ledger = ledger.add_candidate(record)
        ledger = ledger.begin_review(
            work_id=record.work_id,
            artifact_id=record.artifact_id,
            revision=record.revision,
        )
        receipt = ApprovalReceipt.issue(
            gate_id=record.gate_id,
            work_id=record.work_id,
            artifact_id=record.artifact_id,
            revision=record.revision,
            artifact_content_sha256=record.content_sha256,
            parent_content_sha256s=record.parent_content_sha256s,
            parent_approval_receipt_sha256s=(record.parent_approval_receipt_sha256s),
            decision=ReviewDecision.APPROVE,
            reviewer_id=reviewer,
            reviewer_role="owner",
            rubric_version="test-v1",
            review_payload_sha256=digest(
                f"review-{record.artifact_id}-{record.revision}"
            ),
            decided_at="2026-07-30T13:00:00+09:00",
        )
        return ledger.apply_receipt(receipt), receipt

    def test_content_hash_and_approval_receipt_are_separate(self) -> None:
        canonical = make_canonical()
        receipt = make_canonical_receipt(canonical)

        self.assertNotEqual(
            canonical.content_sha256,
            receipt.receipt_sha256,
        )
        self.assertTrue(receipt.verify())

    def test_new_hil_one_approval_stales_arc_and_episode(self) -> None:
        canonical = make_canonical()
        canonical_record = ArtifactRevision(
            work_id=canonical.work_id,
            artifact_id=canonical.artifact_id,
            gate_id=HilGate.HIL1_CANONICAL,
            revision=1,
            content_sha256=canonical.content_sha256,
        )
        ledger, hil1_receipt = self.approve_record(
            ApprovalLedger(),
            canonical_record,
        )

        arc = make_arc(canonical, hil1_receipt)
        arc_record = ArtifactRevision(
            work_id=arc.work_id,
            artifact_id=arc.artifact_id,
            gate_id=HilGate.HIL2_ARC,
            revision=1,
            content_sha256=arc.content_sha256,
            parent_content_sha256s=(canonical.content_sha256,),
            parent_approval_receipt_sha256s=(hil1_receipt.receipt_sha256,),
        )
        ledger, hil2_receipt = self.approve_record(ledger, arc_record)

        episode = make_episode(arc, hil2_receipt)
        episode_record = ArtifactRevision(
            work_id=episode.work_id,
            artifact_id=episode.artifact_id,
            gate_id=HilGate.HIL3_EPISODE_SCRIPT,
            revision=1,
            content_sha256=episode.content_sha256,
            parent_content_sha256s=(arc.content_sha256,),
            parent_approval_receipt_sha256s=(hil2_receipt.receipt_sha256,),
        )
        ledger, _ = self.approve_record(ledger, episode_record)

        revised = replace(
            canonical,
            revision=2,
            primary_reward="new_group_professional_trust",
        )
        revised_record = ArtifactRevision(
            work_id=revised.work_id,
            artifact_id=revised.artifact_id,
            gate_id=HilGate.HIL1_CANONICAL,
            revision=2,
            content_sha256=revised.content_sha256,
        )
        ledger, revised_receipt = self.approve_record(
            ledger,
            revised_record,
        )

        statuses = {
            (record.artifact_id, record.revision): record.status
            for record in ledger.records
        }
        self.assertEqual(
            ArtifactStatus.SUPERSEDED,
            statuses[(canonical.artifact_id, 1)],
        )
        self.assertEqual(
            ArtifactStatus.APPROVED,
            statuses[(canonical.artifact_id, 2)],
        )
        self.assertEqual(
            ArtifactStatus.STALE,
            statuses[(arc.artifact_id, 1)],
        )
        self.assertEqual(
            ArtifactStatus.STALE,
            statuses[(episode.artifact_id, 1)],
        )

        boundary = ledger.resume_boundary(
            work_id=canonical.work_id,
            requirements=(
                ApprovalRequirement(
                    "canonical",
                    HilGate.HIL1_CANONICAL,
                    canonical.artifact_id,
                ),
                ApprovalRequirement(
                    "arc01",
                    HilGate.HIL2_ARC,
                    arc.artifact_id,
                    parent_content_sha256s=(revised.content_sha256,),
                    parent_approval_receipt_sha256s=(revised_receipt.receipt_sha256,),
                ),
            ),
        )
        self.assertFalse(boundary.complete)
        self.assertEqual("arc01", boundary.step_id)
        self.assertEqual(
            "missing_approved_artifact",
            boundary.reason,
        )

    def test_request_changes_never_approves_candidate(self) -> None:
        canonical = make_canonical()
        record = ArtifactRevision(
            work_id=canonical.work_id,
            artifact_id=canonical.artifact_id,
            gate_id=HilGate.HIL1_CANONICAL,
            revision=1,
            content_sha256=canonical.content_sha256,
        )
        ledger = ApprovalLedger().add_candidate(record)
        ledger = ledger.begin_review(
            work_id=record.work_id,
            artifact_id=record.artifact_id,
            revision=record.revision,
        )
        receipt = ApprovalReceipt.issue(
            gate_id=record.gate_id,
            work_id=record.work_id,
            artifact_id=record.artifact_id,
            revision=record.revision,
            artifact_content_sha256=record.content_sha256,
            decision=ReviewDecision.REQUEST_CHANGES,
            reviewer_id="synthetic-owner",
            reviewer_role="owner_fixture",
            rubric_version="test-v1",
            review_payload_sha256=digest("changes-request"),
            decided_at="2026-07-30T13:00:00+09:00",
        )

        updated = ledger.apply_receipt(receipt).records[0]

        self.assertEqual(ArtifactStatus.CANDIDATE, updated.status)
        self.assertIsNone(updated.approval_receipt_sha256)

    def test_non_owner_cannot_approve_hil_artifact(self) -> None:
        canonical = make_canonical()
        record = ArtifactRevision(
            work_id=canonical.work_id,
            artifact_id=canonical.artifact_id,
            gate_id=HilGate.HIL1_CANONICAL,
            revision=1,
            content_sha256=canonical.content_sha256,
        )
        ledger = ApprovalLedger().add_candidate(record)
        ledger = ledger.begin_review(
            work_id=record.work_id,
            artifact_id=record.artifact_id,
            revision=record.revision,
        )
        receipt = ApprovalReceipt.issue(
            gate_id=record.gate_id,
            work_id=record.work_id,
            artifact_id=record.artifact_id,
            revision=record.revision,
            artifact_content_sha256=record.content_sha256,
            decision=ReviewDecision.APPROVE,
            reviewer_id="reviewer-a",
            reviewer_role="br0",
            rubric_version="test-v1",
            review_payload_sha256=digest("unauthorized-approval"),
            decided_at="2026-07-30T13:00:00+09:00",
        )

        with self.assertRaisesRegex(ValueError, "owner"):
            ledger.apply_receipt(receipt)


class EpisodeAndQualityContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.canonical = make_canonical()
        self.hil1_receipt = make_canonical_receipt(self.canonical)
        self.arc = make_arc(self.canonical, self.hil1_receipt)
        self.hil2_receipt = make_arc_receipt(
            self.arc,
            self.canonical,
            self.hil1_receipt,
        )
        self.candidate = make_episode(self.arc, self.hil2_receipt)

    def test_finished_episode_accepts_non_four_bit_pattern(self) -> None:
        report = EpisodeScriptVerifier().verify(
            self.candidate,
            self.arc,
        )

        self.assertTrue(report.passed, report.findings)
        self.assertEqual(
            BeatPatternKind.COMPETENCE_RECOGNITION,
            self.candidate.beat_pattern,
        )
        self.assertEqual(2, len(self.candidate.scenes))

    def test_episode_rejects_automatic_promotion(self) -> None:
        promoted = replace(
            self.candidate,
            status=EpisodeScriptStatus.APPROVED,
        )

        report = EpisodeScriptVerifier().verify(promoted, self.arc)

        self.assertFalse(report.passed)
        self.assertIn(
            "AUTO_PROMOTION_FORBIDDEN",
            {finding.code for finding in report.findings},
        )

    def test_episode_rejects_stale_arc_hash(self) -> None:
        stale = replace(
            self.candidate,
            parent_arc_content_sha256="0" * 64,
        )

        report = EpisodeScriptVerifier().verify(stale, self.arc)

        self.assertFalse(report.passed)
        self.assertIn(
            "ARC_HASH_MISMATCH",
            {finding.code for finding in report.findings},
        )

    def test_creative_floor_requires_independent_br0_br1(self) -> None:
        reviews = make_reviews(self.candidate)
        conflicted = (
            reviews[0],
            replace(reviews[1], reviewer_id=self.candidate.producer_id),
        )

        report = CreativeQualityGate().verify(
            self.candidate,
            conflicted,
        )

        self.assertFalse(report.passed)
        self.assertIn(
            "PRODUCER_REVIEW_CONFLICT",
            {finding.code for finding in report.findings},
        )

    def test_creative_floor_fails_before_pairwise_ranking(self) -> None:
        reviews = make_reviews(
            self.candidate,
            low_axis=CreativeAxis.WORK_SPECIFICITY,
        )

        report = CreativeQualityGate().verify(
            self.candidate,
            reviews,
        )

        self.assertFalse(report.passed)
        self.assertEqual(
            2,
            sum(
                finding.code == "CREATIVE_FLOOR_NOT_MET" for finding in report.findings
            ),
        )

    def test_candidate_set_rejects_cosmetic_variants(self) -> None:
        cosmetic = replace(
            self.candidate,
            original_contributions=("different label only",),
        )

        report = CandidateSetVerifier().verify((self.candidate, cosmetic))

        self.assertFalse(report.passed)
        self.assertIn(
            "CANDIDATES_NOT_STRUCTURALLY_DISTINCT",
            {finding.code for finding in report.findings},
        )

    def test_promotion_requires_hard_creative_pairwise_and_owner(self) -> None:
        competitor = make_episode(
            self.arc,
            self.hil2_receipt,
            contribution="a failed handoff forces a public boundary",
        )
        competitor_first = replace(
            competitor.scenes[0],
            purpose="force a failed handoff before the protagonist intervenes",
            causal_role=CausalRole.EXTERNAL_PRESSURE_CONSEQUENCE,
        )
        competitor = replace(
            competitor,
            scenes=(competitor_first,) + competitor.scenes[1:],
        )
        candidate_set_report = CandidateSetVerifier().verify(
            (self.candidate, competitor)
        )
        self.assertTrue(
            candidate_set_report.passed,
            candidate_set_report.findings,
        )
        comparisons = tuple(
            PairwiseComparison(
                reviewer_id=reviewer,
                candidate_a_sha256=self.candidate.content_sha256,
                candidate_b_sha256=competitor.content_sha256,
                preferred_candidate_sha256=(
                    self.candidate.content_sha256
                    if reviewer == "reviewer-a"
                    else competitor.content_sha256
                ),
                rationale=("the preferred candidate has the stronger causal opening"),
            )
            for reviewer in ("reviewer-a", "reviewer-b")
        )
        owner_receipt = ApprovalReceipt.issue(
            gate_id=HilGate.HIL3_EPISODE_SCRIPT,
            work_id=self.candidate.work_id,
            artifact_id=self.candidate.artifact_id,
            revision=self.candidate.revision,
            artifact_content_sha256=self.candidate.content_sha256,
            parent_content_sha256s=(self.arc.content_sha256,),
            parent_approval_receipt_sha256s=(self.hil2_receipt.receipt_sha256,),
            decision=ReviewDecision.APPROVE,
            reviewer_id="synthetic-owner",
            reviewer_role="owner",
            rubric_version="hil3-v1",
            review_payload_sha256=digest("hil3-review"),
            decided_at="2026-07-30T14:00:00+09:00",
        )

        readiness = PromotionReadinessVerifier().verify(
            candidate=self.candidate,
            arc=self.arc,
            creative_reviews=(make_reviews(self.candidate) + make_reviews(competitor)),
            candidates=(self.candidate, competitor),
            pairwise_comparisons=comparisons,
            owner_receipt=owner_receipt,
        )

        self.assertTrue(readiness.passed, readiness.findings)
        self.assertTrue(
            set(COMMON_FLOOR_AXES).issubset(
                {score.axis for score in make_reviews(self.candidate)[0].scores}
            )
        )


if __name__ == "__main__":
    unittest.main()
