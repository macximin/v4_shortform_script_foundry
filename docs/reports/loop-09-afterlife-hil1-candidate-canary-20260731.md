# Loop 09 — 저승식당 HIL 1 Candidate Canary

Date: 2026-07-31

Status: three unapproved HIL 1 candidates, no HIL 2 descent

## Shared authority

The candidate set uses one shared Fact Ledger with three source classes:

- current owner instructions for immutable setting and story-function boundaries;
- the production-team relay for distribution, tone, payoff, runtime, action, and
  principal-cast constraints;
- the current Storyyard episode 1–3 read surface for existing work facts.

Confirmed facts, relayed brief facts, and inferred operating identity remain
separate records. No candidate changes the existing setting.

Common invariants:

- the present-tense main story is Doyun and the underworld girl running the
  restaurant;
- they are not reframed as father and daughter;
- the real-world daughter is a long-horizon return purpose and future-season
  seed, not the per-episode engine;
- every episode pays an emotional turn;
- an active story unit moves or closes within a two-to-three episode band;
- runtime is 180–300 seconds;
- state change is action-driven;
- each scene has at most three principal characters.

## Candidate set

### A — emotional mystery

Primary reward: `guest_emotional_turn_each_episode`

The gap between a guest's surface order and unspoken emotion is narrowed through
action and cooking. A guest need not lie, and a hidden-story twist is not
mandatory.

Main risk: formulaic secret reveals and food reduced to an answer announcement.

### B — restaurant accumulation

Primary reward: `restaurant_operational_accumulation`

Each resolved story unit changes one durable restaurant affordance such as an
ingredient, menu, space, or rule.

Main risk: dead guests becoming upgrade materials and the healing tone drifting
into business-growth progression.

### C — duo operating relationship

Primary reward: `doyun_girl_operating_trust`

Guest work moves decision authority and operating trust between the two
co-leads.

Main risk: repetitive arguments, the girl becoming a blocker, or the
relationship sliding into a substitute father-daughter frame.

## First recommendation

Candidate A is the strongest primary HIL 1 because it directly realizes the
production brief's per-episode emotional payoff and uses Doyun's observed
competence as a means rather than the final reward.

B may contribute a small season residue and C may contribute a relation-authority
delta, but neither should receive equal primary weight. This is a recommendation,
not an owner approval.

## Fail-closed boundary

Each candidate binds a real pending-status premise-distance receipt object:

```text
status = pending_not_evaluated
promotion_allowed = false
```

The hash records the blocker and must not be described as a pass. No HIL 1 owner
approval receipt exists. The candidate set must stop before HIL 2 until the owner
selects, combines with explicit hierarchy, or requests revision.

## Verification

```text
python3 tools/build_afterlife_restaurant_hil1_candidates.py --check
passed

python3 -m unittest discover -s tests -v
Ran 77 tests
OK
```

The canary tests verify:

- exactly three candidates;
- one shared Fact Ledger hash;
- structurally distinct primary rewards;
- the Doyun/underworld-girl core pair;
- the no-father-daughter invariant;
- future-seed treatment of the real-world daughter;
- three-principal production constraint;
- exact canonical content hashes;
- no false premise-distance promotion readiness.
