#!/usr/bin/env python3
"""Build the owner-approved HIL 2 first-service arc lock."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from v4_shortform_script_foundry.approval import (  # noqa: E402
    ApprovalReceipt,
    HilGate,
    ReviewDecision,
)
from v4_shortform_script_foundry.canonical import (  # noqa: E402
    canonical_json,
    canonical_sha256,
    canonical_text_sha256,
)
from v4_shortform_script_foundry.planning_artifact import (  # noqa: E402
    export_hil2_planning_document,
)


OUTPUT_ROOT = (
    ROOT
    / "artifacts"
    / "approved"
    / "afterlife_restaurant"
    / "hil2"
    / "arc01_first_service"
)
CANDIDATE_BUILDER_PATH = (
    ROOT / "tools" / "build_afterlife_restaurant_hil2_arc01_candidate.py"
)
DECIDED_AT = "2026-08-02T02:27:56+09:00"


def _load_candidate_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "afterlife_restaurant_hil2_arc01_candidate_builder",
        CANDIDATE_BUILDER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load the HIL 2 candidate builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_approval() -> tuple[object, ApprovalReceipt, dict[str, object]]:
    candidate_builder = _load_candidate_builder()
    arc = candidate_builder.build_arc()
    canonical, hil1_manifest = candidate_builder.build_hil1_context()
    review_payload = {
        "decision": "approve",
        "owner_instruction": "좋아 가 볼까...?",
        "approved_scope": (
            "HIL 2 first-service arc state transitions, two-to-three episode "
            "band, three-episode default allocation, Doyun early undefeated "
            "cooking rule, and character-appeal boundaries"
        ),
        "excluded_scope": (
            "exact dish names, locked dialogue, HIL 3 episode approval, visual "
            "canon, external delivery, premise-distance clearance, and rights clearance"
        ),
        "adaptation_map_path": candidate_builder.ADAPTATION_MAP_PATH.relative_to(
            ROOT
        ).as_posix(),
        "adaptation_map_sha256": canonical_text_sha256(
            candidate_builder.ADAPTATION_MAP_PATH.read_text(encoding="utf-8")
        ),
        "rough_beat_sheet_path": candidate_builder.EP001_ROUGH_PATH.relative_to(
            ROOT
        ).as_posix(),
        "rough_beat_sheet_sha256": canonical_text_sha256(
            candidate_builder.EP001_ROUGH_PATH.read_text(encoding="utf-8")
        ),
    }
    receipt = ApprovalReceipt.issue(
        gate_id=HilGate.HIL2_ARC,
        work_id=arc.work_id,
        artifact_id=arc.artifact_id,
        revision=arc.revision,
        artifact_content_sha256=arc.content_sha256,
        parent_content_sha256s=(canonical.content_sha256,),
        parent_approval_receipt_sha256s=(
            str(hil1_manifest["approval_receipt_sha256"]),
        ),
        decision=ReviewDecision.APPROVE,
        reviewer_id="workspace_owner",
        reviewer_role="owner",
        rubric_version="afterlife-first-service-arc-v1",
        review_payload_sha256=canonical_sha256(review_payload),
        decided_at=DECIDED_AT,
    )
    return arc, receipt, review_payload


def build_outputs() -> dict[Path, str]:
    candidate_builder = _load_candidate_builder()
    canonical, hil1_manifest = candidate_builder.build_hil1_context()
    arc, receipt, review_payload = build_approval()
    planning = export_hil2_planning_document(arc).markdown
    planning = planning.replace(
        "# HIL 2 아크 기획 후보",
        "# HIL 2 아크 기획 정본",
        1,
    ).replace(
        "> 상태: candidate. Owner 승인 전에는 대본 정본이 아니다.",
        (
            "> 상태: owner approved HIL 2. HIL 3 대본과 외부 제작 전달은 "
            "별도 승인 전까지 금지한다."
        ),
        1,
    )
    planning += (
        "\n\n## 승인 결합\n\n"
        f"- approval_receipt_sha256: `{receipt.receipt_sha256}`\n"
        f"- parent_hil1_content_sha256: `{canonical.content_sha256}`\n"
        "- causal_chain_distance: `pending_not_evaluated`\n"
        "- external_promotion_allowed: `false`\n"
    )
    planning = planning.rstrip("\n") + "\n"
    distance_status = candidate_builder.build_distance_status()
    manifest = {
        "schema_version": "1",
        "work_id": arc.work_id,
        "artifact_id": arc.artifact_id,
        "revision": arc.revision,
        "status": "owner_approved_hil2",
        "arc_content_sha256": arc.content_sha256,
        "approval_receipt_sha256": receipt.receipt_sha256,
        "review_payload_sha256": canonical_sha256(review_payload),
        "parent_hil1_content_sha256": canonical.content_sha256,
        "parent_hil1_approval_receipt_sha256": hil1_manifest[
            "approval_receipt_sha256"
        ],
        "adaptation_map_sha256": review_payload["adaptation_map_sha256"],
        "rough_beat_sheet_sha256": review_payload["rough_beat_sheet_sha256"],
        "causal_chain_distance_status": distance_status["status"],
        "causal_chain_distance_status_sha256": canonical_sha256(
            distance_status
        ),
        "external_promotion_allowed": False,
        "hil3_status": "not_started",
        "next_gate": "hil3_episode_candidate",
    }
    return {
        OUTPUT_ROOT / "arc_contract.json": canonical_json(arc) + "\n",
        OUTPUT_ROOT / "arc_planning.md": planning,
        OUTPUT_ROOT / "approval_receipt.json": canonical_json(receipt) + "\n",
        OUTPUT_ROOT / "review_payload.json": canonical_json(review_payload) + "\n",
        OUTPUT_ROOT / "causal_chain_distance_status.json": (
            canonical_json(distance_status) + "\n"
        ),
        OUTPUT_ROOT / "manifest.json": canonical_json(manifest) + "\n",
    }


def check_outputs(outputs: dict[Path, str]) -> tuple[str, ...]:
    findings: list[str] = []
    for path, expected in outputs.items():
        if not path.exists():
            findings.append(f"missing:{path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8") != expected:
            findings.append(f"stale:{path.relative_to(ROOT)}")
    if OUTPUT_ROOT.exists():
        for path in OUTPUT_ROOT.iterdir():
            if path.is_file() and path not in outputs:
                findings.append(f"unexpected:{path.relative_to(ROOT)}")
    return tuple(findings)


def write_outputs(outputs: dict[Path, str]) -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build_outputs()
    if args.check:
        findings = check_outputs(outputs)
        if findings:
            print("\n".join(findings))
            return 1
        print("afterlife_restaurant HIL 2 arc01 approval is current")
        return 0
    write_outputs(outputs)
    print(OUTPUT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
