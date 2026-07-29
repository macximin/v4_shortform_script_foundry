"""Hard verification for fact, continuity, renderer, runtime, and promotion."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .fact_ledger import Certainty, FactLedger
from .genre_grammar import GenreGrammarPacket
from .script_packet import BeatFunction, PacketStatus, ScriptPacket
from .series_plan import EpisodeContract


class Severity(StrEnum):
    HARD = "hard"
    SOFT = "soft"


@dataclass(frozen=True, slots=True)
class VerificationFinding:
    code: str
    severity: Severity
    location: str
    message: str


@dataclass(frozen=True, slots=True)
class VerificationReport:
    episode_number: int
    findings: tuple[VerificationFinding, ...]

    @property
    def passed(self) -> bool:
        return not any(
            finding.severity is Severity.HARD for finding in self.findings
        )


class ScriptVerifier:
    def verify(
        self,
        packet: ScriptPacket,
        contract: EpisodeContract,
        ledger: FactLedger,
        grammar: GenreGrammarPacket,
    ) -> VerificationReport:
        findings: list[VerificationFinding] = []

        def hard(code: str, location: str, message: str) -> None:
            findings.append(
                VerificationFinding(
                    code=code,
                    severity=Severity.HARD,
                    location=location,
                    message=message,
                )
            )

        if packet.status is not PacketStatus.CANDIDATE:
            hard(
                "AUTO_PROMOTION_FORBIDDEN",
                "packet.status",
                "generated packets must remain candidates",
            )
        if packet.premise_id != ledger.premise_id:
            hard(
                "PREMISE_BINDING_MISMATCH",
                "packet.premise_id",
                "packet must bind the exact Fact Ledger premise",
            )
        if packet.grammar_packet_id != grammar.packet_id:
            hard(
                "GRAMMAR_BINDING_MISMATCH",
                "packet.grammar_packet_id",
                "packet must bind the exact grammar version",
            )
        if packet.episode_number != contract.episode_number:
            hard(
                "EPISODE_MISMATCH",
                "packet.episode_number",
                "packet and episode contract must match",
            )
        if packet.state_before.episode_number != contract.episode_number - 1:
            hard(
                "STATE_BEFORE_MISMATCH",
                "packet.state_before",
                "state_before must belong to the previous episode",
            )
        if packet.state_after.episode_number != contract.episode_number:
            hard(
                "STATE_AFTER_MISMATCH",
                "packet.state_after",
                "state_after must belong to the current episode",
            )
        if packet.runtime_seconds != contract.target_runtime_seconds:
            hard(
                "RUNTIME_MISMATCH",
                "packet.beats",
                "beat runtime must equal the episode target",
            )
        if packet.state_after.proof_stage != contract.proof_stage_after:
            hard(
                "PROOF_STAGE_MISMATCH",
                "packet.state_after.proof_stage",
                "state transition must satisfy the episode contract",
            )
        if not set(contract.reward_paid).issubset(packet.state_after.paid_rewards):
            hard(
                "REWARD_STATE_MISMATCH",
                "packet.state_after.paid_rewards",
                "paid rewards must be recorded in episode state",
            )
        beat_ids = [beat.beat_id for beat in packet.beats]
        if len(beat_ids) != len(set(beat_ids)):
            hard("DUPLICATE_BEAT_ID", "packet.beats", "beat ids must be unique")
        if not packet.deferred_question.strip():
            hard(
                "MISSING_DEFERRED_QUESTION",
                "packet.deferred_question",
                "every episode must leave an explicit next question",
            )
        elif packet.deferred_question != contract.deferred_question:
            hard(
                "DEFERRED_QUESTION_MISMATCH",
                "packet.deferred_question",
                "packet must preserve the planned next question",
            )

        functions = {beat.function for beat in packet.beats}
        if BeatFunction.PROOF not in functions:
            hard(
                "MISSING_PROOF_BEAT",
                "packet.beats",
                "episode packet must contain a proof beat",
            )
        if BeatFunction.REWARD_CLIFF not in functions:
            hard(
                "MISSING_REWARD_CLIFF_BEAT",
                "packet.beats",
                "episode packet must contain a reward/cliff beat",
            )

        for beat in packet.beats:
            if beat.renderer is not contract.renderer.primary:
                hard(
                    "RENDERER_MISMATCH",
                    beat.beat_id,
                    "beat renderer must match the routed primary lens",
                )
            for fact_id in beat.required_fact_ids:
                try:
                    fact = ledger.get(fact_id)
                except KeyError:
                    hard(
                        "UNKNOWN_FACT",
                        beat.beat_id,
                        f"beat references unknown fact {fact_id}",
                    )
                    continue
                if (
                    beat.function in {BeatFunction.PROOF, BeatFunction.REWARD_CLIFF}
                    and fact.certainty is not Certainty.CONFIRMED
                ):
                    hard(
                        "UNCONFIRMED_PROOF",
                        beat.beat_id,
                        f"proof beat cannot establish {fact_id} as confirmed",
                    )

        proof_fact_ids = {
            fact_id
            for beat in packet.beats
            if beat.function in {BeatFunction.PROOF, BeatFunction.REWARD_CLIFF}
            for fact_id in beat.required_fact_ids
        }
        missing_bound_facts = (
            set(contract.renderer.bound_fact_ids) - proof_fact_ids
        )
        if missing_bound_facts:
            hard(
                "MISSING_BOUND_PROOF_FACT",
                "packet.beats",
                f"proof beats omit routed facts: {sorted(missing_bound_facts)}",
            )

        return VerificationReport(
            episode_number=packet.episode_number,
            findings=tuple(findings),
        )
