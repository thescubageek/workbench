# Session Journal: adversarial_loop

Append-only, reverse-chronological — newest entry at the top. **No entries yet.**

**Entries open when work starts, not when it ends.** A session does not get to choose how it
ends: a token limit, a closed laptop, or a crashed harness runs no shutdown step. An entry
written only at completion would be silent in exactly those cases, and worse than silent — its
tail would still show the last *finished* phase, so the next session would read a confident,
stale record and never learn that work stopped mid-task. Opening on entry makes the default
residue of an abrupt kill correct: an open entry naming what was being attempted and what came
next.

An open entry beside uncommitted changes means an interrupted task. An open entry beside a
**clean** tree is ambiguous and the tree cannot resolve it: the session may have finished without
closing out, or be **blocked waiting on a human** — a design awaiting approval is exactly this,
and it is the correct residue rather than a fault — or still be running in another session, which
this repository cannot observe at all.

**So read the entry's `Next action` before concluding anything.** The working tree is the
authority on whether work is *in flight*; only the entry says what the work was and what it is
waiting for.

**A heading must end in a literal `(open)` or `(closed)`.** That suffix is what every reader
matches on — the session-start hook, `forge`, `daily-digest`, `resume_handoff`,
`create_handoff`. A heading ending any other way is invisible to all of them, and the failure
is silent: the next session is told "closed" over work that was interrupted.

Entries take these two shapes. **Keep the dates as the literal placeholder `YYYY-MM-DD`.** The
session-start hook finds the newest entry with `grep -E '^## '` and then discards headings whose
date is still a placeholder — so the placeholder is what stops these examples being read as a
real entry. The fence is for readability and is *not* the protection: the hook is not
fence-aware, and these headings still begin at column zero inside it. An example rewritten with
a realistic-looking date would be reported as an interrupted task in every plan generated from
this template, silently, from the moment of creation.

```text
## YYYY-MM-DD HH:MM — <task-id or short label> (open)

- **Task/phase**: <ID and one-line description>
- **Next action**: <the literal next thing to do, specific enough to act on cold>
- **Started at**: <commit hash>

## YYYY-MM-DD HH:MM — <task-id or short label> (closed)

- **Task/phase**: <ID and one-line description>
- **Landed**: <what actually changed>
- **Commits**: <range or hashes>
- **Learned**: <anything that changes how the remaining work should proceed — omit if nothing>
- **Blocked by**: <anything blocking — omit if nothing>
```

<!-- Real entries begin below this line, newest first. -->

## 2026-09-18 20:14 — PHI fix + Phase 7, all 22 tasks (closed)

- **Task/phase**: the PHI regression, then P7-T1 through P7-T22 — close round 2.
- **Landed**: two commits. `1e818ea` restores the Member-ID matcher; `1990b40` closes the
  remaining 21 findings. Counters 46 → 68 of 72.
- **Learned**:
  - **Round 2 found 22 findings and four were created by Phase 6's fixes.** That is the
    plan's most durable result: a fix phase is new unreviewed surface and needs the same
    review as the code it fixed. It is now written into Phase 7's checkpoint as an
    attestation rather than left as a lesson in a journal.
  - **The PHI regression is the shape to remember.** Genericizing an employer name out of a
    de-identification rule also removed the rule's matcher, and the scrub then reported clean
    on a real `BM-CA-12345678`. The edit had a non-safety motive and still needed a safety
    review. The restored rule now *fails closed*: an undeclared repository format widens it
    and can no longer disable it.
  - **`test-guards` earned itself within one commit.** Rewritten to assert *which* finding
    fired rather than just the exit code, it immediately caught a bug the old form could not
    see — the guard-segment walk cut at the first literal `grep`, so `echo "grep || true";
    n=$(grep -c x f)` read as guarded. Verified the new form fails when the fence scanner is
    broken: exit 1, where the old suite stayed 19/19 green.
  - **`check-guards` reported clean on a path that does not exist.** Its own defect class,
    in the script written to catch it, for the fourth time in this plan. It now exits 2 on a
    missing target and refuses to report clean having scanned zero files.
  - **I made the pipe-status mistake twice in this session**, once measuring a regression
    probe through `| tail` and once assuming `$c` word-splits in a `for` loop under zsh. Both
    produced a confident wrong reading in the session that is fixing that exact class.
  - **CI was pinned to a version the tree is not linted with** (0.45.0 against a local
    0.49.0) until I compared them. A pin that differs from the maintainer's version just
    relocates the disagreement into CI.
