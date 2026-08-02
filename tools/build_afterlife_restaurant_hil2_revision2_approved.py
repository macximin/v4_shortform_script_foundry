#!/usr/bin/env python3
"""Build the owner-approved established-service HIL 2 revision-2 lock."""

from __future__ import annotations

import argparse
import hashlib
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
    / "arc01_established_service_rev2"
)
CANDIDATE_BUILDER_PATH = (
    ROOT / "tools" / "build_afterlife_restaurant_hil2_revision2_candidates.py"
)
DECIDED_AT = "2026-08-02T06:15:08+09:00"
OWNER_INSTRUCTION = (
    "2-3화까지만 보고, 기타 영상자료들 혹시 더 분석하고 싶은 거 있으면 분석하고 "
    "그러고 나서 충분히 진짜 세밀하게 분석했다 이후 대본 바로 가자고 대본 1화 분량만"
)


def _load_candidate_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "afterlife_restaurant_hil2_revision2_candidate_builder",
        CANDIDATE_BUILDER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load the HIL 2 revision-2 candidate builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_approval() -> tuple[object, ApprovalReceipt, dict[str, object]]:
    candidate_builder = _load_candidate_builder()
    arc = candidate_builder.build_candidate_a()
    canonical, hil1_manifest = candidate_builder.build_hil1_context()
    previous_hil2 = candidate_builder._approved_hil2_context()
    comparison_path = candidate_builder.OUTPUT_ROOT / "comparison.md"
    allocation_path = candidate_builder.CANDIDATE_A_ROOT / "episode_allocation.md"
    research_receipt = candidate_builder.build_research_receipt()
    review_payload = {
        "decision": "approve",
        "owner_instruction": OWNER_INSTRUCTION,
        "approved_scope": (
            "HIL 2 revision-2 candidate A: already-operating restaurant, complete "
            "Doyun, undefeated early cooking, one-episode guest closure, two planned "
            "complete flavor finishes, the girl's service authority, reusable order "
            "residue, and an eight-to-twelve-second post-guest duo work coda"
        ),
        "excluded_scope": (
            "candidate B, locked dialogue, HIL 3 episode approval, BR0 or BR1, visual "
            "canon, premise-distance clearance, rights clearance, external delivery, "
            "and any episode after episode one"
        ),
        "superseded_parent_hil2_arc_content_sha256": previous_hil2[
            "arc_content_sha256"
        ],
        "superseded_parent_hil2_approval_receipt_sha256": previous_hil2[
            "approval_receipt_sha256"
        ],
        "comparison_path": comparison_path.relative_to(ROOT).as_posix(),
        "comparison_sha256": hashlib.sha256(comparison_path.read_bytes()).hexdigest(),
        "episode_allocation_path": allocation_path.relative_to(ROOT).as_posix(),
        "episode_allocation_sha256": hashlib.sha256(
            allocation_path.read_bytes()
        ).hexdigest(),
        "research_receipt_sha256": canonical_sha256(research_receipt),
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
        rubric_version="afterlife-established-service-arc-v2",
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
            "> 상태: owner approved HIL 2 revision 2. HIL 3 대본 승인과 "
            "외부 제작 전달은 별도 승인 전까지 금지한다."
        ),
        1,
    )
    planning += (
        "\n\n## 승인 결합\n\n"
        f"- approval_receipt_sha256: `{receipt.receipt_sha256}`\n"
        f"- parent_hil1_content_sha256: `{canonical.content_sha256}`\n"
        "- supersedes: `owner-approved HIL 2 revision 1 first-service arc`\n"
        "- causal_chain_distance: `pending_not_evaluated`\n"
        "- external_promotion_allowed: `false`\n"
    )
    planning = planning.rstrip("\n") + "\n"
    distance_status = candidate_builder.build_distance_status(arc.artifact_id)
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
        "superseded_parent_hil2_arc_content_sha256": review_payload[
            "superseded_parent_hil2_arc_content_sha256"
        ],
        "superseded_parent_hil2_approval_receipt_sha256": review_payload[
            "superseded_parent_hil2_approval_receipt_sha256"
        ],
        "research_receipt_sha256": review_payload["research_receipt_sha256"],
        "causal_chain_distance_status": distance_status["status"],
        "causal_chain_distance_status_sha256": canonical_sha256(distance_status),
        "external_promotion_allowed": False,
        "hil3_status": "not_started",
        "next_gate": "hil3_episode_candidate_ep001_only",
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
        print("afterlife_restaurant HIL 2 revision-2 approval is current")
        return 0
    write_outputs(outputs)
    print(OUTPUT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
