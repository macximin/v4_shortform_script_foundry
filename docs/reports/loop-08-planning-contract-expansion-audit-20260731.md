# Loop 08 — Planning Contract Expansion Audit

Date: 2026-07-31

Status: implemented contract slice, no real-work candidate, no owner promotion

## Why this loop exists

The first planned real-work canary requires a two-character core, episode-level
emotional payoff, multi-episode guest arcs, season accumulation, a future-season
seed, and production limits on runtime, dialogue load, and principal cast.

The previous HIL 1 contract represented one protagonist and an unlayered payoff
list. HIL 2 did not have resource or world-operation state. The legacy
deterministic `SeriesPlanner` also used public-recognition language that could
silently bias a non-recognition work.

## Implemented boundary changes

### HIL 1

- `core_characters` owns one to three central recurring character contracts.
- `PayoffLayer` separates `episode`, `arc`, `season`, and `future_seed`
  promises.
- `primary_reward` must identify one declared payoff layer.
- Every work must declare at least one episode-cadence payoff.
- `ProductionConstraints` owns the runtime range, principal-character limit,
  action-driven policy, dialogue policy, and optional dialogue-line ceiling.

The old `protagonist` and flat `payoff_promises` accessors remain read-only
compatibility views. New artifacts serialize `core_characters` and
`payoff_layers`.

### HIL 2

- `StoryStateAxis` now includes `resource` and `world_operation`.
- Every arc carries the exact HIL 1 production constraints.
- Arc rewards must identify HIL 1 payoff layers.
- A `future_seed` may be deferred but cannot be paid by the current arc.

### HIL 3 and writer handoff

- Every scene declares `principal_character_ids`.
- Hard verification enforces the HIL 1 runtime range, principal-character
  ceiling, and optional dialogue-line ceiling.
- A closure episode must pay an authorized reward, but it may still defer a
  season-level promise. Closure no longer means that every long-horizon promise
  must be consumed.
- `WriterRequest` exposes core character IDs and typed production constraints
  without exposing raw reference text.
- Writer dispatch fails before backend invocation when the requested runtime is
  outside the HIL 1 range.

### Owner-readable planning output

`planning_artifact` deterministically exports:

- HIL 1 canonical JSON plus a Markdown work-plan candidate.
- HIL 2 canonical JSON plus a Markdown arc-plan candidate.

Each document verifies against the exact source contract content hash. The
Markdown is a review surface, not a second planning authority.

## Bias audit

### Audit A — public-recognition leakage

The deterministic canary remains for regression only. Its terminal enum now
uses the genre-neutral `REWARD_REALIZED` name and its state strings no longer
require public reclassification. Actual work planning remains HIL 1/2-owned.

Decision: retain the canary; do not route real works through it as a universal
season planner.

### Audit B — rubric optimization

The new hard checks cover production feasibility only: duration, principal cast
count, and an explicitly configured dialogue-line ceiling. They do not score
warmth, emotion, character appeal, or dialogue quality.

Decision: keep emotional and character quality in candidate comparison and
BR0/BR1 review. Do not turn the production constraints into a universal creative
score.

## Verification

```text
python3 -m unittest discover -s tests -v
Ran 74 tests
OK

python3 -m compileall -q src tests
passed

git diff --check
passed
```

The checked-in Loop 04 functional-draft canary was regenerated after the
genre-neutral state labels changed and its deterministic-current test passes.

## Remaining boundary

- No actual work facts, HIL 1 candidate, HIL 2 candidate, or owner approval was
  created in this loop.
- No Creative Writer model/API backend was connected.
- No owner review UI exists; the output is Markdown and canonical JSON.
- Production constraints do not infer the right values. The project brief or
  owner must supply them.
- A first real-work canary must compare structurally different HIL 1 candidates
  while keeping the same confirmed Fact Ledger. It must stop before HIL 2 until
  the owner selects or revises an HIL 1 candidate.
