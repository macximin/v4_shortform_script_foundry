from __future__ import annotations

from dataclasses import replace
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from v4_shortform_script_foundry.artifacts import ArtifactEnvelope  # noqa: E402
from v4_shortform_script_foundry.canonical import canonical_json  # noqa: E402
from v4_shortform_script_foundry.draft_script import (  # noqa: E402
    DeterministicDraftAdapter,
    DraftStatus,
)
from v4_shortform_script_foundry.draft_verification import (  # noqa: E402
    DraftScriptVerifier,
)
from v4_shortform_script_foundry.fact_ledger import (  # noqa: E402
    Certainty,
    FactLedger,
    FactRecord,
    SourceBinding,
)
from v4_shortform_script_foundry.grammar_import import (  # noqa: E402
    load_approved_grammar_import,
)
from v4_shortform_script_foundry.pipeline import V4ShortformPipeline  # noqa: E402
from v4_shortform_script_foundry.series_plan import ProofStage  # noqa: E402


IMPORT_PATH = (
    ROOT
    / "imports"
    / "approved_genre_grammar"
    / "ep07_external_proof_reading_v1.json"
)


def make_ledger() -> FactLedger:
    return FactLedger(
        premise_id="synthetic-external-proof-reading",
        sources=(
            SourceBinding(
                source_id="owner-original-premise-v1",
                source_kind="synthetic_fixture",
                locator="tests:synthetic-external-proof-reading",
            ),
        ),
        facts=(
            FactRecord(
                fact_id="f-proof",
                subject="portable_evidence",
                predicate="is_disputed",
                value="true",
                certainty=Certainty.CONFIRMED,
                source_ids=("owner-original-premise-v1",),
                tags=(
                    "disputed_portable_proof",
                    "resource_value",
                    "misperception",
                ),
            ),
            FactRecord(
                fact_id="f-validator",
                subject="validator",
                predicate="can_read_marker",
                value="true",
                certainty=Certainty.CONFIRMED,
                source_ids=("owner-original-premise-v1",),
                tags=("external_validator", "authority"),
            ),
        ),
    )


def run_pipeline():
    grammar = load_approved_grammar_import(IMPORT_PATH).grammar
    ledger = make_ledger()
    result = V4ShortformPipeline().run(ledger, grammar)
    return ledger, grammar, result


