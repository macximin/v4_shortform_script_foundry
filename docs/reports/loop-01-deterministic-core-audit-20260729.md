# Loop 01 deterministic core audit

- Date: `2026-07-29`
- Scope: in-memory contracts through three-episode `ScriptPacket`
- Result: `conditional_pass`
- External model calls: none
- Production or owner-approved scripts: none

## Implemented

- immutable `FactLedger` with certainty and source bindings
- versioned `GenreGrammarPacket`
- deterministic `RendererRouter`
- three-episode `SeriesPlan`
- monotonic `EpisodeState` transitions
- prose-free `ScriptPacket`
- hard `ScriptVerifier`

## Evidence

`py -3.12 -m unittest discover -s tests -v`

- 9 tests passed
- the same Fact Ledger produced different primary renderer, threat, proof mode,
  reward target, and final reward under two genre grammar packets
- proof state advanced `unknown -> indicated -> materialized ->
  publicly_recognized`
- every generated packet remained `candidate`
- the verifier rejected simulated automatic promotion

## Audit findings

### L01-F01 — approval hash is syntactically checked but not content-bound

Severity: high

An approved grammar currently requires a 64-character SHA-256 string, but the
code does not prove that the hash was calculated from the canonical grammar
payload. A valid-looking unrelated hash can pass construction.

Required correction:

- define canonical serialization for approval-bearing packets
- calculate a content SHA-256 from the packet excluding approval state
- require an approved packet's owner hash to equal that content hash

### L01-F02 — facts bound the router but do not yet determine lens eligibility

Severity: high

The router refuses to run without confirmed facts and carries their IDs into the
decision, but renderer selection is currently driven by grammar weights alone.
It does not prove that the confirmed facts support the selected proof mode.

Required correction:

- add neutral semantic tags to facts
- allow a renderer preference to declare required confirmed fact tags
- fail closed if no renderer is eligible

### L01-F03 — packets are in-memory only

Severity: medium

The vertical slice has typed Python values but no canonical JSON export. It
cannot yet produce a stable cross-repo packet or receipt.

Required correction:

- reuse the canonical serializer introduced for L01-F01
- add round-trip or exact snapshot evidence before any Eval handoff

### L01-F04 — reference-distance verification is not implementable yet

Severity: expected deferral

`ScriptPacket` intentionally contains no prose and the Writer Adapter does not
exist. Reference phrase distance belongs to the later draft-verification loop,
not this structural packet loop.

## Decision

Do not add a Writer Adapter yet. Correct L01-F01 through L01-F03, expand failure
tests, rerun the vertical slice, and perform Loop 02 audit first.
