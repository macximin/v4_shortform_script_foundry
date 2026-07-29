# Loop 04 — Functional Draft contract audit

Date: 2026-07-29

## Decision

Creative Writer Adapter 앞에 결정론적 `Functional Draft`를 둔다.

기존 Script Packet은 시간, 비트 기능, Renderer, 증거 단계와 사실 ID를
소유했지만 다음 질문에는 답하지 못했다.

- 이 장면은 왜 존재하는가?
- 화면에서 실제로 무엇을 보여야 하는가?
- 대사는 어떤 기능만 수행해야 하는가?
- 어떤 정보를 이번 비트에 공개하고 무엇을 유예하는가?
- 상태가 정확히 어떻게 바뀌는가?
- 다음 화가 반드시 이행할 질문은 무엇인가?

Loop 04는 이 여섯 항목을 모델 호출 전 정본 계약으로 만든다.

## Canonical order

```text
Script Packet
  -> Script hard verification
  -> Deterministic Draft Adapter
  -> Functional Draft
  -> Draft hard verification
  -> future Creative Writer Adapter
```

Functional Draft는 완성 대본이 아니다. 작가 모델이 임의로 이야기 구조를
바꾸지 못하도록 하는 증거급 장면 설계다.

## Draft beat contract

각 비트는 다음을 반드시 가진다.

- stable `beat_id`
- `start_seconds`, `end_seconds`
- `scene_purpose`
- `observable_action`
- `dialogue_function`
- `information_revealed_fact_ids`
- `information_withheld_fact_ids`
- `proof_stage_before`, `proof_stage_after`
- `state_delta_codes`
- `reward_ids`
- 마지막 비트의 `cliff_obligation`

Draft 전체는 canonical Script Packet SHA-256과 승인 grammar packet ID를
고정한다.

## Hard gates

다음은 hard failure다.

- Script Packet hash 불일치
- 자동 `approved` 승격
- approved grammar 이외의 reference content 접근
- beat 시간 누락·겹침 또는 runtime 변경
- hook/pressure에서 proof fact 선공개
- 계획보다 많은 확정 정보 공개
- 공개와 유예에 같은 fact 동시 배치
- unconfirmed fact를 확정 정보로 공개
- proof stage 역행
- 계획과 다른 state delta
- reward ID 불일치
- 마지막 cliff obligation 누락 또는 변조

정보 검증은 “필요한 정보가 포함됐는가”가 아니라 Script Packet과 정확히 같은
공개·유예 집합인지를 본다. 이로써 작가 단계의 정보 과적재도 차단한다.

## Canary

EP07에서 승인한 `external-proof-reading@0.1.0` 문법을 합성 오리지널 Fact
Ledger에 적용해 90초 3회 Functional Draft를 생성했다.

- premise: `synthetic-external-proof-reading`
- episode count: 3
- renderer sequence: grammar/router 결정
- source distance: `approved_grammar_only_no_reference_content`
- status: 모든 draft `candidate`
- bundle payload SHA-256:
  `0235f343aa1c0511863efafc47645e82562d2952e5b6638b9f713d7963644d5c`

Draft payload SHA-256:

- EP001: `ba6f8858ec98b7e7a41c72e1433c22ef4c3aff00972112f0ff4165d9df705a19`
- EP002: `33a71f2c3bbac6ed50775a4ed452999537846e54f8732eb231934a1e826734d8`
- EP003: `abde9eee71eb1ceeae4ef8d9992ae36a56508819197c3deb9194f7e75475b707`

원본 조직명·직접 대사·정확한 금액·증거물/기관 명칭·화말 직접 호칭은 artifact에
포함되지 않는다.

## Verification

```text
py -3.12 -m unittest discover -s tests -v
40 tests
OK
```

Loop 04 전용 검증은 다음을 포함한다.

- 3회 draft 생성·결정론·canonical export
- bundle과 회차별 payload hash
- 원천 고유 token 부재
- 자동 승격 거부
- stale Script Packet hash 거부
- proof 정보 선공개 거부
- 계획된 정보 유예 누락 거부
- Episode Contract와 다른 장면 목적·행동·대사 기능 거부
- unconfirmed 정보 공개 거부
- proof stage 역행 거부
- state delta 변조 거부
- cliff obligation 누락 거부

## Audit conclusion

Creative Writer Adapter를 붙일 최소 입력 계약은 준비됐다. 아직 모델 호출을
허용한 것은 아니다.

다음 Loop 05는 실제 문장을 쓰는 adapter보다 먼저 그 출력 계약을 정의해야 한다.

- 비트별 행동 지문
- 화자 ID와 대사
- fact/정보 delta 역참조
- 금지된 새 사실
- 반복·설명 과다·말투 위장 검증
- 인간 검수 ①: 이야기·정보량·클리프
