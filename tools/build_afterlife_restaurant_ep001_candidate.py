#!/usr/bin/env python3
"""Build the HIL 3 episode-one script candidate for 삼도식당."""

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
    / "ep001"
)
HIL2_APPROVED_BUILDER_PATH = (
    ROOT / "tools" / "build_afterlife_restaurant_hil2_arc01_approved.py"
)
SOURCE_SCAFFOLD_PATH = (
    ROOT
    / "artifacts"
    / "candidates"
    / "afterlife_restaurant"
    / "hil2"
    / "arc01_first_service"
    / "episode_001_rough_beat_sheet_v0.1.md"
)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_hil2_approved_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "afterlife_restaurant_hil2_arc01_approved_builder",
        HIL2_APPROVED_BUILDER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load the approved HIL 2 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_scene_distance_status() -> dict[str, object]:
    return {
        "artifact_id": "afterlife_restaurant:ep001",
        "receipt_type": "scene_distance_status",
        "status": "pending_not_evaluated",
        "promotion_allowed": False,
        "reason": (
            "1화 후보는 승인된 HIL 1·2와 내부 각색표에서 만들었다. 독립 장면 "
            "거리 감리와 BR0·BR1 전에는 승인본이나 외부 전달본이 아니다."
        ),
    }


def build_episode() -> EpisodeScriptCandidate:
    hil2_builder = _load_hil2_approved_builder()
    arc, arc_receipt, _ = hil2_builder.build_approval()
    distance_status = build_scene_distance_status()
    episode = EpisodeScriptCandidate(
        work_id=arc.work_id,
        arc_id=arc.arc_id,
        episode_id="afterlife_restaurant:ep001",
        revision=1,
        producer_id="codex_primary_writer",
        status=EpisodeScriptStatus.CANDIDATE,
        parent_arc_content_sha256=arc.content_sha256,
        parent_arc_approval_receipt_sha256=arc_receipt.receipt_sha256,
        source_scaffold_sha256=_file_sha256(SOURCE_SCAFFOLD_PATH),
        source_distance_receipt_sha256=canonical_sha256(distance_status),
        target_runtime_seconds=270,
        beat_pattern=BeatPatternKind.SUSPENSE_INFORMATION_GAP,
        scenes=(
            EpisodeScene(
                scene_id="S01",
                location="samdo_open_kitchen",
                purpose="첫 8초에 도윤의 조리 능력과 소녀의 식욕을 판다",
                observable_action=(
                    "검은 수조에서 은빛 물고기가 튀어 오른다. 물고기는 도윤의 칼끝을 피해 몸을 꺾지만, 도윤은 아가미 뒤를 맨손으로 낚아채 도마에 눕힌다. 칼이 배를 한 번 지나가자 검은 뼈와 투명한 살이 갈라진다. 푸른 불 위에서 향이 터지고, 문턱의 소녀가 자신도 모르게 반 보 앞으로 나온다."
                ),
                causal_role=CausalRole.MEANINGFUL_ACTION,
                renderer_primary=RendererKind.COMPETENCE,
                renderer_secondary=(RendererKind.RESOURCE,),
                principal_character_ids=("doyun", "underworld_girl"),
                duration_seconds=8,
                dialogue=(),
                information_revealed_ids=(
                    "doyun_underworld_ingredient_competence",
                    "girl_food_appetite",
                ),
                information_withheld_ids=(
                    "doyun_accident",
                    "doyun_contract",
                    "doyun_real_world_daughter",
                ),
                state_delta_codes=(
                    "doyun_underworld_competence:unknown->visible",
                ),
                tension_delta="first_impossible_ingredient_becomes_food",
            ),
            EpisodeScene(
                scene_id="S02",
                location="samdo_dining_hall",
                purpose="김문성의 선택 포기와 두 주연의 권한 차이를 놓는다",
                observable_action=(
                    "김문성은 빈 그릇을 두 손으로 감싼다. 도윤은 작업복의 기름때, 손등의 화상, 오른쪽으로 기울어진 고개를 차례로 본다. 소녀가 주문 목패를 탁자에 놓자 도윤의 손과 작은 목패가 그릇 양쪽을 차지한다."
                ),
                causal_role=CausalRole.MEANINGFUL_CHOICE,
                renderer_primary=RendererKind.SELECTION,
                renderer_secondary=(RendererKind.COMPETENCE,),
                principal_character_ids=(
                    "doyun",
                    "underworld_girl",
                    "guest_kim_munseong",
                ),
                duration_seconds=34,
                dialogue=(
                    DialogueLine(
                        "guest_kim_munseong",
                        "아무거나 주시오. 평생 주는 대로 먹었으니.",
                        "show_choice_abandonment",
                    ),
                    DialogueLine(
                        "underworld_girl",
                        "삼도식당에 아무거나는 없느니라.",
                        "state_guest_choice_rule",
                    ),
                    DialogueLine(
                        "doyun",
                        "고르지 못하면, 반응부터 보죠.",
                        "declare_diagnostic_course",
                    ),
                    DialogueLine(
                        "underworld_girl",
                        "손님을 시험하겠다는 것이냐?",
                        "challenge_cook_intent",
                    ),
                    DialogueLine(
                        "doyun",
                        "첫 코스를 내겠다는 겁니다.",
                        "frame_course_as_service",
                    ),
                ),
                information_revealed_ids=(
                    "guest_refuses_to_name_preference",
                    "girl_holds_guest_choice_rule",
                ),
                information_withheld_ids=("guest_full_life_history",),
                state_delta_codes=(
                    "guest_preference:unspoken->observable_through_course",
                    "first_course:intent_unset->diagnostic_and_delicious",
                ),
                tension_delta="guest_choice_gap_becomes_cooking_task",
            ),
            EpisodeScene(
                scene_id="S03",
                location="samdo_open_kitchen",
                purpose="저승의 감각 제한을 도윤의 새 도구로 바꾼다",
                observable_action=(
                    "소녀가 은빛 결이 든 명경초를 내민다. 도윤은 잎을 씹고 눈을 감는다. 창고의 냄새가 층으로 갈라지자 도윤은 망각어, 푸른 뿌리, 불타는 고추를 망설임 없이 작업 순서대로 놓는다."
                ),
                causal_role=CausalRole.MEANINGFUL_ACTION,
                renderer_primary=RendererKind.COMPETENCE,
                renderer_secondary=(RendererKind.RESOURCE,),
                principal_character_ids=("doyun", "underworld_girl"),
                duration_seconds=30,
                dialogue=(
                    DialogueLine(
                        "underworld_girl",
                        "명경초다. 산 자의 혀로는 끝맛을 못 느끼느니라.",
                        "state_underworld_taste_rule",
                    ),
                    DialogueLine(
                        "underworld_girl",
                        "독인지도 안 묻는구나.",
                        "test_doyun_composure",
                    ),
                    DialogueLine(
                        "doyun",
                        "독이면 뒷맛이 더 길겠지.",
                        "show_dry_confidence",
                    ),
                    DialogueLine(
                        "underworld_girl",
                        "어떠하냐?",
                        "request_readout",
                    ),
                    DialogueLine(
                        "doyun",
                        "차갑고, 비었고, 불을 기다리네요.",
                        "translate_new_sense_into_cooking",
                    ),
                ),
                information_revealed_ids=(
                    "living_tongue_limit",
                    "mingyeongcho_taste_bridge",
                ),
                information_withheld_ids=("underworld_ingredient_full_lore",),
                state_delta_codes=(
                    "doyun_taste_access:living_only->underworld_enabled",
                ),
                tension_delta="new_sense_expands_possible_dishes",
            ),
            EpisodeScene(
                scene_id="S04",
                location="samdo_open_kitchen",
                purpose="망각어 불향 맑은국을 120초 동안 맛과 진단 모두에 성공시킨다",
                observable_action=(
                    "도윤은 앞서 갈라 둔 망각어 살의 물기를 닦고, 검은 뼈만 센 불에 볶아 맑은 육수를 뽑는다. 푸른 뿌리는 직화로 구워 단맛을 끌어낸다. 투명한 살은 푸른 불에 겉면만 스친 뒤 그릇에 담고, 손님 앞에서 뜨거운 육수를 부어 속까지 익힌다. 불향이 맑은 국물 위로 한 겹 피어난다. 소녀는 김을 따라 코를 내밀었다가 도윤과 눈이 마주치자 턱을 든다. 화면에 '망각어 불향 맑은국'이 뜬다. 도윤은 그릇을 손님 앞으로 먼저 보낸다."
                ),
                causal_role=CausalRole.MEANINGFUL_ACTION,
                renderer_primary=RendererKind.COMPETENCE,
                renderer_secondary=(RendererKind.RESOURCE,),
                principal_character_ids=(
                    "doyun",
                    "underworld_girl",
                    "guest_kim_munseong",
                ),
                duration_seconds=120,
                dialogue=(
                    DialogueLine(
                        "underworld_girl",
                        "푸른 불에 닿으니 살이 투명해졌다!",
                        "voice_visible_ingredient_transformation",
                    ),
                    DialogueLine(
                        "doyun",
                        "겉만 익힌 겁니다.",
                        "explain_precise_heat_control",
                    ),
                    DialogueLine(
                        "underworld_girl",
                        "속은 날것 아니더냐?",
                        "register_competence",
                    ),
                    DialogueLine(
                        "doyun",
                        "국물이 마저 익혀요.",
                        "dry_competence_payoff",
                    ),
                    DialogueLine(
                        "underworld_girl",
                        "본녀가 간을 보겠다.",
                        "character_appetite_bid",
                    ),
                    DialogueLine(
                        "doyun",
                        "손님 먼저.",
                        "preserve_guest_priority",
                    ),
                ),
                information_revealed_ids=(
                    "first_course_three_transformations",
                    "girl_appetite_under_royal_pose",
                ),
                information_withheld_ids=("final_guihangtang_method",),
                state_delta_codes=(
                    "first_course:ingredients->completed",
                    "girl_view_of_doyun:outsider->credible_cook",
                ),
                tension_delta="successful_course_creates_readable_guest_reaction",
            ),
            EpisodeScene(
                scene_id="S05",
                location="samdo_dining_hall",
                purpose="완식 반응으로 손님의 숨은 취향을 표면에 올린다",
                observable_action=(
                    "김문성은 첫 숟갈을 삼킨 뒤 곧바로 두 번째 숟갈을 뜬다. 속도가 붙고 이마에 땀이 맺힌다. 국물이 사라져도 그는 빈 그릇을 두 손에서 놓지 않는다. 구운 향이 남은 그릇 가장자리에 코를 가까이 대자 굳었던 어깨가 내려간다. 도윤은 손님의 왼쪽 귀와 화상 자국, 그릇을 감싼 손을 다시 본다."
                ),
                causal_role=CausalRole.PRIOR_CHOICE_CONSEQUENCE,
                renderer_primary=RendererKind.ATTACHMENT_SAFETY,
                renderer_secondary=(RendererKind.SELECTION,),
                principal_character_ids=(
                    "doyun",
                    "underworld_girl",
                    "guest_kim_munseong",
                ),
                duration_seconds=54,
                dialogue=(
                    DialogueLine(
                        "underworld_girl",
                        "처음 먹는 음식 아니더냐?",
                        "name_reaction_anomaly",
                    ),
                    DialogueLine(
                        "guest_kim_munseong",
                        "그런데 오래 먹은 것 같소.",
                        "surface_embodied_familiarity",
                    ),
                    DialogueLine(
                        "underworld_girl",
                        "맛있다는 말을 어렵게도 하는구나.",
                        "comic_register_of_success",
                    ),
                    DialogueLine(
                        "guest_kim_munseong",
                        "불 냄새가 조금 더 나면 좋겠소.",
                        "first_spoken_preference",
                    ),
                ),
                information_revealed_ids=(
                    "guest_likes_heat_and_fire_aroma",
                    "guest_first_spoken_preference",
                ),
                information_withheld_ids=("guest_complete_past",),
                state_delta_codes=(
                    "first_course:completed->fully_consumed",
                    "guest_preference:embodied->first_spoken_choice",
                ),
                tension_delta="successful_taste_opens_personal_final_course",
            ),
            EpisodeScene(
                scene_id="S06",
                location="samdo_dining_hall",
                purpose="첫 성공을 귀항탕의 선택 의무로 연결한다",
                observable_action=(
                    "도윤은 김문성의 손등 화상과 왼쪽 귀를 가리킨다. 소녀는 목패 두 장을 뒤집어 차가운 향과 뜨거운 불향의 표식을 보여 준다. 김문성은 망설이다 뜨거운 쪽을 손가락으로 짚는다. 도윤은 빈 그릇을 들어 주방으로 돌아간다."
                ),
                causal_role=CausalRole.MEANINGFUL_CHOICE,
                renderer_primary=RendererKind.SELECTION,
                renderer_secondary=(RendererKind.COMPETENCE,),
                principal_character_ids=(
                    "doyun",
                    "underworld_girl",
                    "guest_kim_munseong",
                ),
                duration_seconds=24,
                dialogue=(
                    DialogueLine(
                        "doyun",
                        "기관실에서 일하셨죠.",
                        "name_observed_work_identity",
                    ),
                    DialogueLine(
                        "guest_kim_munseong",
                        "그걸 어떻게 알았소?",
                        "register_observation_accuracy",
                    ),
                    DialogueLine(
                        "doyun",
                        "손에 다 남아 있습니다.",
                        "ground_inference_in_visible_evidence",
                    ),
                    DialogueLine(
                        "underworld_girl",
                        "차가운 쪽과 뜨거운 쪽. 네가 고르거라.",
                        "return_choice_to_guest",
                    ),
                    DialogueLine(
                        "guest_kim_munseong",
                        "뜨거운 쪽으로 주시오.",
                        "make_first_direct_choice",
                    ),
                    DialogueLine(
                        "doyun",
                        "그럼 국물부터 바꾸죠.",
                        "open_final_course_obligation",
                    ),
                ),
                information_revealed_ids=(
                    "guest_engine_room_work",
                    "guest_selects_hot_fire_direction",
                ),
                information_withheld_ids=(
                    "final_guihangtang_result",
                    "doyun_accident_and_contract",
                ),
                state_delta_codes=(
                    "guest_choice:none->hot_fire_direction",
                    "next_course:unknown->guihangtang_direction",
                ),
                tension_delta="first_success_commits_doyun_to_more_personal_dish",
            ),
        ),
        final_state_delta_codes=(
            "doyun_underworld_competence:unknown->demonstrated",
            "first_course:planned->completed_and_consumed",
            "guest_preference:unspoken->hot_fire_direction_selected",
            "girl_role:rule_holder->choice_facilitator",
        ),
        rewards_paid=("dish_and_guest_action_payoff",),
        rewards_deferred=(
            "story_unit_closure",
            "restaurant_operational_accumulation",
            "doyun_return_to_daughter",
        ),
        obligation_kind=EpisodeObligationKind.CONTINUATION,
        obligation=(
            "2화는 첫 코스의 완식 반응과 김문성의 직접 선택을 바탕으로 귀항탕을 완성하고 첫 손님을 결산한다"
        ),
        original_contributions=(
            "첫 8초에 저승 물고기를 제압하는 조리 행동으로 설정 설명 없이 셰프 상품을 판다",
            "맛있는 첫 코스를 진단 도구로 사용해 도윤의 연속 성공과 손님의 선택 변화를 함께 지급한다",
            "소녀의 왕실 허세와 식욕을 망자의 선택권을 지키는 현장 판단으로 연결한다",
        ),
    )
    report = EpisodeScriptVerifier().verify(episode, arc)
    if not report.passed:
        findings = ", ".join(finding.code for finding in report.findings)
        raise ValueError(f"invalid episode candidate: {findings}")
    return episode


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
        "# 삼도식당 1화 글콘티 대본 후보 0.1",
        "",
        "> 상태: 후보. 두 차례 감리와 책임자 승인 전에는 대본 정본이 아니다.",
        "",
        f"- 목표 러닝타임: {episode.target_runtime_seconds}초",
        "- 조리 하이라이트: 120초",
        "- 과거 설명: 사고·딸·계약은 이번 화에서 설명하지 않음",
        "",
        "## 회차 약속",
        "",
        "도윤은 처음 보는 저승 재료로 망각어 불향 맑은국을 완성한다. 김문성은 그릇을 비우고 처음으로 자기 취향을 말한다. 첫 성공이 다음 화의 귀항탕을 연다.",
        "",
    ]
    elapsed = 0
    for scene_number, scene in enumerate(episode.scenes, start=1):
        end = elapsed + scene.duration_seconds
        lines.extend(
            (
                f"## 장면 {scene_number} {_timestamp(elapsed)}-{_timestamp(end)}",
                "",
                f"장소: {location_names[scene.location]}",
                "",
                scene.observable_action,
                "",
            )
        )
        if scene.dialogue:
            lines.append("대사:")
            lines.append("")
            lines.extend(
                f"- {speaker_names[line.speaker_id]}: {line.text}"
                for line in scene.dialogue
            )
            lines.append("")
        else:
            lines.extend(("대사 없음.", ""))
        elapsed = end
    lines.extend(
        (
            "## 다음 화 의무",
            "",
            episode.obligation,
            "",
            "## 승격 경계",
            "",
            "- 1차 구조 감리: 시작 전",
            "- 2차 비판 감리: 시작 전",
            "- 책임자 승인: 시작 전",
            "- 장면 유사성 감리: 평가 전",
            "- 외부 전달: 금지",
            "",
        )
    )
    return "\n".join(lines)