- **Commits**: `1e818ea`, `1990b40`, and this one.
- **Blocked by**: nothing. Round 3 is gated on explicit user approval — Phase 7 is exactly the
  kind of surface round 2 proved needs reviewing, and P5-T2 onward follow the review.

## 2026-09-18 18:52 — Phase 6, all 21 tasks (closed)

- **Task/phase**: P6-T1 through P6-T21 — close the findings the dogfood review raised.
- **Landed**: 21 tasks, three commits. Phase 6 added to `tasks.md` before any fix, with the
  three pending decisions recorded and resolved. Counters 25 → 46 of 50.
- **Learned**:
  - **The base-ref fix is verified in both directions.** In a scratch repo with no
    `origin/main` and a hostile `REVIEW.md` staged: the old one-liner printed the malicious
    text and exited 0; the new form prints `REVIEW.md NOT READ` and never reads it.
  - **`check-guards` had a fifth hole nobody had found — its guard test.** `|| echo` was
    matched anywhere on the line, so `$([[ $(… | grep -c .) -le 2 ]] && echo 1 || echo 0)`
    read as guarded. That is why `test-quiet`'s two captures survived every prior run. The
    guard is now anchored to the capture itself, which also cleared a false positive the
    first tightening introduced on `wb-prime.sh:177`.
  - **Fixing the checker surfaced more than it closed, which is the expected direction.**
    Widening the detectors immediately flagged `test-count:66` — the "control" assertion that
    asserted the opposite of its own label. It had been passing since it was written.
  - **`test-guards` now exists because none of this was catchable.** 19 planted cases, both
    directions. `check-guards` has been an instance of its own defect class three times in
    this plan; a contract test is the only thing that changes that.
  - **A regression probe, not just a pass.** Reverting `count`'s `status -ge 2` to `-gt 2`
    now fails `test-count` (exit 1). Before P6-T15 it passed 13/13.
  - **The release's own vocabulary gate could never have passed.** Unanchored, it matched
    `rspec` inside "perspective" and `redis` inside "rediscovering". Now word-anchored, and
    the shipped plugin no longer names an employer anywhere — including the `daily-digest`
    PHI guardrail, which now applies to any covered organization without naming one.
  - **I did not measure my own regression probe correctly the first time**: I read the exit
    status through a `| tail -3` pipe and got `tail`'s. Re-measured directly. Worth recording
    because it is the exact class this phase is about, made by the session fixing it.
- **Commits**: `46b90f4`, `410c908`, and this one.
- **Blocked by**: nothing. P5-T2 through P5-T5 are next and are deliberately unstarted — the
  user gated the re-review on explicit approval, and the release follows the re-review.

## 2026-09-18 18:24 — P5-T1 + dogfood adversarial review (closed)

- **Task/phase**: P5-T1 — the `## [2.2.0]` CHANGELOG entry; plus a full `adversarial-review`
  run against PR #25, which is the PR that ships the skill.
- **Landed**: `CHANGELOG.md` gains `## [2.2.0]` (Added / Fixed / Changed / Migration) in the
  existing bolded-lead-sentence style. P5-T1 ticked; counters reconciled 23 → 25.
