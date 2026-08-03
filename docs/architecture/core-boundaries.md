# Core boundaries

| Module | Owns | Does not own |
|---|---|---|
| `fact_ledger` | fact certainty and source bindings | plot interpretation |
| `genre_grammar` | versioned renderer preferences and evidence bindings | reverse-analysis source ownership |
| `grammar_import` | manually copied approved abstract blueprint envelopes and hash verification | source media, reverse scripts or automatic cross-repo sync |
| `renderer_router` | active reward/threat/proof lens selection | fact mutation or prose |
| `series_plan` | episode function, proof curve, reward and deferral | dialogue or scene prose |
| `episode_state` | state transitions and deferred rewards | dialogue generation |
| `script_packet` | thin writer-facing episode contract | model execution |
| `verification` | contract and boundary checks | owner approval |
| `draft_script` | scene purpose, observable action, dialogue function, information/state deltas and cliff obligation | finished dialogue or prose |
| `draft_verification` | exact packet binding, information timing, state continuity, cliff and source distance | creative quality or owner approval |
| `approval` | immutable HIL revisions, content/receipt hash separation, owner approval, stale propagation and resume boundary | story generation or reviewer identity authentication |
| `canonical_package` | HIL 1 creative north star, operating identity, agency range, audience information principles and renderer range | event order, exact reveals or episode prose |
| `arc_contract` | HIL 2 state transition, multi-axis story state, episode band and revision proposal | fixed episode allocation or finished dialogue |
| `beat_patterns` | selectable renderer-compatible episode function patterns | universal beat count or story formula |
| `episode_script` | HIL 3 finished script candidate and hard arc/runtime/state/reward binding | creative preference or automatic promotion |
| `episode_script_text` | owner-approved story text split into stable ordered scene atoms | shooting presentation, camera directions or automatic revision |
| `production_surface` | deterministic human-readable shooting-script presentation and P0 equivalence verification | story changes or directing decisions |
| `production_annotation` | hash-bound camera, shot, insert and edit suggestions anchored to text atoms | screenplay text mutation or owner approval |
| `story_change_request` | explicit owner decision route for dialogue, action, order and continuity changes found during production review | silently revising approved text |
| `production_gate` | exact-hash P0/P1/P2/external approval receipts and role policy | identity authentication or automatic external approval |
| `production_package` | exact approved text, verified surface, reviewed annotations and receipts as one candidate package | video generation, delivery or promotion |
| `artifact_graph` | dependency DAG, cycle rejection, deterministic order and downstream invalidation | artifact content generation |
| `writer_adapter` | backend-neutral writer request, strict structured-output parsing and unscreened draft projection | source/reference access, model vendor selection or promotion |
| `source_distance_import` | manual Eval receipt verification and exact draft projection binding | source comparison, threshold calibration or raw reference text |
| `creative_review` | common creative floor, independent BR0/BR1, structurally distinct candidate set and promotion readiness | hard fact verification or owner substitution |
| `artifacts` | canonical JSON and packet content hashes | packet ownership or promotion |
| `pipeline` | deterministic legacy-canary orchestration and hard fail-fast | creative model execution |

기존 `Functional Draft`는 EP07 evidence-reversal canary의 엄격한 scaffold다.
새 Creative Writer Adapter는 HIL 1·2 hard invariant와 선택된 Beat Pattern을
보존하되, 장면 수·비트 순서·시간·공개 방식을 후보별로 바꿀 수 있어야 한다.
현재 코어에는 모델 또는 외부 서비스 호출이 없다. 실제 backend는
`WriterBackend` protocol을 구현해 별도 주입하며, adapter는 backend가 어떤
서비스인지 알지 않는다.

## Production-text boundary

HIL 3 owner 승인 뒤의 제작 표면은 승인 대본을 직접 고쳐 쓰지 않는다.

```text
EpisodeScriptText
  -> deterministic HumanProductionSurface -> P0 exact-equivalence receipt
  -> separate ProductionAnnotationSet      -> P1 review receipt
  -> ProductionTextPackage                 -> P2 owner/producer decision
  -> future ShotPlan / GeneratedVideo
```

대사·지문·순서·연속성 변경이 발견되면 `StoryChangeRequest`로 되돌아가 owner
승인 뒤 새 `EpisodeScriptText` revision을 만든다. 새 text hash는 이전 surface,
annotation, package와 향후 영상 노드를 모두 stale로 만든다. 외부 전달 gate는
owner만 승인할 수 있고 현재 package builder는 이를 항상 `false`로 둔다.

## Source-distance boundary

```text
WriterDraft projection (Foundry)
  -> manual input to Eval
  -> calibrated source-distance receipt (no raw source)
  -> manual JSON copy
  -> receipt hash + candidate projection hash verification
  -> EpisodeScriptCandidate(status=candidate)
```

`review_required`나 `fail` receipt는 HIL 3 후보를 만들 수 없다. `pass`여도
정책 tier가 `production_approved`가 아니면 실제 후보 경로에서 거절한다.
합성 canary는 테스트가 별도로 허용한 경우에만 계약 검증에 쓴다. 기준값의
소유와 보정은 Eval, 원문과 권리 상태는 Reference가 소유한다.

## Manual import boundary

`shortform_reverse_lab`에서 가져올 수 있는 것은 owner 승인된 추상 기능 청사진뿐이다.

```text
approved functional blueprint
  -> manually copied JSON envelope
  -> payload SHA-256
  -> source blueprint SHA-256 binding
  -> grammar canonical owner approval SHA-256
  -> GenreGrammarPacket
```

원본 영상, 역대본, 고유명사·직접 대사·정확한 금액·고유 사건 배열은 이 경계를
넘지 않는다. runtime 자동 read, child 간 writeback과 승인 상태 자동 추적도
두지 않는다.
