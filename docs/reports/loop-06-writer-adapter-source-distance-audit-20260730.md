# Loop 06 — Creative Writer Adapter / source-distance 수직 슬라이스 감리

날짜: 2026-07-30

## 결론

Creative Writer Adapter를 Foundry에 붙이는 방향은 유지한다. 다만 실제 모델
SDK를 코어에 직결하지 않고 `WriterBackend` protocol로 분리했다. 현재 완료된
범위는 승인된 HIL 1/2 계약을 backend-neutral request로 만들고, backend의
structured output을 엄격히 해석해 아직 거리 검사를 받지 않은 `WriterDraft`로
만드는 단계다.

원문 대조 계산은 Foundry에 넣지 않았다.

- Reference: 권리 확인된 runtime comparison packet과 원문 없는 manifest
- Eval: 명시적으로 보정된 정책에 의한 거리 계산과 receipt
- Foundry: receipt hash와 WriterDraft projection hash 검증 후 candidate 생성

따라서 Renderer Router와 HIL 1/2/3 이론은 유지되며, source-distance가 새로운
보편 서사 공식이나 Renderer 선택기로 침범하지 않는다.

## 구현된 흐름

```text
HIL 1 Canonical approval
  + HIL 2 Arc approval
  -> WriterRequest
  -> injected WriterBackend
  -> strict structured-output parsing
  -> WriterDraft (unscreened)
  -> source-distance projection
  -> independent Eval receipt
  -> manual receipt import
  -> projection hash / receipt hash verification
  -> EpisodeScriptCandidate(status=candidate)
```

`WriterRequest`에는 Canonical/Arc content hash와 approval receipt hash,
선택된 beat pattern, Renderer 범위, hard invariant, creative latitude와
회차의 압력·선택·결과만 들어간다. 원문, source locator, reference packet은
들어가지 않는다.

## Hard stop

- HIL 1/2 approval receipt가 정확한 content hash를 승인하지 않음
- Arc가 Canonical approval을 정확히 잇지 않음
- backend 출력 필드 누락 또는 임의 필드 추가
- 요청과 다른 episode id
- Arc 밖 Renderer 또는 beat pattern
- 장면 runtime, 상태 delta, reward/obligation 계약 위반
- Eval receipt payload hash 불일치
- WriterDraft projection hash 불일치
- `review_required` 또는 `fail` 판정
- receipt 내부 raw source field

통과해도 결과는 `candidate`다. BR0/BR1과 owner HIL 3 승인을 대신하지 않는다.

## 교차 repo canary

실제 작품이 아닌 합성 자료로 세 독립 repo의 hash 규격을 검증했다.

- WriterDraft projection:
  `4905493ca4e618752f999009449cc2635d9fceda3fa9d3d48446f1f8d2c095e3`
- Reference manifest:
  `977b0ec470ad49bb8617ec83df5efa1488ab9a5dd870f2a7d8036e311a149cc2`
- Eval receipt:
  `d5dfc35e063009ff08fe9e46c5e48eeeb6344796b61b7987bf506f1cccbec12c`

receipt는 `imports/source_distance/`에 수동 복사했다. child 간 runtime 자동
read/writeback은 만들지 않았다.

## 검증

- Foundry unit tests: 66 pass
- 신규 Foundry 파일 Ruff: pass
- 신규 Foundry 파일 mypy: pass
- compileall: pass
- wheel build `v4_shortform_script_foundry-0.3.0`: pass
- Reference unit tests: 2 pass
- Eval unit tests: 4 pass
- Reference/Eval 전체 source Ruff 및 mypy: pass
- Reference/Eval wheel build: pass
- 세 repo `git diff --check`: pass

## 아직 생산 투입이 아닌 이유

1. Reference에는 실제 작품의 권리 확인 packet이 없다.
2. Eval에는 실제 평가 세트로 보정된 production policy가 없다.
3. 실제 Creative Writer backend와 모델 호출은 붙이지 않았다.
4. 실제 owner HIL 1/2/3 승인과 BR0/BR1 결과가 없다.

다음 구현은 실제 원천을 넣는 일이 아니라, 먼저 독립 평가 세트로 거리 정책을
보정하고 owner가 그 policy receipt를 승인하는 작업이다. 그 다음에만 실제
backend를 fixture가 아닌 제한된 candidate lane에 연결할 수 있다.
