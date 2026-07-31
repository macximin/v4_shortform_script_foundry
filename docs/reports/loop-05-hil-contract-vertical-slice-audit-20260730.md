# Loop 05 — HIL contract vertical slice audit

Date: 2026-07-30
Status: implemented contract slice, no model call, no real owner promotion

## Decision

오리지널 숏폼 대본 생성의 승인 해상도를 세 단계로 구현한다.

```text
HIL 1  Canonical Package / 작품 약속
HIL 2  Arc Contract / 상태 전환
HIL 3  Episode Script / 완성 회차 대본
```

기존 `3회 × Hook/Pressure/Proof/Reward-Cliff` 코어는 삭제하지 않는다.
EP07 evidence-reversal 계약 canary와 회귀 기준으로 유지한다. 다만 보편 서사
공식이나 HIL 정본으로 사용하지 않는다.

## Implemented modules

### `approval`

- content hash와 approval receipt hash 분리
- HIL 1/2/3 gate ID
- `candidate`, `in_review`, `approved`, `rejected`, `superseded`,
  `stale`, `blocked`
- immutable revision
- owner 역할만 승인 가능
- 새 상위 revision 승인 시 parent content/receipt chain을 따라 하위 stale 전파
- parent hash가 맞는 첫 미완 승인점 resume boundary

Receipt hash는 결정 이력의 무결성을 검증한다. 별도 전자서명이 없으므로 실제
사람 신원 인증 수단이라고 주장하지 않는다.

### `canonical_package`

HIL 1은 다음을 잠근다.

- 주인공 goal과 failure cost
- operating identity의 invariant kernel
- initial agency state와 allowed transition range
- 객관 사실, 인물별 인식과 관객 정보 비대칭 원칙
- 주 보상과 payoff promise
- 초기 관계 사실과 금지 모순
- Renderer reward hierarchy와 최소 두 개의 allowed range
- originality axes, anti-goals, creative latitude와 premise-distance receipt

사건 배열, 정확한 비트, 회차별 agency 행동과 reveal schedule 필드는 없다.

### `arc_contract`

HIL 2는 다음을 가진다.

- multi-axis Story State:
  `knowledge`, `audience_knowledge`, `relation`, `status`, `belonging`,
  `safety`, `proof_or_equivalent`
- start/end state
- dramatic question, pressure, choice, consequence
- 선택형 attempt/blocker chain
- paid/deferred reward
- irreversible change와 acceptance criteria
- 고정값이 아닌 episode count band
- Renderer mix와 allowed Beat Pattern
- causal-chain distance receipt
- 승인본 overwrite가 아닌 `ArcRevisionProposal`

### `beat_patterns`

다음 네 패턴을 선택지로 구현했다.

- `evidence_reversal`
- `suspense_information_gap`
- `competence_recognition`
- `selection_safety`

패턴은 Renderer와 호환성을 검증하지만 어느 하나도 모든 회차에 강제하지 않는다.

### `episode_script`

HIL 3 후보는 실제 대사·지문 역할을 하는 다음 계약을 가진다.

- 촬영 가능한 scene location, purpose와 observable action
- 의미 있는 선택·행동·이전 선택 결과·외부 압박 결과 중 하나의 causal role
- primary/secondary Renderer
- scene runtime과 dialogue
- revealed/withheld information
- state/tension delta
- paid/deferred reward
- `closure` 또는 `continuation` obligation
- scene-distance receipt와 original contribution

생성 결과는 항상 `candidate`다. Arc content hash가 stale이거나 Arc 밖의
Renderer·Beat Pattern·reward를 쓰면 hard failure다.

### `creative_review`

HIL 3 promotion readiness를 다음 순서로 분리했다.

```text
Episode Script hard verification
  -> common creative absolute floor
  -> 2–4 structurally distinct candidate set
  -> producer-distinct and mutually independent BR0 / BR1
  -> pairwise comparison
  -> owner HIL 3 approval receipt
```

공통 creative floor:

- causal coherence
- character intentionality
- scene necessity
- visual execution
- work specificity

후보 구조 hash는 Beat Pattern, obligation, scene purpose, causal role,
Renderer, runtime과 state delta에 묶인다. 단어와 original-contribution
라벨만 바꾼 후보는 구조적으로 다른 후보로 인정하지 않는다.

### `pipeline`

기존 pipeline은 Script Packet hard verification 또는 Functional Draft hard
verification이 실패하면 즉시 `PipelineHardFailure`를 발생시킨다. 실패한
packet이 draft나 다음 회차의 입력으로 진행하지 않는다.

## Tests

Loop 05 전용 테스트는 다음을 포함한다.

- HIL 1 단일 Renderer lock 거부
- HIL 2 Canonical content hash binding
- Canonical 밖 Renderer mix 거부
- multi-episode 고정 회차 수 거부
- Arc 수정의 새 revision proposal
- content hash와 approval receipt 분리
- non-owner 승인 거부
- request-changes의 자동 승인 방지
- 새 HIL 1 승인 시 HIL 2·3 stale 전파
- 새 parent chain의 첫 미완 HIL 2 resume
- 4비트가 아닌 competence-recognition 완성 회차 통과
- 자동 승인과 stale Arc hash 거부
- producer/BR reviewer 충돌 거부
- creative floor 미달 거부
- 단어만 바꾼 cosmetic 후보 세트 거부
- hard + creative + pairwise + owner receipt의 HIL 3 readiness
- Script Packet hard failure 뒤 Draft Adapter 미호출

검증 결과:

```text
59 tests
ruff: changed scope pass
mypy: 7 changed source modules pass
compileall: pass
wheel: v4_shortform_script_foundry-0.2.0-py3-none-any.whl build pass
git diff --check: pass
```

## Boundary

구현하지 않은 것:

- Creative Writer 모델 호출
- 실제 작품 데이터
- 원천 영상·대사 ingest
- 실제 source-distance 계산기
- 실제 owner receipt
- 승인 대본·프리비즈·외부 배포
- LangGraph, Temporal, Pydantic, Outlines 또는 Guardrails 의존성

테스트의 owner receipt와 완성 대본은 `synthetic fixture`다. 실제 승인이나
제작 후보로 사용할 수 없다.

## Next

다음 구현은 모델부터 연결하지 않는다.

1. HIL 1/2 JSON artifact export와 owner review UI 입력 형식
2. legacy Functional Draft와 새 selectable scaffold 사이 adapter
3. Creative Writer 입력·출력 adapter
4. 권리 경계의 실제 source-distance receipt
5. 같은 HIL 1·2에서 구조적으로 다른 두 후보를 생성하는 canary
6. 독립 BR0/BR1 비교 후 owner가 선택하는 첫 실제 HIL 3
