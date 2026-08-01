#!/usr/bin/env python3
"""Build three unapproved HIL 1 planning candidates for 저승식당."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

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
    ROOT / "artifacts" / "candidates" / "afterlife_restaurant" / "hil1"
)


@dataclass(frozen=True, slots=True)
class CandidateSpec:
    key: str
    label: str
    premise: str
    primary_reward: str
    season_payoff_id: str
    season_payoff_promise: str
    season_delivery_policy: str
    ending_direction: str
    doyun_goal: str
    doyun_failure_cost: str
    doyun_agency: tuple[str, ...]
    girl_goal: str
    girl_failure_cost: str
    girl_agency: tuple[str, ...]
    initial_relation_facts: tuple[str, ...]
    reward_hierarchy: tuple[RendererKind, ...]
    allowed_renderers: tuple[RendererKind, ...]
    originality_axes: tuple[str, ...]
    creative_latitude: tuple[str, ...]
    risk: str


def build_fact_ledger() -> FactLedger:
    sources = (
        SourceBinding(
            source_id="owner-thread-20260731",
            source_kind="owner_instruction",
            locator="conversation:current:2026-07-31",
        ),
        SourceBinding(
            source_id="production-brief-relay-20260731",
            source_kind="production_team_relay",
            locator=(
                "https://chatgpt.com/c/"
                "6a6bf1a4-2828-83ee-ba26-886e16db438e"
            ),
        ),
        SourceBinding(
            source_id="storyyard-afterlife-ep001-003",
            source_kind="current_work_read_surface",
            locator=(
                "https://storyyard-wjjo.macximin11123.chatgpt.site/"
                "works/work-5eac31fd"
            ),
        ),
    )
    facts = (
        FactRecord(
            fact_id="F001",
            subject="work",
            predicate="fixed_setting_policy",
            value="existing setting is immutable material, not redesign scope",
            certainty=Certainty.CONFIRMED,
            source_ids=("owner-thread-20260731",),
            tags=("fixed_setting", "owner_constraint"),
        ),
        FactRecord(
            fact_id="F002",
            subject="doyun_real_world_daughter",
            predicate="story_function",
            value=(
                "reason Doyun remains there, long-horizon purpose, and "
                "possible season-two seed"
            ),
            certainty=Certainty.CONFIRMED,
            source_ids=("owner-thread-20260731",),
            tags=("future_seed", "return_motive"),
        ),
        FactRecord(
            fact_id="F003",
            subject="series",
            predicate="main_story",
            value="Doyun and the underworld girl run the restaurant",
            certainty=Certainty.CONFIRMED,
            source_ids=("owner-thread-20260731",),
            tags=("core_pair", "restaurant_operation"),
        ),
        FactRecord(
            fact_id="F004",
            subject="doyun_and_underworld_girl",
            predicate="forbidden_relation_reframe",
            value="must not be redesigned as a father-daughter relationship",
            certainty=Certainty.CONFIRMED,
            source_ids=("owner-thread-20260731",),
            tags=("anti_goal", "relation"),
        ),
        FactRecord(
            fact_id="F005",
            subject="distribution",
            predicate="targets",
            value="real release planned for Lezhin Snack and Laftel",
            certainty=Certainty.CONFIRMED,
            source_ids=("production-brief-relay-20260731",),
            tags=("commercial_release", "platform"),
        ),
        FactRecord(
            fact_id="F006",
            subject="tone",
            predicate="direction",
            value="Ghibli-like tone with light-novel character appeal",
            certainty=Certainty.CONFIRMED,
            source_ids=("production-brief-relay-20260731",),
            tags=("tone", "character_appeal"),
        ),
        FactRecord(
            fact_id="F007",
            subject="episode",
            predicate="payoff_requirement",
            value="every episode must deliver an emotional payoff",
            certainty=Certainty.CONFIRMED,
            source_ids=("production-brief-relay-20260731",),
            tags=("episode_payoff", "emotional_turn"),
        ),
        FactRecord(
            fact_id="F008",
            subject="format",
            predicate="runtime_and_arc_band",
            value="episodes run three to five minutes and story moves in two to three episodes",
            certainty=Certainty.CONFIRMED,
            source_ids=("production-brief-relay-20260731",),
            tags=("runtime_180_300", "arc_2_3"),
        ),
        FactRecord(
            fact_id="F009",
            subject="story_delivery",
            predicate="preferred_mode",
            value="character and story progression should be action-driven rather than long dialogue",
            certainty=Certainty.CONFIRMED,
            source_ids=("production-brief-relay-20260731",),
            tags=("action_driven", "dialogue_constraint"),
        ),
        FactRecord(
            fact_id="F010",
            subject="scene",
            predicate="principal_character_limit",
            value="avoid four or more principal characters; target three or fewer",
            certainty=Certainty.CONFIRMED,
            source_ids=("production-brief-relay-20260731",),
            tags=("principal_limit_3", "production_constraint"),
        ),
        FactRecord(
            fact_id="F011",
            subject="doyun",
            predicate="observed_operating_identity",
            value=(
                "infers a person's life and need from behavior, body, and "
                "ingredients, then translates the reading into food"
            ),
            certainty=Certainty.INFERRED,
            source_ids=("storyyard-afterlife-ep001-003",),
            tags=("competence", "observation", "cooking"),
        ),
        FactRecord(
            fact_id="F012",
            subject="underworld_girl",
            predicate="identity",
            value="daughter of King Yama and recurring restaurant co-lead",
            certainty=Certainty.CONFIRMED,
            source_ids=("storyyard-afterlife-ep001-003",),
            tags=("core_pair", "underworld_rule_access"),
        ),
        FactRecord(
            fact_id="F013",
            subject="core_pair",
            predicate="romance_policy",
            value="no romance",
            certainty=Certainty.CONFIRMED,
            source_ids=("production-brief-relay-20260731",),
            tags=("no_romance", "owner_constraint"),
        ),
    )
    return FactLedger(
        premise_id="afterlife_restaurant",
        sources=sources,
        facts=facts,
    )


def candidate_specs() -> tuple[CandidateSpec, ...]:
    return (
        CandidateSpec(
            key="a_emotional_mystery",
            label="A. 감정 미스터리형",
            premise=(
                "저승식당의 요리사 도윤과 저승 규칙을 아는 소녀가, 망자가 "
                "겉으로 내놓은 주문과 아직 말하지 못한 감정 사이의 차이를 "
                "행동과 요리로 좁혀 가며 손님을 보낸다. 각 사건은 감정적으로 "
                "결산되지만 식당에는 다음 사건을 바꾸는 작은 흔적이 남는다."
            ),
            primary_reward="guest_emotional_turn_each_episode",
            season_payoff_id="restaurant_rule_trace_accumulates",
            season_payoff_promise=(
                "손님이 떠난 뒤 남은 흔적이 식당의 규칙과 두 주연의 판단을 바꾼다"
            ),
            season_delivery_policy=(
                "사건별 흔적은 작게 남기고 시즌 후반에 하나의 규칙 변화로 연결한다"
            ),
            ending_direction=(
                "시즌의 마지막 손님을 보내며 도윤과 소녀는 이전과 다른 방식으로 "
                "식당을 운영하게 되지만 현실의 딸과 귀환 문제는 미래 질문으로 남는다"
            ),
            doyun_goal=(
                "손님이 직접 설명하지 못한 필요를 관찰하고 음식으로 감정 변화를 만든다"
            ),
            doyun_failure_cost=(
                "요리는 완성돼도 손님의 감정 사건은 멈추고 식당의 역할은 수행되지 않는다"
            ),
            doyun_agency=(
                "surface_order_reading",
                "behavioral_clue_test",
                "emotionally_targeted_cooking_choice",
            ),
            girl_goal=(
                "저승 규칙을 지키면서 도윤이 산 사람의 논리로 손님을 오판하지 않게 한다"
            ),
            girl_failure_cost=(
                "규칙만 집행하다 손님의 실제 선택과 식당의 감정적 기능을 놓친다"
            ),
            girl_agency=(
                "rule_warning",
                "selective_clue_release",
                "joint_guest_judgment",
            ),
            initial_relation_facts=(
                "doyun_is_the_cook_and_the_girl_has_underworld_rule_access",
                "they_are_not_a_father_daughter_pair",
                "they_disagree_about_whether_living_person_logic_explains_the_dead",
            ),
            reward_hierarchy=(
                RendererKind.ATTACHMENT_SAFETY,
                RendererKind.COMPETENCE,
                RendererKind.NORM,
            ),
            allowed_renderers=(
                RendererKind.ATTACHMENT_SAFETY,
                RendererKind.COMPETENCE,
                RendererKind.NORM,
                RendererKind.SELECTION,
            ),
            originality_axes=(
                "order_and_unspoken_need_may_diverge_without_mandatory_lying",
                "food_changes_a_guest_choice_or_emotional_state",
                "guest_closure_leaves_a_small_restaurant_trace",
            ),
            creative_latitude=(
                "guest-specific emotional question",
                "nonverbal clue design",
                "dish and underworld ingredient design",
                "type of trace left in the restaurant",
            ),
            risk=(
                "숨은 사연을 매번 반전처럼 강제하면 공식화되고, 요리가 정답 발표 장치로 축소될 수 있다."
            ),
        ),
        CandidateSpec(
            key="b_restaurant_accumulation",
            label="B. 식당 누적 운영형",
            premise=(
                "도윤과 소녀가 망자의 마지막 식사를 해결할 때마다 저승식당의 "
                "재료, 메뉴, 공간, 손님 규칙 중 하나가 실제로 달라진다. 손님의 "
                "감정은 매회 움직이고, 2~3화 사건의 결과가 다음 사건의 가능성과 "
                "운영 압력을 직접 바꾼다."
            ),
            primary_reward="restaurant_operational_accumulation",
            season_payoff_id="restaurant_operational_accumulation",
            season_payoff_promise=(
                "식당이 손님 사건의 결과를 축적하며 처음과 다른 운영체가 된다"
            ),
            season_delivery_policy=(
                "각 손님 아크는 재료, 메뉴, 공간, 규칙 중 정확히 하나의 지속 변화를 남긴다"
            ),
            ending_direction=(
                "시즌 말 식당은 스스로 다음 손님을 감당할 수 있는 새로운 운영 규칙을 "
                "얻고, 도윤의 귀환 목적은 해결하지 않은 채 다음 시즌 압력으로 보존한다"
            ),
            doyun_goal=(
                "제한된 저승 재료와 규칙 안에서 손님을 먹이고 식당의 운영 가능성을 넓힌다"
            ),
            doyun_failure_cost=(
                "손님의 감정 문제뿐 아니라 다음 손님을 받을 식당의 기능도 축소된다"
            ),
            doyun_agency=(
                "ingredient_repurpose",
                "service_rule_invention",
                "operational_cost_choice",
            ),
            girl_goal=(
                "식당이 저승 질서를 깨지 않으면서 지속 가능하게 움직이도록 규칙을 관리한다"
            ),
            girl_failure_cost=(
                "도윤의 해결이 단발성 기적으로 끝나거나 식당이 감당할 수 없는 예외를 만든다"
            ),
            girl_agency=(
                "rule_boundary_set",
                "underworld_resource_tradeoff",
                "operational_exception_approval_or_refusal",
            ),
            initial_relation_facts=(
                "doyun_optimizes_for_the_guest_and_the_girl_for_restaurant_rules",
                "they_are_not_a_father_daughter_pair",
                "their_operational_priorities_overlap_but_are_not_identical",
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
            ),
            originality_axes=(
                "guest_result_changes_future_restaurant_affordance",
                "underworld_resources_create_visible_operational_choices",
                "growth_is_material_without_becoming_status_flex",
            ),
            creative_latitude=(
                "restaurant residue type",
                "ingredient scarcity",
                "menu and spatial change",
                "operational rule consequence",
            ),
            risk=(
                "손님이 식당 업그레이드 재료로 보이거나 힐링물이 경영 성장물로 변질될 수 있다."
            ),
        ),
        CandidateSpec(
            key="c_duo_operating_relationship",
            label="C. 충돌하는 동업 관계형",
            premise=(
                "도윤과 소녀는 같은 망자를 두고 서로 다른 판단을 내린다. 도윤은 "
                "관찰과 요리로, 소녀는 저승 규칙과 망자의 선택권으로 문제를 풀려 "
                "하고, 매 사건의 결과가 두 사람이 다음 손님을 함께 다루는 방식을 "
                "바꾼다."
            ),
            primary_reward="doyun_girl_operating_trust",
            season_payoff_id="doyun_girl_operating_trust",
            season_payoff_promise=(
                "도윤과 소녀가 서로의 판단을 검증하며 충돌하는 동업자에서 선택을 맡길 수 있는 동료로 변한다"
            ),
            season_delivery_policy=(
                "각 손님 아크는 누가 무엇을 결정할 수 있는지 관계 권한 하나를 이동시킨다"
            ),
            ending_direction=(
                "시즌 말 두 사람은 한쪽이 다른 쪽을 보호하는 관계가 아니라 서로의 "
                "판단을 맡길 수 있는 식당 동료가 되고 귀환 문제는 미래 질문으로 남는다"
            ),
            doyun_goal=(
                "자신의 관찰과 요리 판단을 지키면서도 저승의 선택 규칙을 이해한다"
            ),
            doyun_failure_cost=(
                "요리 실력은 증명해도 손님과 소녀의 선택권을 침범하는 해결자가 된다"
            ),
            doyun_agency=(
                "independent_guest_reading",
                "rule_conflict_choice",
                "shared_judgment_delegation",
            ),
            girl_goal=(
                "도윤을 통제하는 대신 그의 인간적 판단을 언제 신뢰할지 스스로 선택한다"
            ),
            girl_failure_cost=(
                "규칙 전달자나 활기찬 반응역으로만 남아 식당의 공동 주연 기능을 잃는다"
            ),
            girl_agency=(
                "counter_judgment",
                "rule_exception_choice",
                "shared_service_authority",
            ),
            initial_relation_facts=(
                "doyun_and_the_girl_have_distinct_decision_authority",
                "they_are_not_a_father_daughter_pair",
                "trust_must_change_through_joint_guest_work_not_caretaking",
            ),
            reward_hierarchy=(
                RendererKind.ATTACHMENT_SAFETY,
                RendererKind.SELECTION,
                RendererKind.NORM,
            ),
            allowed_renderers=(
                RendererKind.ATTACHMENT_SAFETY,
                RendererKind.SELECTION,
                RendererKind.NORM,
                RendererKind.COMPETENCE,
            ),
            originality_axes=(
                "guest_case_moves_decision_authority_between_co_leads",
                "relationship_progress_comes_from_joint_work_not_caretaking",
                "disagreement_is_resolved_by_consequence_not_long_dialogue",
            ),
            creative_latitude=(
                "type of judgment disagreement",
                "who holds the decisive clue",
                "shared or delegated final action",
                "relationship authority delta",
            ),
            risk=(
                "매 사건이 같은 말다툼으로 반복되거나 소녀가 도윤을 막는 장애물로 축소될 수 있다."
            ),
        ),
    )


def _payoff_layers(spec: CandidateSpec) -> tuple[PayoffLayer, ...]:
    return (
        PayoffLayer(
            payoff_id="guest_emotional_turn_each_episode",
            cadence=PayoffCadence.EPISODE,
            subject_id="current_guest",
            promise="매회 손님의 감정 또는 선택이 관찰 가능하게 한 단계 움직인다",
            delivery_policy=(
                "완전한 성불을 미뤄도 회차 안에서 작은 감정 결산을 지급한다"
            ),
        ),
        PayoffLayer(
            payoff_id="story_unit_closure",
            cadence=PayoffCadence.ARC,
            subject_id="current_story_unit",
            promise="손님 한 명 또는 사건 하나를 2~3화 안에 결산한다",
            delivery_policy=(
                "마지막 화만 보상하지 말고 앞선 화에도 별도 변화와 obligation을 둔다"
            ),
        ),
        PayoffLayer(
            payoff_id=spec.season_payoff_id,
            cadence=PayoffCadence.SEASON,
            subject_id="afterlife_restaurant",
            promise=spec.season_payoff_promise,
            delivery_policy=spec.season_delivery_policy,
        ),
        PayoffLayer(
            payoff_id="doyun_return_to_daughter",
            cadence=PayoffCadence.FUTURE_SEED,
            subject_id="doyun",
            promise="현실의 딸에게 돌아가려는 장기 목적이 미래 시즌 질문으로 남는다",
            delivery_policy=(
                "본편 손님 아크의 매회 보상으로 쓰지 않고 시즌 전환용 떡밥으로만 보존한다"
            ),
        ),
    )


def _core_characters(
    spec: CandidateSpec,
) -> tuple[CoreCharacterContract, ...]:
    return (
        CoreCharacterContract(
            character_id="doyun",
            narrative_role="lead_cook",
            goal=spec.doyun_goal,
            failure_cost=spec.doyun_failure_cost,
            operating_identity_invariant_kernel=(
                "행동, 신체, 재료의 단서를 읽고 필요한 맛으로 번역한다"
            ),
            initial_agency_state="living_world_master_under_underworld_limits",
            allowed_agency_transitions=spec.doyun_agency,
        ),
        CoreCharacterContract(
            character_id="underworld_girl",
            narrative_role="co_lead_rule_holder",
            goal=spec.girl_goal,
            failure_cost=spec.girl_failure_cost,
            operating_identity_invariant_kernel=(
                "저승 규칙과 망자의 선택 정보를 가지고 도윤의 해석을 시험한다"
            ),
            initial_agency_state="restaurant_insider_testing_an_outsider",
            allowed_agency_transitions=spec.girl_agency,
        ),
    )


def _grammar_basis(spec: CandidateSpec) -> dict[str, object]:
    return {
        "status": "research_candidate_not_approved",
        "candidate_key": spec.key,
        "brief_basis": (
            "Ghibli-like tone, light-novel character appeal, per-episode "
            "emotional payoff, two-to-three episode movement, action-driven "
            "delivery, three-or-fewer principals"
        ),
        "reward_hierarchy": spec.reward_hierarchy,
        "allowed_renderers": spec.allowed_renderers,
        "evidence_scope": (
            "owner-thread-20260731",
            "production-brief-relay-20260731",
            "storyyard-afterlife-ep001-003",
            "reverse-lab-strategy-registry-research-candidate",
        ),
    }


def _pending_distance_receipt(
    spec: CandidateSpec,
) -> dict[str, object]:
    return {
        "receipt_type": "premise_distance_status",
        "candidate_key": spec.key,
        "premise_sha256": canonical_sha256(spec.premise),
        "status": "pending_not_evaluated",
        "promotion_allowed": False,
        "reason": (
            "No Reference/Eval premise-distance pass receipt exists. "
            "This hash records the blocker rather than a pass."
        ),
    }


def build_candidate(
    spec: CandidateSpec,
    ledger: FactLedger,
) -> tuple[CanonicalPackage, dict[str, object], dict[str, object]]:
    grammar_basis = _grammar_basis(spec)
    distance_receipt = _pending_distance_receipt(spec)
    canonical = CanonicalPackage(
        work_id="afterlife_restaurant",
        canonical_id=f"afterlife_restaurant:hil1:{spec.key}",
        revision=1,
        target_and_platform_hypothesis=(
            "3–5 minute vertical short-form animation for Lezhin Snack and Laftel"
        ),
        premise=spec.premise,
        core_characters=_core_characters(spec),
        audience_information=AudienceInformationContract(
            objective_fact_policy=(
                "confirmed underworld facts remain separate from guest belief, "
                "Doyun inference, and audience inference"
            ),
            character_perception_policy=(
                "Doyun, the girl, the guest, and the audience may hold "
                "different readings until action tests them"
            ),
            asymmetry_principles=(
                "do_not_require_every_guest_to_lie",
                "clues_may_precede_explanation_but_must_be_actionable",
                "the_girl_may_hold_rule_information_without_becoming_an_exposition_device",
            ),
        ),
        primary_reward=spec.primary_reward,
        payoff_layers=_payoff_layers(spec),
        ending_direction=spec.ending_direction,
        initial_relation_facts=spec.initial_relation_facts,
        forbidden_contradictions=(
            "do_not_reframe_doyun_and_the_girl_as_father_and_daughter",
            "do_not_add_romance_between_doyun_and_the_girl",
            "do_not_replace_the_tone_with_mastery_flex_or_public_humiliation",
            "do_not_end_an_episode_with_atmosphere_only",
            "do_not_make_long_dialogue_the_only_carrier_of_state_change",
            "do_not_resolve_doyun_return_to_daughter_inside_a_guest_arc",
        ),
        world_constraints=(
            "existing_setting_and_episode_one_to_three_facts_are_not_rewritten",
            "the_main_present_story_is_doyun_and_the_girl_running_the_restaurant",
            "an_active_story_unit_moves_or_closes_within_a_two_to_three_episode_band",
            "every_episode_pays_an_emotional_turn_and_carries_an_obligation_or_closure",
            "actions_and_food_must_cause_state_change",
        ),
        production_constraints=ProductionConstraints(
            target_runtime_seconds_min=180,
            target_runtime_seconds_max=300,
            max_principal_characters_per_scene=3,
            action_driven=True,
            dialogue_policy=(
                "character and plot state changes must be visible in action; "
                "long explanatory exchanges cannot carry the episode alone"
            ),
            max_dialogue_lines_per_scene=None,
        ),
        reward_hierarchy=spec.reward_hierarchy,
        allowed_renderers=spec.allowed_renderers,
        originality=OriginalityContract(
            originality_axes=spec.originality_axes,
            anti_goals=(
                "no_father_daughter_substitution",
                "no_mandatory_guest_lie_formula",
                "no_master_food_god_status_flex",
                "no_reference_specific_dialogue_or_event_chain_copy",
            ),
            creative_latitude=spec.creative_latitude,
            source_rights_policy=(
                "owner-asserted internal work; formal rights and premise-distance "
                "pass remain pending; candidate review only"
            ),
            premise_distance_receipt_sha256=canonical_sha256(
                distance_receipt
            ),
            original_contributions=(
                spec.premise,
                spec.season_payoff_promise,
                spec.season_delivery_policy,
            ),
        ),
        source_fact_ledger_sha256=canonical_sha256(ledger),
        source_genre_grammar_sha256=canonical_sha256(grammar_basis),
    )
    return canonical, grammar_basis, distance_receipt


def _comparison_markdown(
    specs: tuple[CandidateSpec, ...],
    candidates: tuple[CanonicalPackage, ...],
) -> str:
    candidate_by_key = {
        spec.key: candidate for spec, candidate in zip(specs, candidates)
    }
    lines = [
        "# 저승식당 HIL 1 후보 비교",
        "",
        "> 세 후보는 같은 고정 설정과 제작사 브리프를 사용한다. 차이는 "
        "시리즈의 주 보상과 누적 엔진이다.",
        "",
        "| 후보 | 주 엔진 | 회차 보상 | 시즌 누적 | 주요 위험 |",
        "| --- | --- | --- | --- | --- |",
    ]
    engine_summary = {
        "a_emotional_mystery": (
            "손님의 겉주문과 말하지 못한 감정 사이를 행동·요리로 좁힘"
        ),
        "b_restaurant_accumulation": (
            "손님 결과가 재료·메뉴·공간·규칙 중 하나를 지속 변경"
        ),
        "c_duo_operating_relationship": (
            "손님 사건이 도윤–소녀 사이의 판단 권한과 동업 신뢰를 변경"
        ),
    }
    for spec in specs:
        canonical = candidate_by_key[spec.key]
        season_layer = next(
            layer
            for layer in canonical.payoff_layers
            if layer.cadence is PayoffCadence.SEASON
        )
        lines.append(
            f"| {spec.label} | {engine_summary[spec.key]} | "
            "손님의 감정·선택이 한 단계 이동 | "
            f"{season_layer.promise} | {spec.risk} |"
        )
    lines.extend(
        (
            "",
            "## 1차 감리",
            "",
            "### 추천 1순위 — A. 감정 미스터리형",
            "",
            "- 제작사의 `회차마다 감정적 페이오프` 요구와 가장 직접적으로 맞는다.",
            "- 도윤의 기존 관찰·요리 능력을 공개 인정물이 아니라 감정 사건 해결 수단으로 쓴다.",
            "- 소녀는 저승 규칙과 정보 차이를 담당해 공동 주연 기능을 확보할 수 있다.",
            "- B의 식당 흔적은 시즌 보조 누적으로, C의 동업 변화는 아크 결과로 제한해 흡수할 수 있다.",
            "",
            "### 2순위 — B. 식당 누적 운영형",
            "",
            "- 다음 화와 다음 손님으로 넘어갈 이유가 가장 가시적이다.",
            "- 다만 손님의 죽음과 감정이 식당 업그레이드 재료처럼 보이면 작품 톤을 훼손한다.",
            "",
            "### 3순위 — C. 충돌하는 동업 관계형",
            "",
            "- 라노벨형 캐릭터 상품성은 가장 강하다.",
            "- 그러나 같은 판단 충돌이 반복되거나 부녀 대체 정서로 미끄러질 위험이 가장 크다.",
            "",
            "## 현재 추천 route",
            "",
            "```text",
            "Primary HIL 1 = A 감정 미스터리",
            "Season support = B의 작은 식당 흔적",
            "Relationship delta = C의 판단 권한 이동",
            "Future seed = 현실의 딸과 귀환",
            "```",
            "",
            "이는 세 후보를 동일 비중으로 혼합하자는 뜻이 아니다. A의 회차 보상을 "
            "주 계약으로 두고, B와 C는 A가 만든 손님 사건의 결과로만 제한한다.",
            "",
            "## Owner가 잠가야 할 미확정값",
            "",
            "- `2~3화 진행`이 손님 한 명의 미니아크인지, 더 큰 연속 사건의 전진 주기인지",
            "- 소녀가 저승식당에서 실제로 가진 결정 권한과 금지선",
            "- 시즌 1의 총 회차와 마지막에 바뀌어야 할 식당 규칙",
            "- 현실의 딸 떡밥을 시즌 1에서 몇 번, 어느 강도로 상기할지",
            "",
            "## 승격 상태",
            "",
            "- 세 후보 모두 `candidate`다.",
            "- premise-distance 상태는 `pending_not_evaluated`다.",
            "- HIL 1 owner approval receipt는 없다.",
            "- 선택 전에는 HIL 2 아크나 신규 대본으로 내려가지 않는다.",
            "",
        )
    )
    return "\n".join(lines)


def build_outputs() -> dict[Path, str]:
    ledger = build_fact_ledger()
    specs = candidate_specs()
    built = tuple(build_candidate(spec, ledger) for spec in specs)
    candidates = tuple(item[0] for item in built)
    research_inputs = {
        "status": "research_candidate_inputs",
        "grammar_bases": {
            spec.key: grammar_basis
            for spec, (_, grammar_basis, _) in zip(specs, built)
        },
        "premise_distance_receipts": {
            spec.key: distance_receipt
            for spec, (_, _, distance_receipt) in zip(specs, built)
        },
    }
    outputs: dict[Path, str] = {
        OUTPUT_ROOT / "fact_ledger.json": canonical_json(ledger) + "\n",
        OUTPUT_ROOT / "research_inputs.json": (
            canonical_json(research_inputs) + "\n"
        ),
        OUTPUT_ROOT / "comparison.md": (
            _comparison_markdown(specs, candidates) + "\n"
        ),
    }
    manifest_candidates: list[dict[str, object]] = []
    for spec, canonical in zip(specs, candidates):
        document = export_hil1_planning_document(canonical)
        json_name = f"candidate_{spec.key}.json"
        markdown_name = f"candidate_{spec.key}.md"
        outputs[OUTPUT_ROOT / json_name] = document.payload_json + "\n"
        outputs[OUTPUT_ROOT / markdown_name] = document.markdown + "\n"
        manifest_candidates.append(
            {
                "key": spec.key,
                "label": spec.label,
                "status": "candidate",
                "owner_approval_receipt": None,
                "canonical_content_sha256": canonical.content_sha256,
                "json": json_name,
                "markdown": markdown_name,
                "premise_distance_status": "pending_not_evaluated",
                "promotion_allowed": False,
            }
        )
    manifest = {
        "schema_version": "1",
        "work_id": "afterlife_restaurant",
        "candidate_set_id": "afterlife_restaurant:hil1:2026-07-31",
        "status": "candidate_set_unapproved",
        "source_fact_ledger_sha256": canonical_sha256(ledger),
        "candidate_count": len(manifest_candidates),
        "candidates": manifest_candidates,
        "comparison": "comparison.md",
        "research_inputs": "research_inputs.json",
        "next_gate": "owner_hil1_selection_or_revision",
    }
    outputs[OUTPUT_ROOT / "manifest.json"] = canonical_json(manifest) + "\n"
    return outputs


def check_outputs(outputs: dict[Path, str]) -> tuple[str, ...]:
    findings: list[str] = []
    for path, expected in outputs.items():
        if not path.exists():
            findings.append(f"missing:{path.relative_to(ROOT)}")
            continue
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            findings.append(f"stale:{path.relative_to(ROOT)}")
    expected_paths = set(outputs)
    if OUTPUT_ROOT.exists():
        for path in OUTPUT_ROOT.iterdir():
            if path.is_file() and path not in expected_paths:
                findings.append(f"unexpected:{path.relative_to(ROOT)}")
    return tuple(findings)


def write_outputs(outputs: dict[Path, str]) -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when checked-in candidate artifacts are missing or stale",
    )
    args = parser.parse_args()
    outputs = build_outputs()
    if args.check:
        findings = check_outputs(outputs)
        if findings:
            print("\n".join(findings))
            return 1
        print("afterlife_restaurant HIL 1 candidates are current")
        return 0
    write_outputs(outputs)
    print(OUTPUT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
