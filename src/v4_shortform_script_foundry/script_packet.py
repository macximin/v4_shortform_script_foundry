"""Thin, prose-free episode contract consumed by a future writer adapter."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .episode_state import EpisodeState
from .fact_ledger import FactLedger
from .genre_grammar import RendererKind
from .series_plan import EpisodeContract, ProofStage


class PacketStatus(StrEnum):
    CANDIDATE = "candidate"
    APPROVED = "approved"


class BeatFunction(StrEnum):
    HOOK = "hook"
    PRESSURE = "pressure"
    PROOF = "proof"
    REWARD_CLIFF = "reward_cliff"


@dataclass(frozen=True, slots=True)
class BeatContract:
    beat_id: str
    function: BeatFunction
    seconds: int
    renderer: RendererKind
    proof_stage: ProofStage
    required_fact_ids: tuple[str, ...]
    reward_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ScriptPacket:
    premise_id: str
    grammar_packet_id: str
    episode_number: int
    status: PacketStatus
    state_before: EpisodeState
    state_after: EpisodeState
    deferred_question: str
    beats: tuple[BeatContract, ...]

    @property
    def runtime_seconds(self) -> int:
        return sum(beat.seconds for beat in self.beats)


class ScriptPacketBuilder:
    def build(
        self,
        ledger: FactLedger,
        grammar_packet_id: str,
        contract: EpisodeContract,
        state_before: EpisodeState,
        state_after: EpisodeState,
    ) -> ScriptPacket:
        if state_after.episode_number != contract.episode_number:
            raise ValueError("state_after and episode contract must match")
        durations = self._allocate_runtime(contract.target_runtime_seconds)
        fact_ids = contract.renderer.bound_fact_ids
        beats = (
            BeatContract(
                beat_id=f"ep{contract.episode_number:03d}-b01",
                function=BeatFunction.HOOK,
                seconds=durations[0],
                renderer=contract.renderer.primary,
                proof_stage=state_before.proof_stage,
                required_fact_ids=(),
            ),
            BeatContract(
                beat_id=f"ep{contract.episode_number:03d}-b02",
                function=BeatFunction.PRESSURE,
                seconds=durations[1],
                renderer=contract.renderer.primary,
                proof_stage=state_before.proof_stage,
                required_fact_ids=(),
            ),
            BeatContract(
                beat_id=f"ep{contract.episode_number:03d}-b03",
                function=BeatFunction.PROOF,
                seconds=durations[2],
                renderer=contract.renderer.primary,
                proof_stage=contract.proof_stage_after,
                required_fact_ids=fact_ids,
            ),
            BeatContract(
                beat_id=f"ep{contract.episode_number:03d}-b04",
                function=BeatFunction.REWARD_CLIFF,
                seconds=durations[3],
                renderer=contract.renderer.primary,
                proof_stage=contract.proof_stage_after,
                required_fact_ids=fact_ids,
                reward_ids=contract.reward_paid,
            ),
        )
        return ScriptPacket(
            premise_id=ledger.premise_id,
            grammar_packet_id=grammar_packet_id,
            episode_number=contract.episode_number,
            status=PacketStatus.CANDIDATE,
            state_before=state_before,
            state_after=state_after,
            deferred_question=contract.deferred_question,
            beats=beats,
        )

    @staticmethod
    def _allocate_runtime(total_seconds: int) -> tuple[int, int, int, int]:
        if total_seconds < 40:
            raise ValueError("script packet runtime must be at least 40 seconds")
        hook = max(5, round(total_seconds * 0.1))
        pressure = round(total_seconds * 0.35)
        proof = round(total_seconds * 0.35)
        reward_cliff = total_seconds - hook - pressure - proof
        if reward_cliff < 5:
            raise ValueError("reward/cliff beat must retain at least five seconds")
        return hook, pressure, proof, reward_cliff
