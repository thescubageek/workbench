---
project: portable-workbench-schema
ticket: N/A
created: 2026-06-07
status: draft
last_updated: 2026-06-07
researcher: scraig
git_branch: prompt-efficiency-research
repository: karachi-v1
relationship: "Parallel track to the wb prompt-efficiency effort (docs/plans/2026-05-28-prompt-efficiency/). Workbench optimization is sequenced first; this runs alongside."
---

# Research: A Portable, Tool-Agnostic Schema for Shareable Agentic Project Work

**Created**: 2026-06-07
**Ticket**: N/A

## Research Question

Is there an emerging, tool-agnostic standard or schema for managing and sharing
collaborative, agent-driven project work — the structured research → design →
tasks documentation a workflow plugin produces — such that the artifacts are
portable and shareable **independent of any single plugin or IDE**? What
concrete building blocks already have multi-tool traction, and what would a
minimal portable schema decoupled from the `wb` plugin look like?

> **Documentarian scope note**: this research describes the EXTERNAL standards
> landscape as it exists (2025–2026), with cited sources. It makes no decision
> about what `wb` should adopt — that belongs in the design phase. Origin: a
> question raised by Jack about whether the ROAR workbench branch approach could
> be generalized into a universal, shareable format rather than something
> entangled with this plugin's slash commands.

## Summary

There is **strong, governed convergence on the peripheral layers** of agentic
project work — the instruction file (`AGENTS.md`), the skill packaging format
(`SKILL.md`), and the wire protocols (MCP and A2A) — all now under the Linux
Foundation's **Agentic AI Foundation** (formed Dec 2025; platinum members incl.
AWS, Anthropic, Block, Bloomberg, Cloudflare, Google, Microsoft, OpenAI).

There is **no ratified standard for the core artifact** a workbench-style flow
produces — the research/design/tasks document trio. Multiple spec-driven
development (SDD) tools (Amazon Kiro, GitHub spec-kit, OpenSpec, spec-workflow
MCP, BMAD-METHOD, Tessl) have **independently reinvented the same on-disk shape**
— a phased, git-committed markdown trio (intent → design → tasks) — **without
agreeing on a format** (filenames, notation, and frontmatter all differ). The
nearest thing to a neutral lingua franca is GitHub **spec-kit**, by virtue of
being the least opinionated (plain markdown, no schema).

`llms.txt` is effectively a dud for this purpose. MCP and A2A are transport
layers, not document schemas. beads is a strong git-native status backend but
one implementation, not a multi-vendor standard.

The practical conclusion: the entanglement is in the **slash commands**, not the
**artifacts**. The artifacts can be made portable today by composing standards
that already have traction.

## Detailed Findings

### 1. Instruction/context files — `AGENTS.md` is the de-facto standard

- `AGENTS.md` began as an OpenAI initiative (Aug 2025); by late 2025/2026
  adopted by 60,000+ projects and 20+ tools (Codex CLI, Cursor, GitHub Copilot,
  Gemini CLI, Google Jules, VS Code, Devin, Aider, Zed, Warp, JetBrains Junie,
  Amp, Factory). Format is deliberately minimal: plain Markdown, no required
  schema, no frontmatter.
- `CLAUDE.md` is Anthropic's equivalent; Claude Code reads it and (as of early–
  mid 2026) does **not** natively read `AGENTS.md`. Common practice: a one-line
  `CLAUDE.md` pointing to / symlinking `AGENTS.md`.
- `llms.txt` is a different problem and largely ineffective for AI-search
  citation; only minor traction as a docs-pointer for IDE agents. Not relevant
  as a project-work-sharing standard.

Sources:
- <https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation>
- <https://vibecoding.app/blog/agents-md-guide>
- <https://codersera.com/blog/agents-md-vs-claude-md-vs-cursor-rules-comparison-2026/>
- <https://www.searchenginejournal.com/google-says-llms-txt-is-purely-speculative-for-now/577576/>

### 2. Spec-driven frameworks — the same trio, independently reinvented

