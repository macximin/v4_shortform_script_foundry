#!/usr/bin/env python3
"""Build the character-forward, human-surface episode-one candidate."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from tools import (  # noqa: E402
    build_afterlife_restaurant_ep001_established_service_candidate as previous,
)
from v4_shortform_script_foundry.beat_patterns import BeatPatternKind  # noqa: E402
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
from v4_shortform_script_foundry.genre_grammar import RendererKind  # noqa: E402


OUTPUT_ROOT = (
    ROOT
    / "artifacts"
    / "candidates"
    / "afterlife_restaurant"
    / "hil3"
    / "ep001_character_surface_rev3"
)
SOURCE_SCAFFOLD_PATH = previous.SOURCE_SCAFFOLD_PATH
PREVIOUS_OUTPUT_ROOT = previous.OUTPUT_ROOT


@dataclass(frozen=True, slots=True)
class ActionBlock:
    text: str


@dataclass(frozen=True, slots=True)
class SpeechBlock:
    speaker_id: str
    text: str
    function: str


ScriptBlock = ActionBlock | SpeechBlock


@dataclass(frozen=True, slots=True)
class SceneDraft:
    scene_id: str
    heading: str
    location: str
    purpose: str
    duration_seconds: int
    causal_role: CausalRole
    renderer_primary: RendererKind
    renderer_secondary: tuple[RendererKind, ...]
    principal_character_ids: tuple[str, ...]
    blocks: tuple[ScriptBlock, ...]
    information_revealed_ids: tuple[str, ...]
    information_withheld_ids: tuple[str, ...]
    state_delta_codes: tuple[str, ...]
    tension_delta: str


SCENE_DRAFTS: tuple[SceneDraft, ...] = (
    SceneDraft(
        scene_id="S01",
        heading="삼도식당 주방 / 실내 / 밤",
        location="samdo_open_kitchen",
        purpose="첫 30초 안에 도윤의 압도적 조리와 소녀의 발랄한 식욕, 두 사람의 오래된 호흡을 함께 판다",
        duration_seconds=36,
        causal_role=CausalRole.MEANINGFUL_ACTION,
        renderer_primary=RendererKind.COMPETENCE,
        renderer_secondary=(RendererKind.ATTACHMENT_SAFETY, RendererKind.RESOURCE),
        principal_character_ids=("doyun", "underworld_girl"),
        blocks=(
            ActionBlock(
                "삼도천의 안개가 창밖을 흐른다. 사용한 그릇이 쌓인 삼도식당 주방. "
                "소녀가 카운터 위에 올라가 영업 목패를 걸고 종을 세 번 울린다."
            ),
            SpeechBlock(
                "underworld_girl",
                "개점이다! 오늘 첫 그릇은 내 것이다!",
                "open_service_with_bright_appetite",
            ),
            ActionBlock("화덕 앞의 강도윤은 고개도 들지 않는다."),
            SpeechBlock(
                "doyun",
                "공주님께선 벌써 두 접시 드셨습니다.",
                "show_dry_familiarity",
            ),
            SpeechBlock(
                "underworld_girl",
                "맛보기는 끼니가 아니니라.",
                "defend_appetite_with_royal_confidence",
            ),
            ActionBlock(
                "검은 수조에서 망각어 한 마리가 솟구친다. 소녀가 쟁반을 낚아채 왼쪽으로 "
                "내민다."
            ),
            SpeechBlock(
                "underworld_girl",
                "왼쪽이다!",
                "join_the_kitchen_action",
            ),
            ActionBlock(
                "도윤은 돌아보지 않고 칼자루로 망각어의 옆구리를 툭 친다. 망각어가 "
                "쟁반 한가운데 떨어진다. 소녀가 손목을 돌려 생선을 도마로 미끄러뜨린다. "
                "칼이 한 번 지나간다. 꿈틀대는 검은 뼈와 흠집 없는 투명한 살이 나뉜다."
            ),
            ActionBlock(
                "소녀가 살 한 점을 집으려 하자 도윤이 칼등으로 손가락 앞을 막는다. 도윤은 "
                "그 한 점을 푸른 불에 스치고 굵은 소금 두 알만 얹어 소녀에게 내민다."
            ),
            SpeechBlock(
                "underworld_girl",
                "흠. 오늘도 간신히 합격이다.",
                "hide_delight_behind_playful_authority",
            ),
            ActionBlock("소녀의 눈은 반짝이고 두 팔은 접시를 꼭 끌어안고 있다."),
            SpeechBlock(
                "doyun",
                "접시를 내려놓고 말씀하시죠.",
                "land_the_duo_comedy_without_losing_control",
            ),
            ActionBlock(
                "현관의 문종이 운다. 소녀는 접시를 든 채 카운터에서 가볍게 뛰어내린다."
            ),
        ),
        information_revealed_ids=(
            "restaurant_already_operating",
            "doyun_overwhelming_established_skill",
            "girl_bright_royal_appetite",
            "duo_practiced_kitchen_rhythm",
        ),
        information_withheld_ids=(
            "doyun_accident",
            "doyun_contract",
            "doyun_real_world_daughter",
            "restaurant_opening_history",
            "girl_long_term_identity_purpose",
        ),
        state_delta_codes=(
            "audience_view:unknown_duo->skilled_playful_duo",
            "restaurant_operation:between_orders->open_for_next_guest",
        ),
        tension_delta="the_leads_take_the_episode_before_the_guest_arrives",
    ),
    SceneDraft(
        scene_id="S02",
        heading="삼도식당 홀 / 실내 / 밤",
        location="samdo_dining_hall",
        purpose="소녀의 활기찬 접객과 도윤의 절제된 확인으로 손님의 첫 주문을 자연스럽게 만든다",
        duration_seconds=29,
        causal_role=CausalRole.MEANINGFUL_CHOICE,
        renderer_primary=RendererKind.SELECTION,
        renderer_secondary=(RendererKind.ATTACHMENT_SAFETY,),
        principal_character_ids=("doyun", "underworld_girl", "guest_kim_munseong"),
        blocks=(
            ActionBlock(
                "기름때 밴 작업복 차림의 김문성(60대)이 들어온다. 소녀는 발끝으로 의자를 쏙 빼고, "
                "손에 든 접시는 등 뒤로 감춘다."
            ),
            SpeechBlock(
                "underworld_girl",
                "어서 앉거라. 오늘 망각어가 아주 좋다.",
                "welcome_and_recommend_with_energy",
            ),
            SpeechBlock(
                "doyun",
                "그건 제가 할 말입니다.",
                "show_proprietary_chef_pride",
            ),
            SpeechBlock(
                "underworld_girl",
                "내가 먼저 먹었으니 내 말이기도 하다.",
                "claim_taster_authority",
            ),
            ActionBlock(
                "김문성은 자리에 앉아 뜨거운 찻잔을 두 손으로 감싼다. 화상과 굳은살이 "
                "겹친 손. 왼손 안에는 그을린 황동 표찰이 반쯤 숨겨져 있다. 푸른 화덕불이 "
                "오를 때마다 그의 눈이 주방으로 간다."
            ),
            SpeechBlock(
                "doyun",
                "뜨거운 국물, 괜찮으십니까?",
                "confirm_one_relevant_preference",
            ),
            SpeechBlock(
                "guest_kim_munseong",
                "따뜻한 거면 됐소.",
                "accept_recommendation_without_personal_choice",
            ),
            ActionBlock("소녀는 빈 주문 목패에 붓을 댄다."),
            SpeechBlock(
                "underworld_girl",
                "망각어 맑은국, 하나!",
                "turn_choice_into_a_lively_order",
            ),
            ActionBlock("목패가 주방 고리에 탁 걸린다."),
        ),
        information_revealed_ids=(
            "guest_passive_order_style",
            "guest_heat_worn_hands",
            "guest_hidden_brass_tag",
            "guest_watches_fire",
        ),
        information_withheld_ids=("guest_brass_tag_identity",),
        state_delta_codes=(
            "guest_order:none->clear_broth_recommendation",
            "girl_role:playful_taster->active_host",
        ),
        tension_delta="a_bright_order_opens_a_quiet_guest_choice_problem",
    ),
    SceneDraft(
        scene_id="S03",
        heading="삼도식당 주방·홀 / 실내 / 밤",
        location="samdo_open_kitchen",
        purpose="100초 조리에서 도윤의 정확성과 소녀의 장난기 뒤에 숨은 관찰력을 함께 증명한다",
        duration_seconds=100,
        causal_role=CausalRole.MEANINGFUL_ACTION,
        renderer_primary=RendererKind.COMPETENCE,
        renderer_secondary=(RendererKind.RESOURCE, RendererKind.ATTACHMENT_SAFETY),
        principal_character_ids=("doyun", "underworld_girl", "guest_kim_munseong"),
        blocks=(
            ActionBlock(
                "도윤은 망각어의 검은 뼈를 푸른 불에 볶는다. 가장자리가 갈색으로 바뀌는 "
                "찰나에 물을 붓는다. 검은 거품이 떠오르자 국자로 한 번 훑어 걷어 낸다. 탁했던 "
                "국물이 바닥까지 비칠 만큼 맑아진다."
            ),
            ActionBlock(
                "푸른 뿌리를 숯불 위에서 굴린다. 껍질은 새까맣게 타고, 갈라진 틈에서 "
                "황금빛 속살이 드러난다. 도윤은 투명한 생선살을 소금에 잠깐 눌렀다가 "
                "일정한 간격으로 저민다. 도마 위에 놓인 살의 두께가 모두 같다."
            ),
            ActionBlock("소녀가 국자를 들고 맑은 육수 쪽으로 다가간다."),
            SpeechBlock(
                "underworld_girl",
                "한 숟갈만.",
                "keep_playful_appetite_alive_during_cooking",
            ),
            SpeechBlock(
                "doyun",
                "합격 판정은 끝나지 않았습니까?",
                "parry_the_girl_without_stopping_work",
            ),
            ActionBlock(
                "소녀가 입을 삐죽이던 중 홀의 김문성을 본다. 김문성의 시선은 음식보다 "
                "화덕불에 오래 머문다. 소녀는 국자를 내려놓고 작은 검은 주전자를 챙긴다."
            ),
            SpeechBlock(
                "underworld_girl",
                "검은 주전자는 내가 맡겠다.",
                "switch_from_mischief_to_service_judgment",
            ),
            SpeechBlock(
                "doyun",
                "불향까지 보셨군요.",
                "recognize_the_girl_as_a_real_partner",
            ),
            SpeechBlock(
                "underworld_girl",
                "손님이 불에서 눈을 못 떼니라.",
                "state_observation_without_diagnosing_history",
            ),
            SpeechBlock(
                "doyun",
                "그럼 두 번째 맛도 준비하죠.",
                "commit_to_two_complete_finishes",
            ),
            ActionBlock(
                "도윤은 남겨 둔 뼈를 쓴내가 나기 직전까지 더 볶는다. 첫 육수로 풀어 검은 "
                "주전자에 거른다. 도윤이 한 숟갈 맛보고 고개를 끄덕인다. 소녀는 주전자를 "
                "보온 화로에 올리고 불을 한 칸 낮춘 뒤 뚜껑을 닫는다."
            ),
            ActionBlock(
                "도윤은 투명한 생선살과 구운 뿌리를 첫 그릇에 담는다. 맑은 육수를 붓자 "
                "생선 가장자리가 꽃잎처럼 하얗게 익는다."
            ),
        ),
        information_revealed_ids=(
            "doyun_exact_heat_and_knife_control",
            "first_clear_broth_completed",
            "second_fire_broth_completed_before_choice",
            "girl_reads_guest_fire_attention",
        ),
        information_withheld_ids=(
            "guest_engine_room_tag",
            "doyun_accident",
            "doyun_contract",
            "doyun_real_world_daughter",
        ),
        state_delta_codes=(
            "dish_state:raw_ingredients->two_complete_finishes",
            "girl_role:playful_taster->necessary_service_observer",
            "duo_relation:comic_rhythm->mutual_professional_trust",
        ),
        tension_delta="two_successful_tastes_wait_for_the_guest_to_choose",
    ),
    SceneDraft(
        scene_id="S04",
        heading="삼도식당 홀 / 실내 / 밤",
        location="samdo_dining_hall",
        purpose="첫 그릇을 완전한 성공으로 지급하면서 소녀의 기대와 도윤에 대한 신뢰를 함께 보인다",
        duration_seconds=44,
        causal_role=CausalRole.PRIOR_CHOICE_CONSEQUENCE,
        renderer_primary=RendererKind.ATTACHMENT_SAFETY,
        renderer_secondary=(RendererKind.COMPETENCE, RendererKind.SELECTION),
        principal_character_ids=("doyun", "underworld_girl", "guest_kim_munseong"),
        blocks=(
            ActionBlock(
                "소녀가 망각어 맑은국을 김문성 앞에 내려놓는다. 두 손을 허리에 얹고, "
                "김문성의 얼굴 가까이 몸을 기울인다."
            ),
            SpeechBlock(
                "underworld_girl",
                "자, 먹어 보거라.",
                "invite_the_first_taste_with_visible_excitement",
            ),
            SpeechBlock(
                "doyun",
                "공주님이 더 긴장하셨습니다.",
                "tease_the_girl_and_mark_shared_stakes",
            ),
            SpeechBlock(
                "underworld_girl",
                "주문은 내가 받았으니라.",
                "claim_real_service_ownership",
            ),
            ActionBlock(
                "김문성은 김을 오래 맡은 뒤 국물을 마신다. 굳었던 어깨가 내려간다. 두 번째 "
                "숟갈부터 속도가 붙는다. 구운 뿌리를 씹자 황동 표찰을 문지르던 엄지도 "
                "멈춘다. 그는 건더기와 국물을 모두 비운다. 소녀는 김문성의 표정에서 "
                "눈을 떼지 않는다."
            ),
            ActionBlock(
                "빈 그릇을 놓지 않은 김문성이 다시 푸른 화덕불을 본다."
            ),
            SpeechBlock(
                "guest_kim_munseong",
                "불 냄새를 더 낼 수 있소?",
                "make_a_first_personal_request",
            ),
            SpeechBlock(
                "underworld_girl",
                "물론이다.",
                "trust_doyun_without_hesitation",
            ),
            SpeechBlock(
                "doyun",
                "이미 데워 뒀습니다.",
                "reveal_prepared_success_not_correction",
            ),
        ),
        information_revealed_ids=(
            "first_soup_fully_successful",
            "guest_requests_more_fire",
            "girl_trusts_doyun_skill",
        ),
        information_withheld_ids=("guest_brass_tag_identity",),
        state_delta_codes=(
            "first_soup:served->fully_consumed",
            "guest_preference:passive->active_fire_request",
            "girl_stake:order_taker->emotionally_invested_host",
        ),
        tension_delta="the_first_success_opens_a_more_personal_second_success",
    ),
    SceneDraft(
        scene_id="S05",
        heading="삼도식당 홀 / 실내 / 밤",
        location="samdo_dining_hall",
        purpose="불향 끝맛과 추가 주문으로 손님을 완결하면서 소녀의 기쁨과 도윤의 흔들림 없는 실행을 지급한다",
        duration_seconds=54,
        causal_role=CausalRole.MEANINGFUL_CHOICE,
        renderer_primary=RendererKind.SELECTION,
        renderer_secondary=(RendererKind.COMPETENCE, RendererKind.RESOURCE),
        principal_character_ids=("doyun", "underworld_girl", "guest_kim_munseong"),
        blocks=(
            ActionBlock(
                "소녀가 기다렸다는 듯 검은 주전자를 가져온다. 도윤은 새 망각어 한 점과 "
                "구운 뿌리를 작은 그릇에 담고 짙은 육수를 붓는다. 맑은 빛은 남아 있지만 "
                "김이 굵고 불향이 깊다."
            ),
            ActionBlock("김문성이 한 모금 마신다. 이번에는 대답을 오래 고르지 않는다."),
            SpeechBlock(
                "guest_kim_munseong",
                "이쪽이 좋소.",
                "name_personal_taste",
            ),
            ActionBlock("소녀가 목패에 불향 진하게라고 적는다."),
            SpeechBlock(
                "underworld_girl",
                "불향 진하게.",
                "record_the_chosen_finish",
            ),
            SpeechBlock(
                "guest_kim_munseong",
                "한 그릇 더 주시오.",
                "place_direct_repeat_order",
            ),
            SpeechBlock(
                "underworld_girl",
                "좋은 주문이다!",
                "celebrate_the_guest_choice",
            ),
            SpeechBlock(
                "doyun",
                "한 그릇 더 나갑니다.",
                "execute_repeat_order_without_hesitation",
            ),
            ActionBlock(
                "도윤은 미리 손질해 둔 재료로 새 그릇을 완성한다. 김문성은 이번에도 국물 한 "
                "방울 남기지 않는다."
            ),
            SpeechBlock(
                "guest_kim_munseong",
                "잘 먹었소.",
                "close_the_guest_meal",
            ),
            ActionBlock(
                "김문성은 검은 엽전을 놓는다. 손안에 숨겼던 황동 표찰을 작업복 바깥주머니에 "
                "단다. 표찰에는 기관실 7호라고 새겨져 있다. 그는 빈 그릇에서 손을 떼고 "
                "곧은 자세로 문을 나간다. 문이 닫히자 소녀가 주문 목패를 결산 고리에 건다."
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
        tension_delta="the_guest_closes_and_the_duo_keeps_a_new_service_record",
    ),
    SceneDraft(
        scene_id="S06",
        heading="삼도식당 주방 / 실내 / 밤",
        location="samdo_open_kitchen",
        purpose="12초 코다에서 소녀의 식욕과 도윤의 익숙한 배려를 다음 영업으로 연결한다",
        duration_seconds=12,
        causal_role=CausalRole.PRIOR_CHOICE_CONSEQUENCE,
        renderer_primary=RendererKind.ATTACHMENT_SAFETY,
        renderer_secondary=(RendererKind.RESOURCE, RendererKind.COMPETENCE),
        principal_character_ids=("doyun", "underworld_girl"),
        blocks=(
            ActionBlock(
                "소녀가 김문성의 목패 옆에 새 목패를 건다. 망각어 볼살 구이, 소금 두 번."
            ),
            SpeechBlock(
                "underworld_girl",
                "내 것은 볼살 구이다. 소금 두 번!",
                "make_a_bright_personal_order",
            ),
            ActionBlock(
                "도윤이 덮개를 연다. 가장자리가 바삭하게 구워진 볼살이 이미 놓여 있다."
            ),
            SpeechBlock(
                "underworld_girl",
                "벌써?",
                "show_delighted_surprise",
            ),
            SpeechBlock(
                "doyun",
                "세 번째라서요.",
                "answer_with_established_familiarity",
            ),
            ActionBlock("소녀가 볼살을 한입 베어 물고 영업 목패를 바로 세운다."),
            SpeechBlock(
                "underworld_girl",
                "네 번째도 가능하다!",
                "end_on_appetite_and_momentum",
            ),
            SpeechBlock(
                "doyun",
                "영업 끝나고요.",
                "keep_the_restaurant_moving",
            ),
            ActionBlock(
                "도윤은 다음 망각어를 수조에서 건지고, 소녀는 새 주문 목패를 집는다."
            ),
        ),
        information_revealed_ids=(
            "girl_preferred_employee_dish",
            "duo_repeat_service_rhythm",
        ),
        information_withheld_ids=(
            "girl_long_term_identity_purpose",
            "doyun_return_plan",
        ),
        state_delta_codes=(
            "girl_role:host->co_owner_of_next_service",
            "duo_relation:professional_trust->playful_repeat_familiarity",
            "restaurant_operation:closed_order->ready_for_next_order",
        ),
        tension_delta="the_guest_is_closed_while_the_leads_keep_the_series_alive",
    ),
)


PRODUCTION_BEATS: dict[str, tuple[tuple[int, str], ...]] = {
    "S01": (
        (8, "소녀의 개점 선언과 두 접시 공방"),
        (8, "망각어 탈출, 소녀의 쟁반과 도윤의 칼자루 합"),
        (10, "한 칼 손질과 푸른 불 맛보기"),
        (10, "소녀의 합격 허세와 손님 문종"),
    ),
    "S02": (
        (8, "소녀의 활기찬 착석과 추천"),
        (9, "김문성의 손·표찰·화덕 시선"),
        (8, "도윤의 한 가지 취향 확인"),
        (4, "소녀의 주문 목패 콜"),
    ),
    "S03": (
        (18, "검은 뼈 볶기와 맑은 육수"),
        (18, "푸른 뿌리와 동일 두께 생선살"),
        (16, "소녀의 한 숟갈 장난"),
        (16, "소녀가 손님의 불 시선을 포착"),
        (18, "별도 불향 육수 완성"),
        (14, "첫 맑은국 조립"),
    ),
    "S04": (
        (8, "소녀가 첫 그릇을 내고 기대를 숨기지 못함"),
        (24, "김문성의 실제 섭취와 완식"),
        (6, "빈 그릇과 화덕 시선"),
        (6, "불향 요청과 이미 준비된 답"),
    ),
    "S05": (
        (8, "소녀가 검은 주전자를 운반"),
        (10, "두 번째 완성품의 김과 향"),
        (8, "손님의 끝맛 선택과 소녀의 기록"),
        (16, "추가 한 그릇 조리와 완식"),
        (12, "결제·표찰·퇴장·결산"),
    ),
    "S06": (
        (3, "소녀의 직원식 목패"),
        (3, "도윤이 준비한 볼살 구이"),
        (3, "네 번째 그릇 공방"),
        (3, "다음 주문 준비"),
    ),
}


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_scene_distance_status() -> dict[str, object]:
    prior = previous.build_episode()
    return {
        "artifact_id": "afterlife_restaurant:ep001:character_surface",
        "receipt_type": "scene_distance_status",
        "status": "pending_not_evaluated",
        "promotion_allowed": False,
        "prior_candidate_content_sha256": prior.content_sha256,
        "reason": (
            "캐릭터 중심 재집필과 인간용 표면 분리는 완료했다. 독립 장면 거리 감리와 "
            "BR0·BR1 전에는 승인본이나 외부 전달본이 아니다."
        ),
    }


def build_format_receipt() -> dict[str, object]:
    return {
        "receipt_type": "human_screenplay_surface_review",
        "surface_contract": (
            "episode_heading_then_scene_heading_then_interleaved_action_and_dialogue"
        ),
        "separate_production_breakdown": True,
        "raw_reference_dialogue_ingested": False,
        "raw_reference_event_order_ingested": False,
        "generator_ingest_allowed": False,
        "rights_or_source_status_inferred": False,
    }


def build_episode() -> EpisodeScriptCandidate:
    hil2_builder = previous._load_hil2_approved_builder()
    arc, arc_receipt, _ = hil2_builder.build_approval()
    distance_status = build_scene_distance_status()
    scenes: list[EpisodeScene] = []
    for draft in SCENE_DRAFTS:
        actions = [block.text for block in draft.blocks if isinstance(block, ActionBlock)]
        dialogue = tuple(
            DialogueLine(block.speaker_id, block.text, block.function)
            for block in draft.blocks
            if isinstance(block, SpeechBlock)
        )
        scenes.append(
            EpisodeScene(
                scene_id=draft.scene_id,
                location=draft.location,
                purpose=draft.purpose,
                observable_action=" ".join(actions),
                causal_role=draft.causal_role,
                renderer_primary=draft.renderer_primary,
                renderer_secondary=draft.renderer_secondary,
                principal_character_ids=draft.principal_character_ids,
                duration_seconds=draft.duration_seconds,
                dialogue=dialogue,
                information_revealed_ids=draft.information_revealed_ids,
                information_withheld_ids=draft.information_withheld_ids,
                state_delta_codes=draft.state_delta_codes,
                tension_delta=draft.tension_delta,
            )
        )
    episode = EpisodeScriptCandidate(
        work_id=arc.work_id,
        arc_id=arc.arc_id,
        episode_id="afterlife_restaurant:ep001:character_surface",
        revision=2,
        producer_id="codex_primary_writer",
        status=EpisodeScriptStatus.CANDIDATE,
        parent_arc_content_sha256=arc.content_sha256,
        parent_arc_approval_receipt_sha256=arc_receipt.receipt_sha256,
        source_scaffold_sha256=_file_sha256(SOURCE_SCAFFOLD_PATH),
        source_distance_receipt_sha256=canonical_sha256(distance_status),
        target_runtime_seconds=275,
        beat_pattern=BeatPatternKind.SELECTION_SAFETY,
        scenes=tuple(scenes),
        final_state_delta_codes=(
            "lead_impression:facilitators->skilled_playful_series_duo",
            "guest_preference:passive_recommendation->named_fire_finish",
            "guest_arc:open->closed_with_payment_and_departure",
            "girl_service:bright_host->observant_choice_recorder",
            "restaurant_operation:no_finish_rule->paid_two_finish_order_record",
        ),
        rewards_paid=(
            "dish_and_guest_action_payoff",
            "story_unit_closure",
            "restaurant_operational_accumulation",
        ),
        rewards_deferred=("doyun_return_to_daughter",),
        obligation_kind=EpisodeObligationKind.CLOSURE,
        obligation=(
            "김문성의 음식·선택·결제·퇴장은 1화에서 완결된다. 도윤의 실력과 소녀의 "
            "발랄함은 첫 36초에 증명되며, 다음 회차는 새 손님으로 시작할 수 있다"
        ),
        original_contributions=(
            "소녀의 요란한 개점과 도윤의 정밀 조리를 한 동작 안에서 맞물려 두 주연을 먼저 세운다",
            "소녀의 식욕과 왕족다운 허세 뒤에 손님의 불 시선을 읽는 서비스 판단을 함께 둔다",
            "첫 맑은국과 별도 불향 국물을 정답과 수정이 아닌 두 완성품으로 먼저 준비한다",
            "손님 퇴장 뒤 소녀의 네 번째 그릇 요구와 도윤의 영업 통제가 반복 동업 호흡을 만든다",
        ),
    )
    report = EpisodeScriptVerifier().verify(episode, arc)
    if not report.passed:
        findings = ", ".join(finding.code for finding in report.findings)
        raise ValueError(f"invalid character-surface episode candidate: {findings}")
    return episode


def export_human_screenplay() -> str:
    speaker_names = {
        "doyun": "도윤",
        "underworld_girl": "소녀",
        "guest_kim_munseong": "김문성",
    }
    lines = [
        "# 제1화 오늘 망각어가 좋습니다",
        "",
        "대본 후보 0.4",
        "",
    ]
    for number, draft in enumerate(SCENE_DRAFTS, start=1):
        lines.extend((f"## {number}. {draft.heading}", ""))
        for block in draft.blocks:
            if isinstance(block, ActionBlock):
                lines.extend((block.text, ""))
            else:
                lines.extend(
                    (
                        f"    {speaker_names[block.speaker_id]}      {block.text}",
                        "",
                    )
                )
    lines.extend(("끝.", ""))
    return "\n".join(lines)


def _timestamp(seconds: int) -> str:
    return f"{seconds // 60}:{seconds % 60:02d}"


def export_production_breakdown(episode: EpisodeScriptCandidate) -> str:
    lines = [
        "# 삼도식당 1화 제작용 장면표",
        "",
        "> 인간용 대본과 분리된 내부 제작 자료다. 이 문서만으로 대본을 읽지 않는다.",
        "",
        "- 목표 길이: `4분 35초`",
        "- 조리 중심 구간: `100초`",
        "- 첫 그릇 실제 섭취: `24초`",
        "- 손님 퇴장 뒤 코다: `12초`",
        "",
    ]
    elapsed = 0
    for scene, draft in zip(episode.scenes, SCENE_DRAFTS, strict=True):
        end = elapsed + scene.duration_seconds
        lines.extend(
            (
                f"## 장면 {scene.scene_id} · {_timestamp(elapsed)}-{_timestamp(end)}",
                "",
                f"- 기능: {scene.purpose}",
                f"- 대사 수: `{len(scene.dialogue)}줄`",
                "- 시간 배분:",
                "",
            )
        )
        beat_elapsed = elapsed
        for seconds, description in PRODUCTION_BEATS[draft.scene_id]:
            beat_end = beat_elapsed + seconds
            lines.append(
                f"  - `{_timestamp(beat_elapsed)}-{_timestamp(beat_end)}` {description}"
            )
            beat_elapsed = beat_end
        lines.append("")
        elapsed = end
    lines.extend(
        (
            "## 승격 경계",
            "",
            "- 장면 거리 감리: `대기`",
            "- BR0: `시작 전`",
            "- BR1: `시작 전`",
            "- HIL 3 책임자 승인: `시작 전`",
            "- 외부 전달·업로드: `금지`",
            "- 2화 대본: `생성하지 않음`",
            "",
        )
    )
    return "\n".join(lines)


def export_author_review(episode: EpisodeScriptCandidate) -> str:
    first_scene = episode.scenes[0]
    return "\n".join(
        (
            "# 삼도식당 1화 0.4 작가 자체 감리",
            "",
            "> 독립 BR0·BR1이 아니다. 승격 근거로 사용할 수 없다.",
            "",
            "## 1차 · 캐릭터",
            "",
            f"- 첫 장면 `{first_scene.duration_seconds}초` 안에서 도윤은 보지 않고 망각어를 받아 한 칼에 손질하고, 정확한 불과 소금으로 맛보기를 완성한다.",
            "- 소녀는 개점을 선언하고 쟁반으로 조리에 합류하며, 접시를 끌어안고 합격을 선언한다. 움직임과 식욕이 첫 장면부터 보인다.",
            "- 도윤은 냉정한 기능인이 아니라 자기 주방에 자부심이 있고 소녀의 허세를 받아치는 인물이다.",
            "- 소녀는 소란스러운 마스코트에 머물지 않는다. 장난을 멈추고 손님의 불 시선을 먼저 읽어 두 번째 육수를 맡는다.",
            "- 손님은 두 주연이 소개된 뒤 입장한다. 김문성의 변화가 도윤과 소녀의 첫인상을 빼앗지 않는다.",
            "",
            "판정: `통과`",
            "",
            "## 2차 · 인간용 표면과 문장",
            "",
            "- 인간용 대본에는 회차, 장면번호, 장소·시간, 행동, 대사만 남겼다.",
            "- 장면 목적, 초 단위 컷, 소리, 감리 상태는 제작용 장면표로 옮겼다.",
            "- 대사는 주문·식욕·주방 공방에서 나온다. 인물이 구조를 설명하거나 손님의 인생을 진단하지 않는다.",
            "- 각 장면 대사는 6줄 이하이며, 사고·현실의 딸·계약·개업 과정은 설명하지 않는다.",
            "- 첫 음식과 불향 음식은 모두 완성품이다. 도윤은 1화에서 실패하지 않는다.",
            "",
            "문체 점검: 직접성 `9/10`, 리듬 `9/10`, 독자 신뢰 `9/10`, 인물성 `9/10`, 밀도 `9/10` = `45/50`.",
            "",
            "판정: `통과`",
            "",
            "## 남은 연출 위험",
            "",
            "- 첫 36초의 망각어 동작은 소녀와 도윤의 합이 한눈에 읽혀야 한다. 컷을 잘게 쪼개면 도윤 혼자 해결한 것처럼 보이거나 소녀가 방해꾼처럼 보일 수 있다.",
            "- 소녀의 고어체는 문장 끝마다 반복하지 않는다. 성우 연기에서도 발랄한 속도를 먼저 살린다.",
            "- 기관실 표찰은 손안에서 바깥주머니로 옮겨지는 위치 변화로 읽힌다. 설명 대사를 추가하지 않는다.",
            "",
        )
    )


def build_outputs() -> dict[Path, str]:
    if not SOURCE_SCAFFOLD_PATH.exists():
        raise FileNotFoundError(SOURCE_SCAFFOLD_PATH)
    episode = build_episode()
    hil2_builder = previous._load_hil2_approved_builder()
    arc, receipt, _ = hil2_builder.build_approval()
    distance_status = build_scene_distance_status()
    research_receipt = previous.build_research_receipt()
    format_receipt = build_format_receipt()
    screenplay = export_human_screenplay()
    breakdown = export_production_breakdown(episode)
    review = export_author_review(episode)
    prior_episode = previous.build_episode()
    manifest = {
        "schema_version": "1",
        "work_id": episode.work_id,
        "episode_id": episode.episode_id,
        "revision": episode.revision,
        "status": "candidate",
        "episode_scope": "ep001_only",
        "episode_content_sha256": episode.content_sha256,
        "human_screenplay_sha256": hashlib.sha256(screenplay.encode("utf-8")).hexdigest(),
        "production_breakdown_sha256": hashlib.sha256(breakdown.encode("utf-8")).hexdigest(),
        "author_review_sha256": hashlib.sha256(review.encode("utf-8")).hexdigest(),
        "parent_arc_content_sha256": arc.content_sha256,
        "parent_arc_approval_receipt_sha256": receipt.receipt_sha256,
        "source_scaffold_sha256": _file_sha256(SOURCE_SCAFFOLD_PATH),
        "research_receipt_sha256": canonical_sha256(research_receipt),
        "format_receipt_sha256": canonical_sha256(format_receipt),
        "scene_distance_status": distance_status["status"],
        "scene_distance_status_sha256": canonical_sha256(distance_status),
        "supersedes_candidate_content_sha256": prior_episode.content_sha256,
        "supersedes_candidate_path": PREVIOUS_OUTPUT_ROOT.relative_to(ROOT).as_posix(),
        "br0_status": "not_started",
        "br1_status": "not_started",
        "owner_approval": "not_started",
        "external_promotion_allowed": False,
        "next_gate": "scene_distance_then_independent_br0_br1",
    }
    return {
        OUTPUT_ROOT / "episode_script.json": canonical_json(episode) + "\n",
        OUTPUT_ROOT / "episode_001_human_screenplay.md": screenplay,
        OUTPUT_ROOT / "production_scene_breakdown.md": breakdown,
        OUTPUT_ROOT / "author_self_review.md": review,
        OUTPUT_ROOT / "research_input_receipt.json": canonical_json(research_receipt) + "\n",
        OUTPUT_ROOT / "format_surface_receipt.json": canonical_json(format_receipt) + "\n",
        OUTPUT_ROOT / "scene_distance_status.json": canonical_json(distance_status) + "\n",
        OUTPUT_ROOT / "manifest.json": canonical_json(manifest) + "\n",
    }


def check_outputs(outputs: dict[Path, str]) -> tuple[str, ...]:
    findings: list[str] = []
    episode = build_episode()
    for scene in episode.scenes:
        allocated = sum(seconds for seconds, _ in PRODUCTION_BEATS[scene.scene_id])
        if allocated != scene.duration_seconds:
            findings.append(f"production_duration_mismatch:{scene.scene_id}")
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
        print("afterlife_restaurant character-surface ep001 candidate is current")
        return 0
    write_outputs(outputs)
    print(OUTPUT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
