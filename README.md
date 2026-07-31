# v4_shortform_script_foundry

Renderer Router 기반 숏폼 스토리보드 대본 생성 코어를 clean-room으로 개발하는 독립 edge repo다.

현재는 **Creative Writer Adapter vertical slice** 상태다. 기존의 deterministic
functional-draft canary를 보존하면서, HIL 1/2/3 계약과 무효화·재개·품질
비교, pluggable writer backend의 strict structured output 검증, Eval
source-distance receipt의 수동 hash-bound 반입을 구현했다.

아직 실제 모델/API backend, 실제 작품 데이터, 실제 owner 승인 대본과 외부
배포 기능은 없다. 테스트의 완성 대본은 계약 검증용 합성 fixture다.

## Core flow

```text
Fact Ledger
  + Approved Genre Grammar Packet
  -> HIL 1 Canonical Package
  -> Renderer Router + HIL 2 state-transition Arc Contract
  -> selectable Beat Pattern + writer scaffold
  -> Creative Writer Adapter -> unscreened Writer Draft
  -> independent Eval source-distance receipt
  -> hash-bound Episode Script candidate
  -> Episode Script hard verifier
  -> creative absolute floor
  -> independent BR0 / BR1 pairwise review
  -> HIL 3 Owner Approval
```

현재 핵심 경계는 다음과 같다.

- `fact_ledger`: 확정 사실, 주장, 추정과 미지정을 분리한다.
- `genre_grammar`: 근거와 owner content hash가 있는 장르 문법 packet을 소유한다.
- `grammar_import`: reverse lab의 승인된 추상 blueprint만 독립 hash envelope로
  수동 반입한다.
- `renderer_router`: 확정 fact tag가 허용하는 위협·증거·보상 렌더러를 선택한다.
- `series_plan`: 3회 시즌 스파인, 증거 단계와 보상 곡선을 만든다.
- `episode_state`: 실제/인식 지위, 지식 지도, 증거 단계와 보상 유예를 관리한다.
- `script_packet`: 작가 어댑터에 넘길 얇은 회차 계약을 소유한다.
- `verification`: 사실·연속성·렌더러 정합성과 레퍼런스 거리를 검증한다.
- `draft_script`: 장면 목적, 관찰 행동, 대사 기능, 정보 공개·유예, 비트별
  상태 delta와 cliff obligation을 소유한다.
- `draft_verification`: 정보 과적재·선공개, 상태 불일치, 클리프 누락,
  자동 승격과 source-distance 위반을 차단한다.
- `approval`: content hash와 승인 receipt를 분리하고 revision, stale,
  resume boundary와 owner-only 승격을 소유한다.
- `canonical_package`: HIL 1 작품 약속, 주인공 작동 정체성, agency 전환
  범위, 관객 정보 원칙과 Renderer 범위를 소유한다.
- `arc_contract`: HIL 2 상태전환, 다차원 Story State, episode count band와
  revision proposal을 소유한다.
- `beat_patterns`: 증거 역전, suspense 정보 격차, 능력 인정, 선택·안전
  패턴을 선택지로 제공하며 어느 하나도 보편 공식으로 만들지 않는다.
- `episode_script`: HIL 3 완성 회차 대본 후보와 hard verifier를 소유한다.
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

## HIL 계약이 보장하는 것

- 승인 hash는 content hash와 별도 receipt다.
- 새 상위 revision 승인 시 의존하는 아크·회차는 `stale`이 된다.
- 재개는 parent content hash와 parent approval receipt가 모두 맞는 첫 미완
  승인점에서 시작한다.
- 단일 Renderer와 고정 4비트를 모든 작품에 강제하지 않는다.
- HIL 3은 hard verifier, creative absolute floor, 구조적으로 다른 후보,
  producer-distinct BR0/BR1과 owner 승인 없이는 준비 완료가 되지 않는다.
- 후보가 creative floor를 하나도 통과하지 못하면 owner 선택으로 우회하지 않는다.
- Writer backend 출력은 필드 추가·누락, 회차 불일치, runtime/renderer/arc
  위반에서 즉시 거절된다.
- 원문 비교 계산은 이 repo에서 하지 않으며, Eval receipt에도 원문 필드를
  반입할 수 없다.
- 합성 canary 정책 receipt는 테스트에서 명시적으로 허용할 때만 결합된다.
  실제 후보 경로는 Eval의 `production_approved` 정책 receipt가 아니면 멈춘다.
