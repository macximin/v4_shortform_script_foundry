# Loop 10 — 제작 텍스트 캐노니컬 파이프라인 조사·감리 및 구현안

날짜: 2026-08-03

상태: `owner direction approved / v0.6.0 production-text contracts implemented / no HIL or external promotion`

이 문서는 현재 캐노니컬을 바꾸는 승인문이 아니다. 잠금 대본, HIL 1·2·3 승인
상태, 외부 제작 전달 상태를 변경하지 않는다.

## 1. 최종 결론

`v4_shortform_script_foundry`의 공식 파이프라인에 **제작 텍스트 레인**을 추가하는
방향이 맞다. 다만 `촬영고` 한 단계를 HIL 3 뒤에 통째로 붙이거나 CAMERA 지시를
HIL 3 본문에 직접 합치면 안 된다.

다음 세 층을 분리한다.

1. **서사 본문**: 대사·지문·장면·사건·행동 순서를 소유한다.
2. **사람용 제작 표면**: 같은 본문을 배우·연출·편집이 읽기 쉬운 촬영고 문법으로
   표현한다.
3. **촬영 주석**: CAMERA·SHOT·INSERT·EDIT, 쇼트 의도와 편집 제안을 별도
   sidecar로 소유한다.

스토리보드 이미지, 애니매틱, 영상·음성 생성은 이 레포의 현재 소유 범위에 넣지
않는다. Foundry는 제작 가능한 **텍스트 패키지**와 hash-bound handoff envelope까지만
소유한다.

## 2. 조사 근거

### 2.1 현재 레포 권위와 구현

- `00_charter/v4_shortform_script_authority.md`는 이 레포의 목표를 5분 이하
  스토리보드 대본으로 정하고, HIL 3에서 실제 대사·지문이 있는 완성 회차 대본을
  승인한다.
- `episode_script.py`의 HIL 3 계약은 scene location, observable action, dialogue,
  runtime, state delta와 reward를 소유하지만, 화면에 표시되는 대본 원문의 순서형
  atom이나 CAMERA 주석은 소유하지 않는다.
- 기존 `ep001_character_surface_rev3`는 `episode_001_human_screenplay.md`와
  `production_scene_breakdown.md`를 이미 분리했고, 테스트도 두 층이 섞이지 않는지
  확인한다.
- `삼도식당_촬영고_대본양식_기준_v0.1.md`는 카메라 각도를 꼭 필요할 때만 쓰고,
  기본은 쇼트리스트가 아니라 행동을 적도록 규정한다.
- 과거 `build_afterlife_restaurant_ep001_previs.py`는 PNG·PDF·MP4 프리비즈까지
  만들었지만, 현재 입력 source·receipt·output 경로가 모두 사라져 실행 불가능한
  고립 도구다. 텍스트 레인과 시각 제작 레인을 분리하지 않았을 때 생기는 부채의
  실제 사례다.

### 2.2 현재 제1~3화 파생본이 드러낸 문제

`v0.1`부터 `v0.5`까지의 작업은 하나가 아니다.

| 작업 | 실제 성격 | 필요한 게이트 |
|---|---|---|
| 회차·장면·대사 열 정리 | 내용 보존형 표면 변환 | 기계적 동등성 검사 |
| SFX 화면 안·밖 구분 | 제작 표면 또는 제작 주석 | 표면 감리 |
| CAMERA·SHOT·INSERT·EDIT | 연출 해석 | 제작 주석 검토 |
| 휴대전화 전달 동작 추가 | 서사 행동 수정 | HIL 3 본문 revision 승인 |
| `한입 → 파삭 → 껍질·육즙` 재배열 | 서사 행동 순서 수정 | HIL 3 본문 revision 승인 |

따라서 v0.5 전체를 `내용 보존형 촬영고`라고 부르면 분류가 틀린다. 현재 v0.5는
후보 파생본으로 보존하되, 새 파이프라인에서는 본문 revision과 촬영 주석으로
분해해야 한다.

### 2.3 외부 제작 관행과의 대조

- BBC Writersroom의 TV 대본 형식은 action을 화면에 보이는 내용으로 제한하고,
  parenthetical을 아껴 쓰며, SFX를 별도 cue로 분리한다.
  <https://downloads.bbc.co.uk/writersroom/scripts/threecamera.pdf>
- Final Draft의 production 기능은 대본이 제작에 들어간 뒤 page/scene을 잠그고
  revision을 별도로 추적하는 이유를, schedule·prop list·call sheet 등 파생 문서의
  참조가 깨지지 않게 하기 위한 것이라고 설명한다.
  <https://www.finaldraft.com/downloads/manuals/fd10win.pdf>
