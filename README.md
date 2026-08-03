# v4_shortform_script_foundry

Renderer Router 기반 숏폼 스토리보드 대본 생성 코어를 clean-room으로 개발하는 독립 edge repo다.

현재는 **owner-readable planning + Creative Writer Adapter + production-text
vertical slice** 상태다. 기존 deterministic functional-draft canary를 보존하면서,
HIL 1/2/3 계약과 무효화·재개·품질 비교, pluggable writer backend의 strict
structured output 검증, Eval source-distance receipt의 수동 hash-bound
반입, 승인 대본 이후의 사람용 촬영 표면·촬영 주석·승인 gate·artifact DAG를
구현했다.

아직 실제 모델/API backend, 실제 owner 승인 대본과 외부 배포 기능은 없다.
첫 실제 작품의 세 HIL 1 비교 후보와 초기 HIL 1·2 승인 산출물은 계약 검증 및
변경 이력으로 보존한다. 현재 `afterlife_restaurant`의 집필 기준은 2026-08-03
owner가 잠근 사람용 제1~3화와 시즌 1 A-Rail/B-Rail 가설이다. 기존 구조화
캐노니컬은 현재 원고와 어긋나므로 새 원고 입력으로 사용하지 않으며, 캐노니컬
v2 구조화는 별도 후속 단계다. premise-distance 검사와 외부 제작 전달 승인은
계속 닫혀 있다. 테스트의 완성 대본은 계약 검증용 합성 fixture다.

## Core flow

```text
Fact Ledger
  + Approved Genre Grammar Packet
  -> HIL 1 Canonical Package
  -> owner-readable HIL 1 planning document
  -> Renderer Router + HIL 2 state-transition Arc Contract
  -> owner-readable HIL 2 planning document
  -> selectable Beat Pattern + writer scaffold
  -> Creative Writer Adapter -> unscreened Writer Draft
  -> independent Eval source-distance receipt
  -> hash-bound Episode Script candidate
  -> Episode Script hard verifier
  -> creative absolute floor
  -> independent BR0 / BR1 pairwise review
  -> HIL 3 Owner Approval
  -> stable Episode Script Text atoms
  -> deterministic Human Production Surface -> P0
  -> separate Production Annotations -> P1
  -> candidate Production Text Package -> P2
```

현재 핵심 경계는 다음과 같다.

- `fact_ledger`: 확정 사실, 주장, 추정과 미지정을 분리한다.
- `genre_grammar`: 근거와 owner content hash가 있는 장르 문법 packet을 소유한다.
- `grammar_import`: reverse lab의 승인된 추상 blueprint만 독립 hash envelope로
  수동 반입한다.
- `renderer_router`: 확정 fact tag가 허용하는 위협·증거·보상 렌더러를 선택한다.
- `series_plan`: deterministic canary용 장르 중립 보상 곡선을 만든다. 실제
  작품의 HIL 1/2 기획 정본이 아니다.
- `episode_state`: 실제/인식 지위, 지식 지도, 증거 단계와 보상 유예를 관리한다.
- `script_packet`: 작가 어댑터에 넘길 얇은 회차 계약을 소유한다.
- `verification`: 사실·연속성·렌더러 정합성과 레퍼런스 거리를 검증한다.
- `draft_script`: 장면 목적, 관찰 행동, 대사 기능, 정보 공개·유예, 비트별
  상태 delta와 cliff obligation을 소유한다.
- `draft_verification`: 정보 과적재·선공개, 상태 불일치, 클리프 누락,
  자동 승격과 source-distance 위반을 차단한다.
- `approval`: content hash와 승인 receipt를 분리하고 revision, stale,
  resume boundary와 owner-only 승격을 소유한다.
- `canonical_package`: HIL 1 작품 약속, 핵심 인물 1–3명의 작동 정체성,
  회차·아크·시즌·미래 떡밥 보상 층위, 제작 제약, 관객 정보 원칙과
  Renderer 범위를 소유한다.
