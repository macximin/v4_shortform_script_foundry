#!/usr/bin/env python3
"""Build the established-service HIL 3 episode-one script candidate."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
from pathlib import Path
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from v4_shortform_script_foundry.beat_patterns import (  # noqa: E402
    BeatPatternKind,
)
from v4_shortform_script_foundry.canonical import (  # noqa: E402
    canonical_json,
    canonical_sha256,
)
from v4_shortform_script_foundry.episode_script import (  # noqa: E402
    CausalRole,
    DialogueLine,
    EpisodeObligationKind,
    EpisodeScene,
    EpisodeScriptCandidate,
    EpisodeScriptStatus,
    EpisodeScriptVerifier,
)
from v4_shortform_script_foundry.genre_grammar import (  # noqa: E402
    RendererKind,
)


OUTPUT_ROOT = (
    ROOT
    / "artifacts"
    / "candidates"
    / "afterlife_restaurant"
    / "hil3"
    / "ep001_established_service_rev2"
)
HIL2_APPROVED_BUILDER_PATH = (
    ROOT / "tools" / "build_afterlife_restaurant_hil2_revision2_approved.py"
)
SOURCE_SCAFFOLD_PATH = (
    ROOT.parent
    / "shortform_reverse_lab"
    / "30_outputs"
    / "references"
    / "2026-08-02_four_anime_final_script_gate.md"
)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_hil2_approved_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "afterlife_restaurant_hil2_revision2_approved_builder",
        HIL2_APPROVED_BUILDER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load approved HIL 2 revision-2 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_scene_distance_status() -> dict[str, object]:
    return {
        "artifact_id": "afterlife_restaurant:ep001:established_service",
        "receipt_type": "scene_distance_status",
        "status": "pending_not_evaluated",
        "promotion_allowed": False,
        "reason": (
            "1화 후보는 승인된 HIL 1·2와 사람이 검토한 구조 가설에서 새로 썼다. "
            "독립 장면 거리 감리와 BR0·BR1 전에는 승인본이나 외부 전달본이 아니다."
        ),
    }


def build_research_receipt() -> dict[str, object]:
    if not SOURCE_SCAFFOLD_PATH.exists():
        raise FileNotFoundError(SOURCE_SCAFFOLD_PATH)
    return {
        "receipt_type": "human_reviewed_research_synthesis",
        "source_path": SOURCE_SCAFFOLD_PATH.relative_to(ROOT.parent).as_posix(),
        "source_sha256": _file_sha256(SOURCE_SCAFFOLD_PATH),
        "use_scope": "structural_decisions_and_missing_function_checks_only",
        "raw_reference_dialogue_ingested": False,
        "raw_reference_frames_ingested": False,
        "generator_ingest_allowed": False,
        "source_specific_copy_allowed": False,
    }


def build_episode() -> EpisodeScriptCandidate:
    hil2_builder = _load_hil2_approved_builder()
    arc, arc_receipt, _ = hil2_builder.build_approval()
    distance_status = build_scene_distance_status()
    episode = EpisodeScriptCandidate(
        work_id=arc.work_id,
        arc_id=arc.arc_id,
        episode_id="afterlife_restaurant:ep001:established_service",
        revision=1,
        producer_id="codex_primary_writer",
        status=EpisodeScriptStatus.CANDIDATE,
        parent_arc_content_sha256=arc.content_sha256,
        parent_arc_approval_receipt_sha256=arc_receipt.receipt_sha256,
        source_scaffold_sha256=_file_sha256(SOURCE_SCAFFOLD_PATH),
        source_distance_receipt_sha256=canonical_sha256(distance_status),
        target_runtime_seconds=275,
        beat_pattern=BeatPatternKind.SELECTION_SAFETY,
        scenes=(
            EpisodeScene(
                scene_id="S01",
                location="samdo_open_kitchen",
                purpose="식당이 이미 영업 중이고 도윤과 소녀가 각자 일을 아는 상태를 무언으로 판다",
                observable_action=(
                    "영업 중 목패 아래 사용한 그릇 두 벌과 주문표 세 장이 보인다. "
                    "소녀가 빈 그릇을 회수하며 주문표 하나를 뒤집는 순간 검은 수조에서 "
                    "망각어가 튀어 오른다. 도윤은 돌아보지 않고 한 손으로 낚아채 도마에 "
                    "눕힌다. 칼이 한 번 지나가 검은 뼈와 투명한 살이 갈리고, 화덕의 푸른 "
                    "불이 솟는다."
                ),
                causal_role=CausalRole.MEANINGFUL_ACTION,
                renderer_primary=RendererKind.COMPETENCE,
                renderer_secondary=(RendererKind.RESOURCE,),
                principal_character_ids=("doyun", "underworld_girl"),
                duration_seconds=12,
                dialogue=(),
                information_revealed_ids=(
                    "restaurant_already_operating",
                    "doyun_established_underworld_competence",
                    "girl_established_service_role",
                ),
                information_withheld_ids=(
                    "doyun_accident",
                    "doyun_contract",
                    "doyun_real_world_daughter",
                    "restaurant_opening_history",
                ),
                state_delta_codes=(
                    "audience_view:unknown_restaurant->established_operation",
                    "audience_view:doyun_unknown->complete_chef",
                ),
                tension_delta="competence_hook_opens_the_day's_order",
            ),
            EpisodeScene(
                scene_id="S02",
                location="samdo_dining_hall",
                purpose="김문성의 수동적 주문 태도와 불을 오래 다룬 현재 물증을 놓고 자연스럽게 메뉴를 정한다",
                observable_action=(
                    "김문성은 기름때 밴 작업복 소매를 걷고 뜨거운 찻잔을 두 손으로 "
                    "감싼다. 손등에는 작은 화상과 굳은살이 겹쳐 있다. 왼손 안에는 그을린 "
                    "황동 표찰이 반쯤 숨겨져 있다. 소녀는 물수건을 놓고 빈 주문 목패를 "
                    "집는다. 주방의 푸른 불이 오를 때마다 김문성의 눈이 그쪽으로 간다. "
                    "도윤은 생선의 탄력을 확인한 뒤 손님에게 말을 건다. 소녀는 합의가 "
                    "끝나자 목패에 망각어 맑은국을 적어 주방 쪽 고리에 건다."
                ),
                causal_role=CausalRole.MEANINGFUL_CHOICE,
                renderer_primary=RendererKind.SELECTION,
                renderer_secondary=(RendererKind.COMPETENCE,),
                principal_character_ids=(
                    "doyun",
                    "underworld_girl",
                    "guest_kim_munseong",
                ),
                duration_seconds=35,
                dialogue=(
                    DialogueLine(
                        "doyun",
                        "뜨거운 국물, 괜찮으십니까?",
                        "offer_temperature_without_interrogation",
                    ),
                    DialogueLine(
                        "guest_kim_munseong",
                        "따뜻한 거면 됐소.",
                        "show_passive_minimum_preference",
                    ),
                    DialogueLine(
                        "doyun",
                        "오늘 망각어 살이 좋습니다. 맑은국으로 내겠습니다.",
                        "make_natural_ingredient_recommendation",
                    ),
                    DialogueLine(
                        "guest_kim_munseong",
                        "그럽시다.",
                        "accept_recommendation_without_active_taste_choice",
                    ),
                ),
                information_revealed_ids=(
                    "guest_work_worn_hands",
                    "guest_hidden_brass_tag",
                    "guest_watches_blue_fire",
                    "mangakeo_clear_soup_order",
                ),
                information_withheld_ids=("guest_full_life_history",),
                state_delta_codes=(
                    "guest_order:none->passive_recommendation_acceptance",
                    "girl_service:waiting->order_recorded",
                ),
                tension_delta="a_valid_order_exists_but_the_guest_has_not_named_a_taste",
            ),
            EpisodeScene(
                scene_id="S03",
                location="samdo_open_kitchen",
                purpose="105초 조리로 도윤의 연속 성공과 소녀의 사전 서비스 판단을 함께 증명한다",
                observable_action=(
                    "도윤은 망각어의 검은 뼈를 푸른 불에 볶는다. 기름이 맺히고 뼈 "
                    "가장자리가 갈색으로 변하는 순간 물을 부어 첫 향을 가둔다. 검은 "
                    "거품이 떠오르자 한 번에 걷어 내고, 국물이 바닥까지 비칠 만큼 맑아질 "
                    "때 불을 낮춘다. 푸른 뿌리는 숯불 위에서 굴려 겉을 검게 태우고 갈라진 "
                    "틈의 황금빛 속살만 꺼낸다. 투명한 망각어 살은 소금에 잠깐 눌러 얇게 "
                    "저민다. 한편 도윤은 남긴 뼈 일부를 쓴내가 나기 직전까지 한 번 더 "
                    "볶아 첫 육수로 풀고 작은 검은 주전자에 거른다. 소녀는 손님이 계속 "
                    "화덕을 보는 것을 확인하고 검은 주전자를 작은 보온 화로로 옮긴다. "
                    "도윤은 그녀의 판단을 받아 두 번째 불을 올린다. 마지막으로 투명한 "
                    "생선살과 구운 뿌리를 그릇에 조립하고, 맑은 육수를 부어 생선 가장자리가 "
                    "하얗게 익는 변화를 보여 준다."
                ),
                causal_role=CausalRole.MEANINGFUL_ACTION,
                renderer_primary=RendererKind.COMPETENCE,
                renderer_secondary=(RendererKind.RESOURCE, RendererKind.SELECTION),
                principal_character_ids=(
                    "doyun",
                    "underworld_girl",
                    "guest_kim_munseong",
                ),
                duration_seconds=105,
                dialogue=(
                    DialogueLine(
                        "underworld_girl",
                        "검은 주전자도 데워 두거라.",
                        "open_planned_second_finish",
                    ),
                    DialogueLine(
                        "doyun",
                        "불을 보고 있습니까?",
                        "confirm_service_observation",
                    ),
                    DialogueLine(
                        "underworld_girl",
                        "들어올 때부터.",
                        "prove_continuous_guest_attention",
                    ),
                    DialogueLine(
                        "doyun",
                        "그럼 두 번째 불도 올리죠.",
                        "accept_co_lead_service_judgment",
                    ),
                ),
                information_revealed_ids=(
                    "clear_broth_three_transformations",
                    "planned_dark_fire_broth",
                    "girl_reads_guest_fire_attention",
                    "doyun_accepts_girl_service_call",
                ),
                information_withheld_ids=("guest_fire_preference_confirmation",),
                state_delta_codes=(
                    "clear_soup:ingredients->completed",
                    "dark_fire_broth:prepared->held_warm",
                    "girl_service:order_taker->second_finish_opener",
                    "duo_authority:parallel_roles->coordinated_service",
                ),
                tension_delta="two_complete_finishes_are_ready_before_the_guest_chooses",
            ),
            EpisodeScene(
                scene_id="S04",
                location="samdo_dining_hall",
                purpose="첫 맑은국의 맛을 충분히 지급한 뒤 빈 그릇과 시선으로 선택 미완료를 드러낸다",
                observable_action=(
                    "소녀가 망각어 맑은국을 내려놓는다. 김문성은 먼저 김을 오래 맡고 "
                    "국물을 마신다. 굳었던 어깨가 내려가고 두 번째 숟갈부터 속도가 붙는다. "
                    "구운 뿌리를 씹은 뒤에는 황동 표찰을 문지르던 엄지도 멈춘다. 그는 "
                    "건더기와 국물을 모두 비우지만 그릇에서 두 손을 떼지 않는다. 빈 그릇 "
                    "너머로 다시 푸른 불을 본다. 소녀는 결산 쪽으로 뒤집으려던 주문 목패를 "
                    "멈추고 선택 쪽으로 돌린다."
                ),
                causal_role=CausalRole.PRIOR_CHOICE_CONSEQUENCE,
                renderer_primary=RendererKind.ATTACHMENT_SAFETY,
                renderer_secondary=(RendererKind.SELECTION,),
                principal_character_ids=(
                    "doyun",
                    "underworld_girl",
                    "guest_kim_munseong",
                ),
                duration_seconds=42,
                dialogue=(
                    DialogueLine(
                        "underworld_girl",
                        "끝맛은 고르실 수 있습니다.",
                        "return_final_taste_authority_to_guest",
                    ),
                    DialogueLine(
                        "guest_kim_munseong",
                        "불 냄새를 더 낼 수 있소?",
                        "make_first_active_taste_request",
                    ),
                    DialogueLine(
                        "doyun",
                        "이미 데워 뒀습니다.",
                        "prove_planned_not_corrective_second_finish",
                    ),
                ),
                information_revealed_ids=(
                    "first_clear_soup_is_completed_and_consumed",
                    "guest_requests_deeper_fire_aroma",
                ),
                information_withheld_ids=("guest_brass_tag_identity",),
                state_delta_codes=(
                    "first_soup:completed->fully_consumed",
                    "guest_preference:passive->active_fire_request",
                    "order_status:closing->choice_opened_by_girl",
                ),
                tension_delta="successful_first_bowl_reveals_a_more_personal_choice",
            ),
            EpisodeScene(
                scene_id="S05",
                location="samdo_dining_hall",
                purpose="별도 완성한 불향 끝맛과 추가 주문으로 손님을 완결하고 식당 기록을 남긴다",
                observable_action=(
                    "소녀가 보온 화로에서 검은 주전자를 직접 가져온다. 도윤은 새 망각어 "
                    "한 점과 구운 뿌리를 작은 시식 그릇에 다시 조립하고 짙은 육수를 붓는다. "
                    "맑은 빛은 유지되지만 김이 굵어지고 불향이 퍼진다. 김문성은 한 모금 "
                    "마신 뒤 처음으로 자기 맛을 단정한다. 소녀는 그의 말을 주문 목패에 "
                    "불향 진하게, 한 그릇 추가라고 적는다. 도윤은 이미 손질한 재료로 새 "
                    "한 그릇을 빠르게 완성한다. 김문성이 실제로 먹어 비운다. 그는 검은 "
                    "엽전을 놓고, 처음부터 쥐고 있던 황동 표찰을 작업복 바깥주머니에 단다. "
                    "표찰의 기관실 7호 글자가 잠깐 보인다. 김문성은 빈 그릇에서 손을 떼고 "
                    "곧은 자세로 문을 나간다. 소녀는 그의 주문 목패를 결산 고리에 건다."
                ),
                causal_role=CausalRole.MEANINGFUL_CHOICE,
                renderer_primary=RendererKind.SELECTION,
                renderer_secondary=(RendererKind.ATTACHMENT_SAFETY, RendererKind.RESOURCE),
                principal_character_ids=(
                    "doyun",
                    "underworld_girl",
                    "guest_kim_munseong",
                ),
                duration_seconds=69,
                dialogue=(
                    DialogueLine(
                        "guest_kim_munseong",
                        "이쪽이 좋소.",
                        "name_personal_taste",
                    ),
                    DialogueLine(
                        "guest_kim_munseong",
                        "한 그릇 더. 불향은 그대로.",
                        "place_direct_repeat_order",
                    ),
                    DialogueLine(
                        "underworld_girl",
                        "불향 진하게, 한 그릇.",
                        "lock_guest_choice_into_order_record",
                    ),
                    DialogueLine(
                        "guest_kim_munseong",
                        "잘 먹었소.",
                        "close_guest_meal_and_departure",
                    ),
                ),
                information_revealed_ids=(
                    "guest_prefers_deep_fire_finish",
                    "guest_engine_room_tag",
                    "guest_pays_and_departs",
                    "fire_finish_order_record",
                ),
                information_withheld_ids=(
                    "doyun_accident",
                    "doyun_contract",
                    "doyun_real_world_daughter",
                ),
                state_delta_codes=(
                    "guest_preference:active_request->named_repeat_order",
                    "guest_arc:open->closed",
                    "restaurant_resource:no_finish_record->paid_fire_finish_record",
                    "guest_object:hidden_in_fist->worn_openly",
                ),
                tension_delta="guest_closure_becomes_a_reusable_service_record",
            ),
            EpisodeScene(
                scene_id="S06",
                location="samdo_open_kitchen",
                purpose="손님 보상 뒤 소녀의 자기 주문과 두 사람의 다음 영업 행동을 12초 코다로 남긴다",
                observable_action=(
                    "소녀는 김문성의 목패를 끝맛 선택 칸에 걸고 새 작은 목패에 망각어 "
                    "볼살 구이, 소금 두 번이라고 적어 패스에 놓는다. 도윤은 기다렸다는 "
                    "듯 덮개를 밀어 보낸다. 안에는 가장자리가 바삭한 볼살 구이가 있다. "
                    "소녀가 한입 베어 무는 동안 한 손으로 영업 중 목패를 바로 세운다. "
                    "도윤은 다음 망각어를 수조에서 건지고, 소녀는 새 빈 주문 목패를 "
                    "집는다. 물소리, 칼 소리, 목패 소리가 이어지며 끝난다."
                ),
                causal_role=CausalRole.PRIOR_CHOICE_CONSEQUENCE,
                renderer_primary=RendererKind.ATTACHMENT_SAFETY,
                renderer_secondary=(RendererKind.RESOURCE, RendererKind.COMPETENCE),
                principal_character_ids=("doyun", "underworld_girl"),
                duration_seconds=12,
                dialogue=(
                    DialogueLine(
                        "underworld_girl",
                        "내 것은 소금 두 번이다.",
                        "make_co_lead_personal_order",
                    ),
                    DialogueLine(
                        "doyun",
                        "알고 있습니다.",
                        "answer_as_established_coworker",
                    ),
                    DialogueLine(
                        "underworld_girl",
                        "말하기도 전에?",
                        "open_cute_status_gap",
                    ),
                    DialogueLine(
                        "doyun",
                        "매번 그렇게 드시니까요.",
                        "close_with_repeat_work_familiarity",
                    ),
                ),
                information_revealed_ids=(
                    "girl_preferred_employee_dish",
                    "duo_repeat_service_rhythm",
                ),
                information_withheld_ids=(
                    "girl_royal_identity_details",
                    "doyun_return_plan",
                ),
                state_delta_codes=(
                    "girl_role:guest_choice_opener->co_owner_of_next_service",
                    "duo_relation:coordinated_service->repeat_work_familiarity",
                    "restaurant_operation:closed_order->ready_for_next_order",
                ),
                tension_delta="the_guest_is_closed_while_the_duo's_next_shift_continues",
            ),
        ),
        final_state_delta_codes=(
            "guest_preference:passive_recommendation->named_fire_finish",
            "guest_arc:open->closed_with_payment_and_departure",
            "girl_service:order_recording->choice_opening_and_finalization",
            "restaurant_operation:no_finish_rule->paid_two_finish_order_record",
            "duo_relation:parallel_roles->repeat_post_service_rhythm",
        ),
        rewards_paid=(
            "dish_and_guest_action_payoff",
            "story_unit_closure",
            "restaurant_operational_accumulation",
        ),
        rewards_deferred=("doyun_return_to_daughter",),
        obligation_kind=EpisodeObligationKind.CLOSURE,
        obligation=(
            "김문성의 음식·선택·결제·퇴장은 1화에서 완결된다. 다음 회차는 새 손님으로 시작할 수 있으며 이 후보는 1화만 작성한다"
        ),
        original_contributions=(
            "첫 맑은국과 별도 불향 국물을 정답과 수정이 아닌 두 완성품으로 먼저 준비한다",
            "소녀가 손님의 불을 보는 습관을 포착해 검은 주전자를 데우고 최종 주문을 기록한다",
            "손님의 숨긴 기관실 표찰이 직접 선택 뒤 바깥으로 나오는 현재 행동으로 바뀐다",
            "손님 퇴장 뒤 소녀의 소금 두 번 주문과 도윤의 사전 준비가 부녀·로맨스 없는 동업 코다가 된다",
        ),
    )
    report = EpisodeScriptVerifier().verify(episode, arc)
    if not report.passed:
        findings = ", ".join(finding.code for finding in report.findings)
        raise ValueError(f"invalid established-service episode candidate: {findings}")
    return episode


SHOT_PLANS: dict[str, tuple[tuple[int, str], ...]] = {
    "S01": (
        (3, "사용한 그릇과 주문표, 영업 중 목패를 한 프레임에 잡는다."),
        (3, "망각어가 수조에서 튀어 오른다. 도윤의 손이 화면 안으로 들어온다."),
        (4, "손으로 낚아챈 망각어를 칼 한 번으로 뼈와 살로 나눈다."),
        (2, "푸른 불이 솟고 소녀가 주문표를 뒤집는다."),
    ),
    "S02": (
        (8, "김문성의 소매, 화상 난 손, 찻잔, 숨긴 황동 표찰을 가까이 보여 준다."),
        (12, "도윤은 주방 안에서 생선을 만지고 소녀는 홀에서 주문 목패를 든다."),
        (11, "자연스러운 추천과 수락을 주고받는다. 손님의 눈은 푸른 불로 한 번 샌다."),
        (4, "소녀가 망각어 맑은국 목패를 주방 고리에 건다."),
    ),
    "S03": (
        (18, "검은 뼈를 볶아 기름과 갈색 가장자리를 만든다."),
        (18, "물을 부어 향을 가두고 검은 거품을 걷어 국물을 투명하게 만든다."),
        (16, "푸른 뿌리의 겉을 태우고 황금빛 속살을 꺼낸다."),
        (18, "생선살을 소금에 눌러 얇게 저미고 결을 빛에 비춘다."),
        (17, "남은 뼈를 더 볶아 별도 불향 육수를 만들고 검은 주전자에 거른다."),
        (10, "소녀가 손님의 시선을 확인해 검은 주전자를 보온 화로로 옮긴다."),
        (8, "생선살과 뿌리를 조립한 뒤 맑은 육수를 부어 가장자리를 익힌다."),
    ),
    "S04": (
        (8, "소녀가 첫 그릇을 놓고 김문성이 향부터 맡는다."),
        (22, "첫입, 어깨 이완, 빨라지는 숟갈, 구운 뿌리, 완식까지 대사를 비운다."),
        (6, "빈 그릇을 놓지 않은 두 손과 화덕을 보는 눈을 교차한다."),
        (6, "소녀가 목패를 선택 쪽으로 돌리고 끝맛 선택을 연다."),
    ),
    "S05": (
        (8, "소녀가 검은 주전자를 가져오고 도윤이 새 시식 그릇을 조립한다."),
        (10, "짙은 육수를 붓는다. 맑은 빛은 남고 김과 향의 결만 굵어진다."),
        (8, "김문성이 맛을 고르고 한 그릇을 추가 주문한다."),
        (7, "소녀가 불향 진하게, 한 그릇 추가를 목패에 적는다."),
        (24, "도윤이 새 그릇을 완성하고 김문성이 실제로 먹어 비운다."),
        (12, "검은 엽전, 바깥주머니의 기관실 표찰, 퇴장, 결산 목패를 차례로 잡는다."),
    ),
    "S06": (
        (3, "김문성의 목패가 끝맛 선택 칸에 걸린다."),
        (3, "소녀가 볼살 구이, 소금 두 번 목패를 써서 패스에 놓는다."),
        (3, "도윤이 이미 구운 볼살을 밀고 두 사람이 짧게 받아친다."),
        (3, "소녀는 먹으며 영업 목패를 세우고 도윤은 다음 망각어를 건진다."),
    ),
}


SOUND_PLANS: dict[str, str] = {
    "S01": "물 튀는 소리, 도마 충격, 칼 한 번, 불이 붙는 저음. 음악은 마지막 2초에만 시작한다.",
    "S02": "찻잔과 목패 소리를 살린다. 대사 사이마다 화덕의 낮은 숨소리를 남긴다.",
    "S03": "뼈 볶는 마찰음, 물을 부을 때의 큰 증기, 거품 걷는 얇은 소리, 뿌리 갈라지는 소리, 육수 거르는 소리를 공정별 표지로 쓴다.",
    "S04": "첫입부터 22초 동안 음악과 대사를 낮추고 숟가락, 삼킴, 숨, 그릇 소리로 실제 섭취를 버틴다.",
    "S05": "검은 주전자의 뚜껑음과 굵어진 증기를 두 번째 보상 신호로 쓴다. 퇴장 때 문종은 한 번만 울린다.",
    "S06": "목패가 걸리는 소리, 볼살의 바삭한 한입, 다시 튀는 수조 물소리로 다음 영업을 연결한다.",
}


def _timestamp(seconds: int) -> str:
    return f"{seconds // 60}:{seconds % 60:02d}"


def export_storyboard_markdown(episode: EpisodeScriptCandidate) -> str:
    speaker_names = {
        "doyun": "도윤",
        "underworld_girl": "소녀",
        "guest_kim_munseong": "김문성",
    }
    location_names = {
        "samdo_open_kitchen": "삼도식당 주방",
        "samdo_dining_hall": "삼도식당 홀",
    }
    lines = [
        "# 삼도식당 1화 대본 후보 0.3",
        "",
        "## 오늘 망각어가 좋습니다",
        "",
        "> 상태: HIL 3 후보. BR0·BR1과 책임자 승인 전에는 대본 정본이 아니다.",
        "",
        "- 목표 러닝타임: `4분 35초`",
        "- 회차 범위: `1화만 작성`",
        "- 조리 하이라이트: `105초`",
        "- 첫 음식: `망각어 맑은국 — 완전한 성공`",
        "- 두 번째 끝맛: `별도 불향 육수 — 처음부터 준비된 완성품`",
        "- 이번 화에서 설명하지 않음: `사고, 현실의 딸, 계약, 개업 과정`",
        "",
        "## 회차 약속",
        "",
        "이미 영업 중인 삼도식당에서 도윤과 소녀는 두 개의 완성된 맛으로 주는 대로 받던 김문성에게 자기 끝맛을 고르게 한다. 손님은 직접 추가 주문하고 결제한 뒤 퇴장한다. 남은 주문 목패와 직원식은 두 주연의 다음 영업 행동으로 이어진다.",
        "",
    ]
    elapsed = 0
    for scene_number, scene in enumerate(episode.scenes, start=1):
        end = elapsed + scene.duration_seconds
        lines.extend(
            (
                f"## 장면 {scene_number} · {_timestamp(elapsed)}–{_timestamp(end)}",
                "",
                f"장소: {location_names[scene.location]}",
                "",
                f"장면 목적: {scene.purpose}",
                "",
                "### 화면과 행동",
                "",
                scene.observable_action,
                "",
                "### 컷 설계",
                "",
            )
        )
        shot_elapsed = elapsed
        for shot_seconds, description in SHOT_PLANS[scene.scene_id]:
            shot_end = shot_elapsed + shot_seconds
            lines.append(
                f"- `{_timestamp(shot_elapsed)}–{_timestamp(shot_end)}` {description}"
            )
            shot_elapsed = shot_end
        lines.extend(("", "### 대사", ""))
        if scene.dialogue:
            lines.extend(
                f"- {speaker_names[line.speaker_id]}: {line.text}"
                for line in scene.dialogue
            )
        else:
            lines.append("- 대사 없음.")
        lines.extend(("", "### 소리와 편집", "", SOUND_PLANS[scene.scene_id], ""))
        elapsed = end
    lines.extend(
        (
            "## 1화에서 닫히는 것",
            "",
            "- 김문성은 추천을 수동적으로 받는 손님에서 불향의 정도와 추가 한 그릇을 직접 주문하는 손님으로 바뀐다.",
            "- 첫 맑은국과 불향 끝맛은 모두 맛에 성공한다.",
            "- 김문성은 결제하고 퇴장한다. 같은 손님의 다음 화 재등장은 필요하지 않다.",
            "- 소녀의 판단은 검은 주전자의 준비와 최종 주문 기록을 실제로 만든다.",
            "- 식당에는 끝맛 선택 주문 목패가 남는다.",
            "- 도윤과 소녀는 손님 퇴장 뒤 각자의 주문·조리 행동으로 다음 영업을 이어간다.",
            "",
            "## 승격 경계",
            "",
            "- 장면 거리 감리: `대기`",
            "- BR0: `시작 전`",
            "- BR1: `시작 전`",
            "- HIL 3 책임자 승인: `시작 전`",
            "- 외부 전달·업로드: `금지`",
            "- 2화 대본 생성: `이번 범위 아님`",
            "",
        )
    )
    return "\n".join(lines)


def export_author_self_review(episode: EpisodeScriptCandidate) -> str:
    scene_by_id = {scene.scene_id: scene for scene in episode.scenes}
    total_dialogue = sum(len(scene.dialogue) for scene in episode.scenes)
    return "\n".join(
        (
            "# 삼도식당 1화 작가 자체 감리",
            "",
            "> 독립 BR0·BR1이 아닌 집필자 자체 점검이다. 승격 근거로 사용할 수 없다.",
            "",
            "## 1차 · 구조와 지급",
            "",
            f"- 총 길이: `{episode.runtime_seconds}초` / 장면 `{len(episode.scenes)}개` / 대사 `{total_dialogue}줄`",
            f"- 요리 중심: 장면 3 조리 `{scene_by_id['S03'].duration_seconds}초`, 첫 그릇 섭취 `22초`, 두 번째 그릇 완성과 섭취 `24초`.",
            "- 도윤의 패배 없음: 첫 맑은국과 별도 불향 육수 모두 손님 선택 전에 완성되어 있다.",
            "- 소녀의 필수 행동: 손님의 불 시선을 먼저 읽고 검은 주전자를 데우며, 선택을 주문 목패로 고정한다.",
            "- 손님 완결: 첫 완식 → 자기 끝맛 선택 → 추가 주문 → 두 번째 완식 → 결제 → 퇴장.",
            "- 회차 잔류물: 끝맛 선택 목패가 남고, 같은 손님의 재등장 의무는 남지 않는다.",
            "- 장기 떡밥 절제: 사고·현실의 딸·계약·개업 과정은 설명하지 않는다.",
            "",
            "판정: `통과`",
            "",
            "## 2차 · 반대 입장에서 깨 보기",
            "",
            "- 설명 과잉 여부: 손님의 과거를 독백으로 풀지 않고 화상 난 손·불을 보는 시선·기관실 표찰로만 둔다.",
            "- 진단 천재 여부: 도윤이 손님의 인생을 맞히지 않는다. 따뜻한 국물을 확인하고 좋은 생선을 추천할 뿐이다.",
            "- 첫 음식 가짜 실패 여부: 첫 그릇은 완식된다. 불향은 교정안이 아니라 미리 만든 별도 완성품이다.",
            "- 감정 보상 여부: 남이 정한 것을 받던 손님이 자기 끝맛과 추가 한 그릇을 직접 주문하고, 숨기던 표찰을 밖에 단다.",
            "- 캐릭터 관계 왜곡 여부: 소녀의 직원식 주문과 도윤의 사전 준비는 반복 영업의 동업 호흡이며 부녀·로맨스로 쓰지 않는다.",
            "- 코다 지연 여부: 손님 퇴장 직후 12초 안에 주문 기록·직원식·다음 영업 준비가 모두 발생한다.",
            "- 대사 부자연 여부: 거창한 규칙 설명과 손님 시험 대사를 제거하고 주문·서비스에 필요한 말만 남겼다.",
            "",
            "판정: `통과`",
            "",
            "## 남은 실제 위험",
            "",
            "- 기관실 표찰의 의미는 연출이 약하면 단순 소품으로 지나갈 수 있다. 표찰을 설명 대사로 보강하지 말고 손 안→바깥주머니의 위치 변화가 읽히게 찍어야 한다.",
            "- 두 번째 그릇 24초는 음식 작화가 약하면 반복처럼 보일 수 있다. 첫 그릇의 투명함과 두 번째 그릇의 굵은 김·불향 반응을 시청각적으로 분리해야 한다.",
            "- 마지막 네 줄은 12초 안에 처리하므로 성우 템포와 행동 겹치기가 필요하다. 숨을 줄이기보다 목패 작성·접시 전달 위에 대사를 포개야 한다.",
            "",
            "## 경계",
            "",
            "이 문서는 작가 자체 감리다. 장면 거리 감리, 독립 BR0·BR1, HIL 3 책임자 승인은 모두 아직 시작 전이다.",
            "",
        )
    )


def build_outputs() -> dict[Path, str]:
    if not SOURCE_SCAFFOLD_PATH.exists():
        raise FileNotFoundError(SOURCE_SCAFFOLD_PATH)
    episode = build_episode()
    hil2_builder = _load_hil2_approved_builder()
    arc, receipt, _ = hil2_builder.build_approval()
    distance_status = build_scene_distance_status()
    research_receipt = build_research_receipt()
    storyboard = export_storyboard_markdown(episode)
    author_self_review = export_author_self_review(episode)
    manifest = {
        "schema_version": "1",
        "work_id": episode.work_id,
        "episode_id": episode.episode_id,
        "revision": episode.revision,
        "status": "candidate",
        "episode_scope": "ep001_only",
        "episode_content_sha256": episode.content_sha256,
        "storyboard_sha256": hashlib.sha256(storyboard.encode("utf-8")).hexdigest(),
        "author_self_review_sha256": hashlib.sha256(
            author_self_review.encode("utf-8")
        ).hexdigest(),
        "parent_arc_content_sha256": arc.content_sha256,
        "parent_arc_approval_receipt_sha256": receipt.receipt_sha256,
        "source_scaffold_sha256": _file_sha256(SOURCE_SCAFFOLD_PATH),
        "research_receipt_sha256": canonical_sha256(research_receipt),
        "scene_distance_status": distance_status["status"],
        "scene_distance_status_sha256": canonical_sha256(distance_status),
        "br0_status": "not_started",
        "br1_status": "not_started",
        "owner_approval": "not_started",
        "external_promotion_allowed": False,
        "next_gate": "scene_distance_then_independent_br0_br1",
    }
    return {
        OUTPUT_ROOT / "episode_script.json": canonical_json(episode) + "\n",
        OUTPUT_ROOT / "episode_001_script_candidate.md": storyboard,
        OUTPUT_ROOT / "author_self_review.md": author_self_review,
        OUTPUT_ROOT / "research_input_receipt.json": (
            canonical_json(research_receipt) + "\n"
        ),
        OUTPUT_ROOT / "scene_distance_status.json": (
            canonical_json(distance_status) + "\n"
        ),
        OUTPUT_ROOT / "manifest.json": canonical_json(manifest) + "\n",
    }


def check_outputs(outputs: dict[Path, str]) -> tuple[str, ...]:
    findings: list[str] = []
    for scene in build_episode().scenes:
        if sum(duration for duration, _ in SHOT_PLANS[scene.scene_id]) != scene.duration_seconds:
            findings.append(f"shot_duration_mismatch:{scene.scene_id}")
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
        print("afterlife_restaurant established-service ep001 candidate is current")
        return 0
    write_outputs(outputs)
    print(OUTPUT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