- ScreenSkills는 storyboard를 script와 director vision을 shot panel로 번역하는
  pre-production 작업으로 설명하고, camera move와 continuity를 그 층의 책임으로
  둔다.
  <https://www.screenskills.com/job-profiles/browse/animation/pre-production/storyboard-artist/>
- ScreenSkills는 previs를 storyboard 뒤에서 shot·scale·timing·character movement를
  시험하는 별도 animatic 단계로 설명한다.
  <https://www.screenskills.com/job-profiles/browse/visual-effects-vfx/pre-production/previsualisation-previs-artist/>

외부 관행은 특정 한국식 촬영고 표면 하나를 강제하지 않는다. 다만 본문 잠금,
제작 revision, storyboard/previs 책임을 구분해야 한다는 구조는 현재 레포의 문제와
일치한다.

## 3. 결론 안정성 감리

### 3.1 1차 결론

초기 결론은 `HIL 3 승인 뒤에 촬영고/프리비즈 단계를 추가한다`였다.

**변경 사유:** B006 이후 신규 원고는 처음부터 촬영고 표면으로 쓰기로 결정돼
있다. 그러므로 사람용 촬영고 표면 전체를 HIL 3 이후로 미루면 신규 집필 흐름과
충돌한다. 또한 v0.5 안에는 형식, 연출 주석, 본문 수정이 섞여 있다.

### 3.2 2차 결론 — 반대안 감리

검토한 반대안은 `목표 산출물이 스토리보드 대본이므로 CAMERA 지시까지 HIL 3
본문에 포함한다`였다.

**기각:**

- 본문과 촬영 주석은 승인 주체와 변경 빈도가 다르다.
- 촬영 주석 수정 때문에 대사·사건 hash가 바뀌면 하위 invalidation이 과도해진다.
- 촬영 검토 중 발견된 행동 오류가 주석 수정으로 위장될 수 있다.
- 기존 코드와 테스트도 human screenplay와 production breakdown을 분리한다.

**유지된 결론:** HIL 3 서사 본문은 제작 친화적 표면으로 처음부터 작성할 수
있지만, CAMERA·SHOT·INSERT·EDIT는 별도 제작 주석이어야 한다.

### 3.3 3차 결론 — 소유 레포와 구현비용 감리

검토한 반대안은 `제작 관련 작업이 생겼으므로 즉시 별도 previs 레포를 만든다`였다.

**기각:**

- 반복된 것은 촬영고 텍스트와 주석 작업이지, 실제 이미지·애니매틱 제작 운영이
  아니다.
- 현재 프리비즈 도구는 한 번의 고립된 pilot이며 입력 경로도 사라졌다.
- HQ 규칙상 실제 반복 작업이 증명되기 전에 새 구조를 만들지 않는다.

**유지된 결론:** 제작 텍스트는 Foundry 안에서 분리 구현하고, 시각 storyboard와
animatic은 handoff envelope까지만 정의한다. 실제 반복 제작이 생길 때 별도 child를
검토한다.

### 3.4 안정성 판정

2차와 3차 감리에서 아래 결론이 연속으로 바뀌지 않았다.

> HIL 3 서사 본문 + 사람용 제작 표면 + 별도 촬영 주석. Foundry는 제작 텍스트와
> handoff까지만 소유하며 시각 프리비즈는 현재 닫는다.

요청된 `동일 결론 2회 이상` 조건을 충족한다.

## 4. 제안하는 캐노니컬 흐름

```text
HIL 1 작품 약속
  -> HIL 2 아크 상태 전환
  -> HIL 3 Episode Script 후보
  -> hard verification + BR0/BR1 + owner story lock
       |
       +-> P0 Human Production Surface
       |     - 배우·연출·편집용 촬영고 표면
       |     - 본문 atom과 1:1 결합
       |     - 레거시 잠금본은 exact-preservation 검사
       |
       +-> P1 Production Annotation Set
             - CAMERA / SHOT / INSERT / EDIT
             - 본문을 복사하지 않고 atom ID에 anchor
             - 항상 candidate recommendation

P0 equivalence pass + P1 production review
  -> P2 Production Text Package
  -> owner external-delivery decision
  -> immutable handoff envelope
  -> [미구현] storyboard / animatic production child
```

### 본문 변경 루프

```text
P0/P1 감리 중 대사·지문·행동·순서 문제 발견
  -> StoryChangeRequest
  -> HIL 3 새 revision
  -> owner story lock
  -> 이전 P0/P1/P2 stale
  -> 새 source hash에서 재생성
```

촬영 주석에서 본문을 직접 고치는 우회로는 두지 않는다.

## 5. artifact와 상태 계약

### 5.1 `EpisodeScriptText`

HIL 3의 의미 계약에 실제 순서형 본문을 결합한다.