| Tool | On-disk artifact schema | Format notes |
|---|---|---|
| Amazon **Kiro** | `.kiro/specs/<f>/` → `requirements.md` · `design.md` · `tasks.md` + steering | Markdown; EARS acceptance notation. Near 1:1 mirror of `wb`. |
| GitHub **spec-kit** | `specs/<f>/` → `spec.md` · `plan.md` · `tasks.md` (+`research.md`, `data-model.md`, `contracts/`) + `.specify/memory/constitution.md` | Plain markdown, no YAML frontmatter, no manifest. Works with 30+ agents. De-facto neutral baseline. |
| **OpenSpec** | `openspec/specs/` + `openspec/changes/<c>/` → `proposal.md` · `design.md` · `tasks.md` + delta specs (ADDED/MODIFIED/REMOVED) | Markdown-in-git, no DB. Brownfield-first. |
| **spec-workflow MCP** | `<f>/` → `requirements.md` · `design.md` · `tasks.md` + steering + approval files | Same trio + EARS, exposed as an MCP server with a dashboard. |
| **BMAD-METHOD** | brief → PRD → architecture → stories → code → tests; agent roles | Agile-process-shaped; every agent emits a persistent reviewable artifact. |
| **Tessl** | spec = description + capabilities-with-linked-tests + API; in-codebase as long-term memory; Spec Registry (10k+ specs) | Spec-as-dependency; commercial; plugs into agents via MCP. |

The pattern (phased git-committed markdown trio: intent → design → tasks) is
industry-wide and validates `wb`'s structure. Fragmentation is real: filenames,
notation (EARS vs prose), and frontmatter all differ; no cross-tool schema or
manifest exists to make one tool's specs readable by another.

Sources:
- <https://kiro.dev/docs/specs/>
- <https://github.com/github/spec-kit> · <https://developer.microsoft.com/blog/spec-driven-development-spec-kit>
- <https://github.com/Fission-AI/OpenSpec>
- <https://github.com/Pimzino/spec-workflow-mcp>
- <https://reenbit.com/the-bmad-method-how-structured-ai-agents-turn-vibe-coding-into-production-ready-software/>
- <https://tessl.io/blog/tessl-launches-spec-driven-framework-and-registry/>
- <https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html> · <https://intent-driven.dev/knowledge/spec-kit-vs-openspec/>

### 3. Wire protocols — MCP and A2A (not document schemas)

- **MCP** standardizes vertical agent↔tools/data/resources access (10,000+
  servers). It can *serve* project docs as resources (spec-workflow, Tessl) but
  does not define the document schema.
- **A2A (Agent2Agent)** standardizes horizontal agent↔agent communication
  (Google Apr 2025 → Linux Foundation Jun 2025; v1.0; 100+ companies). Model:
  Agent Cards (JSON capability metadata), Tasks (lifecycle states), Artifacts
  (typed output containers). A2A Artifacts/Tasks are the closest conceptual fit
  (Artifacts ≈ shared outputs; Tasks ≈ beads issues) but are runtime/in-flight
  objects, not a persistent on-disk doc standard.

Sources:
- <https://a2a-protocol.org/latest/topics/a2a-and-mcp/> · <https://github.com/a2aproject/A2A>
- <https://aws.amazon.com/blogs/opensource/open-protocols-for-agent-interoperability-part-4-inter-agent-communication-on-a2a/>

### 4. Portable skills — `SKILL.md` is a genuine cross-vendor open standard

- Anthropic **Agent Skills**: directory + `SKILL.md` (YAML frontmatter, required
  `name` + `description`; markdown body; optional bundled scripts/references;
  progressive disclosure).
- Released as an open specification (Dec 18, 2025) at agentskills.io. By
  March 2026, 32 tools from competing vendors read the same `SKILL.md` from the
  same directory layout (Gemini CLI, JetBrains Junie, AWS Kiro, Block Goose,
  Codex CLI, plus Claude surfaces).