- **Learned**: the dogfood run returned **22 findings, 18 CONFIRMED**, against the artifacts
  this release ships. Four of the five deliberately-unproven items resolved on their own:
  the built-in leg really does run forked; all five supporting files were read; every
  relative link in the three new skill directories resolves; the shipped model-tier table
  matches the harness enum. The load-bearing ones:
  - `adversarial-review/SKILL.md:71` — `git show "$(git merge-base HEAD origin/main)":REVIEW.md`
    collapses to `git show :REVIEW.md` when `origin/main` does not resolve. `:path` is git's
    **index** syntax, so it reads the staged file and exits 0. The declared security boundary
    inverts into a read of the least trustworthy copy, and the documented absent-tell never
    fires. Reproduced in a scratch repo.
  - `check-guards` has four holes, and the repo it certifies contains the defect it hunts:
    `test-quiet:33` and `:39` carry unguarded `grep -c` captures and the script still prints
    `✅`. It also misses the last line of any file (`flush_pending` is a no-op whose comment
    claims otherwise), never scans the 17 indented ```bash fences, and scans prose in any
    `.md` under `scripts/`.
  - `$REPO` and `$PR` are used by every `gh` command in `reply-to-claude` and
    `adversarial-loop` and assigned by nothing.
  - `git diff --stat <pr#>` is fatal; no step converts a PR number to a range.
  - P5-T3's own vocabulary grep cannot pass: two real `hellobrightline` hits in
    `daily-digest/sources.md`, plus substring false positives (`rspec` inside "perspective",
    `redis` inside "rediscovering").
- **Blocked by**: P5-T2 and P5-T3 should not run until the CONFIRMED findings are
  dispositioned — the release would ship the defects the release exists to prevent.

## 2026-09-18 17:59 — P5-T6 (closed)

- **Task/phase**: P5-T6 — ship plugin/scripts/count with a contract test
- **Landed**: scripts/count + test-count (13 assertions, incl. a control proving grep -c does not
  distinguish), README entry, and a pointer from verification-before-completion
- **Commits**: 042f7af
- **Learned**: writing count exposed two false positives in check-guards — a comment describing
  the bad pattern, and a capture guarded by \$? on the next line. Both were real checker bugs.
  Three responses to this class have now each found a defect in the previous one.
- **Started at**: 3971331

## 2026-09-18 17:55 — handoff written (closed)

- **Task/phase**: session transfer at Phase 5, before the release is cut
- **Landed**: `handoff-2026-09-18-17-55.md`; draft PR #25 opened; 4 knowledge entries added
- **Next action**: a fresh session runs `/wb:adversarial-review 25` against this PR, then
  Phase 5 — P5-T1 CHANGELOG onward, with P5-T6 (`scripts/count`) required before completion
- **Commits**: fd7089d

## 2026-09-18 17:47 — P4-T4 (closed)

- **Task/phase**: P4-T4 — dangling-reference sweep across the whole plugin, run last so it covers
  the documentation change
- **Landed**: sweep narrowed to skill-meaning contexts; found and fixed `wb:loop` in
  touch-grass, a pre-existing dangling reference to a built-in mistaken for a wb skill
- **Commits**: 376173b
- **Learned**: the first sweep matched every backticked token and produced 39 hits, none real —
  a check too broad is as useless as one that cannot fire, just louder. Narrowing to contexts that
  *mean* "a skill" turned 39 false positives into one true one.
- **Started at**: b41834a

## 2026-09-18 17:47 — P4-T5 (closed)

- **Task/phase**: P4-T5 — re-sync help and README now that all three skills exist
- **Landed**: both skills added to help and README; coverage check clean
- **Commits**: d0564c1
- **Started at**: d6c35eb

## 2026-09-18 17:46 — P4-T3 (closed)

- **Task/phase**: P4-T3 — repoint model-help's calibration anchor and add gate-mode rows
- **Landed**: anchor repointed at adversarial-review; two gate-mode rows added, four columns each
- **Commits**: d48956b
- **Learned**: the right session tier for both new skills is Sonnet/medium, which reads as low
  until the fourth column explains it — the cost lives in forked agents, and paying Opus for a
  session that mostly waits is exactly the over-powering the rubric warns about.
