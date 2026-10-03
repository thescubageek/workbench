---
created: 2026-09-28
type: exploration
project: guard_lexer_and_pr_identity
topic: how check-guards lexes a shell line, and what adversarial-review treats as a PR's head
status: decided
---

# Exploration: the lexer, and PR identity

Two decisions, explored together because the same breaker trip escalated both. Identity was
decided in discussion; the lexer was narrowed to two directions and decided by a tracer bullet
the same day. Each has its own record below so `create_design` can formalize both.

## Decision Record — PR identity

**Chosen direction**: I-A — `adversarial-review` identifies a PR head by its commit
(`headRefOid`) and `isCrossRepository`, not by branch name. On the PR's own checkout it reviews
to local `HEAD` only when `HEAD` descends from that OID, and discloses the local commits.
Otherwise it fetches `refs/pull/<N>/head` into `refs/remotes/origin/pr/<N>` as a named,
disclosed step and reviews that. Steps 1 and 2 resolve identity once, in one function that Step 2
reads from rather than recomputes.

**Rationale**: the plugin's rule is that checking a target out is a state change nobody asked
for; a fetch into a remote-tracking ref touches no worktree and no local branch, and it is the
only way the loop can review a PR the user is not on, which design decision Q4 of the parent
plan requires. The mirror-image pair (R9-T2/R9-T26 → R10-T3) came from two independent copies of
a name-only test; one function by OID retires the class rather than the third instance. The
user's words: "Confirmed", on the statement above, 2026-09-28.

**Rejected**:

- **I-B — resolve by commit, refuse rather than fetch** — correct on the cases it can see, but
  the loop then stops at Phase 1 on every off-checkout target: a narrower loop reported as the
  same thing, exactly what Q4 rejected.
- **I-C — keep name matching, add a fork check** — the smallest change, but it keeps two
  independent resolutions in Steps 1 and 2 that already drifted once, and it still reviews
  `origin/<head>` at whatever the last fetch was (R10-T4 unfixed).

**Revisit if**: the plugin is ever pointed at a host where a PR's head is not fetchable from a
`refs/pull/<N>/head`-style ref. GitLab is out of scope by the parent plan's design; if that
changes, the fetch step needs a per-host spelling.

**Also settles**: research Q2 (a fetch of a pull ref into `refs/remotes/` is permitted, named
and disclosed) and Q3 (a same-checkout PR target reviews `HEAD` when `HEAD` descends from
`headRefOid`, with the local commits disclosed; otherwise the fetched OID).

**Tracer bullet required before any fix**: in a scratch clone, construct a fork PR whose branch
name matches the local checkout — or stub `gh` to return `isCrossRepository: true` with a
matching `headRefName` — and show the OID test refuses where the name test proceeds. Also
show the fetch spelling works in a fresh clone (measured once in research; measure again in the
bullet).

**Decided**: 2026-09-28, with scraig, after 2 rounds of discussion.

## Decision Record — the lexer

**Chosen direction**: **L-B** — one hand-written stdlib state machine, `lex(line)`, replacing
`strip_comment`'s, `_quote_spans`'s and `substitutions()`'s three separate quote trackers;
every consumer reads its context, so "inside quotes" has one definition. Decided by the tracer
bullet recorded in `2026-09-28-lexer-tracer-bullet.md` on 2026-09-28: L-B reached 117/117 on
the second attempt with every held finding's case passing; L-C reached 89/117, missing 28
must-fire cases because ShellCheck will not flag a bare assignment (Q8-5 verbatim).

**How it was decided** — the user chose a bullet over a judgement call: the user's words — "I think we should do a tracer bullet before
deciding between L-B and L-C", 2026-09-28. The round-3 spike is the precedent: a pre-registered
probe scoring candidates on the corpus and the mutation sweep decided the last rebuild, and the
breaker's own rule requires a bullet before another attempt.

**Rejected**:

- **L-C — ShellCheck as the engine** — measured at 89/117 on the harness: ShellCheck 0.11 has no
  token or AST output, and its SC2312 does not fire on a bare assignment, so shape 1's rule
  ("captured and the status never tested") cannot be expressed as a code mapping. Reaching the
  bar would mean re-implementing the capture scan and the lookahead in Python, which is L-B
  plus a process per fence.
- **L-A — fix the three trackers in place** — keeps three definitions of "inside quotes". The
  breaker fired on exactly this pattern: R9-T15 changed one tracker's view of double quotes and
  produced R10-T10 because the other two never learned about backslashes. A fourth pass over
  the same functions is the third instance, not the class.