- `arc_contract`: HIL 2 상태전환, 다차원 Story State, episode count band와
  revision proposal을 소유한다. Story State는 resource와 world operation을
  포함하며 HIL 1 제작 제약을 그대로 결합한다.
- `planning_artifact`: 정확한 HIL 1/2 canonical JSON hash에 결합된
  owner-readable Markdown 기획서를 결정론적으로 출력한다.
- `beat_patterns`: 증거 역전, suspense 정보 격차, 능력 인정, 선택·안전
  패턴을 선택지로 제공하며 어느 하나도 보편 공식으로 만들지 않는다.
- `episode_script`: HIL 3 완성 회차 대본 후보와 hard verifier를 소유한다.
  장면별 주요 인물 수, 러닝타임과 선택형 대사 줄 상한을 제작 제약으로
  검증한다.
- `episode_script_text`: owner 승인 대본을 안정된 scene/atom 순서와 hash로
  고정한다. status 변경은 내용 hash를 바꾸지 않는다.
- `production_surface`: 촬영고 사람 표면을 결정론적으로 렌더링하고 모든 atom의
  순서·문구 동치를 P0에서 검증한다.
- `production_annotation`: CAMERA/SHOT/INSERT/EDIT를 대본과 분리된 hash-bound
  주석으로 소유한다.
- `story_change_request`: 제작 감리에서 발견된 행동·대사·순서 변경을 몰래
  반영하지 않고 owner 결정으로 되돌린다.
- `production_gate`와 `production_package`: P0/P1 exact receipt가 있는 경우에만
  후보 제작 텍스트 묶음을 만들며 외부 전달은 자동 승인하지 않는다.
- `artifact_graph`: 대화형 작업이 어느 노드를 만들고 무엇을 stale로 만드는지
  DAG로 고정한다. SHOT/영상 노드는 확장 자리만 있고 아직 생성하지 않는다.
- `writer_adapter`: 승인된 HIL 1/2 hash만 받는 backend-neutral request,
  strict structured output parser와 아직 거리 검사를 통과하지 않은 draft를
  소유한다. 원문·reference packet은 받지 않는다.
- `source_distance_import`: Eval의 `pass` receipt를 candidate projection
  hash로 수동 결합한다. `review_required`와 `fail`은 후보 생성 전에 멈춘다.
- `creative_review`: 공통 creative floor, 독립 BR0/BR1, 구조적으로 다른
  2–4개 후보 비교와 promotion readiness를 소유한다.
- `pipeline`: 기존 canary 단계를 결정론적으로 연결하고 hard failure에서
  즉시 중단한다.
- `artifacts`: cross-repo 전달용 canonical JSON과 SHA-256 envelope를 만든다.

`frozen_shortform_script_foundry`는 기준선과 검증 원리를 확인하는 레퍼런스일 뿐,
이 repo의 자동 입력이나 생성 정본이 아니다.

## Vertical slice check

개발 도구까지 포함한 로컬 설치와 검사는 다음처럼 실행한다.

```powershell
py -3.12 -m pip install --editable ".[dev]"
py -3.12 -m ruff check .
py -3.12 -m mypy
```

전체 계약 회귀 검사는 다음 명령을 쓴다.

```powershell
py -3.12 -m unittest discover -s tests -v
```

EP07 수동 import는 원본 고유명사·대사·금액·고유 사건 배열을 포함하지 않는다.
승인된 추상 기능 청사진만 장르 문법으로 반입하며, 파이프라인 실행에는 여전히
합성 오리지널 premise를 사용한다.

`imports/approved_genre_grammar/ep07_external_proof_reading_v1.json`은 자동
동기화 결과가 아니다. source blueprint hash, owner approval hash와 envelope
payload hash가 모두 맞아야 `grammar_import`가 승인 문법으로 읽는다.

`imports/source_distance/synthetic_ep001_variant_a_receipt_v1.json`은 세
child의 handoff 규격을 검증하기 위한 합성 canary다. 실제 작품·원문·실제
권리 판정을 포함하지 않으며, Eval에서 만든 receipt를 수동 복사한 형태다.

