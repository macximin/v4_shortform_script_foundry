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
| `artifacts` | canonical JSON and packet content hashes | packet ownership or promotion |
| `pipeline` | deterministic stage orchestration | creative model execution |

`creative_writer_adapter`는 Functional Draft를 변경 불가 입력 계약으로 받아
완성 대사·지문 후보를 쓰는 별도 단계다. 현재 코어에는 모델 또는 외부 서비스
호출이 없다.

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
