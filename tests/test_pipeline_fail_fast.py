from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

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
from v4_shortform_script_foundry.pipeline import (  # noqa: E402
    PipelineHardFailure,
    V4ShortformPipeline,
)
from v4_shortform_script_foundry.verification import (  # noqa: E402
    Severity,
    VerificationFinding,
    VerificationReport,
)


def make_inputs() -> tuple[FactLedger, GenreGrammarPacket]:
    ledger = FactLedger(
        premise_id="synthetic-fail-fast",
        sources=(
            SourceBinding(
                source_id="owner-fixture",
                source_kind="synthetic_fixture",
                locator="tests:fail-fast",
            ),
        ),
        facts=(
            FactRecord(
                fact_id="f1",
                subject="protagonist",
                predicate="has_capability",
                value="true",
                certainty=Certainty.CONFIRMED,
                source_ids=("owner-fixture",),
                tags=("capability",),
            ),
        ),
    )
    candidate = GenreGrammarPacket(
        grammar_id="fail-fast-grammar",
        version="0.1.0",
        target_profile="synthetic-test-only",
        entry_pressure="capability_denial",
        primary_reward="earned_authority",
        preferences=(
            RendererPreference(
                renderer=RendererKind.COMPETENCE,
                weight=100,
                threat="capability_denial",
                proof_mode="visible_execution",
                reward_target="earned_authority",
                required_fact_tags=("capability",),
            ),
        ),
        evidence_ids=("synthetic-evidence",),
        status=GrammarStatus.CANDIDATE,
    )
    grammar = replace(
        candidate,
        status=GrammarStatus.APPROVED,
        owner_approval_sha256=candidate.content_sha256,
    )
    return ledger, grammar


class RejectingVerifier:
    def verify(self, packet, contract, ledger, grammar):
        return VerificationReport(
            episode_number=contract.episode_number,
            findings=(
                VerificationFinding(
                    code="SYNTHETIC_HARD_FAILURE",
                    severity=Severity.HARD,
                    location="packet",
                    message="synthetic fail-fast fixture",
                ),
            ),
        )


class CountingDraftAdapter:
    def __init__(self) -> None:
        self.calls = 0

    def build(self, packet, contract, ledger, grammar):
        self.calls += 1
        raise AssertionError("draft adapter must not run after hard failure")


class PipelineFailFastTests(unittest.TestCase):
    def test_script_failure_prevents_draft_and_later_episodes(self) -> None:
        ledger, grammar = make_inputs()
        adapter = CountingDraftAdapter()
        pipeline = V4ShortformPipeline(
            verifier=RejectingVerifier(),
            draft_adapter=adapter,
        )

        with self.assertRaises(PipelineHardFailure) as raised:
            pipeline.run(ledger, grammar)

        self.assertEqual("script_packet", raised.exception.stage)
        self.assertEqual(1, raised.exception.episode_number)
        self.assertEqual(0, adapter.calls)


if __name__ == "__main__":
    unittest.main()