- This is the proof-of-concept for the research question: a `dir + NAME.md (YAML
  frontmatter + markdown body)` unit can become a true cross-vendor portable
  standard quickly. Portability came from (a) a published spec, (b) minimal
  required-field frontmatter, (c) plain markdown.

Sources:
- <https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills>
- <https://agentskills.io/home> · <https://www.paperclipped.de/en/blog/agent-skills-open-standard-interoperability/>

### 5. Git-native issue/task backends

- **beads (`bd`)** — git-backed issue tracker for agents; source of truth is
  JSONL in `.beads/` committed to git (local SQLite is a read cache);
  hash-based IDs avoid multi-agent merge conflicts; dependency graph +
  auto-ready detection; JSON output. Strong momentum but single-project, not a
  multi-vendor standard.
- Competing "issues-as-files" conventions: SDD tools track task state inside
  `tasks.md` checklists + separate approval files (Kiro, spec-workflow,
  OpenSpec). No agreed git-native issue *schema* across tools. A2A Tasks are the
  nearest protocol-level analog but are runtime objects.

Sources:
- <https://github.com/steveyegge/beads> · <https://steveyegge.github.io/beads/>

### 6. Governance — the Agentic AI Foundation

`AGENTS.md`, `SKILL.md`, MCP, and A2A now all sit under the Linux Foundation's
**Agentic AI Foundation** (Dec 2025, 49 members). This is the locus of real,
governed multi-vendor convergence — but note it governs the peripheral layers,
not the doc-trio artifact.

Sources:
- <https://techcrunch.com/2025/12/09/openai-anthropic-and-block-join-new-linux-foundation-effort-to-standardize-the-ai-agent-era/>
- <https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation>

## Architecture Documentation

**Convergence is layered, not unified:**

- **Real / governed / adopted now**: `AGENTS.md` (instruction layer),
  `SKILL.md` (capability layer), MCP (tool/data access), A2A (agent interop).
- **Convention only (same shape, no shared format)**: the research/design/tasks
  doc trio; spec-kit is the least-opinionated de-facto baseline.
- **Aspirational / non-starter**: `llms.txt` for this purpose; a single ratified
  "shareable agentic project research" schema (does not exist; no one is
  standardizing the trio's format).

**Candidate minimal portable schema (building blocks with existing traction):**

1. Instruction layer: `AGENTS.md` at repo root (+ thin `CLAUDE.md` shim).
2. Doc trio: plain markdown, spec-kit- or Kiro-aligned naming for recognition.
3. Self-describing manifest + frontmatter: `SKILL.md`-style YAML (required
   `name`/`description`/`status`; optional git metadata, phase, assignee) + a
   top-level manifest listing the trio and the status backend.
4. Pluggable status backend: beads `.beads/*.jsonl` OR `tasks.md` checkboxes
   (do not hard-wire beads).
5. Optional live-interop bridge: wrap as an MCP server so any MCP-capable agent
   can read/drive the project; the wb slash commands become one client.

## Open Questions

- **PWS-1**: Which doc-trio naming should a portable `wb` schema adopt for
  maximum cross-tool recognition — spec-kit (`spec.md`/`plan.md`/`tasks.md`),
  Kiro (`requirements.md`/`design.md`/`tasks.md`), or keep wb's
  research/design/tasks? Blocks: design of the portable format.
- **PWS-2**: Is the MCP-server wrapper in scope for a first cut, or is
  plain-files-in-git portability sufficient to start?
- **PWS-3**: Should status remain beads-first with a `tasks.md`-checkbox
  fallback, or be abstracted behind a backend-neutral interface from day one?
- **PWS-4**: Relationship to the wb plugin — does the portable schema replace
  the plugin's artifact layer, or define an export/interop target the plugin
  emits to?

## Next Steps

1. Sequenced AFTER the wb prompt-efficiency optimization
   (`docs/plans/2026-05-28-prompt-efficiency/`) lands; this track runs parallel.
2. Resolve PWS-1 … PWS-4 with Jack and the user.
3. Run `/wb:create_design` for this project once questions are resolved.