- **Started at**: 40e906b

## 2026-09-18 17:46 — P4-T2 (closed)

- **Task/phase**: P4-T2 — repoint daily-digest's two review-family references
- **Landed**: both daily-digest references repointed; no ghost names remain in the file
- **Commits**: fa52b8a
- **Started at**: 1cc7222

## 2026-09-18 17:45 — P4-T1 (closed)

- **Task/phase**: P4-T1 — add the hand-off line to review-prep
- **Landed**: hand-off line near the top of review-prep, framed as same-subject-opposite-shape
- **Commits**: 331924c
- **Started at**: 273e6aa

## 2026-09-18 17:42 — P3-T2 + P3-T3 (closed)

- **Task/phase**: P3-T2 — write plugin/skills/adversarial-loop/SKILL.md
- **Landed**: adversarial-loop/SKILL.md and reference.md, in one commit — see below. Plugin
  enumerates 39 skills; no broken links anywhere
- **Commits**: 68a12f9
- **Learned**: writing the SKILL.md created a dangling link to a file the next task would produce,
  and the link check caught it before commit. One task one commit had to yield to not shipping a
  broken directed read. Also: the five CI/bot mechanics are all the same failure shape as the
  silent-measurement class — an absence that means "not yet" versus one that means "broken".
- **Started at**: 86e8c76

## 2026-09-18 17:39 — P3-T1 (closed)

- **Task/phase**: P3-T1 — write plugin/skills/reply-to-claude/SKILL.md
- **Landed**: reply-to-claude/SKILL.md; plugin enumerates 38 skills; dispositions linked to
  adversarial-review/reference.md rather than restated
- **Commits**: 888c0d5
- **Learned**: the `claude[bot]` login gotcha is the silent-measurement class wearing an API
  filter — a filter on `claude` matches nothing and returns success, so it reads as "no
  findings". Same failure shape as a grep that errors and reports zero.
- **Started at**: 84a096e

## 2026-09-18 17:27 — help/README accuracy (closed)

- **Task/phase**: out-of-plan, user-requested — bring wb:help and README.md up to date
- **Landed**: help and README now cover every shipped skill and the three reference docs; P4-T5
  filed to re-sync after Phase 3, with a runnable coverage check as a Phase 4 criterion
- **Commits**: bce0774
- **Learned**: help had drifted eight user-invocable skills behind, none of it caused by this
  work. The plan had no task to update it, which is the mechanism: documentation that nothing
  checks and no task owns falls behind silently, exactly like the review-skill references this
  whole effort is fixing.
- **Started at**: c2d8700

## 2026-09-18 17:24 — P2-T7 (closed)

- **Task/phase**: P2-T7 — make Phase 2's invariant checks runnable, and run them
- **Landed**: eight Phase 2 criteria rewritten as listing-based, shell-agnostic checks; all run
  and ticked; P5-T3's duplicate link check replaced with the working form rather than left fragile
- **Commits**: 0f40336
- **Learned**: the criteria I wrote at create_tasks time contained the very defects this session
  then spent hours finding — a pipeline form that parse-errors under zsh, and two counts where a
  zero is indistinguishable from a broken command. Writing checks before having been burned by
  them produces checks that look right.
- **Started at**: c8aeaa6

## 2026-09-18 17:18 — P2-T6 (closed)

- **Task/phase**: P2-T6 — write plugin/skills/adversarial-review/SKILL.md, the skill body
- **Landed**: SKILL.md — seven steps plus verify-only mode; all five supporting links resolve;
  plugin loads with 37 skills at ~180 always-on / ~3.3k on-invoke
- **Commits**: 815955e
- **Learned**: declaring `Skill` in `allowed-tools` is untested territory — no shipped skill had
  done it. Loading is unaffected, so the value is at worst inert; whether it actually pre-approves
  the call is still unproven and only P5-T4's smoke session can settle it.
- **Started at**: 1105065