Loop 04 canary는 다음 명령으로 재생성한다.

```powershell
py -3.12 tools/build_loop04_canary.py
```

결과는 `artifacts/canaries/loop04/functional_draft_bundle.json`에 저장된다.
완성 대사나 지문이 아니라 Creative Writer Adapter가 따라야 할 증거급 기능
계약이며 모든 draft는 `candidate`다.

현재 삼도식당 제1~3화의 레거시 촬영고 체인은 다음 읽기 전용 canary로
검증한다. 원본이나 파생본을 수정하지 않고 해시·대사·장면·단계 분류만 읽는다.

```powershell
py -3.12 tools/audit_afterlife_restaurant_ep001_003_production_canary.py
```

v0.1~v0.2는 P0 표면 후보, v0.3~v0.4는 분리가 필요한 레거시 혼합 주석 후보,
v0.5의 휴대전화·취식 동선은 `StoryChangeRequest`가 필요한 내용 변경으로
분류한다. 어느 단계도 자동 승격하거나 외부 전달하지 않는다.

첫 실제 작품 HIL 1 후보 세 개는 다음 명령으로 재생성·검증한다.

```powershell
py -3.12 tools/build_afterlife_restaurant_hil1_candidates.py
py -3.12 tools/build_afterlife_restaurant_hil1_candidates.py --check
```

결과는 `artifacts/candidates/afterlife_restaurant/hil1/`에 저장된다. 동일한
Fact Ledger 위에서 감정 미스터리, 식당 누적 운영, 충돌하는 동업 관계의
서로 다른 주 보상을 비교한다. 세 후보 모두 owner 미승인이고 HIL 2 입력이
아니다.

Owner가 승인한 수정 통합 기획은 다음 명령으로 재생성·검증한다.

```powershell
py -3.12 tools/build_afterlife_restaurant_hil1_approved_plan.py
py -3.12 tools/build_afterlife_restaurant_hil1_approved_plan.py --check
```

결과는 `artifacts/approved/afterlife_restaurant/hil1/`에 있다. canonical JSON,
owner-readable 정본, 상세 애니메이션 기획서, review payload와 owner 승인 receipt가
exact hash로 묶인다. 이 승인은 HIL 1만 닫으며 HIL 2 사건 배열, 캐릭터 디자인 정본,
premise-distance, 외부 납품 승인을 대신하지 않는다.

## HIL 계약이 보장하는 것

- 승인 hash는 content hash와 별도 receipt다.
- 새 상위 revision 승인 시 의존하는 아크·회차는 `stale`이 된다.
- 재개는 parent content hash와 parent approval receipt가 모두 맞는 첫 미완
  승인점에서 시작한다.
- 단일 Renderer와 고정 4비트를 모든 작품에 강제하지 않는다.
- 단일 주인공이나 단일 보상 cadence를 모든 작품에 강제하지 않는다.
- 미래 시즌 떡밥은 현재 아크에서 지급 보상으로 소진할 수 없다.
- HIL 1/2 기획서는 원본 계약과 같은 canonical content hash를 검증한다.
- HIL 3은 hard verifier, creative absolute floor, 구조적으로 다른 후보,
  producer-distinct BR0/BR1과 owner 승인 없이는 준비 완료가 되지 않는다.
- 후보가 creative floor를 하나도 통과하지 못하면 owner 선택으로 우회하지 않는다.
- Writer backend 출력은 필드 추가·누락, 회차 불일치, runtime/renderer/arc
  위반에서 즉시 거절된다.
- 원문 비교 계산은 이 repo에서 하지 않으며, Eval receipt에도 원문 필드를
  반입할 수 없다.
- 합성 canary 정책 receipt는 테스트에서 명시적으로 허용할 때만 결합된다.
  실제 후보 경로는 Eval의 `production_approved` 정책 receipt가 아니면 멈춘다.
