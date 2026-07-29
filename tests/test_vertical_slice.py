from __future__ import annotations

from dataclasses import replace
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from v4_shortform_script_foundry.episode_state import (  # noqa: E402
    EpisodeState,
    EpisodeStatePlanner,
)
from v4_shortform_script_foundry.artifacts import ArtifactEnvelope  # noqa: E402
from v4_shortform_script_foundry.canonical import canonical_json  # noqa: E402
from v4_shortform_script_foundry.fact_ledger import (  # noqa: E402
    Certainty,
    FactLedger,
    FactRecord,
    SourceBinding,
)
from v4_shortform_script_foundry.genre_grammar import (  # noqa: E402
    GenreGrammarPacket,
    GrammarStatus,
    RendererKind,
    RendererPreference,
)
from v4_shortform_script_foundry.renderer_router import RendererRouter  # noqa: E402
from v4_shortform_script_foundry.pipeline import V4ShortformPipeline  # noqa: E402
from v4_shortform_script_foundry.script_packet import (  # noqa: E402
    BeatContract,
    PacketStatus,
    ScriptPacketBuilder,
)
from v4_shortform_script_foundry.series_plan import (  # noqa: E402
    ProofStage,
    SeriesPlanner,
)
from v4_shortform_script_foundry.verification import ScriptVerifier  # noqa: E402


def make_ledger() -> FactLedger:
    return FactLedger(
        premise_id="synthetic-hidden-value",
        sources=(
            SourceBinding(
                source_id="owner-premise-v1",
                source_kind="synthetic_fixture",
                locator="tests:synthetic-hidden-value",
            ),
        ),
        facts=(
            FactRecord(
                fact_id="f-identity",
                subject="protagonist",
                predicate="has_hidden_authority",
                value="true",
                certainty=Certainty.CONFIRMED,
                source_ids=("owner-premise-v1",),
                tags=(
                    "latent_capability",
                    "authority",
                    "protective_capacity",
                ),
            ),
            FactRecord(
                fact_id="f-misperception",
                subject="group",
                predicate="perceives_protagonist_as",
                value="low_value",
                certainty=Certainty.CONFIRMED,
                source_ids=("owner-premise-v1",),
                tags=("misperception", "relationship_asymmetry"),
            ),
        ),
    )


def make_grammar(
    grammar_id: str,
    primary_reward: str,
    preferences: tuple[RendererPreference, ...],
) -> GenreGrammarPacket:
    candidate = GenreGrammarPacket(
        grammar_id=grammar_id,
        version="0.1.0",
        target_profile="synthetic-test-only",
        entry_pressure="public_misclassification",
        primary_reward=primary_reward,
        preferences=preferences,
        evidence_ids=("synthetic-evidence",),
        status=GrammarStatus.CANDIDATE,
    )
    return replace(
        candidate,
        status=GrammarStatus.APPROVED,
        owner_approval_sha256=candidate.content_sha256,
    )


def achievement_grammar() -> GenreGrammarPacket:
    return make_grammar(
        "achievement-reversal",
        "earned_public_status_reversal",
        (
            RendererPreference(
                RendererKind.COMPETENCE,
                100,
                "capability_denial",
                "problem_resolution",
                "authority_through_result",
                ("latent_capability", "misperception"),
            ),
            RendererPreference(
                RendererKind.STATUS,
                90,
                "status_devaluation",
                "credible_public_recognition",
                "status_reversal",
                ("authority", "misperception"),
            ),
            RendererPreference(
                RendererKind.RESOURCE,
                80,
                "resource_exclusion",
                "material_control",
                "resource_agency",
                ("authority",),
            ),
        ),
    )


def selection_grammar() -> GenreGrammarPacket:
    return make_grammar(
        "selection-safety",
        "exclusive_choice_and_safety",
        (
            RendererPreference(
                RendererKind.ATTACHMENT_SAFETY,
                100,
                "abandonment_threat",
                "protective_exception",
                "exclusive_safety",
                ("protective_capacity", "relationship_asymmetry"),
            ),
            RendererPreference(
                RendererKind.SELECTION,
                90,
                "replacement_pressure",
                "exclusive_choice",
                "being_chosen",
                ("relationship_asymmetry",),
            ),
            RendererPreference(
                RendererKind.SOCIAL_RECOGNITION,
                80,
                "group_ridicule",
                "credible_witness",
                "public_reclassification",
                ("misperception",),
            ),
        ),
    )


