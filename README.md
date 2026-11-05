# Laravel Best Practices

An opinionated, additive overlay of Laravel best practices for AI coding assistants. Composes alongside [Laravel Boost](https://github.com/laravel/boost) — it does not replace it.

Boost ships an excellent built-in `laravel-best-practices` skill (19 rules) that covers the mechanics of Laravel and PHP. This package adds the practices Boost is *silent* on (control-flow opinions, architectural defaults, money-handling, named queues) plus a small set of deliberate opinionated counter-positions (clearly flagged where they exist). It also ships `session-scoping`, a skill for how to run AI-agent sessions against this codebase — separate from what the code should look like.

## Install

```bash
composer require --dev jpswade/laravel-best-practices
```

Then make sure Laravel Boost is installed and rerun its installer so it picks up the breadcrumb guideline and the skills shipped by this package:

```bash
composer require --dev laravel/boost
php artisan boost:install
```

When Boost prompts *"Which third-party AI guidelines/skills would you like to install?"*, tick **`jpswade/laravel-best-practices`**. That writes the choice into `boost.json` so subsequent runs (including non-interactive CI) pick it up automatically.

> **Non-interactive installs require explicit opt-in.** `php artisan boost:install --no-interaction` will silently skip every third-party package by default, because the multiselect defaults to the empty list saved in `boost.json`. If you want to run the installer non-interactively from CI, commit a `boost.json` first with:
>
> ```json
> {
>     "agents": ["claude_code", "codex", "grok_build", "antigravity"],
>     "guidelines": true,
>     "mcp": false,
>     "packages": ["jpswade/laravel-best-practices"],
>     "skills": ["laravel-best-practices", "laravel-best-practices-overlay", "tdd-bug-fixing", "adrs", "session-scoping"]
> }
> ```

Boost auto-discovers content from `resources/boost/{guidelines,skills}/` inside directly required Composer packages, so once opted in, the breadcrumb in this package's `core.blade.php` is composed into the consumer's agent instruction file (usually `AGENTS.md`), and the four skills (`laravel-best-practices-overlay`, `tdd-bug-fixing`, `adrs`, and `session-scoping`) are written to the agent's skills directory (e.g. `.cursor/skills/`) for on-demand activation.

### Claude Code, Codex, Grok Build, Antigravity, and T3 Code

Use Laravel Boost **2.10.2** as the verified installation baseline for these
instructions. Its PHP requirement is 8.2+, with Laravel 11.45.3+, 12.41.1+, or
13 (Laravel 13 itself requires PHP 8.3+). This package also supports Laravel 10,
but that does not make Laravel 10 compatible with this Boost release.

Run `php artisan boost:install`, enable guidelines and skills, select the
agents you use, and opt into `jpswade/laravel-best-practices`. The example
`boost.json` above selects all four native Boost adapters; keep only those you
need. These are Boost 2.10.2's default output paths, which project configuration
can override:

| Agent | `boost.json` agent ID | Guidelines | Skills |
| --- | --- | --- | --- |
| Claude Code | `claude_code` | Existing `CLAUDE.md`, otherwise `AGENTS.md` | `.claude/skills/` |
| Codex | `codex` | `AGENTS.md` | `.agents/skills/` |
| Grok Build | `grok_build` | `AGENTS.md` | `.grok/skills/` |
| Antigravity | `antigravity` | `AGENTS.md` | `.agents/skills/` |

Codex and Antigravity share the same skill destination. Keep one source of
truth in this package; let Boost distribute it rather than maintaining
separate agent-specific copies of the rules.

**T3 Code:** configure the agent/provider running the thread. T3 Code is not a
separate Boost adapter: do not add a `t3` agent ID or invent a `.t3/skills`
directory. For a Codex-backed thread, use the Codex output; for a Claude
Code-backed thread, use the Claude Code output. Select both when switching
between them. A model name alone does not determine skill discovery: using a
Grok model through another harness does not imply that harness reads
`.grok/skills`. Follow that provider's skill-loading configuration. Install in
the actual working directory/worktree used by the thread, and verify the
skills are visible there. Follow T3 Code's supplied orchestration instructions
for its tools and task lifecycle.

#### Instruction loading

**Instruction loading is separate from installation.** The table above describes
Boost output, not a promise that a host loads it. Keep common guidance in
`AGENTS.md` and use the host's documented adapter/import where needed. Never
assume identical discovery, scope, or precedence across hosts.

The following instruction conventions were checked against official docs on
**2026-11-05** (rolling documentation unless a version is stated):

- **Codex:** loads global guidance and a project-root-to-working-directory
  chain, with `AGENTS.override.md` preferred over `AGENTS.md` at each level;
  deeper guidance overrides earlier guidance. See [Codex instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
- **Claude Code:** direct `AGENTS.md` support requires **v2.1.277+**. By default,
  project `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` in the working
  directory or ancestors suppress the `AGENTS.md` fallback. The Project
  instructions setting can change this; disabled support and older sessions
  still need `CLAUDE.md`. Preserve existing instructions and add `@AGENTS.md`
  to a sibling `CLAUDE.md` for compatibility when needed. The import remains
  valid on newer versions. Check `/context all`; do not assume Codex's
  `AGENTS.override.md` semantics apply. See [Claude instruction loading](https://code.claude.com/docs/en/memory).
  With this shared-file arrangement, set Boost's
  `agents.claude_code.guidelines_path` to `AGENTS.md` in `config/boost.php`
  so Boost maintains one shared block.
- **Gemini CLI:** defaults to hierarchical `GEMINI.md` context files; a
  `GEMINI.md` can import shared guidance with `@./AGENTS.md`. Use `/memory show`
  to inspect loaded context. See [Gemini context and imports](https://geminicli.com/docs/cli/gemini-md/).
- **Cursor:** supports `AGENTS.md` and scoped project rules in `.cursor/rules/`;
  check the rule's activation settings. See [Cursor rules](https://cursor.com/docs/rules).
- **JetBrains AI Assistant:** uses `.aiassistant/rules/*.md` project rules
  with configurable activation. Put essential guidance in an Always rule and
  verify it is included; do not assume a root `AGENTS.md` is loaded by chat.
  See [JetBrains project rules (2026.2)](https://www.jetbrains.com/help/ai-assistant/configure-project-rules.html).
- **Gemini Code Assist:** check the selected IDE and mode's context support.
  VS Code agent mode uses Gemini CLI; this does not make every Code Assist
  feature a CLI session. See [Code Assist agent mode](https://docs.cloud.google.com/gemini/docs/codeassist/use-agentic-chat-pair-programmer).

**Verify discovery after installation:** confirm that each selected destination
contains all four `SKILL.md` files and that the overlay's `rules/` directory
was copied too. Refresh or restart the agent if necessary. In a new session,
ask it to locate `laravel-best-practices-overlay` and identify the rule file
for integer money handling without editing anything. It should read
`rules/eloquent-opinions.md`. A question unrelated to Laravel should not load
all the overlay rules. Repeat in each host/provider you use; copied files
alone do not prove automatic activation.

These skills use standard Agent Skills metadata and plain Markdown; they do
not require a provider-specific tool, model, slash command, or subagent.
Essential activation criteria are in `description`, with detailed applicability
in the body. See the [Agent Skills specification](https://agentskills.io/specification),
[Claude skills](https://code.claude.com/docs/en/skills),
[Codex skills](https://learn.chatgpt.com/docs/build-skills),
[Antigravity skills](https://antigravity.google/docs/skills), and the
[Boost 2.10.2 adapters](https://github.com/laravel/boost/tree/v2.10.2/src/Install/Agents)
for the underlying formats and paths.

### Optional: publish the bundled configs

The package ships `pint.json`, `phpstan.neon.dist`, and a conservative `.aiignore`
template. Publish the files you need into your application root:

```bash
# Pint config only
php artisan vendor:publish --tag=laravel-best-practices-pint

# PHPStan config only
php artisan vendor:publish --tag=laravel-best-practices-phpstan

# Credential exclusion template only
php artisan vendor:publish --tag=laravel-best-practices-aiignore

# All three at once
php artisan vendor:publish --tag=laravel-best-practices-all
```

For the PHPStan config, install the matching analysers (suggested in `composer.json`):

```bash
composer require --dev larastan/larastan phpstan/phpstan-strict-rules
vendor/bin/phpstan analyse
```

### Credential protection

The Boost guideline, when loaded into the host's instructions, prohibits
reading credentials on **every task**:
API keys, tokens, passwords, `.env` values, private keys, signing secrets, and
session credentials. It explicitly covers `.env*`, Composer `auth.json`
(including `~/.composer/auth.json` and `~/.config/composer/auth.json`), other
credential stores, logs, dumps, and Laravel's cached configuration. It also
prohibits indirect retrieval through shell commands, environment/config dumps,
Git history, MCP tools, symlinks, or other agents. Reading and then redacting
does not satisfy this rule. Agents should use variable names and explicitly
sanitised examples, and ask users to configure secrets locally without sharing
their values.

Publish the bundled [`.aiignore`](.aiignore) with the command above. It uses
gitignore-style patterns for common credential sources and runtime artifacts,
including nested files. There is deliberately no exemption for `.env.example`
or `.env.testing`. Do not use `--force` to replace an existing exclusion file;
merge the template while retaining the project's existing protections.

### Instructions, exclusions, and access controls

These are three different layers:

- **Instructions** describe the sensitive-path policy the agent must follow.
  `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, and project rules supply guidance;
  they do not revoke filesystem access.
- **Context exclusions** filter the files a particular host indexes, attaches,
  or reads through covered features. An ignore file is not a universal
  security boundary and does not necessarily cover terminal or MCP access.
- **Enforced access controls** restrict operations through host permissions,
  an OS sandbox, or an isolated environment. Their scope depends on the tool,
  platform, version, and active configuration. Read-only access prevents
  writes; it does **not** prevent reading secrets.

Maintain a sensitive-path policy covering the credential sources above even
when no exclusion file exists. Retain `.aiignore` for compatibility and honour
its exclusions as project policy, then configure the active host's supported
controls. Project-relative patterns do not cover outside-workspace credential
stores, and filenames alone cannot identify every secret-bearing file.

#### Host controls and documented limits

Each entry was verified against the linked official documentation on
**2026-11-05**. These are documentation checks, not runtime enforcement tests;
recheck the installed version and settings before relying on a control.

| Host | Supported convention and boundary | Official source / version |
| --- | --- | --- |
| JetBrains AI Assistant | `.aiignore` restricts AI processing when enabled in Project Settings. JetBrains documents possible unexpected processing; do not treat it as an OS sandbox or assume it governs every integrated agent. | [Restrictions](https://www.jetbrains.com/help/ai-assistant/disable-ai-assistant.html), 2026.2 help |
| Cursor | `.cursorignore` restricts Agent/Tab and context references. Terminal and MCP tools are explicitly outside that protection. | [Ignore files](https://cursor.com/docs/reference/ignore-file), rolling docs |
| Gemini Code Assist | `.aiexclude` is the default context-exclusion file; `.gitignore` also participates in supported context exclusion. This is not a general filesystem permission policy. | [Context exclusion](https://docs.cloud.google.com/gemini/docs/codeassist/create-aiexclude-file), rolling docs |
| Gemini CLI | `.geminiignore` excludes paths from tools that respect it, including `@` file sharing. Do not extend that claim to arbitrary shell commands or MCP servers. | [Ignoring files](https://geminicli.com/docs/cli/gemini-ignore/), rolling docs |
| Claude Code | `.claude/settings.json` supports `permissions.deny`, including `Read` rules for sensitive paths. File-tool rules are not a blanket restriction on Bash or MCP; review their permissions and sandbox coverage separately, including home/absolute paths. | [Permissions](https://code.claude.com/docs/en/permissions), rolling docs |
| Codex | Beta permission profiles use `default_permissions` and `[permissions]` with filesystem `read`, `write`, and `deny` access for local sandboxed commands. Older sandbox settings can take precedence; verify the effective configuration. MCP, connectors, browser, and cloud controls are separate. Deny-glob enforcement varies by platform and can snapshot existing paths before command startup. | [Permission profiles and enforcement limits](https://learn.chatgpt.com/docs/permissions), beta; managed profile allowlists require 0.138.0+ |
| ChatGPT uploads | Attachments supply content to a conversation. Review and sanitise what you upload; a repository ignore file does not remove content already supplied. Upload handling is distinct from Codex local filesystem permissions. Do not invent a universal OpenAI ignore filename. | [Working with ChatGPT files](https://learn.chatgpt.com/docs/use-chatgpt), rolling docs |

For **T3 Code**, the [official project overview](https://github.com/pingdotgg/t3code#readme)
describes a control surface for installed agent harnesses; its
[permission-mode documentation](https://github.com/pingdotgg/t3code/blob/main/docs/user/permission-modes.md)
explicitly distinguishes provider behavior (both checked 2026-11-05).
Apply the controls of the active provider/harness and separately
review app-provided tools, terminal access, and MCP servers. A model name does
not establish a filesystem boundary. Follow the active session's orchestration
and permission instructions; changing providers requires checking discovery
and access again. This is a deployment requirement, not a claim that T3 adds
an ignore-file enforcement layer.

Use an isolated environment without real credentials for stronger protection.
Check file reads, terminal commands, integrations, and outside-workspace paths
using synthetic fixtures only; never probe real secrets. Record the host,
version, active settings, and tested tool surfaces, and report untested surfaces
as unverified. This package publishes guidance and a compatibility template;
it does not install host permissions or enforce the policy itself.

For prevention at commit and release time, choose **one pinned secret scanner:
Gitleaks, evaluated Betterleaks, or an existing equivalent** in developer-controlled
pre-commit hooks and required CI checks. Scan built container images separately with an image-capable scanner,
exclude credentials from the Docker build context, and use BuildKit secret
mounts for build-time authentication. The
[operational safety rules](resources/boost/skills/laravel-best-practices-overlay/rules/operational-safety.md#scan-for-secrets-before-committing-and-publishing)
cover history/layer coverage, safe handling of findings, and credential
rotation. This is a recommendation, not an installed hook or workflow, and
does not authorise an AI agent to inspect credentials or raw scan findings.

Secret scanning is distinct from **PII detection and handling**. Prefer synthetic
data in fixtures and agent inputs; production exports, logs, support transcripts
and screenshots require authorised owner minimisation and review before they
reach an agent. Detection/redaction is not proof of safety or permission to
inspect protected inputs. Presidio is optional controlled preprocessing.

The on-demand [scanner comparison and executable examples](resources/boost/skills/laravel-best-practices-overlay/rules/secret-scanning.md)
record pinned Gitleaks/Betterleaks results on synthetic Laravel fixtures,
coverage gaps, false positives, report handling, maintenance and licensing.
The [PII practice](resources/boost/skills/laravel-best-practices-overlay/rules/pii-handling.md)
includes executed synthetic detections and misses. Credential validation and
revocation are separate authorised operations, never routine scan steps.
These development/CI tools add no package runtime dependencies.

## What's inside

```
resources/boost/
├── guidelines/
│   └── core.blade.php                              # thin breadcrumb routing to the four skills
└── skills/
    ├── laravel-best-practices-overlay/
    │   ├── SKILL.md                                # frontmatter + Quick Reference index
    │   └── rules/
    │       ├── control-flow.md
    │       ├── eloquent-opinions.md
    │       ├── architecture-additions.md
    │       ├── naming.md
    │       ├── general-design.md
    │       ├── operational-safety.md
    │       ├── blade-views.md
    │       ├── display-values.md
    │       ├── page-toolbar.md
    │       ├── flash-messages.md
    │       └── localization.md
    ├── tdd-bug-fixing/
    │   └── SKILL.md                                # six-step TDD bug-fix loop
    ├── adrs/
    │   └── SKILL.md                                # Nygard ADRs in docs/adr/
    └── session-scoping/
        └── SKILL.md                                # bounded tasks, task contracts, targeted verification, handoff notes
pint.json                                           # Laravel preset + strict_types / strict_comparison / is_null / modernize_types_casting
phpstan.neon.dist                                   # Larastan + phpstan-strict-rules at level 6 with exception strictness
.aiignore                                          # credential and sensitive runtime-file exclusions
```

The overlay's eleven topic files — **Control Flow**, **Eloquent Opinions**, **Architecture Additions**, **Naming**, **General Design**, **Operational Safety**, **Blade Views**, **Display Values**, **Page Toolbar**, **Flash Messages**, **Localisation** — each end with the Boost rules they compose alongside. `SKILL.md` is a thin Quick-Reference index that points at them; agents read it first (via its `description`) to decide whether to activate the skill.

`session-scoping` is a different kind of skill: instead of code-style rules, it covers how to run the AI-agent session itself — one bounded deliverable at a time, a task contract up front, host-aware effort recommendations, targeted verification before required project checks, recovering stalled work, and a short handoff note for work spanning multiple sessions.

## Why a skill rather than one big guideline?

Boost composes content into the consumer at install time, but it routes the two source directories differently:

- `resources/boost/guidelines/` → concatenated into the agent's always-on instructions file (e.g. `AGENTS.md` for Cursor). Boost 2.10.2 supports multiple guideline files per package; this package intentionally keeps only a small always-on breadcrumb.
- `resources/boost/skills/<name>/` → written verbatim into the agent's skills directory (e.g. `.cursor/skills/<name>/`), preserving any subdirectories. The agent loads each `SKILL.md` frontmatter at startup and activates the body **on demand** when its `description` matches the current task.

The topic files in this overlay live as separate `rules/*.md` files inside the `laravel-best-practices-overlay` skill rather than as one big guideline because that lets each topic be a self-contained file (better diffs, better navigation, easier to remove an opinion you disagree with) while keeping detailed rules out of the always-on context.

The trade-off is honest: skill content is **not** always-on. The agent only loads the body of `laravel-best-practices-overlay` (or `session-scoping`) after it decides the skill is relevant — driven by the frontmatter `description` in each `SKILL.md`, written to be broad enough to fire on any Laravel PHP work (or, for `session-scoping`, on the start of substantial agent work). The thin breadcrumb in `core.blade.php` is what *is* always-on, and its job is to nudge the agent towards both skills if its description matching ever misses.

## Position relative to Boost

This package is **strictly additive**. Each `rules/*.md` file inside `laravel-best-practices-overlay` ends with a **Composes with Boost** block that links to the Boost rule it sits alongside. Where this overlay takes an opposite position to Boost (currently only "avoid database transactions" vs. Boost's `database.md`), it is flagged in-file so you can delete that subsection if you prefer Boost's default.

The Pint and PHPStan configs are similarly additive: Pint layers four extra rules on top of the standard `laravel` preset, and the PHPStan config is a baseline you can extend.

`session-scoping` has no Boost equivalent — Boost does not cover session workflow — so there is nothing to compose it against; it composes only with this package's own `tdd-bug-fixing` and `adrs` skills.

## Other agents and non-Boost setup

For agents without a Boost adapter, copy each complete skill directory into the
agent's documented project skill location, preserving `SKILL.md` and `rules/`.
Do not copy just the entrypoint. Add a short reference to the guideline below
in the agent's project instructions. If the host has no skill loader, tell it
to read the relevant `SKILL.md` and follow its relative links explicitly:


```
vendor/jpswade/laravel-best-practices/resources/boost/guidelines/core.blade.php
vendor/jpswade/laravel-best-practices/resources/boost/skills/laravel-best-practices-overlay/SKILL.md
vendor/jpswade/laravel-best-practices/resources/boost/skills/laravel-best-practices-overlay/rules/*.md
vendor/jpswade/laravel-best-practices/resources/boost/skills/tdd-bug-fixing/SKILL.md
vendor/jpswade/laravel-best-practices/resources/boost/skills/adrs/SKILL.md
vendor/jpswade/laravel-best-practices/resources/boost/skills/session-scoping/SKILL.md
```

For Cursor, a project rule can point to these files. For chat-only AI tools,
provide the selected skill and relevant rule files as context; automatic
discovery and filesystem access are not assumed. The content is plain
Markdown and remains usable without Boost. Host permissions and explicit user
instructions still govern what the agent can do.

## Adding a new practice

Open the relevant file under `resources/boost/skills/laravel-best-practices-overlay/rules/` (or create a new one if the practice opens a new topic) and add a new `## H2` subsection. Follow the existing shape:

- An `## H2` title naming the practice.
- A short rationale paragraph.
- **Incorrect:** / **Correct:** code blocks where they aid understanding.
- If the new practice has a direct Boost counterpart, add a bullet to the file's existing **Composes with Boost** list.

After adding or renaming a rule, also update the **Quick Reference** in `resources/boost/skills/laravel-best-practices-overlay/SKILL.md` so the one-line summary stays in sync.

## Validate skill changes

CI validates portable YAML metadata, skill names, description lengths, and
bundled rule references. Install the Composer development dependencies and run
the same check locally:

```bash
composer install
composer validate:skills
```

After changes to packaging or supported agent paths, rerun `boost:install` in
a disposable Laravel application that directly requires this package and
Boost. Verify the four skills and nested rule files at each selected agent's
destination. Host activation still needs the discovery check described above.

## What this package deliberately does not ship

- No `.ai/` directory — Boost installs this package's `resources/boost/` content into each selected agent's instruction and skill locations.
- No service-provider beyond `vendor:publish` for the bundled configs and `.aiignore`. No Artisan commands, no facades, no migrations.
- No content that overlaps Boost's built-in `laravel-best-practices/rules/*.md` — verified at authoring time.
- No Rector config, no `tomasvotruba/unused-public` in the baseline PHPStan config (both are referenced from the relevant overlay subsections as opt-in follow-ons).

For per-practice rejections — specific best-practices that were considered and deliberately left out, plus the small set of deliberate deviations from common Laravel advice — see [`DECISIONS.md`](DECISIONS.md). Consult it before proposing a new rule, so the project doesn't keep rediscovering the same answers.

## RFC nature

These are best practices, not coding standards. Coding standards are the things that Pint can mechanically enforce — bracket placement, trailing commas, type-cast syntax. Best practices are the design defaults that need a person (or an AI) to apply judgement.

This package is a working set of opinions. Where the opinions are widely accepted in the Laravel community, they are stated firmly. Where they are deliberately contrarian (e.g. avoiding database transactions by default), they are flagged in-file so you can take the opposite view without rewriting the file.

If you disagree with anything here, open an issue or a pull request — the bar is "is this useful to teach an AI?", not "is this universally correct?".

## Licence

MIT. See [`LICENSE`](LICENSE).
