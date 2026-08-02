#!/usr/bin/env python3
"""Build two unapproved HIL 2 revision-2 candidates for Afterlife Restaurant."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from tools.build_afterlife_restaurant_hil2_arc01_candidate import (  # noqa: E402
    build_hil1_context,
)
from v4_shortform_script_foundry.arc_contract import (  # noqa: E402
    ArcAcceptanceCriterion,
    ArcContract,
    ArcContractVerifier,
    ArcRevisionProposal,
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
    / "arc01_established_service_rev2"
)
CANDIDATE_A_ROOT = OUTPUT_ROOT / "candidate_a_single_episode_closure"
CANDIDATE_B_ROOT = OUTPUT_ROOT / "candidate_b_completion_then_return"
APPROVED_HIL2_ROOT = (
    ROOT
    / "artifacts"
    / "approved"
    / "afterlife_restaurant"
    / "hil2"
    / "arc01_first_service"
)
REPLANNING_PATH = (
    ROOT
    / "artifacts"
    / "candidates"
    / "afterlife_restaurant"
    / "replanning_status_v0.2.md"
)
EPISODE_EXPLORATION_PATH = (
    ROOT
    / "artifacts"
    / "candidates"
    / "afterlife_restaurant"
    / "episode_001_storyboard_exploration_v0.2.md"
)
RESEARCH_PATH = (
    ROOT.parent
    / "shortform_reverse_lab"
    / "30_outputs"
    / "references"
    / "2026-08-02_four_anime_final_script_gate.md"
)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative_to_hq(path: Path) -> str:
    return path.relative_to(ROOT.parent).as_posix()


def _approved_hil2_context() -> dict[str, object]:
    manifest_path = APPROVED_HIL2_ROOT / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["status"] != "owner_approved_hil2":
        raise ValueError("parent HIL 2 is not owner approved")
    if manifest["revision"] != 1:
        raise ValueError("parent HIL 2 revision must be one")
    return manifest


def build_research_receipt() -> dict[str, object]:
    if not RESEARCH_PATH.exists():
        raise FileNotFoundError(RESEARCH_PATH)
    return {
        "receipt_type": "structural_research_input",
        "source_path": _relative_to_hq(RESEARCH_PATH),
        "source_sha256": _file_sha256(RESEARCH_PATH),
        "use_scope": "human_reviewed_structural_hypotheses_only",
        "source_specific_copy_allowed": False,
        "generator_ingest_allowed": False,
        "writeback_to_reverse_lab_allowed": False,
    }


def build_distance_status(artifact_id: str) -> dict[str, object]:
    return {
        "artifact_id": artifact_id,
        "receipt_type": "causal_chain_distance_status",
        "status": "pending_not_evaluated",
        "promotion_allowed": False,
        "reason": (
            "이 revision 2 후보는 아직 독립 거리 감리를 받지 않았다. "
            "내부 HIL 2 비교는 가능하지만 승인본이나 HIL 3 입력으로 승격할 수 없다."
        ),
    }


def _common_state_before() -> StoryState:
    return StoryState(
        entries=(
            StoryStateEntry(
                StoryStateAxis.KNOWLEDGE,
                "도윤",
                "저승 식재료와 조리법을 이미 숙지한 완성형 셰프지만 손님의 수동적 반응을 명시적 선택으로 바꾸는 접객 규칙은 아직 화면에서 증명하지 않았다",
            ),
            StoryStateEntry(
                StoryStateAxis.AUDIENCE_KNOWLEDGE,
                "영업_중_식당",
                "삼도식당이 이미 영업 중이고 도윤과 소녀가 각자 일을 맡는다는 사실만 알며 두 사람이 까다로운 주문을 어떻게 함께 닫는지는 모른다",
            ),
            StoryStateEntry(
                StoryStateAxis.RELATION,
                "도윤_소녀",
                "도윤은 조리하고 소녀는 접객과 규칙을 맡는 동업 관계가 형성되어 있으나 추천 뒤 주문 변경 권한은 명시되지 않았다",
            ),
            StoryStateEntry(
                StoryStateAxis.BELONGING,
                "소녀",
                "소녀는 식당의 실무자지만 첫 화 시청자는 그녀의 판단이 음식 결과를 바꾸는 장면을 아직 보지 못했다",
            ),
            StoryStateEntry(
                StoryStateAxis.RESOURCE,
                "삼도식당",
                "망각어와 두 종류의 완성형 육수는 있으나 손님 취향 선택을 반복 주문으로 기록하는 운영 자산은 없다",
            ),
            StoryStateEntry(
                StoryStateAxis.WORLD_OPERATION,
                "삼도식당",
                "추천 메뉴는 운영되지만 첫 그릇 뒤 손님이 다른 끝맛을 직접 선택하는 절차는 정착되지 않았다",
            ),
            StoryStateEntry(
                StoryStateAxis.PROOF_OR_EQUIVALENT,
                "김문성",
                "추천을 받아들이고 음식에 반응하지만 자기 취향을 말이나 주문 행동으로 확정하지 않았다",
            ),
        ),
        open_questions=(
            "도윤은 실패 없이 두 개의 완성된 맛으로 손님의 선택을 끌어낼 수 있는가",
            "소녀의 접객 판단은 실제 주문과 결산을 바꿀 수 있는가",
            "한 끼의 감정적 변화가 식당의 반복 가능한 운영 자산으로 남는가",
        ),
    )


def _common_acceptance_criteria() -> tuple[ArcAcceptanceCriterion, ...]:
    return (
        ArcAcceptanceCriterion(
            "AC01",
            "첫 화는 이미 영업 중인 삼도식당과 능숙한 도윤의 손기술로 시작하며 사고·딸·계약·개업 경위를 설명하지 않는다",
        ),
        ArcAcceptanceCriterion(
            "AC02",
            "첫 그릇과 대비 그릇은 모두 처음부터 의도된 완성품이다. 도윤의 실패·오답·맛없음을 수정하는 구조로 보이지 않는다",
        ),
        ArcAcceptanceCriterion(
            "AC03",
            "음식은 전경에 놓이고 90~120초 조리 하이라이트 안에서 최소 세 번의 감각적 상태 변화를 보여 준다",
        ),
        ArcAcceptanceCriterion(
            "AC04",
            "손님은 눈물이나 과거 설명 대신 완식·그릇을 붙드는 행동·직접 주문 중 두 가지 이상으로 현재의 변화를 증명한다",
        ),
        ArcAcceptanceCriterion(
            "AC05",
            "소녀는 관찰·서비스 판단·주문 확정 중 하나를 독자적으로 수행해 음식 결과와 결산을 실제로 바꾼다",
        ),
        ArcAcceptanceCriterion(
            "AC06",
            "각 회차는 4~5분, 주요 인물 세 명 이하, 고정 식당 세트, 짧은 대사라는 HIL 1 제약을 지킨다",
        ),
        ArcAcceptanceCriterion(
            "AC07",
            "도윤과 소녀는 부녀 대체나 로맨스가 아닌 공동 주연 동업자이며 현실의 딸은 장기 목적과 후속 시즌 씨앗으로만 남는다",
        ),
        ArcAcceptanceCriterion(
            "AC08",
            "손님의 감정적 결산과 별개로 주문표·결제·서비스 규칙 중 하나가 식당의 다음 영업에 재사용 가능한 흔적으로 남는다",
        ),
        ArcAcceptanceCriterion(
            "AC09",
            "손님 퇴장 뒤 8~12초 안에 소녀가 다음 주문표나 자기 몫을 직접 선택하고 도윤이 직원식 또는 다음 영업 준비로 응답해 두 주연의 반복 동업 행동을 남긴다",
        ),
    )


def _common_invariants() -> tuple[str, ...]:
    return (
        "도윤은 식당을 막 연 초보가 아니라 저승 식재료까지 숙지한 완성형 셰프다",
        "초반 1~3화에서 도윤의 음식은 실패·오답·맛없음으로 긴장을 만들지 않는다",
        "첫 화는 삼도식당의 기원이나 도윤이 저승에 있는 이유를 선설명하지 않는다",
        "추천은 자연스러운 재료와 메뉴 제안이며 손님을 시험하거나 진단 대상으로 선언하지 않는다",
        "소녀는 설정 설명기가 아니라 규칙과 접객 판단을 가진 공동 주연이다",
        "도윤과 소녀는 부녀나 연인이 아닌 동업자다",
        "현실의 딸은 귀환 목적과 후속 시즌 씨앗으로 남고 손님 감정의 지름길로 쓰지 않는다",
        "매화 음식 완성·첫입 반응·현재 행동 변화·식당 운영 흔적을 보존한다",
        "귀여움은 소녀의 무능이나 음식 오염이 아니라 왕실 허세·식욕·빠른 실무 판단의 충돌에서 만든다",
        "참조 작품의 고유 명칭·대사·인물 관계·사건 배열을 가져오지 않는다",
    )


def _common_chain() -> tuple[AttemptBlockerMove, ...]:
    return (
        AttemptBlockerMove(
            "도윤은 그날 상태가 좋은 망각어를 자연스럽게 추천하고 손질을 시작한다",
            "손님은 추천을 받아들이지만 자기 취향을 말하지 않아 주문의 종착점이 보이지 않는다",
            "설명 대신 칼질·불·국물의 세 변화를 연속 성공으로 보여 주고 소녀는 손님의 시선과 손동작을 관찰한다",
        ),
        AttemptBlockerMove(
            "도윤은 맑고 따뜻한 첫 국물을 완성해 낸다",
            "손님은 분명히 맛있게 완식하면서도 빈 그릇을 놓지 않아 감정과 주문이 완전히 닫히지 않는다",
            "도윤은 첫 성공을 부정하지 않고 소녀는 이미 준비된 두 번째 끝맛을 선택할 기회를 연다",
        ),
        AttemptBlockerMove(
            "소녀는 손님의 불을 좇는 반응을 근거로 주문을 열어 두고 도윤에게 대비 그릇을 요청한다",
            "두 번째 그릇이 첫 그릇의 수정처럼 보이면 도윤의 완성형 캐릭터와 첫 보상이 훼손된다",
            "도윤은 처음부터 따로 완성해 둔 깊은 불향 육수를 사용해 서로 다른 두 정답을 병치한다",
        ),
        AttemptBlockerMove(
            "손님은 두 맛을 비교한다",
            "감동 표정만으로는 평생 수동적으로 살아온 상태가 바뀌었다고 증명할 수 없다",
            "손님이 더 깊은 불향과 한 그릇 추가를 직접 선택하고 소녀가 그 선택을 주문표에 확정한다",
        ),
        AttemptBlockerMove(
            "도윤과 소녀는 접객을 결산한다",
            "개별 손님의 감동만 남으면 식당 서사는 다음 화에 축적되지 않는다",
            "결제와 두 단계 끝맛 표기가 남고 소녀의 다음 주문 행동에 도윤이 직원식 또는 준비 행동으로 응답해 서비스 규칙과 동업 관계가 함께 축적된다",
        ),
    )


def _base_arc_kwargs(artifact_id: str) -> dict[str, object]:
    canonical, hil1_manifest = build_hil1_context()
    distance_status = build_distance_status(artifact_id)
    return {
        "work_id": canonical.work_id,
        "arc_id": artifact_id,
        "revision": 2,
        "parent_canonical_content_sha256": canonical.content_sha256,
        "parent_canonical_approval_receipt_sha256": str(
            hil1_manifest["approval_receipt_sha256"]
        ),
        "state_before": _common_state_before(),
        "attempt_blocker_chain": _common_chain(),
        "rewards_paid": (
            "dish_and_guest_action_payoff",
            "story_unit_closure",
            "restaurant_operational_accumulation",
        ),
        "rewards_deferred": ("doyun_return_to_daughter",),
        "acceptance_criteria": _common_acceptance_criteria(),
        "production_constraints": canonical.production_constraints,
        "continuity_invariants": _common_invariants(),
        "renderer_mix": (
            RendererKind.COMPETENCE,
            RendererKind.ATTACHMENT_SAFETY,
            RendererKind.RESOURCE,
            RendererKind.SELECTION,
        ),
        "allowed_beat_patterns": (
            BeatPatternKind.SUSPENSE_INFORMATION_GAP,
            BeatPatternKind.SELECTION_SAFETY,
            BeatPatternKind.EVIDENCE_REVERSAL,
        ),
        "causal_chain_distance_receipt_sha256": canonical_sha256(
            distance_status
        ),
    }


def build_candidate_a() -> ArcContract:
    artifact_id = "afterlife_restaurant:arc01:established_service_single_closure"
    kwargs = _base_arc_kwargs(artifact_id)
    arc = ArcContract(
        **kwargs,
        state_after=StoryState(
            entries=(
                StoryStateEntry(
                    StoryStateAxis.KNOWLEDGE,
                    "도윤",
                    "완성된 두 맛을 병치하면 손님의 말하지 않은 반응을 자기 선택으로 바꿀 수 있음을 운영 경험으로 확인했다",
                ),
                StoryStateEntry(
                    StoryStateAxis.AUDIENCE_KNOWLEDGE,
                    "영업_중_식당",
                    "도윤은 처음부터 두 정답을 준비하는 셰프이고 소녀는 손님 반응을 주문으로 확정하는 실무자임을 확인했다",
                ),
                StoryStateEntry(
                    StoryStateAxis.RELATION,
                    "도윤_소녀",
                    "도윤의 조리 결정과 소녀의 서비스 결정이 하나의 주문을 닫고 손님 퇴장 뒤 다음 영업 행동까지 맞물리는 동업 절차로 연결됐다",
                ),
                StoryStateEntry(
                    StoryStateAxis.BELONGING,
                    "소녀",
                    "소녀의 관찰과 주문 확정 권한이 첫 화 결과를 바꾸고 자기 몫과 다음 주문을 직접 선택하는 필수 노동으로 증명됐다",
                ),
                StoryStateEntry(
                    StoryStateAxis.RESOURCE,
                    "삼도식당",
                    "결제와 두 단계 끝맛 주문표가 남아 기존 재료를 다른 손님에게 제안할 수 있는 운영 자산이 생겼다",
                ),
                StoryStateEntry(
                    StoryStateAxis.WORLD_OPERATION,
                    "삼도식당",
                    "첫 완성 그릇 뒤에도 손님이 다른 끝맛을 직접 선택할 수 있는 반복 서비스 규칙이 정착됐다",
                ),
                StoryStateEntry(
                    StoryStateAxis.PROOF_OR_EQUIVALENT,
                    "김문성",
                    "첫 그릇을 완식한 뒤 더 깊은 불향과 한 그릇 추가를 직접 주문하고 결제해 자기 취향을 현재 행동으로 확정했다",
                ),
            ),
            open_questions=(
                "새 서비스 규칙은 다른 유형의 손님에게도 통하는가",
                "제한된 공급으로 대비 그릇을 계속 준비할 수 있는가",
                "도윤과 소녀의 주문 권한은 더 까다로운 규칙 앞에서 어디까지 나뉘는가",
            ),
        ),
        dramatic_question=(
            "이미 능숙한 도윤과 소녀는 주는 대로 받던 손님을 한 회 안에 자기 맛을 직접 주문하는 사람으로 바꾸고 그 변화를 식당 규칙으로 남길 수 있는가"
        ),
        core_pressure=(
            "첫 그릇은 반드시 맛있게 성공해야 하지만 손님의 수동적인 태도는 맛만으로 자동 해소되지 않는다. 두 번째 맛은 수정이 아니라 선택지여야 하고 소녀의 판단도 결과를 바꿔야 한다"
        ),
        core_choice=(
            "도윤은 처음부터 완성해 둔 두 육수를 한 정답과 오답이 아닌 서로 다른 정답으로 내고, 소녀는 손님의 비언어 반응을 근거로 주문을 열어 두었다가 손님의 직접 선택으로 확정한다"
        ),
        consequence=(
            "손님은 한 회 안에 자기 취향을 직접 주문하고 결제하며 퇴장한다. 삼도식당에는 두 단계 끝맛 서비스와 주문표가 남고, 소녀의 다음 행동에 도윤이 응답하는 짧은 동업 결산 뒤 새 손님으로 완전히 시작할 수 있다"
        ),
        irreversible_change=(
            "삼도식당은 손님의 직접 선택으로 추천을 갱신하는 반복 서비스 규칙과 그 규칙을 다음 영업으로 옮기는 도윤·소녀의 상호 행동을 보유한다"
        ),
        episode_count_min=1,
        episode_count_max=2,
        original_contributions=(
            "한 그릇의 실패와 수정이 아니라 두 개의 완성된 정답을 비교하게 해 완성형 셰프의 긴장을 선택 문제로 전환한다",
            "손님의 빈 그릇을 붙드는 행동을 소녀가 포착하고 주문 확정 권한으로 연결해 공동 주연성을 증명한다",
            "손님의 직접 추가 주문이 감정적 결산과 식당 운영 자산을 동시에 만든다",
            "첫 화에서 손님 이야기를 완전히 닫고 다음 화가 같은 손님에게 의존하지 않게 한다",
            "손님 퇴장 뒤 소녀의 주문표 또는 자기 몫 선택에 도윤이 응답하는 8~12초 코다로 고정 주연의 다음 영업을 계약한다",
        ),
    )
    _verify(arc)
    return arc


def build_candidate_b() -> ArcContract:
    artifact_id = "afterlife_restaurant:arc01:completion_then_return"
    kwargs = _base_arc_kwargs(artifact_id)
    arc = ArcContract(
        **kwargs,
        state_after=StoryState(
            entries=(
                StoryStateEntry(
                    StoryStateAxis.KNOWLEDGE,
                    "도윤",
                    "완성된 두 맛은 손님의 첫 선택뿐 아니라 다음 방문의 구체적인 주문까지 만들 수 있음을 확인했다",
                ),
                StoryStateEntry(
                    StoryStateAxis.AUDIENCE_KNOWLEDGE,
                    "영업_중_식당",
                    "도윤과 소녀가 한 끼를 완결한 뒤에도 손님이 의무가 아닌 욕망으로 돌아오게 만드는 팀임을 확인했다",
                ),
                StoryStateEntry(
                    StoryStateAxis.RELATION,
                    "도윤_소녀",
                    "도윤의 조리와 소녀의 접객이 첫 주문, 식후 다음 영업 행동, 재방문 접수와 새 주문을 닫는 동업 절차가 됐다",
                ),
                StoryStateEntry(
                    StoryStateAxis.BELONGING,
                    "소녀",
                    "소녀가 재방문 허용 조건과 새 주문 접수를 책임지는 운영자로 증명됐다",
                ),
                StoryStateEntry(
                    StoryStateAxis.RESOURCE,
                    "삼도식당",
                    "첫 결제와 두 단계 끝맛 주문표에 더해 재방문 예약과 두 번째 결제가 운영 자산으로 남았다",
                ),
                StoryStateEntry(
                    StoryStateAxis.WORLD_OPERATION,
                    "삼도식당",
                    "완결된 식사 뒤 손님의 자발적 재방문을 제한적으로 허용하고 새 주문으로 취급하는 규칙이 생겼다",
                ),
                StoryStateEntry(
                    StoryStateAxis.PROOF_OR_EQUIVALENT,
                    "김문성",
                    "첫 화에 자기 취향을 주문해 완결한 뒤 다음 회에 스스로 돌아와 이전과 다른 구체적인 주문을 선택했다",
                ),
            ),
            open_questions=(
                "재방문 허용은 마지막 식사의 희소성을 훼손하지 않고 어디까지 확장할 수 있는가",
                "다른 손님의 재방문 욕망은 어떤 운영 비용을 만드는가",
                "도윤과 소녀는 재방문 허용 권한을 누구에게 둘 것인가",
            ),
        ),
        dramatic_question=(
            "도윤과 소녀는 첫 화에 한 끼를 완전히 결산하면서도 손님이 의무가 아닌 자기 욕망으로 다시 찾아오는 두 번째 주문을 만들 수 있는가"
        ),
        core_pressure=(
            "첫 화의 감정적 결산은 스스로 완전해야 한다. 재방문이 첫 화의 미완성을 수습하는 장치로 보이면 안 되며 저승식당의 마지막 식사 희소성도 훼손해서는 안 된다"
        ),
        core_choice=(
            "도윤과 소녀는 첫 화에 손님의 선택과 결제를 완전히 닫고, 두 번째 화에는 같은 손님이 이전 문제를 반복하지 않은 채 새 욕망과 구체적 주문을 들고 돌아온 경우만 별도 접객으로 받아들인다"
        ),
        consequence=(
            "손님은 첫 식사와 독립된 두 번째 주문을 자발적으로 완식한다. 식당에는 제한적 재방문 규칙과 예약 흔적이 생기지만 마지막 식사의 희소성을 지키는 세계 규칙을 추가로 승인해야 한다"
        ),
        irreversible_change=(
            "삼도식당은 한 번의 위로 장소를 넘어 손님이 자기 욕망으로 다시 선택할 수 있는 장소가 되고 재방문 접수 규칙을 보유한다"
        ),
        episode_count_min=2,
        episode_count_max=3,
        original_contributions=(
            "첫 화의 완결을 훼손하지 않은 채 자발적 재방문을 별개의 욕망 증거로 사용한다",
            "같은 손님의 두 주문을 대비해 수동적 수용에서 구체적 선택으로의 변화를 반복 행동으로 증명한다",
            "소녀에게 재방문 허용과 접수 권한을 부여해 세계 규칙과 실무 판단을 동시에 맡긴다",
            "재방문 예약을 식당의 관계 자산으로 만들되 마지막 식사의 희소성 훼손을 명시적 승인 위험으로 남긴다",
        ),
    )
    _verify(arc)
    return arc


def _verify(arc: ArcContract) -> None:
    canonical, _ = build_hil1_context()
    report = ArcContractVerifier().verify(arc, canonical)
    if not report.passed:
        findings = ", ".join(finding.code for finding in report.findings)
        raise ValueError(f"invalid HIL 2 revision-2 candidate: {findings}")


def build_revision_proposal(arc: ArcContract) -> ArcRevisionProposal:
    parent = _approved_hil2_context()
    return ArcRevisionProposal(
        work_id=arc.work_id,
        arc_id=arc.arc_id,
        proposed_revision=2,
        parent_arc_content_sha256=str(parent["arc_content_sha256"]),
        reason=(
            "승인된 revision 1의 폐점 주방·첫 영업·낯선 재료 적응을 재개방하고, 사용자 결정인 이미 영업 중인 식당·완성형 도윤·초반 무패·선설명 금지를 첫 아크의 시작 상태로 반영한다"
        ),
        affected_nodes=(
            "state_before.knowledge.doyun",
            "state_before.world_operation.samdo_restaurant",
            "dramatic_question",
            "attempt_blocker_chain",
            "episode_allocation",
            "guest_closure",
            "girl_service_authority",
            "restaurant_operational_residue",
        ),
        continuity_risks=(
            "폐점 식당을 일으키는 기존 성장선을 첫 화에서 사용할 수 없어 제한된 메뉴와 공급 압력으로 장기 축적을 다시 보여 줘야 한다",
            "도윤과 소녀의 관계가 이미 작동하므로 관계 변화는 역할 소개가 아니라 권한과 판단의 축적으로 설계해야 한다",
            "기존 HIL 2 승인본은 이 후보가 소유자 승인을 받기 전까지 계속 권위본이다",
        ),
        reward_impact=(
            "조리 가능성 증명 보상을 삭제하고 완성형 조리 쾌감·손님의 직접 선택·공동 운영 규칙 축적으로 보상을 앞당긴다"
        ),
        closure_or_cliff_impact=(
            "첫 음식의 실패나 미완성 주문을 다음 화로 넘기지 않는다. 후보 A는 한 회에 손님을 완결하고 후보 B도 첫 화를 닫은 뒤 별개의 자발적 재방문만 추가한다"
        ),
    )


def _episode_allocation_a() -> str:
    return """# 후보 A 회차 배분 — 한 회 완결 우선

