# v4_shortform_script_foundry

Renderer Router 기반 숏폼 스토리보드 대본 생성 코어를 clean-room으로 개발하는 독립 edge repo다.

현재는 **deterministic pre-writer vertical slice** 상태다. Fact Ledger와 승인된
Genre Grammar Packet으로 3회 Series Plan, Episode State와 Script Packet을
재현 가능하게 만들고 hard verification까지 실행한다.

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
  -> [future] Writer Adapter
  -> BR0 / BR1 / Owner Approval
```

첫 구현 범위는 다음 다섯 경계다.

- `fact_ledger`: 확정 사실, 주장, 추정과 미지정을 분리한다.
- `genre_grammar`: 근거와 owner content hash가 있는 장르 문법 packet을 소유한다.
- `renderer_router`: 확정 fact tag가 허용하는 위협·증거·보상 렌더러를 선택한다.
- `series_plan`: 3회 시즌 스파인, 증거 단계와 보상 곡선을 만든다.
- `episode_state`: 실제/인식 지위, 지식 지도, 증거 단계와 보상 유예를 관리한다.
- `script_packet`: 작가 어댑터에 넘길 얇은 회차 계약을 소유한다.
- `verification`: 사실·연속성·렌더러 정합성과 레퍼런스 거리를 검증한다.
- `pipeline`: 위 단계를 결정론적으로 연결한다.
- `artifacts`: cross-repo 전달용 canonical JSON과 SHA-256 envelope를 만든다.

`frozen_shortform_script_foundry`는 기준선과 검증 원리를 확인하는 레퍼런스일 뿐,
이 repo의 자동 입력이나 생성 정본이 아니다.

## Vertical slice check

```powershell
py -3.12 -m unittest discover -s tests -v
```

현재 수직 슬라이스의 fixture는 실제 레퍼런스가 아닌 합성 premise와 합성 장르
문법만 사용한다.
