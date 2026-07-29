# AGENTS.md — v4_shortform_script_foundry

이 repo의 정본 경계는 [V4 Shortform Script Authority](00_charter/v4_shortform_script_authority.md)다.

- 목표 산출물은 5분 이하 숏폼용 스토리보드 대본이다.
- 이 repo는 Renderer Router 기반 신규 대본 생성 코어, 후보본, 감리 기록과 승인본을 소유한다.
- `frozen_shortform_script_foundry`는 읽기 전용 레퍼런스이며 자동 입력이나 코드 복제 원천이 아니다.
- 기존 작품, novel relay, source map, model run과 장기 연재 상태를 가져오지 않는다.
- 재사용이 필요한 승인·hash·BR0/BR1·형식 검증 원리는 기능 단위로 새로 구현하고 테스트한다.
- `shortform_reverse_lab`의 결과는 구조 가설로만 읽으며 원천의 고유명사·대사·사건 배열을 복제하지 않는다.
- 후보를 승인본으로 자동 승격하거나 외부 공개·제작 전달하지 않는다. 승격은 owner만 한다.

현재 단계는 skeleton이다. 수직 슬라이스 승인 전에는 실제 생성 로직이나 모델 호출을 붙이지 않는다.
