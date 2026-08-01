# V4 Shortform Script Authority

## 1. Authority

이 저장소는 Renderer Router 기반 신규 숏폼 대본 생성 코어의 권위 저장소다.
5분 이하 스토리보드 대본의 생성 계약, 후보, 검증, 감리와 owner 승인 상태를 소유한다.

## 2. Clean-room boundary

- `frozen_shortform_script_foundry`의 작품과 장기 연재 상태는 가져오지 않는다.
- 기존 relay와 validator를 통째로 복제하지 않는다.
- 승인, exact hash, BR0/BR1 분리와 형식 검증 원리는 요구사항으로 다시 구현한다.
- 레퍼런스 원문의 고유명사, 대사와 고유 사건 배열을 생성 fixture에 넣지 않는다.

## 3. Core order

```text
Fact Ledger + Approved Genre Grammar
  -> HIL 1 Canonical Package
  -> owner-readable HIL 1 planning document
  -> Renderer Router + HIL 2 state-transition Arc Contract
  -> owner-readable HIL 2 planning document
  -> selectable Beat Pattern + writer scaffold
  -> Creative Writer candidate
  -> hard verification
  -> independent BR0 / BR1 creative floor and pairwise review
  -> HIL 3 finished Episode Script owner approval
```

Fact Ledger가 Renderer 해석보다 우선한다. 해석이 입력 사실을 바꾸거나 불확실성을
확정 사실로 승격할 수 없다.

HIL 1은 사건 배열을 잠그지 않고 작품 약속, 핵심 인물 1–3명의 작동 정체성,
agency 전환 범위, 회차·아크·시즌·미래 떡밥 보상 층위, 제작 제약, 관객 정보
비대칭 원칙과 Renderer 범위를 승인한다. HIL 2는 고정 회차 수가 아니라 관계,
지식, 자원과 세계 운영을 포함한 상태 전환을 승인한다. HIL 3만 실제
대사·지문이 있는 완성 회차 대본을 승인한다.

기존 `Series Plan -> Script Packet -> Functional Draft`는 EP07 계약 canary와
writer scaffold로 유지하되 HIL 승인 정본이나 모든 작품의 보편 4비트 공식으로
승격하지 않는다.

## 4. Promotion gate

후보는 verification, BR0, BR1과 owner 승인을 모두 통과하기 전까지 승인본이 아니다.
자동 승격, 외부 공개와 제작 전달은 금지한다.

## 5. Current stage

현재 단계는 **HIL contract vertical slice**다.

- 기존 deterministic functional-draft canary는 회귀 기준으로 유지한다.
- HIL 1 Canonical Package와 HIL 2 Arc Contract가 구현됐다.
- HIL 1은 1–3명의 핵심 인물과 cadence별 payoff layer를 소유한다.
- HIL 2는 resource/world-operation 상태와 HIL 1 제작 제약을 보존한다.
- HIL 1/2의 canonical JSON과 동일 hash에 결합된 사람이 읽는 Markdown
  기획서 출력이 구현됐다.
- content hash와 approval receipt가 분리됐다.
- immutable revision, stale 전파, 첫 미완 승인점 재개와 fail-fast가 구현됐다.
- 선택형 Beat Pattern, 완성 회차 대본 후보 계약, creative absolute floor,
  독립 BR0/BR1, 구조적으로 다른 후보 비교와 HIL 3 promotion readiness가
  구현됐다.

첫 실제 작품 HIL 1 candidate set은 생성됐지만 owner 미승인이고
premise-distance 검사는 pending이다. 아직 Creative Writer 모델 호출, 실제
HIL 2/3 작품 후보, 실제 owner 승인본, 기획서 review UI와 외부 배포는 없다.
