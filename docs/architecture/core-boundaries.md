# Core boundaries

| Module | Owns | Does not own |
|---|---|---|
| `fact_ledger` | fact certainty and source bindings | plot interpretation |
| `genre_grammar` | versioned renderer preferences and evidence bindings | reverse-analysis source ownership |
| `renderer_router` | active reward/threat/proof lens selection | fact mutation or prose |
| `series_plan` | episode function, proof curve, reward and deferral | dialogue or scene prose |
| `episode_state` | state transitions and deferred rewards | dialogue generation |
| `script_packet` | thin writer-facing episode contract | model execution |
| `verification` | contract and boundary checks | owner approval |
| `artifacts` | canonical JSON and packet content hashes | packet ownership or promotion |
| `pipeline` | deterministic stage orchestration | creative model execution |

`writer_adapter`는 독립 장르 문법 packet과 draft verification 계약이 승인된 뒤
별도 추가한다. 현재 코어에는 모델 또는 외부 서비스 호출이 없다.