## 2026-09-18 00:54 — P2-T5 (closed)

- **Task/phase**: P2-T5 — write plugin/skills/adversarial-review/reference.md
- **Landed**: reference.md as the adjudication authority; P3-T3 amended in tasks.md to link to
  it rather than restate the dispositions
- **Commits**: 1f0863f
- **Learned**: my own portability check had an unreachable negative branch — piping grep into sed
  masked its exit status, so `|| echo silent` could never fire. The check was right about the
  file and wrong about itself. Same family as everything else this session, in a new disguise.
- **Started at**: 49e0317

## 2026-09-18 00:51 — P2-T4 (closed)

- **Task/phase**: P2-T4 — write plugin/skills/adversarial-review/templates.md
- **Landed**: templates.md — six output shapes, with the reconnaissance summary emitted before
  any spawn so the cost is arguable before it is paid
- **Commits**: 4f347ea
- **Learned**: writing the Checked-and-clear shape was where the probe's correction actually bit.
  The natural framing is "here is what we covered"; the true framing is "here are claims we are
  making", and only the second one implies each line needs a file:line behind it.
- **Started at**: 6d6e92f

## 2026-09-18 00:45 — silent-measurement checks (closed)

- **Task/phase**: out-of-plan — ship a mechanical guard check (1) and change the documented
  measurement idiom to show-don't-count (2); file scripts/count (3) against Phase 5
- **Landed**: plugin/scripts/check-guards (three patterns, each falsified), scripts/quiet
  guarded, verification-before-completion now prefers listing to counting, scripts/count filed
  as P5-T6
- **Commits**: d291042
- **Learned**: the check I wrote to catch silent failures reported clean while holding a real
  finding — `FOUND=1` inside a pipeline subshell. Third occurrence of that trap in this repo,
  and `scripts/lint` already documents it. The pattern across all of this: the assurance
  machinery fails the same way as the thing it assures, so it needs the same scrutiny rather
  than more trust.
- **Started at**: 40d041e

## 2026-09-18 00:31 — L1 fix (closed)

- **Task/phase**: out-of-plan — close L1, the last unfixed defect from the P1-T3 probe
- **Landed**: indented-heading ERROR in validation-rules.md (before the extraction) and a
  Check it in journal-entries.md, both falsified; limitation recorded rather than engineered around
- **Commits**: c835266
- **Learned**: the silent-measurement class caught me a fourth time, inside the verification of
  the fix for the third — `grep -c` printing 0 and exiting 1 made `|| echo 0` emit a second
  zero, producing a bogus "WOULD FLAG". `wb-prime.sh:55-63` documents exactly this. Knowing a
  trap and not reaching for the guard are different things, which is an argument for the guard
  being in the prompt rather than in anyone's memory.
- **Started at**: 90a05c0

## 2026-09-18 00:26 — P2-T3 (closed)

- **Task/phase**: P2-T3 — write plugin/skills/adversarial-review/prompts.md
- **Landed**: prompts.md — shared evidence-contract preamble, stance agent, lens agent,
  verifier, and the four-value tier table
- **Commits**: 307fff8
- **Learned**: the stance agent's prompt is better written as "review only what a hunk-scoped pass
  cannot see" than as a second sweep — it composes with the built-in's `low` pass instead of
  contradicting its explicit hunk-only instruction, which was the Tier 0 conflict from
  explore_design, resolved in prompt text rather than in the ladder.
- **Deviation**: placed the verifier prompt here though the task did not assign it; recorded in
  tasks.md Implementation Notes.
- **Started at**: fb82f8e

## 2026-09-18 00:23 — P2-T2 (closed)

- **Task/phase**: P2-T2 — write plugin/skills/adversarial-review/lenses.md
- **Landed**: plugin/skills/adversarial-review/lenses.md — ten lens rows stated as behaviour
  rather than framework, four mandatory triggers that raise the tier, signal-ranked category
  recognition, the six-lens guard, and user-named lenses used verbatim
