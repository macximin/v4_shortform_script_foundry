"""Evidence-grade, prose-free draft contract produced before model writing."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .canonical import canonical_sha256
from .fact_ledger import FactLedger
from .genre_grammar import GenreGrammarPacket, RendererKind
from .script_packet import BeatFunction, ScriptPacket
from .series_plan import EpisodeContract, ProofStage


class DraftStatus(StrEnum):
    CANDIDATE = "candidate"
    APPROVED = "approved"


@dataclass(frozen=True, slots=True)
class DraftBeat:
    beat_id: str
    function: BeatFunction
    start_seconds: int
    end_seconds: int
    renderer: RendererKind
    scene_purpose: str
    observable_action: str
    dialogue_function: str
    information_revealed_fact_ids: tuple[str, ...]
    information_withheld_fact_ids: tuple[str, ...]
    proof_stage_before: ProofStage
    proof_stage_after: ProofStage
    state_delta_codes: tuple[str, ...]
    reward_ids: tuple[str, ...]
    cliff_obligation: str | None = None

    @property
    def duration_seconds(self) -> int:
        return self.end_seconds - self.start_seconds


@dataclass(frozen=True, slots=True)
class DraftScript:
    premise_id: str
    grammar_packet_id: str
    episode_number: int
    status: DraftStatus
    source_packet_sha256: str
    source_distance: str
    deferred_question: str
    beats: tuple[DraftBeat, ...]

    @property
    def runtime_seconds(self) -> int:
        return sum(beat.duration_seconds for beat in self.beats)


class DeterministicDraftAdapter:
    """Expands a Script Packet into auditable functions, not finished prose."""

    SOURCE_DISTANCE = "approved_grammar_only_no_reference_content"

    def build(
        self,
        packet: ScriptPacket,
        contract: EpisodeContract,
        ledger: FactLedger,
        grammar: GenreGrammarPacket,
    ) -> DraftScript:
        if packet.premise_id != ledger.premise_id:
            raise ValueError("packet and Fact Ledger premise must match")
        if packet.grammar_packet_id != grammar.packet_id:
            raise ValueError("packet and approved grammar must match")
        if packet.episode_number != contract.episode_number:
            raise ValueError("packet and episode contract must match")

        start = 0
        rolling_stage = packet.state_before.proof_stage
        beats: list[DraftBeat] = []
        final_index = len(packet.beats) - 1
        bound_facts = tuple(contract.renderer.bound_fact_ids)

        for index, beat in enumerate(packet.beats):
            end = start + beat.seconds
            stage_after = beat.proof_stage
            revealed = (
                beat.required_fact_ids
                if beat.function is BeatFunction.PROOF
                else ()
            )
            withheld = (
                bound_facts
                if beat.function in {BeatFunction.HOOK, BeatFunction.PRESSURE}
                else ()
            )
            beats.append(
                DraftBeat(
                    beat_id=beat.beat_id,
                    function=beat.function,
                    start_seconds=start,
                    end_seconds=end,
                    renderer=beat.renderer,
                    scene_purpose=self.expected_scene_purpose(
                        beat.function,
                        contract,
                    ),
                    observable_action=self.expected_observable_action(
                        beat.function,
                        contract,
                    ),
                    dialogue_function=self.expected_dialogue_function(
                        beat.function
                    ),
                    information_revealed_fact_ids=revealed,
                    information_withheld_fact_ids=withheld,
                    proof_stage_before=rolling_stage,
                    proof_stage_after=stage_after,
                    state_delta_codes=self.expected_state_delta_codes(
                        beat.function,
                        rolling_stage,
                        stage_after,
                        packet,
                    ),
                    reward_ids=beat.reward_ids,
                    cliff_obligation=(
                        f"next_episode_must_answer_or_escalate:"
                        f"{packet.deferred_question}"
                        if index == final_index
                        else None
                    ),
                )
            )
            rolling_stage = stage_after
            start = end

        return DraftScript(
            premise_id=packet.premise_id,
            grammar_packet_id=packet.grammar_packet_id,
            episode_number=packet.episode_number,
            status=DraftStatus.CANDIDATE,
            source_packet_sha256=canonical_sha256(packet),
            source_distance=self.SOURCE_DISTANCE,
            deferred_question=packet.deferred_question,
            beats=tuple(beats),
        )

    @staticmethod
    def expected_scene_purpose(
        function: BeatFunction,
        contract: EpisodeContract,
    ) -> str:
        decision = contract.renderer
        if function is BeatFunction.HOOK:
            return f"surface_{decision.primary_threat}_as_immediate_anomaly"
        if function is BeatFunction.PRESSURE:
            return (
                f"intensify_{decision.primary_threat}_without_resolving_"
                f"{decision.proof_mode}"
            )
        if function is BeatFunction.PROOF:
            return (
                f"stage_{decision.proof_mode}_to_reach_"
                f"{contract.proof_stage_after.name.lower()}"
            )
        return (
            f"pay_{decision.reward_target}_and_defer_"
            f"{contract.deferred_question}"
        )

    @staticmethod
    def expected_observable_action(
        function: BeatFunction,
        contract: EpisodeContract,
    ) -> str:
        if function is BeatFunction.HOOK:
            return "show_observable_consequence_before_explanation"
        if function is BeatFunction.PRESSURE:
            return (
                f"show_actor_enforcing_primary_threat:"
                f"{contract.renderer.primary_threat}"
            )
        if function is BeatFunction.PROOF:
            return (
                f"show_physical_or_social_proof_operation:"
                f"{contract.renderer.proof_mode}"
            )
        return "show_credible_reaction_then_hold_material_resolution"

    @staticmethod
    def expected_dialogue_function(function: BeatFunction) -> str:
        return {
            BeatFunction.HOOK: "open_information_gap",
            BeatFunction.PRESSURE: "state_current_misclassification",
            BeatFunction.PROOF: "name_only_claim_needed_for_proof",
            BeatFunction.REWARD_CLIFF: (
                "register_judgment_change_and_pose_next_question"
            ),
        }[function]

    @staticmethod
    def expected_state_delta_codes(
        function: BeatFunction,
        stage_before: ProofStage,
        stage_after: ProofStage,
        packet: ScriptPacket,
    ) -> tuple[str, ...]:
        codes: list[str] = []
        if stage_after != stage_before:
            codes.append(
                f"proof_stage:{stage_before.name.lower()}->"
                f"{stage_after.name.lower()}"
            )
        if function is BeatFunction.PRESSURE:
            codes.append("humiliation_debt:pressure_added")
        if function is BeatFunction.REWARD_CLIFF:
            codes.append(
                f"perceived_status:{packet.state_before.perceived_status}->"
                f"{packet.state_after.perceived_status}"
            )
            codes.extend(f"reward_paid:{reward}" for reward in packet.beats[-1].reward_ids)
        if not codes:
            codes.append("state:no_change")
        return tuple(codes)