**Measured after the discussion, before the record was written**: ShellCheck 0.11.0's output
formats are `checkstyle, diff, gcc, json, json1, quiet, tty` — every one is a list of findings.
There is no token stream and no AST. So L-C cannot use ShellCheck as a *tokenizer*; it can only
use ShellCheck's *findings* as a second detector, which is the shape the round-3 spike scored as
candidate B (71% corpus, 10 false positives on 15 clean files) and rejected as the engine. The
tracer bullet should be designed knowing this: if L-C is scored, it is scored as "ShellCheck
findings mapped to the six shapes", not as a parser under the existing shapes.

**Tracer bullet, pre-registration to write before it runs**: score each candidate with
`test-guards <path>` against the 114-case corpus and the 395-mutant sweep (`--generated`, in
the background). Pass bar for either: corpus 114/114 including every held finding's case
(R10-T7, T10, T11, T21 need new must-fire/must-not-fire cases first — write them before
scoring, so the bar cannot be retrofitted); integrity 15/15; zero unwaived survivors after
argued waivers. Predicted outcome, recorded so the run can be read against it: L-B reaches the
bar with a survivor regrowth of 10–20 to close; L-C does not reach it on the must-not-fire
half, for the reason candidate B did not.

**Revisit if**: the bullet shows L-B cannot reach 114/114 without encoding tracker-specific
behaviours the corpus happens to pin — then the corpus, not the lexer, is what needs redesign.

**Decided**: the narrowing on 2026-09-28 with scraig, after 2 rounds; the choice by the
tracer bullet the same day, read against its pre-registration.

---

## The Decision Space

**What is actually being decided**:

1. How `check-guards` tokenizes a fenced shell line so that quotes, backslash escapes and
   nested substitutions are decided by one mechanism instead of three regex trackers that
   disagree.
2. What `adversarial-review` treats as the head of a PR target: a branch name matched against
   the current checkout, or the commit the PR actually points at.

**What is NOT being decided here**: which detector shapes exist or what they flag; the loop's
publishing and ledger mechanics (round 10's cluster 3, ordinary tasks); whether the mutation
sweep joins CI (research Q4 — a gate question); the breaker's shape.

**Constraints that bound any answer**:

- The shipped file stays Python with no third-party package unless research Q1 says otherwise.
  `shlex` is present; `bashlex` is not (research → Shell facts).
- The 114-case corpus and the 395-mutant sweep are the acceptance bar, and `test-guards <path>`
  scores a candidate without touching the shipped file (research → test apparatus;
  `test-guards:12, 28-29`).
- A fenced block is executed by zsh, where `path` is tied to `PATH` (research → Shell facts).
- A `SKILL.md` fence may contain no bare `$1`; shape 6 enforces it on every shipped skill
  (`check-guards:76-77, 363-366`).
- Checking a target out is a state change nobody asked for (`adversarial-loop/SKILL.md:125`);
  `return`, never `exit`, inside a block (`adversarial-review/SKILL.md:160-166`).
- `headRefOid`, `isCrossRepository` and `refs/pull/<N>/head` are all available from `gh` and
  the remote; nothing local resolves the pull ref today; `remote.origin.fetch` covers
  `refs/heads/*` only (research → What `gh` and `git` expose).

**What would make this decision wrong**:

- Lexer: if the held defects were in the shape regexes rather than the lexing. Checked: of the
  six held lexer findings, four are lexing (T10 escapes, T11 nesting, T21 fence label, T7 fence
  class) and two are regex or hint text (T12 `GUARD`, T5 the fix hint). A lexer change addresses
  four; two remain regex edits whichever direction wins.
- Identity: if the review's never-fetch stance were load-bearing. It is stated for checkout
  only; a fetch writes a ref under `refs/remotes/` and touches no worktree. The user settled it
  by confirming I-A.

## Directions Considered

### L-A — Fix the trackers in place

- **Shape**: add backslash handling to `strip_comment`, `_quote_spans` and `substitutions()`;
  make `substitutions()` return every span rather than the outermost; add `zsh` to
  `SHELL_INFO`; relabel the unclosed-fence finding.
- **Precedent**: every patch in the research's table, rounds 4 through 10 (21 tasks, 14
  commits).
- **Buys**: the smallest diff; no new abstraction.
- **Costs**: a fourth pass over the same three functions, each historically written to make one
  corpus case pass; R9-T15 → R10-T10 is the measured consequence.
- **Fails if**: the next round finds a fifth quoting case, which the round history predicts.

### L-B — One tokenizer, stdlib only

- **Shape**: a single pass emitting characters (or tokens) with their context — quoted, escaped,
  substitution depth — and `substitutions()`, `strip_comment` and the shape scans rebuilt on it.
  Hand-written state machine of roughly 60 lines; `shlex` was considered and set aside because
  it does not track `$( )` nesting and its `punctuation_chars` splitting undoes the shape-4
  statement splitter.
