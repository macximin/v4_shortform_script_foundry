# Loop 07 — Distance calibration / production 승격 차단 감리

날짜: 2026-07-31

## 결론

현재 로컬 분석 corpus로 production 거리 임계값을 정할 수 없다. 대부분 원천
권리 상태가 미확인이며, EP07의 `owner_authorized_private_research`도 곧바로
Reference의 production 거리평가 승격을 의미하지 않는다.

따라서 임계값을 만들지 않고, 임계값이 정당하게 만들어지는 절차와 실패 차단만
구현했다.

## 구현

Eval:

- pass/review/fail 기대 사례를 모두 요구하는 CalibrationDataset
- synthetic / rights-cleared dataset tier
- trial policy의 case별 CalibrationRun과 exact content hash
- exact run을 승인하는 owner CalibrationApprovalReceipt
- rights-cleared + 전 case 일치 + exact owner approval일 때만
  `production_approved` 정책 승격
- synthetic dataset의 production 승격 hard fail

Foundry:

- Eval receipt의 `policy_tier` 검증
- 기본 경로에서 `production_approved`만 candidate 결합 허용
- synthetic canary는 테스트가 명시적으로 opt-in할 때만 허용

## Renderer/HIL 영향

없다. calibration은 원천 거리 정책의 정당성만 다루며 Canonical, Arc,
Renderer 선택, beat pattern, creative review 점수에 관여하지 않는다.

## 현재 상태

- 실제 production policy: 없음
- 실제 threshold 승인: 없음
- 실제 모델 backend: 없음
- 합성 3종 canary: original/pass, borderline/review, protected-copy/fail

다음 unblock 조건은 Reference에 production 거리평가가 허용된 원천 packet과
독립 benchmark label이 들어오는 것이다. 그 전에는 실제 기준을 만들거나
Foundry 후보를 production-ready라고 표시하지 않는다.

## 검증

- Foundry: 67 tests pass, 신규 범위 Ruff/mypy pass
- Eval: 9 tests pass, 전체 source Ruff/mypy pass
- Reference: 2 tests pass, 전체 source Ruff/mypy pass
- compileall: 세 repo pass
- wheel build: Foundry 0.4.0, Eval 0.2.0, Reference 0.1.0 pass
- `git diff --check`: 세 repo pass