- `episode_id`, `revision`
- `parent_episode_contract_sha256`
- `atoms[]`
- `content_sha256`
- `status = candidate | approved | superseded | stale`

atom 종류:

- `scene_heading`
- `action`
- `dialogue`
- `performance_cue`
- `sfx`
- `transition`
- `screen_text`

모든 atom은 안정적인 `atom_id`, `scene_id`, `ordinal`, 원문 text를 가진다.

### 5.2 `HumanProductionSurface`

- `source_episode_text_sha256`
- `surface_profile_id` 예: `samdo_korean_shooting_surface@0.1`
- `rendered_text_sha256`
- `atom_projection[]`
- `equivalence_status`
- `status = candidate_surface | equivalent_surface | stale`

레거시 변환은 모든 atom의 text와 ordinal이 동일해야 한다. 줄바꿈, 들여쓰기,
회차·장면 머리 표기만 profile이 허용한 projection으로 바꾼다.

B006 이후 신규 원고는 이 profile로 처음부터 작성할 수 있다. 이 경우 표면이
별도 사후 변환물이 아니라 HIL 3 본문의 owner-readable projection이 된다.

### 5.3 `ProductionAnnotationSet`

- `source_episode_text_sha256`
- `source_surface_sha256`
- `annotations[]`
- `status = candidate_annotation | reviewed_annotation | stale`

annotation 필드:

- `annotation_id`
- `kind = camera | shot | insert | edit`
- `anchor_atom_id`
- `intent`
- `instruction`
- `required = false` 기본값
- `reviewer_role`

주석에는 본문 text 사본을 넣지 않는다. anchor가 사라지거나 source hash가 바뀌면
자동으로 stale이다.

### 5.4 `StoryChangeRequest`

촬영 감리에서 발견한 본문 문제를 별도 승격 요청으로 만든다.

- `source_episode_text_sha256`
- `affected_atom_ids`
- `change_type = dialogue | action | order | continuity`
- `before`
- `after`
- `reason`
- `owner_decision = pending | approved | rejected`

승인된 request는 HIL 3 새 revision의 입력일 뿐, 기존 잠금본을 직접 수정할 권한이
아니다.

### 5.5 `ProductionTextPackage`

- exact HIL 3 approval receipt
- `EpisodeScriptText` hash
- `HumanProductionSurface` hash
- 선택된 `ProductionAnnotationSet` hash
- production reviewer receipt
- external delivery status

`production reviewed`와 `external delivery approved`는 별도 값이어야 한다.

## 6. 코드 구현 위치

### 새 모듈

- `src/v4_shortform_script_foundry/episode_script_text.py`
  - 순서형 atom과 HIL 3 text hash
- `src/v4_shortform_script_foundry/production_surface.py`
  - profile renderer, projection map, exact-preservation verifier
- `src/v4_shortform_script_foundry/production_annotation.py`
  - CAMERA·SHOT·INSERT·EDIT sidecar와 anchor verifier
- `src/v4_shortform_script_foundry/production_gate.py`
  - P0/P1/P2 상태, stale 전파, production/external-delivery 분리
- `src/v4_shortform_script_foundry/story_change_request.py`
  - 제작 감리에서 HIL 3 revision으로 돌아가는 유일한 변경 경로
- `src/v4_shortform_script_foundry/production_package.py`
  - hash-bound text handoff envelope

### 기존 모듈 변경

- `approval.py`
  - HIL gate를 억지로 HIL 4로 늘리지 않는다.
  - 별도 `ProductionGate` receipt를 연결한다.
- `episode_script.py`
  - 의미 계약은 유지하고 `EpisodeScriptText` hash binding만 추가한다.
- `artifacts.py`
  - production text package envelope type을 추가한다.
- `README.md`, `00_charter/v4_shortform_script_authority.md`,
  `docs/architecture/core-boundaries.md`
  - owner 승인 후에만 최종 흐름을 반영한다.

### 도구

- `tools/build_production_surface.py`
- `tools/verify_production_surface.py`
- `tools/build_production_annotation_package.py`

기존 `build_afterlife_restaurant_ep001_previs.py`는 새 모듈의 기반으로 재사용하지
않는다. 시각 출력 책임과 사라진 절대 입력을 함께 가진 고립 pilot이므로, 이력
보존 후 비활성 상태를 명시하거나 향후 별도 previs child에서 clean-room으로 다시
구현한다.

## 7. 필수 검증

### 본문/표면

- 대사 text, speaker, 순서 exact match
- action text와 순서 exact match
- scene 수·ID·순서 exact match
- 음식·조리·반응·훅 atom 누락 금지
- source hash mismatch fail-closed
- 표면 renderer의 재실행 결과 deterministic

### 촬영 주석