상태: `candidate / owner approval not started`

## 기본 배분

- **1화(필수, 4~5분):** 능숙한 망각어 손질 → 맑은 첫 국물의 명백한 성공 → 소녀가 손님의 불을 좇는 반응을 포착 → 처음부터 준비된 깊은 불향 국물 제시 → 손님이 더 강한 끝맛과 한 그릇 추가를 직접 주문 → 결제와 두 단계 끝맛 주문표를 남기고 퇴장 → 소녀가 다음 주문표나 자기 몫을 고르고 도윤이 직원식 또는 다음 준비로 응답.
- **2화(선택):** 새 손님이 새 서비스 규칙을 다른 방식으로 사용한다. 김문성의 감정 문제를 다시 열거나 그의 재방문에 의존하지 않는다.

## 잠금

- 1화만으로 음식 보상, 손님 행동 변화, 감정 결산, 식당 운영 흔적이 모두 지급된다.
- 두 번째 국물은 수정본이 아니라 처음부터 완성된 대비 메뉴다.
- 손님 퇴장 뒤 8~12초 코다는 부녀·로맨스가 아니라 두 주연의 반복 동업 행동만 남긴다.
- 대사와 샷은 HIL 3에서 작성한다. 이 문서는 사건 기능과 상태 변화만 잠근다.
"""


def _episode_allocation_b() -> str:
    return """# 후보 B 회차 배분 — 완결 뒤 자발적 재방문

