# Handoff: Add a "dispositive-issue-first" discipline to CaseSmith

## Context — why we're doing this

In wb (the software sibling plugin) we just encoded a "tracer bullet" optimization: at points of high uncertainty, fire one bounded probe at the riskiest load-bearing assumption *before* committing to a path, so the result culls whole branches of wasted work. It shipped as an ambient discipline skill plus gates in the design/execution commands.

The legal-domain counterpart is even higher-value: the **threshold / dispositive issue**. Before investing in a full theory of the case, you resolve the things that can moot everything — statute of limitations, standing/jurisdiction, applicable coverage and policy limits, a controlling adverse bar, or whether a key element is provable on the available facts. The cost asymmetry is more extreme than in software: building a demand or brief on a time-barred or uncovered theory wastes client money, can blow a deadline, and is malpractice-adjacent (cf. the *Mata v. Avianca* framing already cited in `verification-before-filing`).

A review of the current CaseSmith pipeline confirmed there is **no "probe the dispositive issue first" gate anywhere today**. The existing disciplines sit at other altitudes (see below), so this fills a real gap rather than duplicating one.

## Design decisions (please honor these)

1. **Name it for the legal idiom, not the software metaphor.** Use `dispositive-issue-first` (or `threshold-screen`). Do NOT call it "tracer bullet" — that reads as foreign to an attorney audience. This matches how CaseSmith re-skins (`legal-tdd-discipline`, `verification-before-filing`).

2. **It is NOT redundant with existing disciplines** — keep it at its own altitude:
   - `legal-tdd-discipline` fires at *drafting* (issue-spot before prose, one document). This new skill fires earlier, at *research → strategy*, across the whole matter.
   - `verification-before-filing` is a *terminal* gate. This is the *opening* gate.
   - The closest overlap is the **Assumptions / Open Questions / Pending Decisions** tables in `matter_research.md` and `create_strategy.md`. Those tables *defer* an unknown (document it, validate later). This skill is the inverse: when an unknown is *dispositive*, resolve it NOW instead of tabling it. Scope the skill narrowly to "*dispositive* unknown → probe now," NOT general risk-listing, so it sharpens those tables rather than duplicating them.

3. **The probe is research, not a prototype.** In law the bounded probe is "read the policy dec page / check the SOL clock / pull the controlling case / confirm the named insured" — not "build a thin end-to-end slice." Lean the wording toward read-one-thing.

4. **Bounding matters more than in software.** A legal spike can cost real attorney hours and sometimes needs client authorization. Keep the "one bounded probe, stop on the answer" rule AND a strong skip-clause: if there is no single dispositive unknown, proceed — don't manufacture one. Many matters have an obvious clean path.

## Tasks

### 1. New skill: `claude-code/skills/dispositive-issue-first/SKILL.md`

Match the house style of `skills/legal-tdd-discipline/SKILL.md`: frontmatter with `name`, `description` (a "Use when…" activation sentence), `allowed-tools: Read, Grep, Glob`, and the `**Pre-execution**: Read lib/skill-style.md …` line. Discipline format mirrors `legal-tdd-discipline` / wb's `tdd-discipline` (Iron Law → When to Fire → Economics → Keep It Bounded → Report → Rationalizations → Red Flags → Integration). A ready-to-edit draft is at the bottom of this handoff.

### 2. Gate in `claude-code/commands/law/create_strategy.md`

Insert a "Dispositive-Issue Screen" gate at the top of **Step 4: Strategy Exploration** (anchor: line 170 `### Step 4: Strategy Exploration`, before line 172 `**Interactive Strategy Discussion**` / line 174 `1. Generate strategy options`). Before presenting Options A/B/C, ask: is there one dispositive issue whose answer would collapse the option set? If yes, resolve it (or the bounded portion that's cheaply knowable) and report what it culled, THEN present surviving options. Cross-reference the `dispositive-issue-first` skill. This is the legal analog of wb's `create_design` Step 4 gate. Note the existing **Assumptions** table at line 287 is the "defer" mechanism this gate front-runs for the *dispositive* row only.

### 3. Scoping note in `claude-code/commands/law/matter_research.md`

At **Step 4: Spawn Parallel Research Sub-Agents** (anchor: line 125), add a lighter note: if a dispositive threshold issue is in play (e.g. SOL clock, coverage existence), aim one sub-agent (authority-finder / matter-file-analyzer) at confirming it first so the full fan-out isn't spent building toward a theory that's already dead. Frame as scoping, consistent with the documentarian rule — not strategy selection. Note the Step 2.1 refuse-fast preflight already exists; this is additive and narrower.

### 4. Tweak `claude-code/commands/law/create_workplan.md`

At **"Don't Block on Unknowns"** (anchor: line 512, under "Handling Drafting Discoveries" line 503), carve out load-bearing unknowns: keep "make reasonable assumptions" for low-stakes details, but add — if an unknown is *dispositive* (its failure invalidates the theory or moots the matter), don't assume; it should already have been screened at strategy via `dispositive-issue-first`, and if it surfaces here, stop and resolve it before drafting.

### 5. Release hygiene

Follow CaseSmith's normal release process for a new skill: bump the version in `.claude-plugin/marketplace.json` (and the `dist/` / `plugins/casesmith` mirror if that's how the build works) and add a `CHANGELOG.md` entry. Register the skill wherever CaseSmith enumerates skills (check `casesmith-status` and the plugin packaging so the new skill ships). Run `meta-review-casesmith` (legal-reviewer + engineering-reviewer) against the change — the legal-reviewer will append the "needs attorney confirmation" caveat on any legal-substance wording, which is expected.