- 존재하지 않는 atom anchor 거부
- stale source/surface hash 거부
- CAMERA·SHOT·INSERT·EDIT 외 임의 kind 거부
- 주석 안의 대사·지문 대체 text 거부
- `required=true`는 production reviewer 없이는 거부
- 주석 변경이 HIL 3 content hash를 바꾸지 않는지 검증

### 변경 요청

- action 추가·삭제·재배열을 표면 변환으로 위장하면 거부
- owner 승인 없는 StoryChangeRequest의 HIL 3 반영 거부
- 새 HIL 3 revision 승인 시 연결된 P0/P1/P2 stale

### 승격/전달

- P0 equivalence와 P1 review 전 P2 생성 금지
- P2가 있어도 외부 전달 자동 허용 금지
- external delivery receipt는 owner 역할과 exact package hash 요구

## 8. 제1~3화 migration 판정

현재 파일은 삭제하거나 덮어쓰지 않는다.

1. 잠금 원본 세 파일을 `EpisodeScriptText` revision 1의 source로 고정한다.
2. v0.1의 형식 변환 결과를 P0 후보로 재검증한다.
3. v0.2의 SFX 표기를 atom 또는 surface annotation으로 분류한다.
4. v0.3·v0.4의 CAMERA·SHOT·INSERT·EDIT를 P1 sidecar로 추출한다.
5. v0.5의 휴대전화 동선과 취식 순서 변경은 `StoryChangeRequest`로 분리한다.
6. owner가 본문 revision을 승인하기 전에는 v0.5를 `equivalent_surface`나 P2로
   승격하지 않는다.

노션 사람용 표면도 같은 package hash를 표시하도록 하되, 노션은 권위 저장소가
아니라 projection이다.

## 9. 구현 순서

### Phase 0 — 현재 기준선 복구

새 기능보다 먼저 테스트 기준선을 복구한다.

현재 확인 결과:

- `121 tests`
- `14 failures + 1 error`
- 주요 원인: 외부 sibling research file hash drift로 인한 checked-in artifact stale,
  generator 산출물 hash 불일치, encoding 미지정 `read_text()` 1건
- 고립 previs 도구의 source·receipt·output 경로 부재

Phase 0 완료 조건:

- 현재 owner 변경을 덮지 않고 failure를 분류한다.
- runtime sibling read를 immutable 수동 receipt/envelope로 바꾸거나 명시적으로
  차단한다.
- 모든 테스트 green을 만든 뒤 baseline commit을 분리한다.

### Phase 1 — 계약과 verifier

새 dataclass, canonical hash, fail-closed verifier와 unit test만 구현한다. 실제
삼도식당 파일을 승격하지 않는다.

### Phase 2 — 제1~3화 read-only migration canary

기존 파일을 읽어 P0/P1/StoryChangeRequest로 분류하고 report만 만든다. 원본이나
노션을 자동 수정하지 않는다.

### Phase 3 — B006 native-authoring canary

owner가 B006 방향을 선택한 뒤, 첫 후보를 촬영고 profile로 직접 작성하고
EpisodeScriptText ↔ HumanProductionSurface round-trip을 검증한다. CAMERA 주석은
별도 P1에서 시작한다.

### Phase 4 — production text package

P0/P1 review와 owner external-delivery gate를 구현한다. 실제 외부 전달은 별도
owner 지시가 있을 때만 수행한다.

### Phase 5 — 시각 프리비즈 여부 재판정

실제 storyboard/animatic 반복 작업이 두 번 이상 발생했을 때만 별도 child repo와
handoff adapter를 제안한다.

## 10. 구현 중에도 유지하는 금지선

- 현재 잠금본 수정 또는 파일명 변경
- v0.5를 내용 동일본으로 표시
- CAMERA 주석을 서사 캐논으로 승격
- 노션을 source of truth로 사용
- P2와 외부 제작 전달 승인을 같은 상태로 취급
- 고립 previs 도구를 현재 파이프라인 구현 증거로 주장
- 테스트가 red인 상태에서 새 production gate를 main 기준으로 선언

## 11. owner 결정 및 구현 기록

owner가 다음 핵심 결정을 승인했다.

> `HIL 3 서사 본문`, `사람용 제작 표면`, `촬영 주석`을 서로 다른 hash와
> 승인 상태로 관리하고, Foundry의 현재 끝점을 production text package로 둔다.

v0.6.0에서 Phase 0 테스트 기준선 복구, Phase 1 계약/verifier, Phase 2 읽기
전용 migration canary와 production text package 계약까지 구현했다. 현재
v0.1~v0.5는 여전히 후보·조사 이력이며 승인본이나 외부 전달본이 아니다.
Phase 3의 B006 집필과 실제 P0/P1/P2 승인, 영상 child는 각각 별도 owner 선택과
반복 작업 증거 전에는 시작하지 않는다.