상태: `candidate / owner approval not started`

## 기본 배분

- **1화(필수, 4~5분):** 후보 A와 같은 완결 기준을 지킨다. 맑은 첫 국물과 깊은 불향 국물은 모두 성공하고, 김문성은 자기 주문과 결제를 끝낸 뒤 퇴장한다.
- **2화(기본, 4~5분):** 김문성이 이전 문제의 수습이 아닌 새 욕망과 구체적 주문을 들고 자발적으로 돌아온다. 소녀가 재방문 허용 조건과 접수를 판단하고 도윤은 이전 음식과 다른 완성형 한 끼를 낸다.
- **3화(선택):** 재방문 규칙의 비용이나 제한을 새 손님 사례로 검증한다. 김문성의 첫 화 결산은 다시 열지 않는다.

## 잠금과 위험

- 1화는 독립 완결이어야 하며 2화를 보지 않아도 보상 누락이 없어야 한다.
- 재방문은 미련 때문에 갇힌 상태가 아니라 식당과 음식에 대한 새 선택이어야 한다.
- 이 안은 `마지막 식사`의 희소성과 손님의 재방문 권리를 새로 잠가야 하므로 후보 A보다 세계관 승인 비용이 높다.
- 대사와 샷은 HIL 3에서 작성한다. 이 문서는 사건 기능과 상태 변화만 잠근다.
"""


def _comparison_markdown(
    arc_a: ArcContract,
    arc_b: ArcContract,
) -> str:
    return f"""# 저승식당 HIL 2 revision 2 후보 비교