## Verification

- New skill present and well-formed; `casesmith-status` lists it as a registered skill.
- `meta-review-casesmith` passes (engineering) with legal-reviewer caveats noted.
- Manual read-through: the `create_strategy` gate fires *before* options, the skip-clause is intact, and the wording does not duplicate the Assumptions/Risk tables.
- Confirm no cross-matter or path-resolution conventions are violated (skill is pure-reasoning; `allowed-tools` limited to Read/Grep/Glob, no matter writes, so `lib/preflight.md` matter-context guards are not required — verify this against how other discipline skills declare tools).

---

## Draft skill content (starting point — adapt wording to CaseSmith voice)

```markdown
---
name: dispositive-issue-first
description: Use when about to commit to a theory of the case or pick among strategy options under uncertainty — screen for the dispositive/threshold issue (SOL, jurisdiction/standing, coverage & limits, controlling bar, provability) and resolve it FIRST, before building the full strategy or draft. Activates at the research → strategy boundary.
allowed-tools: Read, Grep, Glob
---

# Dispositive-Issue-First

**Pre-execution**: Read `lib/skill-style.md` for the structured-prompt contract. This skill is a discipline rule with no user-facing prompts; the contract still applies to any nested skill or command it activates inside.

Before committing effort to a theory of the case, resolve the one issue that could moot it. Let the answer cull whole strategy branches before you build them.

**Core principle:** A theory built on an unscreened threshold issue is a theory you may have to throw away — after the client has paid for it and a deadline has passed.

## The Iron Law

```
DON'T COMMIT TO A THEORY (OR PICK AMONG STRATEGY OPTIONS) WHILE A
DISPOSITIVE THRESHOLD ISSUE IS STILL UNRESOLVED
```

Listing options on paper, or starting a draft, while the case-dispositive
unknown stays open is gambling with the client's matter. Screen first.

## When to Screen

Run a dispositive-issue screen when **ALL** hold:

1. You are about to generate strategy options OR commit to a theory of the case / posture.
2. There is a threshold issue whose answer changes whether the matter is viable at all — not a detail, a gating question.
3. One bounded action would resolve it — read the policy declarations page, check the SOL clock against the docket/intake, confirm the named insured, pull the one controlling authority, verify standing.
4. Resolving it would eliminate options or moot significant downstream work.

## The Threshold Checklist (non-exhaustive)

- **Limitations / repose** — is the claim timely? (most common matter-killer)
- **Jurisdiction / venue / standing** — can this client bring this claim here?
- **Coverage & limits** — is there an applicable policy, and what are the limits? (sizes or moots the whole demand)
- **Controlling bar** — a statute, immunity, exclusion, or binding precedent that defeats the theory.
- **Provability of a key element** — does the matter file actually contain facts to support a required element, or only assert it?

## The Economics

```
screen NOW  when  cost(probe)  ≪  cost(building a doomed theory)
            and the downside includes client cost, blown deadlines, and malpractice exposure
```

The screen earns its keep by what it *kills*. Aim it at the issue whose
failure would waste the most work or expose the client to the most risk.

## Keep It Bounded

A screen that sprawls into full research defeats its purpose.

- **One issue** — the single dispositive one. Not a full risk survey (that's the Risk Analysis / Assumptions tables).
- **Read, don't build** — the probe is reading the controlling document or pulling the controlling authority, not drafting.
- **Mind the cost** — a legal spike can consume real attorney time; if the probe itself is expensive or needs client authorization, surface that and get it before proceeding.
- **Stop on the answer** — the moment the threshold issue resolves, stop and return to strategy.

## Report What It Screened

After the probe, state plainly:

- What was checked (the document/authority and what it said).
- Whether it **kills, sizes, or confirms** the theory.
- What now survives to be decided or drafted.

"Dec page confirms $25k policy limit → the $2M demand theory is out; pivot to
underinsured-motorist" beats a tidy options table that ignored coverage.

## Common Rationalizations

| Excuse | Reality |
| --- | --- |
| "I'll list the options first and validate the SOL later" | Validating later means building options on a theory that may already be dead. Screen the dispositive issue now. |
| "Intake probably covers it" | Probably is the trigger, not the excuse. Read the one document. |
| "Screening will slow the matter down" | Screening is faster than drafting a demand that gets mooted by an exclusion. |
| "We'll catch it before filing" | Catching a time-bar at the filing gate means the strategy work was wasted — and a deadline may already be gone. |
| "There's no single dispositive issue here" | Then this doesn't apply — proceed. Don't manufacture a screen. |

## Red Flags — STOP and Screen

- About to present strategy Options A/B/C whose viability all depend on the same unconfirmed threshold (coverage, timeliness, standing).
- Starting a theory of the case on "assuming the claim is timely…".
- Logging the dispositive question in the Assumptions/Open Questions table and moving on to options.
- "We'll confirm coverage/limits when we draft the demand."

**All of these mean: name the dispositive issue, run one bounded screen, then proceed.**

## Integration with CaseSmith Commands

- In `/law:create_strategy`, before **Step 4 (Strategy Exploration)** presents Options A/B/C: screen for the dispositive issue and report what it culled before listing surviving options. Resolve the dispositive row of the **Assumptions** table now rather than deferring it.
- In `/law:matter_research`, when a threshold issue is in play, aim one sub-agent at confirming it first so the full fan-out isn't spent toward a dead theory (scoping, not strategy selection).
- This is the opening-gate complement to `legal-tdd-discipline` (drafting altitude) and `verification-before-filing` (terminal gate).
```
