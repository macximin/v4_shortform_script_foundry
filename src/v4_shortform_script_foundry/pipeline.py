"""Deterministic orchestration for the pre-writer vertical slice."""

from __future__ import annotations

from dataclasses import dataclass

from .episode_state import EpisodeState, EpisodeStatePlanner
from .fact_ledger import FactLedger
from .genre_grammar import GenreGrammarPacket
from .script_packet import ScriptPacket, ScriptPacketBuilder
from .series_plan import SeriesPlan, SeriesPlanner
from .verification import ScriptVerifier, VerificationReport


@dataclass(frozen=True, slots=True)
class PipelineResult:
    plan: SeriesPlan
    states: tuple[EpisodeState, ...]
    packets: tuple[ScriptPacket, ...]
    reports: tuple[VerificationReport, ...]

    @property
    def passed(self) -> bool:
        return all(report.passed for report in self.reports)


class V4ShortformPipeline:
    """Runs Fact -> Renderer -> Plan -> State -> Packet -> Verify."""

    def __init__(
        self,
        *,
        series_planner: SeriesPlanner | None = None,
        state_planner: EpisodeStatePlanner | None = None,
        packet_builder: ScriptPacketBuilder | None = None,
        verifier: ScriptVerifier | None = None,
    ) -> None:
        self._series_planner = series_planner or SeriesPlanner()
        self._state_planner = state_planner or EpisodeStatePlanner()
        self._packet_builder = packet_builder or ScriptPacketBuilder()
        self._verifier = verifier or ScriptVerifier()

    def run(
        self,
        ledger: FactLedger,
        grammar: GenreGrammarPacket,
        *,
        episode_count: int = 3,
        target_runtime_seconds: int = 90,
    ) -> PipelineResult:
        plan = self._series_planner.plan(
            ledger,
            grammar,
            episode_count=episode_count,
            target_runtime_seconds=target_runtime_seconds,
        )
        states = [EpisodeState.initial()]
        packets: list[ScriptPacket] = []
        reports: list[VerificationReport] = []

        for contract in plan.episodes:
            state_after = self._state_planner.advance(states[-1], contract)
            packet = self._packet_builder.build(
                ledger,
                grammar.packet_id,
                contract,
                states[-1],
                state_after,
            )
            report = self._verifier.verify(packet, contract, ledger, grammar)
            states.append(state_after)
            packets.append(packet)
            reports.append(report)

        return PipelineResult(
            plan=plan,
            states=tuple(states),
            packets=tuple(packets),
            reports=tuple(reports),
        )