상태: `candidate set / owner approval not started`
기존 권위본: `HIL 2 revision 1 — arc01_first_service`
자동 승격: `금지`

## 공통 잠금

- 삼도식당은 이미 영업 중이다.
- 도윤은 저승 식재료까지 아는 완성형 셰프이며 초반 1~3화 음식은 실패하지 않는다.
- 첫 화는 도윤의 사고·딸·계약·개업 경위를 선설명하지 않는다.
- 음식과 감각적 조리 변화가 전경이고, 감정은 먹은 뒤의 직접 행동으로 결산한다.
- 소녀는 설정 설명기가 아니라 접객 판단으로 결과를 바꾸는 공동 주연이다.
- 도윤과 소녀는 부녀 대체나 로맨스가 아닌 동업자다.

## 구조 비교

| 항목 | 후보 A — 한 회 완결 우선 | 후보 B — 완결 뒤 재방문 |
|---|---|---|
| 계약 ID | `{arc_a.arc_id}` | `{arc_b.arc_id}` |
| 회차 밴드 | 1~2화, 기본 1화 | 2~3화, 기본 2화 |
| 1화 보상 | 음식·선택·결제·운영 흔적까지 전부 지급 | 후보 A와 동일하게 전부 지급 |
| 후속 구조 | 다음 화는 새 손님으로 독립 시작 가능 | 같은 손님이 새 욕망과 주문으로 자발적 재방문 |
| 장점 | 파일럿 밀도, 게스트 순환, 세계관 설명 부담 최소 | 반복 시청 애착, 손님 캐릭터 축적, 관계 자산 강화 |
| 핵심 위험 | 장기 감정선이 얕아질 수 있음 | 마지막 식사 희소성과 재방문 권리까지 새로 승인해야 함 |
| 제작 부담 | 낮음 | 중간 — 같은 손님 자산 재사용 이점은 있으나 세계 규칙 검증 필요 |

