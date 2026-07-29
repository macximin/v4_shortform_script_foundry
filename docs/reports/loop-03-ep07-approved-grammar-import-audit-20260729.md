# Loop 03 — EP07 approved grammar import audit

Date: 2026-07-29

## Decision

EP07 reverse canary에서 owner 승인된 `external-proof-reading-v1` 기능 청사진을
v4의 첫 실제 근거 장르 문법으로 수동 반입했다.

반입한 것은 원본 내용이 아니라 다음 추상 연산이다.

- 분쟁 중인 휴대 증거가 사회적으로 읽히지 않는 압력
- 자격 있는 외부 판정자의 표식 판독
- 물질 보상보다 먼저 지급되는 공적 인식 변화
- 실물 지급을 유예하는 출처·신원 질문

## Boundary proof

- source repo: `shortform_reverse_lab`
- source canary: `ep07-institutional-proof-reading`
- source blueprint: `external-proof-reading-v1`
- source blueprint SHA-256:
  `de89ec9fb0d2cbfe42dd39f20fdb784d953c7aeb13fa3cf9baa6923c05d31219`
- grammar canonical approval SHA-256:
  `67a650273543cc3787096ffd24e47b7b2442bcca6580ca84dd368364c1d738a5`
- import payload SHA-256:
  `19956320412cb687f73922622487812a290ff295c72dfb78c4f461136f3fb1f6`

`grammar_import`는 세 hash/binding 중 하나라도 오래됐거나 변조되면 실패한다.
artifact ID와 grammar packet ID도 같아야 한다.

## Source-distance proof

import fixture에는 source-specific token을 넣지 않았다. 테스트는 다음 계열의
원천 고유 요소가 존재하지 않는지 검사한다.

- 원작 조직명
- 책임자 서명 표현
- 정확한 액면
- 원작 증거물 명칭
- 원작 기관 명칭
- 화말의 직접 호칭

직접 source content를 뜻하는 distance로 바꾸고 envelope hash를 새로 계산해도
importer가 거부한다.

## Execution proof

승인 문법은 원작 premise가 아니라 합성 오리지널 Fact Ledger에 연결했다.
다음 tag만 맞춘다.

- `disputed_portable_proof`
- `external_validator`
- `misperception`
- `authority`
- `resource_value`

같은 입력을 두 번 실행한 3회 Series Plan, Episode State, Script Packet과
verification 결과가 완전히 동일하며 모든 hard verification이 통과한다.

## Verification

```text
py -3.12 -m unittest discover -s tests -v
25 tests
OK
```

새 import 전용 검증:

- approved import로 deterministic vertical slice 실행
- source-specific token 부재
- envelope payload 변조 거부
- direct source distance 거부
- stale owner approval hash 거부
- artifact/grammar ID 불일치 거부

## Remaining gate

이 loop는 Writer Adapter나 완성 대본을 만들지 않는다. 다음 loop에서는 먼저
장면 기능·행동·정보 delta·상태 delta·클리프 의무를 갖는 draft contract와
검증기를 세운다. 해당 계약이 감리되기 전에는 모델 호출을 붙이지 않는다.