class ContractTests(unittest.TestCase):
    def test_confirmed_fact_requires_source(self) -> None:
        with self.assertRaisesRegex(ValueError, "confirmed facts require"):
            FactRecord(
                fact_id="f1",
                subject="p",
                predicate="is",
                value="valuable",
                certainty=Certainty.CONFIRMED,
            )

    def test_approved_grammar_requires_owner_hash(self) -> None:
        with self.assertRaisesRegex(ValueError, "approval hash"):
            GenreGrammarPacket(
                grammar_id="bad",
                version="0.1.0",
                target_profile="test",
                entry_pressure="pressure",
                primary_reward="reward",
                preferences=achievement_grammar().preferences,
                evidence_ids=("e1",),
                status=GrammarStatus.APPROVED,
            )

    def test_approved_grammar_hash_must_bind_canonical_content(self) -> None:
        candidate = replace(
            achievement_grammar(),
            status=GrammarStatus.CANDIDATE,
            owner_approval_sha256=None,
        )
        with self.assertRaisesRegex(ValueError, "canonical content hash"):
            replace(
                candidate,
                status=GrammarStatus.APPROVED,
                owner_approval_sha256="0" * 64,
            )

    def test_canonical_packet_json_is_stable_and_machine_readable(self) -> None:
        grammar = achievement_grammar()
        first = canonical_json(grammar)
        second = canonical_json(grammar)

        self.assertEqual(first, second)
        self.assertEqual(grammar.grammar_id, json.loads(first)["grammar_id"])

    def test_packet_content_change_invalidates_previous_approval_hash(self) -> None:
        approved = achievement_grammar()
        candidate = replace(
            approved,
            primary_reward="changed_reward",
            status=GrammarStatus.CANDIDATE,
            owner_approval_sha256=None,
        )

        self.assertNotEqual(approved.content_sha256, candidate.content_sha256)
        with self.assertRaisesRegex(ValueError, "canonical content hash"):
            replace(
                candidate,
                status=GrammarStatus.APPROVED,
                owner_approval_sha256=approved.owner_approval_sha256,
            )

    def test_string_enum_values_are_not_silently_accepted(self) -> None:
        with self.assertRaisesRegex(TypeError, "Certainty"):
            replace(make_ledger().facts[0], certainty="confirmed")  # type: ignore[arg-type]
        with self.assertRaisesRegex(TypeError, "GrammarStatus"):
            replace(achievement_grammar(), status="approved")  # type: ignore[arg-type]


class RendererTests(unittest.TestCase):
    def test_same_facts_route_to_different_genre_rewards(self) -> None:
        ledger = make_ledger()
        router = RendererRouter()
        achievement = router.route(ledger, achievement_grammar(), 1)
        selection = router.route(ledger, selection_grammar(), 1)

        self.assertEqual(RendererKind.COMPETENCE, achievement.primary)
        self.assertEqual(RendererKind.ATTACHMENT_SAFETY, selection.primary)
        self.assertNotEqual(achievement.primary_threat, selection.primary_threat)
        self.assertNotEqual(achievement.reward_target, selection.reward_target)
        self.assertEqual(
            ("f-identity", "f-misperception"),
            achievement.bound_fact_ids,
        )

    def test_routing_is_deterministic_and_penalizes_repetition(self) -> None:
        ledger = make_ledger()
        router = RendererRouter()
        grammar = achievement_grammar()
        first = router.route(ledger, grammar, 1)
        repeated = router.route(ledger, grammar, 1)
        second = router.route(ledger, grammar, 2, (first.primary,))

        self.assertEqual(first, repeated)
        self.assertNotEqual(first.primary, second.primary)

    def test_router_fails_when_facts_do_not_support_any_lens(self) -> None:
        ledger = make_ledger()
        candidate = GenreGrammarPacket(
            grammar_id="unsupported",
            version="0.1.0",
            target_profile="synthetic-test-only",
            entry_pressure="pressure",
            primary_reward="reward",
            preferences=(
                RendererPreference(
                    RendererKind.SCARCITY,
                    100,
                    "mispricing",
                    "provenance_reveal",
                    "value_reclassification",
                    ("scarce_object_provenance",),
                ),
            ),
            evidence_ids=("synthetic-evidence",),
        )
        grammar = replace(
            candidate,
            status=GrammarStatus.APPROVED,
            owner_approval_sha256=candidate.content_sha256,
        )

        with self.assertRaisesRegex(ValueError, "no renderer is eligible"):
            RendererRouter().route(ledger, grammar, 1)

    def test_router_rejects_candidate_grammar(self) -> None:
        grammar = replace(
            achievement_grammar(),
            status=GrammarStatus.CANDIDATE,
            owner_approval_sha256=None,
        )
        with self.assertRaisesRegex(ValueError, "approved genre grammar"):
            RendererRouter().route(make_ledger(), grammar, 1)

    def test_router_binds_only_facts_supporting_selected_lens(self) -> None:
        ledger = make_ledger()
        irrelevant = FactRecord(
            fact_id="f-weather",
            subject="weather",
            predicate="is",
            value="clear",
            certainty=Certainty.CONFIRMED,
            source_ids=("owner-premise-v1",),
            tags=("environment",),
        )
        expanded = replace(ledger, facts=ledger.facts + (irrelevant,))

        decision = RendererRouter().route(
            expanded,
            achievement_grammar(),
            1,
        )

        self.assertNotIn("f-weather", decision.bound_fact_ids)


