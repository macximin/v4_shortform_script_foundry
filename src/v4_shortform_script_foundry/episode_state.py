"""Knowledge, proof-stage, status, and reward state transitions."""

from __future__ import annotations

from dataclasses import dataclass

from .series_plan import EpisodeContract, ProofStage


@dataclass(frozen=True, slots=True)
class EpisodeState:
    episode_number: int
    actual_status: str
    perceived_status: str
    proof_stage: ProofStage
    humiliation_debt: int
    paid_rewards: tuple[str, ...]
    open_questions: tuple[str, ...]

    @classmethod
    def initial(
        cls,
        *,
        actual_status: str = "latent_value",
        perceived_status: str = "devalued",
    ) -> "EpisodeState":
        return cls(
            episode_number=0,
            actual_status=actual_status,
            perceived_status=perceived_status,
            proof_stage=ProofStage.UNKNOWN,
            humiliation_debt=0,
            paid_rewards=(),
            open_questions=(),
        )


class EpisodeStatePlanner:
    def advance(
        self,
        previous: EpisodeState,
        contract: EpisodeContract,
    ) -> EpisodeState:
        if contract.episode_number != previous.episode_number + 1:
            raise ValueError("episode state must advance consecutively")
        if contract.proof_stage_after < previous.proof_stage:
            raise ValueError("proof stage cannot move backwards")

        rewards = list(previous.paid_rewards)
        for reward in contract.reward_paid:
            if reward not in rewards:
                rewards.append(reward)

        if contract.function.value == "payoff_and_reopen":
            humiliation_debt = max(0, previous.humiliation_debt - 1)
        else:
            humiliation_debt = previous.humiliation_debt + 1

        return EpisodeState(
            episode_number=contract.episode_number,
            actual_status=previous.actual_status,
            perceived_status=contract.perception_after,
            proof_stage=contract.proof_stage_after,
            humiliation_debt=humiliation_debt,
            paid_rewards=tuple(rewards),
            open_questions=(contract.deferred_question,),
        )
