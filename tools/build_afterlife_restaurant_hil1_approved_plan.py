#!/usr/bin/env python3
"""Build the owner-approved HIL 1 planning lock for 삼도식당."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys


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
from v4_shortform_script_foundry.canonical_package import (  # noqa: E402
    AudienceInformationContract,
    CanonicalPackage,
    CoreCharacterContract,
    OriginalityContract,
    PayoffCadence,
    PayoffLayer,
    ProductionConstraints,
)
from v4_shortform_script_foundry.fact_ledger import (  # noqa: E402
    Certainty,
    FactLedger,
    FactRecord,
    SourceBinding,
)
from v4_shortform_script_foundry.genre_grammar import (  # noqa: E402
    RendererKind,
)
from v4_shortform_script_foundry.planning_artifact import (  # noqa: E402
    export_hil1_planning_document,
)


OUTPUT_ROOT = (
    ROOT / "artifacts" / "approved" / "afterlife_restaurant" / "hil1"
)
SERIES_PLAN_PATH = OUTPUT_ROOT / "animation_series_plan_v1.md"
DECIDED_AT = "2026-08-02T01:09:58+09:00"


def build_fact_ledger() -> FactLedger:
    owner_source = "owner-thread-20260802"
    brief_source = "production-drive-brief-20260802"
    sources = (
        SourceBinding(
            source_id=owner_source,
            source_kind="owner_instruction",
            locator="conversation:current:2026-08-02",
        ),
        SourceBinding(
            source_id=brief_source,
            source_kind="production_team_drive_readback",
            locator=(
                "https://drive.google.com/drive/folders/"
                "1jMinWnqbUMRzts0jnaf52hXzxrGWy-ME"
            ),
        ),
    )
    facts = (
        FactRecord(
            "F001",
            "work",
            "fixed_material",
            "Doyun, the underworld girl, the daughter motive, and the restaurant remain",
            Certainty.CONFIRMED,
            (owner_source,),
            ("fixed_setting", "core_pair"),
        ),
        FactRecord(
            "F002",
            "doyun_real_world_daughter",
            "story_function",
            "return motive and future-season seed, not a guest-arc payoff",
            Certainty.CONFIRMED,
            (owner_source,),
            ("future_seed", "return_motive"),
        ),
        FactRecord(
            "F003",
            "series",
            "main_story",
            "Doyun and the underworld girl run the restaurant as co-leads",
            Certainty.CONFIRMED,
            (owner_source,),
            ("restaurant_operation", "co_leads"),
        ),
        FactRecord(
            "F004",
            "core_pair",
            "relation_boundary",
            "no father-daughter substitution and no romance",
            Certainty.CONFIRMED,
            (owner_source,),
            ("no_father_daughter", "no_romance"),
        ),
        FactRecord(
            "F005",
            "distribution",
            "target",
            "Laftel delivery with a five-minute absolute episode ceiling",
            Certainty.CONFIRMED,
            (owner_source, brief_source),
            ("laftel", "runtime_max_300"),
        ),
        FactRecord(
            "F006",
            "episode",
            "front_product",
            "food and the two lead characters are the foreground product; the underworld is the stage",
            Certainty.CONFIRMED,
            (owner_source,),
            ("food_forward", "character_appeal"),
        ),
        FactRecord(
            "F007",
            "cooking",
            "highlight_duration",
            "the cooking highlight targets 90 to 120 seconds",
            Certainty.CONFIRMED,
            (owner_source, brief_source),
            ("cooking_90_120", "production_constraint"),
        ),
        FactRecord(
            "F008",
            "episode",
            "payoff_and_delivery",
            "each episode pays an observable emotional turn through action rather than prose explanation",
            Certainty.CONFIRMED,
            (owner_source, brief_source),
            ("episode_payoff", "action_driven"),
        ),
        FactRecord(
            "F009",
            "production",
            "economy",
            "one sequence, four to six scenes, at most three principals, and a fixed restaurant set are the default",
            Certainty.CONFIRMED,
            (owner_source, brief_source),
            ("scene_budget", "principal_limit_3", "fixed_set"),
        ),
        FactRecord(
            "F010",
            "underworld_market",
            "entry_gate",
            "defer the market until its background, crowd, character, and ingredient sheets exist",
            Certainty.CONFIRMED,
            (owner_source, brief_source),
            ("asset_gate", "market_deferred"),
        ),
        FactRecord(
            "F011",
            "adaptation",
            "authority",
            "scenes, order, dialogue, and episode endpoints may be cut, merged, or rearranged",
            Certainty.CONFIRMED,
            (owner_source,),
            ("adaptation_allowed", "production_first"),
        ),
        FactRecord(
            "F012",
            "series_plan",
            "owner_decision",
            "the animation series plan version one is closed and owner approved",
            Certainty.CONFIRMED,
            (owner_source,),
            ("owner_approved", "hil1_lock"),
        ),
    )
    return FactLedger(
        premise_id="afterlife_restaurant",
        sources=sources,
        facts=facts,
    )


def build_canonical(
    ledger: FactLedger,
) -> tuple[CanonicalPackage, dict[str, object], dict[str, object]]:
    grammar_basis = {
        "status": "owner_approved_hil1_planning_basis",
        "direction": (
            "food-forward character comedy and emotional action payoff inside "
            "a bounded restaurant-production grammar"
        ),
        "renderer_range": (
            RendererKind.RESOURCE,
            RendererKind.COMPETENCE,
            RendererKind.ATTACHMENT_SAFETY,
            RendererKind.NORM,
            RendererKind.SELECTION,
        ),
        "source": "owner-thread-20260802-and-production-drive-readback",
    }
    distance_status = {
        "receipt_type": "premise_distance_status",
        "artifact_id": "afterlife_restaurant:hil1:animation_series_plan",
        "status": "pending_not_evaluated",
        "external_promotion_allowed": False,
        "reason": (
            "The owner approved the internal planning lock. No independent "
            "Reference/Eval premise-distance pass was asserted."
        ),
    }
    canonical = CanonicalPackage(
        work_id="afterlife_restaurant",
        canonical_id="afterlife_restaurant:hil1:animation_series_plan",
        revision=1,
        target_and_platform_hypothesis=(
            "4:00–4:40 recommended, 5:00 maximum Laftel-delivery cooking animation"
        ),
        premise=(
            "죽음 직전의 셰프 강도윤은 현실의 딸에게 돌아가기 위해 이승의 "
            "시간이 멈춘 저승에서 삼 년 계약을 맺고, 염라의 가출한 딸과 함께 "
            "망자조차 설명하지 못하는 마지막 식사를 요리하며 폐허인 삼도식당을 "
            "저승에서 가장 기다려지는 맛집으로 만들어 간다."
        ),
        core_characters=(
            CoreCharacterContract(
                character_id="doyun",
                narrative_role="lead_cook",
                goal="삼 년을 버티며 망자의 조건을 음식으로 풀고 현실의 딸에게 돌아간다",
                failure_cost="자기 해석을 정답처럼 밀어붙이면 손님의 선택과 식당의 반복 가능성을 함께 잃는다",
                operating_identity_invariant_kernel="행동, 신체, 재료의 단서를 읽고 필요한 맛으로 번역한다",
                initial_agency_state="living_world_master_under_underworld_limits",
                allowed_agency_transitions=(
                    "ingredient_reading_and_transformation",
                    "guest_choice_respecting_revision",
                    "shared_restaurant_authority",
                ),
            ),
            CoreCharacterContract(
                character_id="underworld_girl",
                narrative_role="co_lead_rule_and_service_holder",
                goal="왕실의 이름이 아니라 자신의 판단과 노동으로 식당에 있을 이유를 만든다",
                failure_cost="규칙 뒤에 숨으면 도윤의 단발성 해결을 막지 못하고 공동 주연의 권한을 잃는다",
                operating_identity_invariant_kernel="저승 규칙과 망자의 선택 정보를 가지고 도윤의 해석을 시험한다",
                initial_agency_state="restaurant_insider_testing_an_outsider",
                allowed_agency_transitions=(
                    "guest_choice_interpretation",
                    "service_exception_decision",
                    "shared_order_and_operation_authority",
                ),
            ),
        ),
        audience_information=AudienceInformationContract(
            objective_fact_policy=(
                "confirmed underworld facts remain separate from guest belief, "
                "Doyun inference, and audience inference"
            ),
            character_perception_policy=(
                "Doyun, the girl, and the guest may read the same appetite or "
                "rule differently until cooking action tests it"
            ),
            asymmetry_principles=(
                "food_problem_precedes_world_explanation",
                "the_girl_may_hold_rules_without_becoming_an_exposition_device",
                "guest_history_must_surface_through_present_behavior_or_objects",
            ),
        ),
        primary_reward="restaurant_operational_accumulation",
        payoff_layers=(
            PayoffLayer(
                "dish_and_guest_action_payoff",
                PayoffCadence.EPISODE,
                "current_guest_and_dish",
                "매회 음식의 완성과 손님의 관찰 가능한 행동 변화가 함께 지급된다",
                "조리 3변환, 첫입 신체 반응, 현재 행동의 전후 차이를 보존한다",
            ),
            PayoffLayer(
                "story_unit_closure",
                PayoffCadence.ARC,
                "current_story_unit",
                "손님 한 명 또는 사건 하나가 2~3화 안에 결산된다",
                "중간 화도 독립 행동 변화와 다음 의무를 지급한다",
            ),
            PayoffLayer(
                "restaurant_operational_accumulation",
                PayoffCadence.SEASON,
                "afterlife_restaurant",
                "재료, 메뉴, 공간, 규칙, 역할 중 하나가 누적되어 식당이 운영체로 변한다",
                "손님을 업그레이드 재료로 소비하지 않고 사건 결과만 다음 영업에 남긴다",
            ),
            PayoffLayer(
                "doyun_return_to_daughter",
                PayoffCadence.FUTURE_SEED,
                "doyun",
                "현실의 딸에게 돌아가려는 목적은 미래 시즌 질문으로 남는다",
                "손님 아크의 회차 보상이나 소녀와의 관계 비유로 소진하지 않는다",
            ),
        ),
        ending_direction=(
            "도윤과 소녀가 각자의 판단 권한을 가진 공동 운영자가 되고, 식당은 "
            "다음 손님을 반복해서 받을 기준을 갖추지만 도윤의 귀환은 해결하지 않는다"
        ),
        initial_relation_facts=(
            "doyun_controls_cooking_and_the_girl_holds_underworld_rules",
            "they_are_co_leads_not_a_father_daughter_pair",
            "their_authority_changes_through_joint_guest_work",
        ),
        forbidden_contradictions=(
            "do_not_reframe_doyun_and_the_girl_as_father_and_daughter",
            "do_not_add_romance_between_doyun_and_the_girl",
            "do_not_make_the_underworld_lore_displace_food_and_character_appeal",
            "do_not_make_long_dialogue_the_only_carrier_of_state_change",
            "do_not_resolve_doyun_return_to_daughter_inside_a_guest_arc",
            "do_not_treat_rubric_score_as_the_creative_objective",
        ),
        world_constraints=(
            "the_underworld_is_the_stage_while_food_and_two_leads_are_foreground",
            "the_main_present_story_is_doyun_and_the_girl_running_the_restaurant",
            "the_restaurant_fixed_set_precedes_large_new_locations",
            "the_underworld_market_requires_background_crowd_character_and_ingredient_sheets",
            "an_active_story_unit_moves_or_closes_within_two_to_three_episodes",
            "cooking_highlight_targets_ninety_to_one_hundred_twenty_seconds",
            "scene_order_dialogue_and_episode_endpoints_may_be_adapted_for_production",
            "hil1_does_not_lock_the_exact_episode_event_order",
        ),
        production_constraints=ProductionConstraints(
            target_runtime_seconds_min=240,
            target_runtime_seconds_max=300,
            max_principal_characters_per_scene=3,
            action_driven=True,
            dialogue_policy=(
                "one sequence and four to six scenes are the default; total "
                "dialogue targets at most 24 turns; no more than two consecutive "
                "explanation turns; food, objects, and reactions carry state change"
            ),
            max_dialogue_lines_per_scene=6,
        ),
        reward_hierarchy=(
            RendererKind.RESOURCE,
            RendererKind.COMPETENCE,
            RendererKind.ATTACHMENT_SAFETY,
        ),
        allowed_renderers=(
            RendererKind.RESOURCE,
            RendererKind.COMPETENCE,
            RendererKind.ATTACHMENT_SAFETY,
            RendererKind.NORM,
            RendererKind.SELECTION,
        ),
        originality=OriginalityContract(
            originality_axes=(
                "food_transformation_changes_guest_choice_and_restaurant_state",
                "co_lead_authority_moves_through_joint_work_not_caretaking",
                "fixed_set_pressure_creates_repeatable_visual_comedy_and_cooking",
            ),
            anti_goals=(
                "no_father_daughter_substitution",
                "no_mandatory_tearful_guest_formula",
                "no_world_lore_before_food_problem",
                "no_reference_specific_dialogue_or_event_chain_copy",
            ),
            creative_latitude=(
                "guest and dish design",
                "specific cooking transformation",
                "comedy timing and surface expression",
                "restaurant residue type",
                "episode scene order within approved HIL 2 state transitions",
            ),
            source_rights_policy=(
                "owner-approved internal planning lock; source rights and "
                "premise-distance remain separate gates before external delivery"
            ),
            premise_distance_receipt_sha256=canonical_sha256(distance_status),
            original_contributions=(
                "저승은 무대, 요리와 두 주연은 전면 상품이다",
                "조리 결과가 손님의 현재 행동과 다음 영업 상태를 함께 바꾼다",
                "고정 식당 세트와 자산 진입 조건이 회차 창작 범위를 만든다",
            ),
        ),
        source_fact_ledger_sha256=canonical_sha256(ledger),
        source_genre_grammar_sha256=canonical_sha256(grammar_basis),
    )
    return canonical, grammar_basis, distance_status


def build_outputs() -> dict[Path, str]:
    if not SERIES_PLAN_PATH.exists():
        raise FileNotFoundError(SERIES_PLAN_PATH)
    series_plan_sha256 = hashlib.sha256(SERIES_PLAN_PATH.read_bytes()).hexdigest()
    ledger = build_fact_ledger()
    canonical, grammar_basis, distance_status = build_canonical(ledger)
    review_payload = {
        "decision": "approve",
        "owner_instruction": "계획서는 닫자",
        "approved_scope": "HIL 1 series direction and production constraints",
        "excluded_scope": (
            "HIL 2 event order, character-design canon, episode script, "
            "external delivery, and rights clearance"
        ),
        "series_plan_path": SERIES_PLAN_PATH.relative_to(ROOT).as_posix(),
        "series_plan_sha256": series_plan_sha256,
    }
    receipt = ApprovalReceipt.issue(
        gate_id=HilGate.HIL1_CANONICAL,
        work_id=canonical.work_id,
        artifact_id=canonical.artifact_id,
        revision=canonical.revision,
        artifact_content_sha256=canonical.content_sha256,
        decision=ReviewDecision.APPROVE,
        reviewer_id="workspace_owner",
        reviewer_role="owner",
        rubric_version="animation-series-plan-v1",
        review_payload_sha256=canonical_sha256(review_payload),
        decided_at=DECIDED_AT,
    )
    generated = export_hil1_planning_document(canonical).markdown
    generated = generated.replace(
        "# HIL 1 작품 기획 후보",
        "# HIL 1 작품 기획 정본",
        1,
    ).replace(
        "> 상태: candidate. Owner 승인 전에는 HIL 2 또는 대본 정본이 아니다.",
        (
            "> 상태: owner approved HIL 1. 정확한 사건 배열은 HIL 2 전까지 "
            "정본이 아니며 외부 제작 전달은 금지한다."
        ),
        1,
    )
    generated += (
        "\n\n## 승인 결합\n\n"
        f"- approval_receipt_sha256: `{receipt.receipt_sha256}`\n"
        f"- companion_plan_sha256: `{series_plan_sha256}`\n"
        "- premise_distance: `pending_not_evaluated`\n"
        "- external_promotion_allowed: `false`\n"
    )
    manifest = {
        "schema_version": "1",
        "work_id": canonical.work_id,
        "artifact_id": canonical.artifact_id,
        "revision": canonical.revision,
        "status": "owner_approved_hil1",
        "canonical_content_sha256": canonical.content_sha256,
        "approval_receipt_sha256": receipt.receipt_sha256,
        "review_payload_sha256": canonical_sha256(review_payload),
        "series_plan": SERIES_PLAN_PATH.name,
        "series_plan_sha256": series_plan_sha256,
        "premise_distance_status": "pending_not_evaluated",
        "external_promotion_allowed": False,
        "hil2_status": "not_started",
        "next_gate": "hil2_arc_candidate",
    }
    research_inputs = {
        "grammar_basis": grammar_basis,
        "premise_distance_status": distance_status,
    }
    return {
        OUTPUT_ROOT / "fact_ledger.json": canonical_json(ledger) + "\n",
        OUTPUT_ROOT / "canonical.json": canonical_json(canonical) + "\n",
        OUTPUT_ROOT / "canonical_planning.md": generated.rstrip("\n") + "\n",
        OUTPUT_ROOT / "review_payload.json": canonical_json(review_payload) + "\n",
        OUTPUT_ROOT / "approval_receipt.json": canonical_json(receipt) + "\n",
        OUTPUT_ROOT / "research_inputs.json": canonical_json(research_inputs) + "\n",
        OUTPUT_ROOT / "manifest.json": canonical_json(manifest) + "\n",
    }


def check_outputs(outputs: dict[Path, str]) -> tuple[str, ...]:
    findings: list[str] = []
    for path, expected in outputs.items():
        if not path.exists():
            findings.append(f"missing:{path.relative_to(ROOT)}")
            continue
        if path.read_text(encoding="utf-8") != expected:
            findings.append(f"stale:{path.relative_to(ROOT)}")
    allowed_paths = set(outputs) | {SERIES_PLAN_PATH}
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
        print("afterlife_restaurant approved HIL 1 plan is current")
        return 0
    write_outputs(outputs)
    print(OUTPUT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
