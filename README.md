# v4_shortform_script_foundry

Renderer Router 기반 숏폼 스토리보드 대본 생성 코어를 clean-room으로 개발하는 독립 edge repo다.

현재는 **skeleton only** 상태다. 패키지 경계와 테스트 진입점만 있고 생성 로직, 모델 호출,
작품 데이터, 승인본과 외부 배포 기능은 없다.

## Core flow

```text
Fact Ledger
  -> Renderer Router
  -> Episode State Planner
  -> Script Packet
  -> Writer Adapter
  -> Script Verifier
  -> BR0 / BR1 / Owner Approval
```

첫 구현 범위는 다음 다섯 경계다.

- `fact_ledger`: 확정 사실, 주장, 추정과 미지정을 분리한다.
- `renderer_router`: 회차별 위협·증거·보상 렌더러 조합을 선택한다.
- `episode_state`: 실제/인식 지위, 지식 지도, 증거 단계와 보상 유예를 관리한다.
- `script_packet`: 작가 어댑터에 넘길 얇은 회차 계약을 소유한다.
- `verification`: 사실·연속성·렌더러 정합성과 레퍼런스 거리를 검증한다.

`frozen_shortform_script_foundry`는 기준선과 검증 원리를 확인하는 레퍼런스일 뿐,
이 repo의 자동 입력이나 생성 정본이 아니다.

## Skeleton check

```powershell
py -3.12 -m unittest discover -s tests -v
```
