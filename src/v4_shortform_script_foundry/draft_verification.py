"""Hard verification for evidence-grade functional draft scripts."""

from __future__ import annotations

from dataclasses import dataclass

from .canonical import canonical_sha256
from .draft_script import (
    DeterministicDraftAdapter,
    DraftScript,
    DraftStatus,
)
from .fact_ledger import Certainty, FactLedger
from .script_packet import BeatFunction, ScriptPacket
from .series_plan import EpisodeContract


@dataclass(frozen=True, slots=True)
class DraftFinding:
    code: str
    location: str
    message: str


@dataclass(frozen=True, slots=True)
class DraftVerificationReport:
    episode_number: int
    findings: tuple[DraftFinding, ...]

    @property
    def passed(self) -> bool:
        return not self.findings


class DraftScriptVerifier:
    def verify(
        self,
        draft: DraftScript,
        packet: ScriptPacket,
        contract: EpisodeContract,
        ledger: FactLedger,
    ) -> DraftVerificationReport:
        findings: list[DraftFinding] = []

        def hard(code: str, location: str, message: str) -> None:
            findings.append(DraftFinding(code, location, message))

        if draft.status is not DraftStatus.CANDIDATE:
            hard(
                "AUTO_PROMOTION_FORBIDDEN",
                "draft.status",
                "generated drafts must remain candidates",
            )
        if draft.source_packet_sha256 != canonical_sha256(packet):
            hard(
                "SOURCE_PACKET_HASH_MISMATCH",
                "draft.source_packet_sha256",
                "draft must bind the exact canonical Script Packet",
            )
        if draft.source_distance != DeterministicDraftAdapter.SOURCE_DISTANCE:
            hard(
                "SOURCE_DISTANCE_VIOLATION",
                "draft.source_distance",
                "draft may use approved grammar only, never reference content",
            )
        for field_name in (
            "premise_id",
            "grammar_packet_id",
            "episode_number",
            "deferred_question",
        ):
            if getattr(draft, field_name) != getattr(packet, field_name):
                hard(
                    f"{field_name.upper()}_MISMATCH",
                    f"draft.{field_name}",
                    f"draft must preserve packet {field_name}",
                )
        if draft.runtime_seconds != packet.runtime_seconds:
            hard(
                "RUNTIME_MISMATCH",
                "draft.beats",
                "draft runtime must equal Script Packet runtime",
            )
        if len(draft.beats) != len(packet.beats):
            hard(
                "BEAT_COUNT_MISMATCH",
                "draft.beats",
                "draft and Script Packet beat counts must match",
            )
            return DraftVerificationReport(draft.episode_number, tuple(findings))

        expected_start = 0
        rolling_stage = packet.state_before.proof_stage
        revealed_proof_facts: set[str] = set()
        packet_proof_fact_ids = {
            fact_id
            for beat in packet.beats
            if beat.function is BeatFunction.PROOF
            for fact_id in beat.required_fact_ids
        }
        beat_ids: list[str] = []
        for index, (draft_beat, packet_beat) in enumerate(
            zip(draft.beats, packet.beats, strict=True)
        ):
            location = draft_beat.beat_id
            beat_ids.append(draft_beat.beat_id)
            if draft_beat.beat_id != packet_beat.beat_id:
                hard("BEAT_ID_MISMATCH", location, "beat ids must match")
            if draft_beat.function is not packet_beat.function:
                hard("BEAT_FUNCTION_MISMATCH", location, "beat functions must match")
            if draft_beat.renderer is not packet_beat.renderer:
                hard("RENDERER_MISMATCH", location, "beat renderers must match")
            if draft_beat.start_seconds != expected_start:
                hard(
                    "TIMELINE_GAP_OR_OVERLAP",
                    location,
                    "draft beats must be contiguous from zero",
                )
            if draft_beat.duration_seconds != packet_beat.seconds:
                hard(
                    "BEAT_DURATION_MISMATCH",
                    location,
                    "draft beat duration must preserve the packet",
                )
            expected_start = draft_beat.end_seconds

            for field_name in (
                "scene_purpose",
                "observable_action",
                "dialogue_function",
            ):
                if not getattr(draft_beat, field_name).strip():
                    hard(
                        f"MISSING_{field_name.upper()}",
                        location,
                        f"{field_name} must not be empty",
                    )
            expected_functional_fields = {
                "scene_purpose": (
                    DeterministicDraftAdapter.expected_scene_purpose(
                        draft_beat.function,
                        contract,
                    )
                ),
                "observable_action": (
                    DeterministicDraftAdapter.expected_observable_action(
                        draft_beat.function,
                        contract,
                    )
                ),
                "dialogue_function": (
                    DeterministicDraftAdapter.expected_dialogue_function(
                        draft_beat.function
                    )
                ),
            }
            for field_name, expected_value in expected_functional_fields.items():
                if getattr(draft_beat, field_name) != expected_value:
                    hard(
                        f"{field_name.upper()}_MISMATCH",
                        location,
                        f"{field_name} must preserve the Episode Contract",
                    )

            revealed = set(draft_beat.information_revealed_fact_ids)
            withheld = set(draft_beat.information_withheld_fact_ids)
            if len(revealed) != len(draft_beat.information_revealed_fact_ids):
                hard(
                    "DUPLICATE_REVEALED_FACT_ID",
                    location,
                    "revealed fact ids must be unique",
                )
            if len(withheld) != len(draft_beat.information_withheld_fact_ids):
                hard(
                    "DUPLICATE_WITHHELD_FACT_ID",
                    location,
                    "withheld fact ids must be unique",
                )
            if revealed.intersection(withheld):
                hard(
                    "INFORMATION_REVEALED_AND_WITHHELD",
                    location,
                    "the same fact cannot be revealed and withheld",
                )
            expected_revealed = (
                set(packet_beat.required_fact_ids)
                if draft_beat.function is BeatFunction.PROOF
                else set()
            )
            if revealed != expected_revealed:
                hard(
                    "INFORMATION_REVEAL_MISMATCH",
                    location,
                    "draft reveals must exactly match the planned proof beat",
                )
                if (
                    draft_beat.function
                    in {BeatFunction.HOOK, BeatFunction.PRESSURE}
                    and revealed
                ):
                    hard(
                        "INFORMATION_REVEALED_TOO_EARLY",
                        location,
                        "hook and pressure beats cannot spend proof facts",
                    )
            expected_withheld = (
                packet_proof_fact_ids
                if draft_beat.function
                in {BeatFunction.HOOK, BeatFunction.PRESSURE}
                else set()
            )
            if withheld != expected_withheld:
                hard(
                    "INFORMATION_WITHHOLD_MISMATCH",
                    location,
                    "draft withholds must exactly preserve the information plan",
                )
            for fact_id in revealed.union(withheld):
                try:
                    fact = ledger.get(fact_id)
                except KeyError:
                    hard("UNKNOWN_FACT", location, f"unknown fact {fact_id}")
                    continue
                if (
                    fact_id in revealed
                    and fact.certainty is not Certainty.CONFIRMED
                ):
                    hard(
                        "UNCONFIRMED_INFORMATION_REVEAL",
                        location,
                        f"draft cannot reveal {fact_id} as confirmed",
                    )
            if draft_beat.function is BeatFunction.PROOF:
                missing = set(packet_beat.required_fact_ids) - revealed
                if missing:
                    hard(
                        "MISSING_PROOF_INFORMATION",
                        location,
                        f"proof beat omits facts: {sorted(missing)}",
                    )
                revealed_proof_facts.update(revealed)

            if draft_beat.proof_stage_before != rolling_stage:
                hard(
                    "PROOF_STAGE_BEFORE_MISMATCH",
                    location,
                    "proof stage must continue from the prior beat",
                )
            if draft_beat.proof_stage_after != packet_beat.proof_stage:
                hard(
                    "PROOF_STAGE_AFTER_MISMATCH",
                    location,
                    "proof stage must preserve the Script Packet",
                )
            if draft_beat.proof_stage_after < draft_beat.proof_stage_before:
                hard(
                    "PROOF_STAGE_REGRESSION",
                    location,
                    "proof stage cannot move backwards",
                )
            rolling_stage = draft_beat.proof_stage_after

            expected_delta_codes = (
                DeterministicDraftAdapter.expected_state_delta_codes(
                    draft_beat.function,
                    draft_beat.proof_stage_before,
                    draft_beat.proof_stage_after,
                    packet,
                )
            )
            if draft_beat.state_delta_codes != expected_delta_codes:
                hard(
                    "STATE_DELTA_MISMATCH",
                    location,
                    "state delta codes must exactly match the bound packet",
                )

            if draft_beat.reward_ids != packet_beat.reward_ids:
                hard(
                    "REWARD_BINDING_MISMATCH",
                    location,
                    "reward ids must preserve the Script Packet",
                )
            is_final = index == len(draft.beats) - 1
            if is_final:
                expected_cliff = (
                    f"next_episode_must_answer_or_escalate:"
                    f"{packet.deferred_question}"
                )
                if draft_beat.cliff_obligation != expected_cliff:
                    hard(
                        "MISSING_CLIFF_OBLIGATION",
                        location,
                        "final beat must bind the deferred question",
                    )
            elif draft_beat.cliff_obligation is not None:
                hard(
                    "EARLY_CLIFF_OBLIGATION",
                    location,
                    "only the final beat may carry the cliff obligation",
                )

        if len(beat_ids) != len(set(beat_ids)):
            hard("DUPLICATE_BEAT_ID", "draft.beats", "beat ids must be unique")
        if packet_proof_fact_ids != revealed_proof_facts:
            hard(
                "DRAFT_OMITS_PACKET_PROOF",
                "draft.beats",
                "draft must reveal every packet proof fact in a proof beat",
            )
        if rolling_stage != packet.state_after.proof_stage:
            hard(
                "FINAL_PROOF_STAGE_MISMATCH",
                "draft.beats",
                "draft must reach the packet state_after proof stage",
            )

        return DraftVerificationReport(draft.episode_number, tuple(findings))