- **Commits**: 868981a
- **Learned**: the hard part of generalising was not removing framework names but replacing them
  with something that still discriminates — "persistence, data models, background jobs" carries
  the same selection power as the original's "models, commands, jobs" without naming a stack.
  Path conventions had to be ranked last as a signal; they are what mislead across ecosystems.
- **Started at**: 15e7dec

## 2026-09-18 00:14 — silent-check root cause (closed)

- **Task/phase**: out-of-plan, user-requested — fix the cause of the recurring
  "measurement fails and reads as success" class rather than more instances
- **Landed**: FALSIFY added as step 2 of verification-before-completion's gate, with the
  mechanism table and authoring red flags; pointers added in create_tasks' template and
  validate_execution Step 3. Stated once, referenced twice.
- **Commits**: 375d5c2
- **Learned**: the old gate could not catch this class by construction — all three failures
  passed IDENTIFY/RUN/READ/VERIFY. Also that the glob defect is shell-dependent: zsh reports 0
  where bash reports the truth, so "it worked when I ran it" is weaker evidence than it reads as.
- **Started at**: 4a01988

## 2026-09-18 00:08 — P2-T1 (closed)

- **Task/phase**: P2-T1 — write plugin/docs/reference/code-review-integration.md
- **Landed**: plugin/docs/reference/code-review-integration.md — rely-on/do-not-rely-on split,
  ReportFindings contract, /verify chaining, and the model-family table demoted to a dated
  observation with a working `Check it`
- **Commits**: bd654e7
- **Learned**: my own `Check it` command was unfirable on first write — `strings` emits the
  em-dash as the literal `\u2014`, so matching it with `.` returned nothing and read as clean.
  Every check in a reference doc needs running before the doc is committed.
- **Started at**: 17e3fba

## 2026-09-17 23:57 — P1-T4 (closed)

- **Task/phase**: P1-T4 — close out the probe document and delete the fixture
- **Landed**: probe document closed out with both commits in its frontmatter; fixture and bare
  origin deleted. Phase 1 complete — 4/4 tasks.
- **Commits**: 83ff352
- **Learned**: nothing new beyond P1-T3's findings; this task was bookkeeping and cleanup.
- **Started at**: 9f3caf1

## 2026-09-17 23:42 — P1-T3 (closed)

- **Task/phase**: P1-T3 — run both halves of the probe and append verbatim results
- **Landed**: both halves run and appended to the probe document; verdict — the wrapper shape
  holds. Pre-registration untouched.
- **Commits**: 9f3caf1
- **Learned**: a leg's *clearance* can be wrong, and only verification catches it. The lens leg
  cleared `daily-digest/sources.md:77`; the built-in flagged it; source settled it as a real
  bug. Also: the recon step's own measurement can fail silently and read as clean.
- **Blocked by**: nothing — B1 is recorded against P4-T2, not blocking.
- **Started at**: ef24356

## 2026-09-17 23:42 — P1-T2 (closed)

- **Task/phase**: P1-T2 — pre-register the wrapper-shape probe before running it
- **Landed**: thoughts/2026-09-17-wrapper-shape-probe.md, pre-registration only — rubric,
  predictions for both branches, and pass/fail conditions for Half A (sizing) and Half B (merge)
- **Commits**: ef24356
- **Learned**: the probe had to split targets. `/code-review` resolves from the current
  repository, so the fixture answers the sizing question and this repository answers the merge
  question. Skill-file loading is not probed here at all; P5-T4 covers it.
- **Started at**: d994b1f

## 2026-09-17 23:35 — P1-T1 (closed)

- **Task/phase**: P1-T1 — build the throwaway fixture repo for the wrapper-shape probe
- **Landed**: fixture at /tmp/wb-adv-probe with bare origin; `trivial` (docs, 4 insertions) and
  `risky` (app/auth.py, 6 changed lines, two planted defects). Build cwd recorded in tasks.md.
