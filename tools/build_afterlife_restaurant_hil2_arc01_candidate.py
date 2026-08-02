#!/usr/bin/env python3
"""Build the unapproved HIL 2 first-service arc candidate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from v4_shortform_script_foundry.arc_contract import (  # noqa: E402
    ArcAcceptanceCriterion,
    ArcContract,
    ArcContractVerifier,
    AttemptBlockerMove,
    StoryState,
    StoryStateAxis,
    StoryStateEntry,
)
from v4_shortform_script_foundry.beat_patterns import (  # noqa: E402
    BeatPatternKind,
)
from v4_shortform_script_foundry.canonical import (  # noqa: E402
    canonical_json,
    canonical_sha256,
)
from v4_shortform_script_foundry.genre_grammar import (  # noqa: E402
    RendererKind,
)
from v4_shortform_script_foundry.planning_artifact import (  # noqa: E402
    export_hil2_planning_document,
)


OUTPUT_ROOT = (
    ROOT
    / "artifacts"
    / "candidates"
    / "afterlife_restaurant"
    / "hil2"
    / "arc01_first_service"
)
ADAPTATION_MAP_PATH = OUTPUT_ROOT / "adaptation_map_v0.1.md"
EP001_ROUGH_PATH = OUTPUT_ROOT / "episode_001_rough_beat_sheet_v0.1.md"
HIL1_BUILDER_PATH = ROOT / "tools" / "build_afterlife_restaurant_hil1_approved_plan.py"
HIL1_ROOT = ROOT / "artifacts" / "approved" / "afterlife_restaurant" / "hil1"
SOURCE_ROOT = (
    ROOT.parent
    / "frozen_shortform_script_foundry"
    / "10_inbox"
    / "2026-07-24_afterlife_restaurant_candidates"
    / "source_packet"
    / "저승식당"
)
SOURCE_PATHS = (
    SOURCE_ROOT / "Brief.txt",
    SOURCE_ROOT / "1화.txt",
    SOURCE_ROOT / "2화.txt",
    SOURCE_ROOT / "3화.txt",
)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_hil1_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "afterlife_restaurant_hil1_approved_builder",
        HIL1_BUILDER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load the HIL 1 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_hil1_context() -> tuple[object, dict[str, object]]:
    module = _load_hil1_builder()
    ledger = module.build_fact_ledger()
    canonical, _, _ = module.build_canonical(ledger)
    manifest = json.loads(
        (HIL1_ROOT / "manifest.json").read_text(encoding="utf-8")
    )
    if canonical.content_sha256 != manifest["canonical_content_sha256"]:
        raise ValueError("approved HIL 1 canonical hash is stale")
    if manifest["status"] != "owner_approved_hil1":
        raise ValueError("HIL 1 is not owner approved")
    return canonical, manifest


def build_distance_status() -> dict[str, object]:
    return {
        "artifact_id": "afterlife_restaurant:arc01:first_service",
        "receipt_type": "causal_chain_distance_status",
        "status": "pending_not_evaluated",
        "promotion_allowed": False,
        "reason": (
            "첫 영업 아크의 인과 사슬은 아직 독립 거리 감리를 받지 않았다. "
            "내부 후보 검토는 가능하지만 HIL 2 승인본으로 승격할 수 없다."
        ),
    }


def build_arc() -> ArcContract:
    canonical, manifest = build_hil1_context()
    distance_status = build_distance_status()
    state_before = StoryState(
        entries=(
            StoryStateEntry(
                StoryStateAxis.KNOWLEDGE,
                "doyun",
                "딸에게 돌아가야 하지만 저승 재료와 손님 배정 규칙을 읽지 못한다",
            ),
            StoryStateEntry(
                StoryStateAxis.AUDIENCE_KNOWLEDGE,
                "first_service",
                "도윤이 이승의 요리는 잘하지만 망자와 저승 재료 앞에서도 통할지는 증명되지 않았다",
            ),
            StoryStateEntry(
                StoryStateAxis.RELATION,
                "doyun_underworld_girl",
                "외부인 셰프와 규칙 보유자 사이에 검증된 운영 신뢰가 없다",
            ),
            StoryStateEntry(
                StoryStateAxis.BELONGING,
                "underworld_girl",
                "신분과 출입 권한으로 식당에 있지만 스스로 노동을 선택하지 않았다",
            ),
            StoryStateEntry(
                StoryStateAxis.RESOURCE,
                "samdo_restaurant",
                "검증되지 않은 잔여 재료만 있고 운영 자본이 없다",
            ),
            StoryStateEntry(
                StoryStateAxis.WORLD_OPERATION,
                "samdo_restaurant",
                "반복 가능한 접객과 공급 규칙이 없는 폐점 상태의 주방이다",
            ),
            StoryStateEntry(
                StoryStateAxis.PROOF_OR_EQUIVALENT,
                "guest_kim_munseong",
                "자기 취향을 말하지 않았고 마지막 식사를 선택하지 않았다",
            ),
        ),
        open_questions=(
            "도윤은 저승 조건에서 한 그릇을 완성할 수 있는가",
            "손님은 주는 대로 받는 대신 자기 음식을 선택할 수 있는가",
            "도윤과 소녀는 한 번의 접객 결정을 함께 내릴 수 있는가",
        ),
    )
    state_after = StoryState(
        entries=(
            StoryStateEntry(
                StoryStateAxis.KNOWLEDGE,
                "doyun",
                "맛있는 첫 코스의 반응을 진단 정보로 사용해 최종 식사의 조건을 좁히는 법을 안다",
            ),
            StoryStateEntry(
                StoryStateAxis.AUDIENCE_KNOWLEDGE,
                "first_service",
                "완성된 음식이 손님의 선택과 다음 영업 상태를 함께 바꿀 수 있음을 확인했다",
            ),
            StoryStateEntry(
                StoryStateAxis.RELATION,
                "doyun_underworld_girl",
                "서로에게 필요한 정보를 한 번씩 증명했고 최소 역할은 나눴지만 공동 권한은 아직 없다",
            ),
            StoryStateEntry(
                StoryStateAxis.BELONGING,
                "underworld_girl",
                "직원식과 구체적인 접객 책임 하나를 스스로 선택했다",
            ),
            StoryStateEntry(
                StoryStateAxis.RESOURCE,
                "samdo_restaurant",
                "첫 자본이 남았고 빈 창고라는 다음 비용이 드러났다",
            ),
            StoryStateEntry(
                StoryStateAxis.WORLD_OPERATION,
                "samdo_restaurant",
                "첫 손님을 결산했고 손님이 재료와 주문 단서를 가져오는 경로가 열렸다",
            ),
            StoryStateEntry(
                StoryStateAxis.PROOF_OR_EQUIVALENT,
                "guest_kim_munseong",
                "첫 코스를 완식하며 행동으로 취향을 드러내고 최종 귀항탕을 자기 선택으로 완식했다",
            ),
        ),
        open_questions=(
            "혀 없는 손님도 만족할 마지막 식사를 선택할 수 있는가",
            "부족한 재료로 두 사람이 접객을 반복할 수 있는가",
            "소녀는 언제 더 큰 운영 권한을 요구할 것인가",
        ),
    )
    arc = ArcContract(
        work_id=canonical.work_id,
        arc_id="afterlife_restaurant:arc01:first_service",
        revision=1,
        parent_canonical_content_sha256=canonical.content_sha256,
        parent_canonical_approval_receipt_sha256=str(
            manifest["approval_receipt_sha256"]
        ),
        state_before=state_before,
        state_after=state_after,
        dramatic_question=(
            "도윤은 망자가 자기 의지로 선택하는 한 끼를 완성하고 소녀와 첫 반복 영업 규칙을 만들 수 있는가"
        ),
        core_pressure=(
            "도윤은 딸에게 돌아가야 하지만 손님은 취향을 말하지 않고 창고의 재료는 낯설다. 조리 성공만으로는 마지막 식사의 선택 조건이 자동으로 주어지지 않는다"
        ),
        core_choice=(
            "도윤은 첫 코스를 맛과 진단 모두에 성공하도록 설계해 반응에서 최종 주문을 읽고, 소녀는 규칙 지식과 식욕을 접객 책임으로 바꾸기로 선택한다"
        ),
        consequence=(
            "첫 손님이 자신이 선택한 음식을 완식하고 식당은 첫 자본과 손님 반입 재료 경로를 얻지만, 공급이 안정되기 전에 다음 불가능 주문이 도착한다"
        ),
        attempt_blocker_chain=(
            AttemptBlockerMove(
                "도윤은 죽음과 계약을 요리하겠다는 선택으로 압축한다",
                "이승의 요리 경력만으로는 망자의 실제 조건을 알 수 없다",
                "도윤은 사연 설명보다 먼저 저승 재료를 능숙하게 다뤄 자신이 이 주방에 필요한 이유를 행동으로 증명한다",
            ),
            AttemptBlockerMove(
                "도윤은 손님의 감각과 반응을 깨우는 첫 코스를 완성한다",
                "음식은 완벽하게 맛있지만 손님은 아직 자기 최종 주문을 말하지 못한다",
                "손님의 완식 속도·그릇을 쥔 손·남긴 향 반응이 더 깊은 취향 단서가 된다",
            ),
            AttemptBlockerMove(
                "도윤은 현재의 몸과 식습관을 읽고 소녀는 재료 규칙을 제공한다",
                "손님의 선택권과 재료의 가능성을 두고 두 사람의 확신이 충돌한다",
                "다음 조리는 첫 성공을 부정하지 않고 재료·판단·의미를 더 깊은 단계로 변화시켜야 한다",
            ),
            AttemptBlockerMove(
                "손님은 최종 귀항탕을 맛본다",
                "눈물이나 과거 설명만으로는 수용을 증명할 수 없다",
                "손님은 처음으로 자기 취향을 말하거나 행동하고 자기 선택으로 완식한다",
            ),
            AttemptBlockerMove(
                "도윤은 잔여 재료로 소녀의 직원식을 만든다",
                "소녀는 책임을 지지 않고 왕족 구경꾼으로 남을 수 있다",
                "소녀가 선택한 음식과 접객 행동이 최소 역할 분담을 만들고 혀 없는 손님이 도착한다",
            ),
        ),
        rewards_paid=(
            "dish_and_guest_action_payoff",
            "story_unit_closure",
            "restaurant_operational_accumulation",
        ),
        rewards_deferred=("doyun_return_to_daughter",),
        irreversible_change=(
            "삼도식당은 첫 손님 접객을 마쳤고 화면에 드러난 공급·주문 규칙으로 다음 손님을 받을 수 있다"
        ),
        acceptance_criteria=(
            ArcAcceptanceCriterion(
                "AC01",
                "배정된 모든 회차가 먹을 수 있는 결과물을 완성하고 시식 뒤 관찰 가능한 행동 변화를 보여 준다",
            ),
            ArcAcceptanceCriterion(
                "AC02",
                "첫 화는 도윤의 능숙한 저승 재료 조리로 시작하고 맛있는 첫 코스의 완식과 다음 주문 단서를 지급한다. 도윤이 저승에 온 이유는 8초 안에 설명하지 않는다",
            ),
            ArcAcceptanceCriterion(
                "AC03",
                "손님의 과거는 긴 회상 대신 현재의 몸·물건·섭취·선택 증거로 드러난다",
            ),
            ArcAcceptanceCriterion(
                "AC04",
                "도윤과 소녀가 각각 결과를 바꾸는 선택을 한 번 이상 하고 누구도 설명이나 보호 대상으로 축소되지 않는다",
            ),
            ArcAcceptanceCriterion(
                "AC05",
                "아크는 첫 자본·직원식·최소 역할 분담·손님 반입 재료 경로를 남긴다",
            ),
            ArcAcceptanceCriterion(
                "AC06",
                "모든 회차가 HIL 1의 러닝타임·주요 인물·대사·고정 세트·조리 하이라이트 제약을 지킨다",
            ),
            ArcAcceptanceCriterion(
                "AC07",
                "현실의 딸은 귀환 목적으로 남고 두 주연은 부녀 대체나 로맨스가 아닌 동업자로 유지된다",
            ),
        ),
        episode_count_min=2,
        episode_count_max=3,
        production_constraints=canonical.production_constraints,
        continuity_invariants=(
            "도윤의 삼 년 계약을 한 그릇당 수명 점수로 바꾸지 않는다",
            "현실의 딸을 손님 아크의 감정 지름길로 사용하지 않는다",
            "명계시장은 HIL 1 자산 진입 조건을 통과하기 전에 등장하지 않는다",
            "소녀는 설명 장치가 되지 않으면서 규칙과 손님 선택 정보를 소유한다",
            "도윤과 소녀는 부녀나 연인이 아닌 공동 주연 동업자다",
            "매화 음식 완성·첫입 반응·현재 행동 변화를 보존한다",
            "초반 1~3화의 도윤 조리는 실패·오답·맛없음으로 긴장을 만들지 않는다. 모든 음식은 맛에 성공하고 다음 압력은 정보·규칙·선택에서 나온다",
            "소녀의 귀여움은 무능·음식 오염·보호 대상화가 아니라 왕실 허세·식욕·빠른 판단이 노동과 충돌하는 행동에서 만든다",
            "도윤의 매력은 큰 손의 전문성·연속 성공·다음 수를 즉시 고르는 행동·건조한 응대에서 만든다",
        ),
        renderer_mix=(
            RendererKind.COMPETENCE,
            RendererKind.ATTACHMENT_SAFETY,
            RendererKind.RESOURCE,
            RendererKind.SELECTION,
        ),
        allowed_beat_patterns=(
            BeatPatternKind.SUSPENSE_INFORMATION_GAP,
            BeatPatternKind.SELECTION_SAFETY,
            BeatPatternKind.EVIDENCE_REVERSAL,
        ),
        original_contributions=(
            "첫 화의 맛있는 첫 코스가 성공 반응을 통해 최종 주문의 더 깊은 조건을 드러낸다",
            "남이 주는 대로 먹던 손님이 음식을 통해 현재 시점의 자기 취향을 획득한다",
            "잔여 재료 직원식이 소녀의 식욕을 선택한 접객 책임으로 바꾸고 손님 반입 공급을 연다",
            "왕실 허세와 식욕이 현장 노동에 부딪히고 도윤의 건조한 전문성이 이를 받아치는 반복 캐릭터 구도를 만든다",
        ),
        causal_chain_distance_receipt_sha256=canonical_sha256(distance_status),
    )
    report = ArcContractVerifier().verify(arc, canonical)
    if not report.passed:
        findings = ", ".join(finding.code for finding in report.findings)
        raise ValueError(f"invalid HIL 2 arc candidate: {findings}")
    return arc


def build_outputs() -> dict[Path, str]:
    if not ADAPTATION_MAP_PATH.exists():
        raise FileNotFoundError(ADAPTATION_MAP_PATH)
    if not EP001_ROUGH_PATH.exists():
        raise FileNotFoundError(EP001_ROUGH_PATH)
    canonical, hil1_manifest = build_hil1_context()
    arc = build_arc()
    planning_document = export_hil2_planning_document(arc)
    if not planning_document.verify():
        raise ValueError("HIL 2 planning document does not verify")
    distance_status = build_distance_status()
    source_hashes = {
        "../" + path.relative_to(ROOT.parent).as_posix(): _file_sha256(path)
        for path in SOURCE_PATHS
    }
    planning_markdown = planning_document.markdown.rstrip("\n") + "\n"
    manifest = {
        "schema_version": "1",
        "work_id": canonical.work_id,
        "artifact_id": arc.artifact_id,
        "revision": arc.revision,
        "status": "candidate",
        "owner_approval": "not_started",
        "external_promotion_allowed": False,
        "hil3_status": "blocked_until_hil2_owner_approval",
        "next_gate": "owner_hil2_arc_review",
        "episode_count_band": [arc.episode_count_min, arc.episode_count_max],
        "default_review_allocation": 3,
        "parent_hil1_content_sha256": canonical.content_sha256,
        "parent_hil1_approval_receipt_sha256": hil1_manifest[
            "approval_receipt_sha256"
        ],
        "arc_contract_sha256": arc.content_sha256,
        "arc_planning_sha256": hashlib.sha256(
            planning_markdown.encode("utf-8")
        ).hexdigest(),
        "adaptation_map_sha256": _file_sha256(ADAPTATION_MAP_PATH),
        "episode_001_rough_beat_sheet_sha256": _file_sha256(
            EP001_ROUGH_PATH
        ),
        "episode_001_rough_status": "working_sketch_not_hil3",
        "causal_chain_distance_status": distance_status["status"],
        "causal_chain_distance_status_sha256": canonical_sha256(
            distance_status
        ),
        "source_inputs": source_hashes,
    }
    return {
        OUTPUT_ROOT / "arc_contract.json": canonical_json(arc) + "\n",
        OUTPUT_ROOT / "arc_planning.md": planning_markdown,
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
    allowed_paths = set(outputs) | {ADAPTATION_MAP_PATH, EP001_ROUGH_PATH}
    if OUTPUT_ROOT.exists():
        for path in OUTPUT_ROOT.iterdir():
            if path.is_file() and path not in allowed_paths:
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
        print("afterlife_restaurant HIL 2 arc01 candidate is current")
        return 0
    write_outputs(outputs)
    print(OUTPUT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