def build_outputs() -> dict[Path, str]:
    if not SOURCE_SCAFFOLD_PATH.exists():
        raise FileNotFoundError(SOURCE_SCAFFOLD_PATH)
    episode = build_episode()
    hil2_builder = _load_hil2_approved_builder()
    arc, receipt, _ = hil2_builder.build_approval()
    distance_status = build_scene_distance_status()
    storyboard = export_storyboard_markdown(episode)
    manifest = {
        "schema_version": "1",
        "work_id": episode.work_id,
        "episode_id": episode.episode_id,
        "revision": episode.revision,
        "status": "candidate",
        "episode_content_sha256": episode.content_sha256,
        "storyboard_sha256": hashlib.sha256(
            storyboard.encode("utf-8")
        ).hexdigest(),
        "parent_arc_content_sha256": arc.content_sha256,
        "parent_arc_approval_receipt_sha256": receipt.receipt_sha256,
        "source_scaffold_sha256": _file_sha256(SOURCE_SCAFFOLD_PATH),
        "scene_distance_status": distance_status["status"],
        "scene_distance_status_sha256": canonical_sha256(distance_status),
        "br0_status": "not_started",
        "br1_status": "not_started",
        "owner_approval": "not_started",
        "external_promotion_allowed": False,
        "next_gate": "br0_br1_review",
    }
    return {
        OUTPUT_ROOT / "episode_script.json": canonical_json(episode) + "\n",
        OUTPUT_ROOT / "episode_001_storyboard_candidate.md": storyboard,
        OUTPUT_ROOT / "scene_distance_status.json": (
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
        print("afterlife_restaurant ep001 candidate is current")
        return 0
    write_outputs(outputs)
    print(OUTPUT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
