# v4_shortform_script_foundry

Renderer Router 기반 숏폼 스토리보드 대본 생성 코어를 clean-room으로 개발하는 독립 edge repo다.

현재는 **deterministic functional-draft vertical slice** 상태다. Fact Ledger와
승인된 Genre Grammar Packet으로 3회 Series Plan, Episode State, Script Packet과
증거급 Functional Draft를 재현 가능하게 만들고 두 단계 hard verification까지
실행한다.

아직 대사·지문 생성, 모델 호출, 실제 작품 데이터, 승인 대본과 외부 배포 기능은 없다.

## Core flow

```text
Fact Ledger
  + Approved Genre Grammar Packet
  -> Renderer Router
  -> Series Plan
  -> Episode State Planner
  -> Script Packet
  -> Script Verifier
  -> Deterministic Draft Adapter
  -> Functional Draft
  -> Draft Verifier
  -> [future] Creative Writer Adapter
  -> BR0 / BR1 / Owner Approval
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
- `pipeline`: 위 단계를 결정론적으로 연결한다.
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

Loop 04 canary는 다음 명령으로 재생성한다.

```powershell
py -3.12 tools/build_loop04_canary.py
```

결과는 `artifacts/canaries/loop04/functional_draft_bundle.json`에 저장된다.
완성 대사나 지문이 아니라 Creative Writer Adapter가 따라야 할 증거급 기능
계약이며 모든 draft는 `candidate`다.
