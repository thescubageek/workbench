# The findings ledger, and the thrash breaker

**Read this when a step directs you to.** It is the plugin's single authority on what a review
loop records between rounds, and on when the loop must stop reviewing and escalate.

It exists because of a measured failure. Across four adversarial review rounds on this plugin,
the fixes introduced defects at roughly the rate the reviews removed them:

| Round | Findings | In the previous fix's surface | Scope |
| ----- | -------- | ----------------------------- | ----- |
| 1 | 22 | — | full diff |
| 2 | 22 | 14 (64%) | full diff |
| 3 | 12 | ~8 (67%) | scoped to ~12% of the surface |

**The rate did not decay, and normalised for scope it rose.** Nothing in the loop could see
that, because the gate is a *level* test — it measures the current round, never the trend — and
because there was no record of previous rounds to compare against. A human had to notice.

## The ledger

`docs/plans/<plan>/review-log.md` where the work has a plan directory. **Where it does not, the
ledger still has to exist somewhere the next round can read it** — pick one location, name it in
the round report, and use that one for every round of the run. There is no version of this loop
that runs without a ledger: both Blocking triggers below read it, and a file that was never
created reads exactly like a clean one.

One row per finding per round:

| Field | Meaning |
| ----- | ------- |
| `round` | which pass raised it |
| `file:line` | where |
| `class` | a short slug — the same defect in the same place next round is the same class |
| `verdict` | the reviewer's label: `CONFIRMED` or `PLAUSIBLE` |
| `disposition` | yours: `Valid`, `Wrong`, `Over-fitted`, `Real but disproportionate`, `Pre-existing` |
| `evidence` | what settled it — the `file:line` that disproved it, or the commit that fixed it |
| `introduced_by` | `prev-fix` or `pre-existing` — **derived, never judged** |

**`introduced_by` is computed, not decided.** Intersect the finding's path with the files the
previous round's fixes touched:

```bash
git diff --name-only <previous-round-base>..HEAD
```

A finding in a file that list contains is `prev-fix`. That is the whole rule, and it must stay
mechanical: a session asked to judge whether it caused a defect is the least reliable witness
available.

**The ledger is also what makes the gate auditable.** Without it, *"no finding adjudicated
Valid"* is a claim the session makes about itself, settled by nothing a human or the next
session can check — and a loop can satisfy it by declaring everything `Wrong`.

## The breaker

Evaluated after each round, from the ledger.

| Trigger | Mode |
| ------- | ---- |
| A **mirror-image regression** — a new finding that is the inverse of one already fixed | **Blocking** |
| The **introduced-rate fails to fall** between two consecutive rounds | **Blocking** |
| The **same file** appears in three consecutive rounds | Advisory |

**A trend test, not a threshold.** Fire on *"the rate did not fall from round N−1 to N"*, never
on *"the rate exceeds X%"*. That is scale-free, needs no magic number, and transplants to a
repository whose numbers look nothing like these. It is also the correct shape: the original
diagnosis was that the gate is a level test and so cannot see oscillation, and fixing that with
another level test would repeat the mistake.

**Minimum-N floor: three findings.** Below that the rate is meaningless — one of two is 50% and
says nothing — so do not evaluate the trend at all.

**Blocking means stop and surface, not refuse.** The user says proceed and it proceeds. The
asymmetry that matters is that a block requires an answer while an advisory can be stepped past
in silence. This departs from the plugin's non-blocking advisory precedent deliberately: those
are cost optimisations, and getting one wrong wastes tokens. This guards against continuing to
ship defects while believing you are fixing them.

### Why a mirror-image regression blocks on its own

It is near-proof that a fix was **pattern-matched rather than understood**. Both observed
instances came from the same shape — generalising from the single input the finding showed:

- the fix for *"a fixed path gets reused across runs"* shipped a `mktemp` template whose `X`s
  were not trailing, which on BSD **is** a fixed path;
- the fix for *"a guard on a later capture excuses an earlier one"* shipped *"a guard on an
  earlier capture excuses a later one"*.

## What to do when it trips

**Stop fixing. Do not run another round.**

A review loop reviews diffs, and a design defect is not in the diff — so the loop cannot fix one
by construction. It will keep finding its symptoms, forever, and each fix will look locally
reasonable. Thrashing is the loop's signal that it is operating above its competence.

Escalate out of the loop and back into the pipeline: `create_research`, then `create_design`, on
the component that tripped it. **Require a tracer bullet before the next attempt** — one bounded
probe at the assumption every candidate fix shares, so its result can cull whole branches.

That path is not hypothetical. `check-guards` tripped all three triggers, the escalation
produced a probe that scored three implementations against one corpus, and the verdict — rebuild
rather than patch a fourth time — retired six open findings at once by replacement.

## Provenance of the numbers

Every threshold here derives from **this plan, rounds 1–4, n=1**: one repository, one plan,
prose-heavy, with the same model reviewing and fixing. The **relation** generalises — a
mirror-image regression is a semantic relation, not a rate. The **numbers** do not: a repository
with real tests would start far below 64%. Treat them as a starting point, and say so wherever
they are restated.
