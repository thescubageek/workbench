---
name: tracer-bullet
description: Use when about to fan out into multiple speculative approaches, or start a large build that rests on an unverified assumption - fire one cheap probe at the riskiest load-bearing uncertainty FIRST, so its result can cull whole branches of wasted work. Activates at points of high uncertainty, before committing to a path.
---

# Tracer Bullet

Before committing to a path under uncertainty, fire one cheap probe at the riskiest load-bearing assumption. Let the result cull the misguided branches.

**Core principle:** One deep dive that invalidates whole approaches is cheaper than discovering they were wrong after you built them.

## The Iron Law

```
DON'T COMMIT TO N APPROACHES (OR A BIG BUILD) ON AN UNTESTED
LOAD-BEARING ASSUMPTION WHEN ONE PROBE WOULD RESOLVE IT
```

Generating options on paper, or starting implementation, while the decisive
unknown stays unknown is gambling. Probe first.

## When to Fire

Fire a tracer bullet when **ALL** of these hold:

1. **Branching or big**: you're about to generate multiple candidate approaches, OR start a large build / multi-phase plan.
2. **Load-bearing uncertainty**: those options (or that build) share an assumption you cannot currently evaluate — and the answer changes which path is viable.
3. **Cheap probe exists**: one bounded action would resolve it — read the one file end-to-end, run a minimal end-to-end slice, make the one API call, run the one query, write the one throwaway spike.
4. **High cull**: resolving it eliminates options or reorders significant downstream work.

If all four hold, run the probe **before** presenting options or writing code.

## The Economics

```
probe NOW  when  cost(probe)  ≪  E[ cost of pursuing the wrong path ]
```

The probe earns its keep by what it *kills*, not what it builds. Aim it at the
assumption whose failure would waste the most work.

## Keep It Bounded

A tracer bullet that sprawls becomes the scope creep it was meant to prevent.

- **One** assumption — the single highest-leverage one. Not a survey.
- **Throwaway or thin** — a spike you discard, or a minimal end-to-end slice. Not the feature.
- **Step-boxed** — smallest action that flips the unknown to known.
- **Stop on answer** — the moment the assumption resolves, stop. Don't gold-plate, don't keep digging, don't expand into the build.

## Report What It Culled

After the probe, state plainly:

- What the probe found (the evidence).
- Which approaches/assumptions it **killed or confirmed**.
- What now survives to be decided or built.

Culling is the deliverable. "Probe found X, so Options B and C are out" beats a tidy options table that ignored the unknown.

## Common Rationalizations

| Excuse | Reality |
| -------- | --------- |
| "I'll list the options first, validate later" | Validating later means building on the assumption you skipped. Probe the load-bearing one now. |
| "I'm fairly sure it works that way" | Fairly sure is the trigger, not the excuse. One read settles it. |
| "Probing will slow me down" | Probing is faster than building the wrong thing and unwinding it. |
| "I'll find out during implementation" | Finding out mid-build is the expensive path this skill exists to avoid. |
| "There's no single decisive unknown" | Then this doesn't apply — proceed. Don't manufacture a probe. |

## Red Flags - STOP and Probe

- About to present 2–3 approaches whose viability all hinge on the same unverified claim.
- Starting a multi-phase build on "assuming X works...".
- Tracking the decisive assumption in a "validate later" table instead of resolving it.
- Saying "we'll see if this works once it's built."

**All of these mean: identify the load-bearing assumption, fire one bounded probe, then proceed.**

## Integration with wb Commands

In `/wb:create_design`, before **Step 4 (Solution Exploration)** presents options:
ask whether one probe would collapse the option set. If yes, run it and report
the cull before listing what survives. A tracer bullet resolves the
highest-leverage entry in the design's **Assumptions** table *now* rather than
deferring every assumption to a beads "validate later" issue.