class VerticalSliceTests(unittest.TestCase):
    def run_slice(
        self, grammar: GenreGrammarPacket
    ) -> tuple[list[EpisodeState], list[object]]:
        ledger = make_ledger()
        plan = SeriesPlanner().plan(ledger, grammar)
        state_planner = EpisodeStatePlanner()
        packet_builder = ScriptPacketBuilder()
        verifier = ScriptVerifier()
        states = [EpisodeState.initial()]
        packets = []

        for contract in plan.episodes:
            next_state = state_planner.advance(states[-1], contract)
            packet = packet_builder.build(
                ledger,
                grammar.packet_id,
                contract,
                states[-1],
                next_state,
            )
            report = verifier.verify(packet, contract, ledger, grammar)
            self.assertTrue(report.passed, report.findings)
            states.append(next_state)
            packets.append(packet)
        return states, packets

    def test_three_episode_slice_advances_proof_and_pays_reward(self) -> None:
        grammar = achievement_grammar()
        states, packets = self.run_slice(grammar)

        self.assertEqual(
            [
                ProofStage.UNKNOWN,
                ProofStage.INDICATED,
                ProofStage.MATERIALIZED,
                ProofStage.PUBLICLY_RECOGNIZED,
            ],
            [state.proof_stage for state in states],
        )
        self.assertIn(grammar.primary_reward, states[-1].paid_rewards)
        self.assertTrue(all(packet.runtime_seconds == 90 for packet in packets))
        self.assertTrue(
            all(packet.status is PacketStatus.CANDIDATE for packet in packets)
        )

    def test_genre_profiles_produce_different_episode_packets(self) -> None:
        _, achievement_packets = self.run_slice(achievement_grammar())
        _, selection_packets = self.run_slice(selection_grammar())

        self.assertNotEqual(
            achievement_packets[0].beats[0].renderer,
            selection_packets[0].beats[0].renderer,
        )
        self.assertNotEqual(
            achievement_packets[-1].beats[-1].reward_ids,
            selection_packets[-1].beats[-1].reward_ids,
        )

    def test_verifier_rejects_automatic_promotion(self) -> None:
        ledger = make_ledger()
        grammar = achievement_grammar()
        contract = SeriesPlanner().plan(ledger, grammar).episodes[0]
        before = EpisodeState.initial()
        after = EpisodeStatePlanner().advance(before, contract)
        packet = ScriptPacketBuilder().build(
            ledger, grammar.packet_id, contract, before, after
        )
        promoted = replace(packet, status=PacketStatus.APPROVED)

        report = ScriptVerifier().verify(promoted, contract, ledger, grammar)

        self.assertFalse(report.passed)
        self.assertIn(
            "AUTO_PROMOTION_FORBIDDEN",
            {finding.code for finding in report.findings},
        )

    def test_verifier_rejects_runtime_and_unconfirmed_proof(self) -> None:
        base_ledger = make_ledger()
        claimed = FactRecord(
            fact_id="f-rumor",
            subject="group",
            predicate="claims",
            value="unsupported",
            certainty=Certainty.CLAIMED,
            source_ids=("owner-premise-v1",),
            tags=("rumor",),
        )
        ledger = replace(base_ledger, facts=base_ledger.facts + (claimed,))
        grammar = achievement_grammar()
        contract = SeriesPlanner().plan(ledger, grammar).episodes[0]
        before = EpisodeState.initial()
        after = EpisodeStatePlanner().advance(before, contract)
        packet = ScriptPacketBuilder().build(
            ledger, grammar.packet_id, contract, before, after
        )
        proof = packet.beats[2]
        broken_proof = BeatContract(
            beat_id=proof.beat_id,
            function=proof.function,
            seconds=proof.seconds + 1,
            renderer=proof.renderer,
            proof_stage=proof.proof_stage,
            required_fact_ids=("f-rumor",),
            reward_ids=proof.reward_ids,
        )
        broken = replace(
            packet,
            beats=packet.beats[:2] + (broken_proof,) + packet.beats[3:],
        )

        report = ScriptVerifier().verify(broken, contract, ledger, grammar)
        codes = {finding.code for finding in report.findings}

        self.assertFalse(report.passed)
        self.assertIn("RUNTIME_MISMATCH", codes)
        self.assertIn("UNCONFIRMED_PROOF", codes)

    def test_state_planner_rejects_nonconsecutive_transition(self) -> None:
        ledger = make_ledger()
        grammar = achievement_grammar()
        contract = SeriesPlanner().plan(ledger, grammar).episodes[1]

        with self.assertRaisesRegex(ValueError, "consecutively"):
            EpisodeStatePlanner().advance(EpisodeState.initial(), contract)

    def test_pipeline_runner_and_artifact_envelope(self) -> None:
        result = V4ShortformPipeline().run(
            make_ledger(),
            achievement_grammar(),
        )

        self.assertTrue(result.passed)
        self.assertEqual(3, len(result.packets))
        self.assertEqual(4, len(result.states))
        envelope = ArtifactEnvelope.create(
            artifact_type="script_packet",
            artifact_id="synthetic-hidden-value:ep001",
            payload=result.packets[0],
        )
        self.assertTrue(envelope.verify())
        exported = json.loads(envelope.to_json())
        self.assertEqual("script_packet", exported["artifact_type"])
        self.assertEqual(
            result.packets[0].premise_id,
            exported["payload"]["premise_id"],
        )


if __name__ == "__main__":
    unittest.main()