- **Commits**: be0d107
- **Learned**: the risky branch came out at 6 lines while carrying a privilege-escalation path —
  a cleaner demonstration of the LOC-is-not-complexity premise than the plan assumed.
- **Started at**: 2f00ea9

## 2026-09-17 23:21 — create_tasks (closed)

- **Task/phase**: P0-T4 — execution plan for 2026-09-17-adversarial_loop
- **Landed**: tasks.md — 6 phases, 27 tasks (4 already complete), 5 checkpoints. Phase 1 is a
  tracer bullet on the wrapper shape; everything after it is contingent on that verdict.
- **Commits**: plan promoted in a1793aa; this revision pending
- **Learned**: A1 proved the built-in is *invocable*, not that the two-leg *shape* holds — recon
  sizing, both legs spawning, two finding sets merging into one verified report. That gap is what
  Phase 1 exists to close before any shipped file is written.
- **Started at**: a1793aa

## 2026-09-17 21:31 — create_design (closed)

- **Task/phase**: P0-T3 — design for 2026-09-17-adversarial_loop
- **Landed**: design.md written and approved (`status: approved`); all 11 open records resolved —
  6 assumptions validated (A1/A2/A4/A5 by probe, A3 dissolved by PD1, A6 from knowledge.md) and
  5 pending decisions decided. Separately fixed the journal-ordering contract across the plugin
  and six defects the built-in review surfaced.
- **Commits**: see the two commits made at close of this entry
- **Learned**: the built-in `/code-review` is invocable from a wb skill via the `Skill` tool and
  runs **forked**, so it does not consume the caller's context — this is what makes the two-leg
  design affordable, and it was the assumption everything else rested on. Running it at `low` and
  `high` on our own tree found six real defects, three of them incomplete applications of my own
  journal fix.
- **Started at**: 46ef587
- **Superseded**: this entry was closed by writing a *second* heading (the 18:00 entry) rather
  than editing this one in place — the failure `journal-entries.md` names. Left in place with its
  state corrected rather than deleted, so the record of the mistake survives.

## 2026-09-17 19:15 — explore_design + resolve_questions (closed)

- **Task/phase**: architecture exploration, then all 11 open questions resolved
- **Landed**: `thoughts/2026-09-17-adversarial-review-architecture.md` (direction B, wrapper +
  lens injection, reconnaissance tiering); 11 decisions in `design.md` →
  `## Technical Decisions` → `### Resolved Decisions`; every `research.md` question row now
  carries a pointer; follow-up research appended on the built-in review machinery
- **Commits**: none yet (plan directory is gitignored until promoted)
- **Learned**: the built-in `/code-review` is a full multi-agent reviewer (8–10 finder angles,
  CONFIRMED/PLAUSIBLE/REFUTED vocabulary, `ReportFindings`), and `/verify` already implements
  prefer-the-repo's-own-skill with a bootstrap fallback. `review-strict` is not a real artifact
  anywhere. Both facts reshaped the design from "port two skills" to "wrap the standard install".

## 2026-09-17 18:00 — create_research (closed)

- **Task/phase**: P0-T2 — research for 2026-09-17-adversarial_loop
- **Landed**: research.md complete — 4 parallel agents, dependency + portability inventory of the two adversarial skills, wb shipping contract, 8 open questions
- **Commits**: none yet (plan directory is gitignored until promoted)
- **Learned**: `review-reef`, `review-security`, `review-strict`, `review-terse` are dangling symlinks into a missing `/Users/scraig/projects/prompts/` tree — adversarial-review's stated rule-catalogue dependency is unreadable. `plugin/skills/daily-digest/SKILL.md:204,278` and `plugin/skills/model-help/SKILL.md:160` already route to that non-existent review-skill family.

## 2026-09-17 17:53 — create_research (superseded, closed)

- **Task/phase**: P0-T2 — research for 2026-09-17-adversarial_loop
- **Next action**: spawn the Step 4 agents, then synthesize into research.md
- **Started at**: 46ef587
