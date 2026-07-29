"""Three-level series plan: season spine, episode function, and reward curve."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum, StrEnum

from .fact_ledger import FactLedger
from .genre_grammar import GenreGrammarPacket, RendererKind
from .renderer_router import RendererDecision, RendererRouter


class ProofStage(IntEnum):
    UNKNOWN = 0
    CLAIMED = 1
    INDICATED = 2
    MATERIALIZED = 3
    PUBLICLY_RECOGNIZED = 4


class EpisodeFunction(StrEnum):
    PROMISE = "promise"
    ESCALATION = "escalation"
    PAYOFF_AND_REOPEN = "payoff_and_reopen"


@dataclass(frozen=True, slots=True)
class EpisodeContract:
    episode_number: int
    function: EpisodeFunction
    renderer: RendererDecision
    proof_stage_after: ProofStage
    reward_paid: tuple[str, ...]
    deferred_question: str
    perception_after: str
    irreversible_change: str
    target_runtime_seconds: int


@dataclass(frozen=True, slots=True)
class SeriesPlan:
    premise_id: str
    grammar_packet_id: str
    episodes: tuple[EpisodeContract, ...]

    def episode(self, episode_number: int) -> EpisodeContract:
        for contract in self.episodes:
            if contract.episode_number == episode_number:
                return contract
        raise KeyError(episode_number)


class SeriesPlanner:
    def __init__(self, router: RendererRouter | None = None) -> None:
        self._router = router or RendererRouter()

    def plan(
        self,
        ledger: FactLedger,
        grammar: GenreGrammarPacket,
        *,
        episode_count: int = 3,
        target_runtime_seconds: int = 90,
    ) -> SeriesPlan:
        if episode_count < 1:
            raise ValueError("episode_count must be positive")
        if not 40 <= target_runtime_seconds <= 300:
            raise ValueError("target runtime must be between 40 and 300 seconds")

        used: list[RendererKind] = []
        contracts: list[EpisodeContract] = []
        for episode_number in range(1, episode_count + 1):
            decision = self._router.route(
                ledger,
                grammar,
                episode_number,
                tuple(used),
            )
            used.append(decision.primary)
            function, stage, rewards, question, perception, change = self._curve(
                episode_number,
                episode_count,
                grammar,
                decision,
            )
            contracts.append(
                EpisodeContract(
                    episode_number=episode_number,
                    function=function,
                    renderer=decision,
                    proof_stage_after=stage,
                    reward_paid=rewards,
                    deferred_question=question,
                    perception_after=perception,
                    irreversible_change=change,
                    target_runtime_seconds=target_runtime_seconds,
                )
            )
        return SeriesPlan(
            premise_id=ledger.premise_id,
            grammar_packet_id=grammar.packet_id,
            episodes=tuple(contracts),
        )

    @staticmethod
    def _curve(
        episode_number: int,
        episode_count: int,
        grammar: GenreGrammarPacket,
        decision: RendererDecision,
    ) -> tuple[
        EpisodeFunction,
        ProofStage,
        tuple[str, ...],
        str,
        str,
        str,
    ]:
        if episode_count == 1 or episode_number == episode_count:
            return (
                EpisodeFunction.PAYOFF_AND_REOPEN,
                ProofStage.PUBLICLY_RECOGNIZED,
                (grammar.primary_reward,),
                f"what_cost_follows_{decision.reward_target}",
                "publicly_reclassified",
                "primary_reward_paid",
            )
        if episode_number == 1:
            return (
                EpisodeFunction.PROMISE,
                ProofStage.INDICATED,
                ("curiosity_lock",),
                f"can_{decision.proof_mode}_survive_challenge",
                "devaluation_contested",
                "pressure_registered",
            )
        return (
            EpisodeFunction.ESCALATION,
            ProofStage.MATERIALIZED,
            ("proof_progress",),
            f"will_{decision.proof_mode}_change_public_judgment",
            "credible_minority_updates",
            "proof_moved",
        )
