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

`Fact Ledger -> Renderer Router -> Episode State -> Script Packet -> Writer Adapter -> Verification`

Fact Ledger가 Renderer 해석보다 우선한다. 해석이 입력 사실을 바꾸거나 불확실성을
확정 사실로 승격할 수 없다.

## 4. Promotion gate

후보는 verification, BR0, BR1과 owner 승인을 모두 통과하기 전까지 승인본이 아니다.
자동 승격, 외부 공개와 제작 전달은 금지한다.

## 5. Current stage

현재 단계는 skeleton이다. 첫 수직 슬라이스 계약이 승인되기 전에는 생성 로직,
모델 호출, 실제 작품과 승인본을 추가하지 않는다.