class DraftContractTests(unittest.TestCase):
    def test_pipeline_builds_three_evidence_grade_drafts(self) -> None:
        _, _, result = run_pipeline()

        self.assertTrue(result.passed)
        self.assertEqual(3, len(result.drafts))
        self.assertTrue(all(report.passed for report in result.draft_reports))
        for draft, packet in zip(result.drafts, result.packets, strict=True):
            self.assertEqual(packet.runtime_seconds, draft.runtime_seconds)
            self.assertEqual(DraftStatus.CANDIDATE, draft.status)
            self.assertEqual(
                DeterministicDraftAdapter.SOURCE_DISTANCE,
                draft.source_distance,
            )
            self.assertTrue(
                all(
                    beat.scene_purpose
                    and beat.observable_action
                    and beat.dialogue_function
                    for beat in draft.beats
                )
            )
            self.assertIn(
                packet.deferred_question,
                draft.beats[-1].cliff_obligation,
            )

    def test_drafts_are_deterministic_and_exportable(self) -> None:
        _, _, first = run_pipeline()
        _, _, second = run_pipeline()

        self.assertEqual(first.drafts, second.drafts)
        envelope = ArtifactEnvelope.create(
            artifact_type="functional_draft_script",
            artifact_id="synthetic-external-proof-reading:ep001",
            payload=first.drafts[0],
        )
        self.assertTrue(envelope.verify())
        self.assertIn("information_revealed_fact_ids", envelope.to_json())

    def test_drafts_contain_no_ep07_source_specific_tokens(self) -> None:
        _, _, result = run_pipeline()
        rendered = canonical_json(result.drafts)
        forbidden = (
            "한강그룹",
            "회장님 서명",
            "3천만 원",
            "수표",
            "은행",
            "백수 이모부",
        )

        self.assertTrue(all(token not in rendered for token in forbidden))

    def test_automatic_draft_promotion_is_rejected(self) -> None:
        ledger, _, result = run_pipeline()
        promoted = replace(result.drafts[0], status=DraftStatus.APPROVED)

        report = DraftScriptVerifier().verify(
            promoted,
            result.packets[0],
            result.plan.episodes[0],
            ledger,
        )

        self.assertFalse(report.passed)
        self.assertIn(
            "AUTO_PROMOTION_FORBIDDEN",
            {finding.code for finding in report.findings},
        )

    def test_stale_source_packet_hash_is_rejected(self) -> None:
        ledger, _, result = run_pipeline()
        stale = replace(result.drafts[0], source_packet_sha256="0" * 64)

        report = DraftScriptVerifier().verify(
            stale,
            result.packets[0],
            result.plan.episodes[0],
            ledger,
        )

        self.assertFalse(report.passed)
        self.assertIn(
            "SOURCE_PACKET_HASH_MISMATCH",
            {finding.code for finding in report.findings},
        )

    def test_proof_fact_cannot_be_spent_in_hook(self) -> None:
        ledger, _, result = run_pipeline()
        draft = result.drafts[0]
        hook = replace(
            draft.beats[0],
            information_revealed_fact_ids=("f-proof",),
            information_withheld_fact_ids=(),
        )
        broken = replace(draft, beats=(hook,) + draft.beats[1:])

        report = DraftScriptVerifier().verify(
            broken,
            result.packets[0],
            result.plan.episodes[0],
            ledger,
        )

        self.assertFalse(report.passed)
        self.assertIn(
            "INFORMATION_REVEALED_TOO_EARLY",
            {finding.code for finding in report.findings},
        )

    def test_final_beat_requires_cliff_obligation(self) -> None:
        ledger, _, result = run_pipeline()
        draft = result.drafts[0]
        final = replace(draft.beats[-1], cliff_obligation=None)
        broken = replace(draft, beats=draft.beats[:-1] + (final,))

        report = DraftScriptVerifier().verify(
            broken,
            result.packets[0],
            result.plan.episodes[0],
            ledger,
        )

        self.assertFalse(report.passed)
        self.assertIn(
            "MISSING_CLIFF_OBLIGATION",
            {finding.code for finding in report.findings},
        )

    def test_scene_purpose_must_match_episode_contract(self) -> None:
        ledger, _, result = run_pipeline()
        draft = result.drafts[0]
        hook = replace(
            draft.beats[0],
            scene_purpose="generic_hook_that_ignores_renderer",
        )
        broken = replace(draft, beats=(hook,) + draft.beats[1:])

        report = DraftScriptVerifier().verify(
            broken,
            result.packets[0],
            result.plan.episodes[0],
            ledger,
        )

        self.assertFalse(report.passed)
        self.assertIn(
            "SCENE_PURPOSE_MISMATCH",
            {finding.code for finding in report.findings},
        )

    def test_hook_must_preserve_planned_information_withholding(self) -> None:
        ledger, _, result = run_pipeline()
        draft = result.drafts[0]
        hook = replace(
            draft.beats[0],
            information_withheld_fact_ids=(),
        )
        broken = replace(draft, beats=(hook,) + draft.beats[1:])

        report = DraftScriptVerifier().verify(
            broken,
            result.packets[0],
            result.plan.episodes[0],
            ledger,
        )

        self.assertFalse(report.passed)
        self.assertIn(
            "INFORMATION_WITHHOLD_MISMATCH",
            {finding.code for finding in report.findings},
        )

    def test_proof_stage_cannot_regress(self) -> None:
        ledger, _, result = run_pipeline()
        draft = result.drafts[0]
        final = replace(
            draft.beats[-1],
            proof_stage_after=ProofStage.UNKNOWN,
        )
        broken = replace(draft, beats=draft.beats[:-1] + (final,))

        report = DraftScriptVerifier().verify(
            broken,
            result.packets[0],
            result.plan.episodes[0],
            ledger,
        )
        codes = {finding.code for finding in report.findings}

        self.assertFalse(report.passed)
        self.assertIn("PROOF_STAGE_REGRESSION", codes)
        self.assertIn("FINAL_PROOF_STAGE_MISMATCH", codes)

    def test_state_delta_codes_must_match_packet(self) -> None:
        ledger, _, result = run_pipeline()
        draft = result.drafts[0]
        pressure = replace(
            draft.beats[1],
            state_delta_codes=("state:no_change",),
        )
        broken = replace(
            draft,
            beats=(draft.beats[0], pressure) + draft.beats[2:],
        )

        report = DraftScriptVerifier().verify(
            broken,
            result.packets[0],
            result.plan.episodes[0],
            ledger,
        )

        self.assertFalse(report.passed)
        self.assertIn(
            "STATE_DELTA_MISMATCH",
            {finding.code for finding in report.findings},
        )

    def test_unconfirmed_fact_cannot_be_revealed_as_proof(self) -> None:
        ledger, _, result = run_pipeline()
        claimed = FactRecord(
            fact_id="f-rumor",
            subject="observer",
            predicate="claims_value",
            value="unverified",
            certainty=Certainty.CLAIMED,
            source_ids=("owner-original-premise-v1",),
            tags=("rumor",),
        )
        expanded = replace(ledger, facts=ledger.facts + (claimed,))
        draft = result.drafts[0]
        proof = replace(
            draft.beats[2],
            information_revealed_fact_ids=(
                *draft.beats[2].information_revealed_fact_ids,
                "f-rumor",
            ),
        )
        broken = replace(
            draft,
            beats=draft.beats[:2] + (proof,) + draft.beats[3:],
        )

        report = DraftScriptVerifier().verify(
            broken,
            result.packets[0],
            result.plan.episodes[0],
            expanded,
        )

        self.assertFalse(report.passed)
        self.assertIn(
            "UNCONFIRMED_INFORMATION_REVEAL",
            {finding.code for finding in report.findings},
        )


if __name__ == "__main__":
    unittest.main()
