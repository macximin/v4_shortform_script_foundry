# Core boundaries

| Module | Owns | Does not own |
|---|---|---|
| `fact_ledger` | fact certainty and source bindings | plot interpretation |
| `renderer_router` | active reward/threat/proof lens selection | fact mutation or prose |
| `episode_state` | state transitions and deferred rewards | dialogue generation |
| `script_packet` | thin writer-facing episode contract | model execution |
| `verification` | contract and boundary checks | owner approval |

`writer_adapter`는 수직 슬라이스에서 위 다섯 경계가 증명된 뒤 별도 추가한다.
현재 skeleton에는 모델 또는 외부 서비스 호출이 없다.