- **Precedent**: candidate C in the round-3 spike — the same shape at ~130 lines, 97% on the
  38-case corpus, 87% mutation survivability.
- **Buys**: one definition of "inside quotes" shared by every shape.
- **Costs**: a rewrite of about 90 lines; a mutation sweep that regrows (shapes 4, 5 and 6 each
  regrew by 10–20 survivors).
- **Fails if**: the corpus pins behaviours only the current trackers produce, which the sweep
  would expose as false positives.

### L-C — ShellCheck as the engine

- **Shape**: run ShellCheck 0.11 (already required by `check`) over each fence and map its
  findings onto the six shapes.
- **Precedent**: candidate B in the round-3 spike, rejected as engine: 71% corpus, 10 false
  positives on 15 clean files.
- **Buys**: a real parser behind the findings.
- **Costs**: a process per fence; JSON correlated back to line numbers; and — measured after
  the discussion — no token or AST output exists in any of its seven formats, so it cannot
  supply spans to the existing shapes; the shapes would have to be re-expressed as ShellCheck
  rules or their absence.
- **Fails if**: its must-not-fire behaviour has not changed since 0.9, which nobody has checked
  and which the tracer bullet will.

### I-A — Resolve by commit, fetch the pull ref

- **Shape**: read `headRefOid` and `isCrossRepository`; on the own checkout, review to `HEAD` if
  `HEAD` descends from the OID and disclose the delta; otherwise
  `git fetch origin refs/pull/<N>/head:refs/remotes/origin/pr/<N>` as a named step and review
  that ref. One resolver function feeds Steps 1 and 2.
- **Precedent**: none in the plugin; the fetch measured working in a scratch clone (research).
- **Buys**: correctness on forks, same-name branches and stale remotes — T3, T4 and the
  mirror-image pair in one move.
- **Costs**: a fetch, which writes a ref; a new stop-table entry naming what a fetch may touch.
- **Fails if**: the skill may never write any ref (research Q2, now answered: it may).

### I-B — Resolve by commit, refuse rather than fetch

- **Shape**: the same OID test; when the head is not present locally, stop with a named reason.
- **Precedent**: the `return 1` discipline and the "NOT reviewing" lines at Step 1.
- **Buys**: no writes at all.
- **Costs**: Phase 1 stops on every off-checkout target.
- **Fails if**: the loop is meant to review PRs the user is not on — which Q4 says it is.

### I-C — Keep name matching, add the fork check

- **Shape**: leave Steps 1 and 2; refuse when `isCrossRepository` is true or the name matches
  but `headRefOid` is not an ancestor of `HEAD`.
- **Precedent**: the current code (`adversarial-review/SKILL.md:125, :221`).
- **Buys**: the smallest change.
- **Costs**: two independent resolutions kept; `origin/<head>` still reviewed at the last fetch
  (T4 unfixed).
- **Fails if**: the goal is to retire the class rather than the third instance.

## Discussion

The frame was confirmed as stated ("confirm"). On the directions, the user asked for advice on
each rather than choosing from the table.

The advice given: L-B hand-written, because the breaker's evidence is three trackers disagreeing
and L-A keeps three; L-C costs a process per fence and the spike had already measured that its
output lacks the spans the shapes need. I-A, because a fetch into a remote-tracking ref is the
same class of write any `gh pr view` user has already made, and I-B makes the loop stop on every
off-checkout target, which Q4 rejected.

The user accepted I-A in as many words ("Confirmed"). On the lexer, the user declined to choose:
"I think we should do a tracer bullet before deciding between L-B and L-C." L-A was not
defended by either side and is rejected.

After the discussion closed, one cheap check was run on the assumption L-C rested on:
`shellcheck --help` lists formats `checkstyle, diff, gcc, json, json1, quiet, tty`, and a probe
file run through `json1`, `json` and `gcc` returned findings only. That fact is recorded above
for the bullet's design; it was not used to overrule the user's request for a bullet.

## Open Threads

- **The lexer choice** was made by the tracer bullet the same day; its write-up is
  `2026-09-28-lexer-tracer-bullet.md`, and the record above was amended rather than re-opened.
- **Research Q1** (may the lexer take a non-stdlib dependency) is moot for L-B and L-C as
  framed — neither needs one — but stays open in `research.md` until `resolve_questions` closes
  it.
- **Research Q4** (does `--generated` join `check` and CI) is a gate question, deliberately out
  of scope here; it bears on the bullet's acceptance bar only in that the bar uses the sweep.
- **Where the resolver lives**: I-A says one function feeds Steps 1 and 2. Whether that
  function is a fenced block in `SKILL.md` or a shipped script under `plugin/scripts/` is a
  design detail for `create_design`, not decided here; the constraint that a `SKILL.md` fence
  may carry no bare `$1` bears on it.
