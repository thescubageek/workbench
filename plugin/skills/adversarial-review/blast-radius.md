# Measuring the blast radius

**Read this when Step 3 directs you to**, before you run the search. It gives the reason for
each of six details in the command. Each one, dropped, fails toward "isolated".

Six details in the Step 3 command are the difference between a measurement and a guess:

- **`command grep` pins the engine.** In a top-level Bash-tool call bare `grep` is a shell
  function from `~/.claude/shell-snapshots/` that re-execs as ugrep honoring `.gitignore`, so a
  tracked-but-ignored file is skipped at exit 0 and no status guard in the command can see it; the same
  line inside a script gets the system binary. So the count varied by invocation — measured on
  one symbol, bare 30 hits against `command grep`'s 52 (`.claude/wb/knowledge.md`).
  `command` bypasses the function, so one engine answers in both. Do not re-add the gitignore
  behavior as a flag: `--exclude-dir` is the scope, and a gitignore-honoring engine fails
  toward "isolated".
- **`-F`** treats the symbol as a literal. Without it a name containing `[`, `(` or `\` is an
  invalid pattern, grep exits 2 printing nothing, and the empty output reads as "no callers".
- **`--`** terminates the options. Without it a symbol beginning with `-` is consumed as a flag,
  which fails in the other direction and returns a flood.
- **`--exclude-dir` keeps the search on the repository's sources** and off the session's own
  working artifacts, and off `.git`, whose logs and commit message file name the symbol in prose. `grep -r .` recurses everything under the working directory, and a session
  transcript names files and symbols in prose without calling any of them. Measured 2026-09-28
  with the block's own `command grep` on `review-ledger.md`: 56 hits, **22 of them (39%) lines in
  `.context/attachments/*.txt` session transcripts**; on `check-guards`, 32 of 207. Since the
  tier is the maximum of the six axes, that noise can raise the tier — and the fleet it pays for
  — on its own. The rule is the scope, not
  the name: add an `--exclude-dir` for any other non-source tree the repository carries, such as
  `node_modules`, `vendor` or build output. Naming a directory that does not exist was measured a
  no-op, not an error, so the flag costs nothing in a repository without one. This shell has been
  seen to reject the flag outright on some invocations, which is why the flag sits *behind* the
  status guard in the command and not instead of it: a rejected flag exits 2 and is announced, rather than
  returning the emptiness that reads as "no callers". Do not narrow it
  further than non-source trees: an over-exclusion fails toward "isolated", which is the
  direction every other detail here exists to prevent. Measured after the exclusion: 0 transcript
  hits, and every non-transcript path present at the same line count as before it.
- **The status is captured from grep directly, not from a pipeline.** `search=$?` on the line
  after the assignment is grep's own exit code. This used to read `${PIPESTATUS[0]}`, which is a
  **bash** array — and the Bash tool runs zsh, where it expands to nothing, `[ "" -le 1 ]` is
  true, and a grep that exited 2 passed the guard in silence. Measured: with the old line, a
  search against a nonexistent path printed no diagnostic at all. Do not send grep's stderr to
  `/dev/null` either: the diagnostic is the only thing distinguishing a broken search from a
  clean one, and this measurement's errors all point toward believing the change is safe. The
  guard runs before the output is printed, so a failed search is announced ahead of the
  emptiness that would otherwise read as "no callers".
- **The exclusion compares the path field literally**, and not as a pattern. The loop cuts
  each `path:line:text` hit at its first `:` and tests that path with `[ = ]`, string equality,
  against the changed file —
  against both spellings, bare and `./`-prefixed, because the leading `./` depends on the engine
  (first bullet): the ugrep shim emits the path with no `./`, the system binary emits it
  `./`-prefixed. The block pins the binary, but a user's own `grep`, or a run that drops the
  `command` spelling, can produce either, so both are matched. The path is compared as a quoted
  shell variable, which interprets no escapes; the `awk -v` route would read a `\t` in a
  filename as a tab. The filter carries no awk field token either: the harness substitutes
  `$<digit>` in a skill body with the invocation's arguments, and an awk field was measured
  becoming `25 != …`, which kept every line, and `feature/foo != …`, which made awk exit 2. The
  loop variable is `file`, not `path`, because zsh ties `path` to `PATH`. Two earlier
  spellings each failed, in opposite directions. An unanchored `grep -v "<file>"` drops every
  line whose *text* mentions that path — which, for a script invoked by path, is exactly its
  callers: measured on `shellcheck-gate`, unanchored returned one hit, a README heading, and
  read as an isolated change, where anchoring returns four, including `plugin/scripts/check:52`,
  the line that makes the script part of the release gate. Anchoring it as an ERE,
  `^(\./)?<file>:`, then interpolated the path into a regular expression: measured for
  `app/[id].tsx`, `[id]` became a character class, the changed file's own lines were no longer
  excluded and `app/i_tsx:9` — a real caller — was dropped in their place; for `app/[id.tsx`
  the pattern was invalid, grep exited 2 printing nothing, and the empty output read as "no
  callers".
