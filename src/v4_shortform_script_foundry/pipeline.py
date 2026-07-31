"""Deterministic orchestration for the pre-writer vertical slice."""

from __future__ import annotations

from dataclasses import dataclass

from .draft_script import DeterministicDraftAdapter, DraftScript
from .draft_verification import DraftScriptVerifier, DraftVerificationReport
from .episode_state import EpisodeState, EpisodeStatePlanner
from .fact_ledger import FactLedger
from .genre_grammar import GenreGrammarPacket
from .script_packet import ScriptPacket, ScriptPacketBuilder
from .series_plan import SeriesPlan, SeriesPlanner
from .verification import ScriptVerifier, VerificationReport


class PipelineHardFailure(RuntimeError):
    """Stops the pipeline before a failed artifact can feed downstream work."""

    def __init__(
        self,
        *,
        stage: str,
        episode_number: int,
        report: VerificationReport | DraftVerificationReport,
    ) -> None:
        super().__init__(
            f"{stage} hard verification failed for episode {episode_number}"
        )
        self.stage = stage
        self.episode_number = episode_number
        self.report = report


@dataclass(frozen=True, slots=True)
class PipelineResult:
    plan: SeriesPlan
    states: tuple[EpisodeState, ...]
    packets: tuple[ScriptPacket, ...]
    reports: tuple[VerificationReport, ...]
    drafts: tuple[DraftScript, ...]
    draft_reports: tuple[DraftVerificationReport, ...]

    @property
    def passed(self) -> bool:
        return all(report.passed for report in self.reports) and all(
            report.passed for report in self.draft_reports
        )


class V4ShortformPipeline:
    """Runs Fact -> Renderer -> Plan -> State -> Packet -> Verify."""

    def __init__(
        self,
        *,
        series_planner: SeriesPlanner | None = None,
        state_planner: EpisodeStatePlanner | None = None,
        packet_builder: ScriptPacketBuilder | None = None,
        verifier: ScriptVerifier | None = None,
        draft_adapter: DeterministicDraftAdapter | None = None,
        draft_verifier: DraftScriptVerifier | None = None,
    ) -> None:
        self._series_planner = series_planner or SeriesPlanner()
        self._state_planner = state_planner or EpisodeStatePlanner()
        self._packet_builder = packet_builder or ScriptPacketBuilder()
        self._verifier = verifier or ScriptVerifier()
        self._draft_adapter = draft_adapter or DeterministicDraftAdapter()
        self._draft_verifier = draft_verifier or DraftScriptVerifier()

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
        drafts: list[DraftScript] = []
        draft_reports: list[DraftVerificationReport] = []

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
            if not report.passed:
                raise PipelineHardFailure(
                    stage="script_packet",
                    episode_number=contract.episode_number,
                    report=report,
                )
            draft = self._draft_adapter.build(
                packet,
                contract,
                ledger,
                grammar,
            )
            draft_report = self._draft_verifier.verify(
                draft,
                packet,
                contract,
                ledger,
            )
            if not draft_report.passed:
                raise PipelineHardFailure(
                    stage="functional_draft",
                    episode_number=contract.episode_number,
                    report=draft_report,
                )
            states.append(state_after)
            packets.append(packet)
            reports.append(report)
            drafts.append(draft)
            draft_reports.append(draft_report)

        return PipelineResult(
            plan=plan,
            states=tuple(states),
            packets=tuple(packets),
            reports=tuple(reports),
            drafts=tuple(drafts),
            draft_reports=tuple(draft_reports),
        )
