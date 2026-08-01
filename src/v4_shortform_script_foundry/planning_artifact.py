"""Deterministic owner-readable HIL 1/2 planning documents."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

from .arc_contract import ArcContract, StoryState
from .canonical import canonical_json
from .canonical_package import CanonicalPackage


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _bullets(values: tuple[str, ...]) -> list[str]:
    return [f"- {value}" for value in values]


def _state_table(state: StoryState) -> list[str]:
    lines = [
        "| axis | subject | value |",
        "| --- | --- | --- |",
    ]
    lines.extend(
        f"| {_cell(entry.axis.value)} | {_cell(entry.subject_id)} | "
        f"{_cell(entry.value)} |"
        for entry in state.entries
    )
    if state.open_questions:
        lines.extend(("", "열린 질문:", *_bullets(state.open_questions)))
    return lines


@dataclass(frozen=True, slots=True)
class PlanningDocument:
    artifact_type: str
    artifact_id: str
    source_content_sha256: str
    payload_json: str
    markdown: str

    def verify(self) -> bool:
        actual = hashlib.sha256(self.payload_json.encode("utf-8")).hexdigest()
        return actual == self.source_content_sha256


def export_hil1_planning_document(
    canonical: CanonicalPackage,
) -> PlanningDocument:
    constraints = canonical.production_constraints
    lines = [
        f"# HIL 1 작품 기획 후보 — {canonical.work_id}",
        "",
        "> 상태: candidate. Owner 승인 전에는 HIL 2 또는 대본 정본이 아니다.",
        "",
        f"- canonical_id: `{canonical.canonical_id}`",
        f"- revision: `{canonical.revision}`",
        f"- content_sha256: `{canonical.content_sha256}`",
        f"- target/platform: {canonical.target_and_platform_hypothesis}",
        "",
        "## 작품 약속",
        "",
        canonical.premise,
        "",
        f"- 주 보상 계층: `{canonical.primary_reward}`",
        f"- 종결 방향: {canonical.ending_direction}",
        "",
        "## 핵심 인물",
        "",
        "| id | 역할 | 목표 | 실패 비용 | 작동 정체성 |",
        "| --- | --- | --- | --- | --- |",
    ]
    lines.extend(
        f"| {_cell(character.character_id)} | "
        f"{_cell(character.narrative_role)} | "
        f"{_cell(character.goal)} | "
        f"{_cell(character.failure_cost)} | "
        f"{_cell(character.operating_identity_invariant_kernel)} |"
        for character in canonical.core_characters
    )
    lines.extend(
        (
            "",
            "### Agency 전환",
            "",
            *(
                f"- `{character.character_id}` "
                f"`{character.initial_agency_state}` → "
                + ", ".join(
                    f"`{transition}`"
                    for transition in character.allowed_agency_transitions
                )
                for character in canonical.core_characters
            ),
            "",
            "## 보상 층위",
            "",
            "| payoff_id | cadence | subject | promise | delivery policy |",
            "| --- | --- | --- | --- | --- |",
        )
    )
    lines.extend(
        f"| {_cell(layer.payoff_id)} | {_cell(layer.cadence.value)} | "
        f"{_cell(layer.subject_id)} | {_cell(layer.promise)} | "
        f"{_cell(layer.delivery_policy)} |"
        for layer in canonical.payoff_layers
    )
    lines.extend(
        (
            "",
            "## 제작 제약",
            "",
            f"- 회차 길이: `{constraints.target_runtime_seconds_min}`–"
            f"`{constraints.target_runtime_seconds_max}`초",
            "- 장면당 주요 인물 상한: "
            f"`{constraints.max_principal_characters_per_scene}`명",
            f"- 행동 중심: `{str(constraints.action_driven).lower()}`",
            f"- 대화 정책: {constraints.dialogue_policy}",
            "- 장면당 대사 줄 상한: "
            f"`{constraints.max_dialogue_lines_per_scene}`"
            if constraints.max_dialogue_lines_per_scene is not None
            else "- 장면당 대사 줄 상한: `not_set`",
            "",
            "## 초기 관계 사실",
            "",
            *_bullets(canonical.initial_relation_facts),
            "",
            "## 세계·연속성 제약",
            "",
            *_bullets(canonical.world_constraints),
            "",
            "## 금지 모순",
            "",
            *_bullets(canonical.forbidden_contradictions),
            "",
            "## 관객 정보 원칙",
            "",
            f"- 객관 사실: {canonical.audience_information.objective_fact_policy}",
            "- 인물 인식: "
            f"{canonical.audience_information.character_perception_policy}",
            *_bullets(canonical.audience_information.asymmetry_principles),
            "",
            "## 창작 범위",
            "",
            "### Anti-goals",
            "",
            *_bullets(canonical.originality.anti_goals),
            "",
            "### Creative latitude",
            "",
            *_bullets(canonical.originality.creative_latitude),
            "",
        )
    )
    return PlanningDocument(
        artifact_type="hil1_planning_document",
        artifact_id=canonical.artifact_id,
        source_content_sha256=canonical.content_sha256,
        payload_json=canonical_json(canonical),
        markdown="\n".join(lines),
    )


def export_hil2_planning_document(arc: ArcContract) -> PlanningDocument:
    lines = [
        f"# HIL 2 아크 기획 후보 — {arc.arc_id}",
        "",
        "> 상태: candidate. Owner 승인 전에는 대본 정본이 아니다.",
        "",
        f"- work_id: `{arc.work_id}`",
        f"- revision: `{arc.revision}`",
        f"- content_sha256: `{arc.content_sha256}`",
        f"- 회차 범위: `{arc.episode_count_min}`–`{arc.episode_count_max}`화",
        "",
        "## 아크 질문과 인과",
        "",
        f"- 극적 질문: {arc.dramatic_question}",
        f"- 핵심 압력: {arc.core_pressure}",
        f"- 핵심 선택: {arc.core_choice}",
        f"- 결과: {arc.consequence}",
        f"- 비가역 변화: {arc.irreversible_change}",
        "",
        "## 시작 상태",
        "",
        *_state_table(arc.state_before),
        "",
        "## 종결 상태",
        "",
        *_state_table(arc.state_after),
        "",
        "## 시도·장애·결과",
        "",
    ]
    if arc.attempt_blocker_chain:
        lines.extend(
            f"- {move.attempt} → {move.blocker} → {move.consequence}"
            for move in arc.attempt_blocker_chain
        )
    else:
        lines.append("- 명시된 chain 없음")
    lines.extend(
        (
            "",
            "## 보상",
            "",
            "### 이번 아크에서 지급",
            "",
            *_bullets(arc.rewards_paid),
            "",
            "### 유예",
            "",
            *_bullets(arc.rewards_deferred),
            "",
            "## 승인 기준",
            "",
            *(
                f"- `{criterion.criterion_id}` {criterion.description}"
                for criterion in arc.acceptance_criteria
            ),
            "",
            "## 연속성 불변값",
            "",
            *_bullets(arc.continuity_invariants),
            "",
            "## 허용 실행 문법",
            "",
            "- Renderer mix: "
            + ", ".join(renderer.value for renderer in arc.renderer_mix),
            "- Beat patterns: "
            + ", ".join(pattern.value for pattern in arc.allowed_beat_patterns),
            "",
        )
    )
    return PlanningDocument(
        artifact_type="hil2_planning_document",
        artifact_id=arc.artifact_id,
        source_content_sha256=arc.content_sha256,
        payload_json=canonical_json(arc),
        markdown="\n".join(lines),
    )
