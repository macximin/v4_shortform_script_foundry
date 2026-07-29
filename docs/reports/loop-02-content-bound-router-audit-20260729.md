# Loop 02 content-bound router audit

- Date: `2026-07-29`
- Scope: canonical approval hash, fact-tag eligibility, pipeline orchestration,
  artifact envelope, and verifier failure matrix
- Result: `pass_for_pre_writer_vertical_slice`
- External model calls: none
- Real reference text or production story data: none

## Loop 01 finding closeout

| Finding | Resolution | Evidence |
|---|---|---|
| L01-F01 approval hash not content-bound | closed | changing approved grammar content invalidates its prior hash |
| L01-F02 facts did not determine lens eligibility | closed | unsupported fact tags fail closed; irrelevant facts are not proof-bound |
| L01-F03 packets were in-memory only | closed | canonical JSON artifact envelope with exact payload SHA-256 |
| L01-F04 reference distance absent | deferred by boundary | no prose exists before Writer Adapter |

## Acceptance evidence

`py -3.12 -m unittest discover -s tests -v`

- 19 tests passed
- same Fact Ledger, two approved genre profiles:
  - selected different primary renderers
  - produced different threats and proof modes
  - produced different reward targets and final reward IDs
- three episodes advanced:
  - `unknown`
  - `indicated`
  - `materialized`
  - `publicly_recognized`
- every generated Script Packet remained `candidate`
- generated packets passed hard verification
- simulated auto-promotion, stale approval hash, unsupported renderer,
  nonconsecutive state, runtime corruption, and unconfirmed proof failed
- the production pipeline runner returned three packets and four states
- canonical artifact envelope verified its exact payload hash

## Remaining boundaries

This pass proves a structural generator, not a finished screenplay generator.

- no Writer Adapter
- no dialogue, action lines, or Fountain export
- no reference-distance check because no prose is generated
- no BR0/BR1 run because `shortform_script_eval` has no approved rubric
- no real Genre Grammar Packet has been promoted from Reverse Lab

## Decision

The initial goal's deterministic three-episode vertical slice is accepted.
Do not add a model-backed Writer Adapter merely because the structural tests
pass. The next owner gate should choose one real versioned Genre Grammar
Candidate and approve the draft-output and reference-distance contracts.
