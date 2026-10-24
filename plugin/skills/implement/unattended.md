# Closing a checkpoint under `--auto`

**Read this when Step 8 directs you to.** It says what an unattended run ticks, what it leaves
`[ ]`, and what its report must say.

## The checkpoint

**Under `--auto`.** Do not wait. Tick the checkpoint conditions you actually established —
every phase checkbox `[x]`, automated verification passing, and the `update_status` box once
Step 9 has run it — and **leave "Manual verification confirmed by human" as `[ ]`**, because
no human was asked. Then add one line under the checkpoint naming the run unattended, with
`${phaseLabel}`, the time, and the manual steps nobody performed — from `design.md` on a
phased plan, and on a remediation plan from the outstanding tasks' own acceptance criteria in
the round's `tasks.md`, which is where a round's manual steps live because it has no
`design.md` (Step 3).
**Attestation tasks stay `[ ]`** and are listed there too — the phase still closes,
unattended, so the run terminates instead of stalling, and the report tells a person exactly
which judgments are outstanding.

**The unticked box is the feature, not an oversight.** `--auto` buys the wait, not the
attestation: that box records what a person did, and no run may tick it on its own authority.
An attestation task's checkbox is that same box under another name, and the same rule holds
for it.

## The final phase

**On the final phase under `--auto`, say plainly that the plan cannot close itself.**
`status: in-progress → complete` is a `status:` change gated by `/wb:update_status`'s own
barrier, which `--auto` does not reach — so the run ends with the work committed, the
counters reconciled, and the plan still `in-progress`, waiting on a person. Name that in the
report.