## Foundry 추천

**후보 A를 HIL 2 소유자 검토 1순위로 추천한다.** 4~5분 파일럿에서 요리 성공, 손님 변화, 소녀의 실무 판단, 식당의 축적을 한 번에 증명하고, 손님 퇴장 뒤 8~12초 동업 코다로 고정 주연의 다음 행동까지 남기면서 다음 화의 자유도를 보존한다. 후보 B는 작품의 핵심 약속이 `마지막 한 끼`보다 `다시 찾고 싶은 식당`에 가깝다고 결정할 때 선택할 수 있다.

이 추천은 승인이 아니다. 소유자가 하나를 승인하기 전까지 revision 1 승인본이 계속 권위본이며, 두 후보 모두 거리 감리와 HIL 3 진입이 막혀 있다.
"""


def _candidate_outputs(
    root: Path,
    arc: ArcContract,
    allocation: str,
    default_allocation: int,
) -> dict[Path, str]:
    _, hil1_manifest = build_hil1_context()
    parent_hil2 = _approved_hil2_context()
    proposal = build_revision_proposal(arc)
    distance_status = build_distance_status(arc.artifact_id)
    planning_document = export_hil2_planning_document(arc)
    if not planning_document.verify():
        raise ValueError(f"planning document does not verify: {arc.artifact_id}")
    planning = planning_document.markdown.rstrip("\n") + "\n"
    allocation = allocation.rstrip("\n") + "\n"
    proposal_json = canonical_json(proposal) + "\n"
    distance_json = canonical_json(distance_status) + "\n"
    manifest = {
        "schema_version": "1",
        "work_id": arc.work_id,
        "artifact_id": arc.artifact_id,
        "revision": 2,
        "status": "candidate",
        "owner_approval": "not_started",
        "external_promotion_allowed": False,
        "supersedes_parent_only_if_owner_approved": True,
        "hil3_status": "blocked_until_hil2_revision_owner_approval",
        "next_gate": "owner_hil2_revision_review",
        "episode_count_band": [arc.episode_count_min, arc.episode_count_max],
        "default_review_allocation": default_allocation,
        "parent_hil1_content_sha256": arc.parent_canonical_content_sha256,
        "parent_hil1_approval_receipt_sha256": hil1_manifest[
            "approval_receipt_sha256"
        ],
        "parent_hil2_revision": parent_hil2["revision"],
        "parent_hil2_content_sha256": parent_hil2["arc_content_sha256"],
        "parent_hil2_approval_receipt_sha256": parent_hil2[
            "approval_receipt_sha256"
        ],
        "arc_contract_sha256": arc.content_sha256,
        "arc_planning_sha256": hashlib.sha256(
            planning.encode("utf-8")
        ).hexdigest(),
        "revision_proposal_sha256": proposal.content_sha256,
        "episode_allocation_sha256": hashlib.sha256(
            allocation.encode("utf-8")
        ).hexdigest(),
        "causal_chain_distance_status": distance_status["status"],
        "causal_chain_distance_status_sha256": canonical_sha256(
            distance_status
        ),
        "research_receipt_sha256": canonical_sha256(
            build_research_receipt()
        ),
    }
    return {
        root / "arc_contract.json": canonical_json(arc) + "\n",
        root / "arc_planning.md": planning,
        root / "revision_proposal.json": proposal_json,
        root / "episode_allocation.md": allocation,
        root / "causal_chain_distance_status.json": distance_json,
        root / "manifest.json": canonical_json(manifest) + "\n",
    }


def build_outputs() -> dict[Path, str]:
    for path in (
        APPROVED_HIL2_ROOT / "manifest.json",
        REPLANNING_PATH,
        EPISODE_EXPLORATION_PATH,
        RESEARCH_PATH,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    arc_a = build_candidate_a()
    arc_b = build_candidate_b()
    outputs = {}
    outputs.update(
        _candidate_outputs(
            CANDIDATE_A_ROOT,
            arc_a,
            _episode_allocation_a(),
            1,
        )
    )
    outputs.update(
        _candidate_outputs(
            CANDIDATE_B_ROOT,
            arc_b,
            _episode_allocation_b(),
            2,
        )
    )
    comparison = _comparison_markdown(arc_a, arc_b).rstrip("\n") + "\n"
    receipt = build_research_receipt()
    set_manifest = {
        "schema_version": "1",
        "work_id": arc_a.work_id,
        "artifact_id": "afterlife_restaurant:arc01:established_service_revision2_candidate_set",
        "status": "candidate_set",
        "owner_approval": "not_started",
        "external_promotion_allowed": False,
        "recommendation_is_approval": False,
        "recommended_for_owner_review": arc_a.artifact_id,
        "hil3_status": "blocked_until_one_hil2_revision_candidate_is_owner_approved",
        "parent_hil2": {
            "revision": _approved_hil2_context()["revision"],
            "arc_content_sha256": _approved_hil2_context()[
                "arc_content_sha256"
            ],
            "approval_receipt_sha256": _approved_hil2_context()[
                "approval_receipt_sha256"
            ],
        },
        "candidate_contracts": {
            arc_a.artifact_id: arc_a.content_sha256,
            arc_b.artifact_id: arc_b.content_sha256,
        },
        "comparison_sha256": hashlib.sha256(
            comparison.encode("utf-8")
        ).hexdigest(),
        "research_receipt_sha256": canonical_sha256(receipt),
        "discussion_inputs": {
            _relative_to_hq(REPLANNING_PATH): _file_sha256(REPLANNING_PATH),
            _relative_to_hq(EPISODE_EXPLORATION_PATH): _file_sha256(
                EPISODE_EXPLORATION_PATH
            ),
        },
    }
    outputs[OUTPUT_ROOT / "comparison.md"] = comparison
    outputs[OUTPUT_ROOT / "research_input_receipt.json"] = (
        canonical_json(receipt) + "\n"
    )
    outputs[OUTPUT_ROOT / "manifest.json"] = canonical_json(set_manifest) + "\n"
    return outputs


def check_outputs(outputs: dict[Path, str]) -> tuple[str, ...]:
    findings: list[str] = []
    for path, expected in outputs.items():
        if not path.exists():
            findings.append(f"missing:{path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8") != expected:
            findings.append(f"stale:{path.relative_to(ROOT)}")
    if OUTPUT_ROOT.exists():
        actual_files = {path for path in OUTPUT_ROOT.rglob("*") if path.is_file()}
        for path in sorted(actual_files - set(outputs)):
            findings.append(f"unexpected:{path.relative_to(ROOT)}")
    return tuple(findings)


def write_outputs(outputs: dict[Path, str]) -> None:
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
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
        print("afterlife_restaurant HIL 2 revision-2 candidates are current")
        return 0
    write_outputs(outputs)
    print(OUTPUT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
