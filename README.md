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

**Claude instruction loading:** if shared project guidance lives in
`AGENTS.md` and Claude does not load it, add `@AGENTS.md` to the project's
`CLAUDE.md`, preserving any existing instructions. This also covers older
Claude Code versions and configurations that read only `CLAUDE.md`. When
using this arrangement, configure Boost's `agents.claude_code.guidelines_path`
to `AGENTS.md` in `config/boost.php` so Boost maintains one shared guideline
block. In Claude Code, use `/context` to check loaded instruction files.

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

The always-on Boost guideline prohibits reading credentials on **every task**:
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

**An ignore file is not an enforced security boundary.** JetBrains AI Assistant
[documents `.aiignore` support](https://www.jetbrains.com/help/ai-assistant/disable-ai-assistant.html)
when enabled. Do not assume Claude Code, Codex, Grok Build, Antigravity, or
T3 Code enforce this filename. The always-on instructions tell agents to honour
its exclusions regardless, but instructions alone cannot guarantee access
control. Project-relative patterns also cannot protect files in the user's
home directory, and a filename list cannot identify every secret-bearing file.

Configure the selected host's supported file permissions or sandbox separately;
for example, Claude Code has documented
[Read deny rules](https://code.claude.com/docs/en/permissions).
Check their coverage for file tools, terminal commands, integrations, and
outside-workspace paths. For T3 Code, check the active provider as well as
app-provided tools. An environment without real credentials provides a stronger
boundary. Verify protections using synthetic fixtures, never real secrets.
This package publishes guidance and a template; it does not silently modify
host permissions or claim to enforce them.

For prevention at commit and release time, use **Gitleaks or an equivalent
secret scanner** in developer-controlled pre-commit hooks and required CI
checks. Scan built container images separately with an image-capable scanner,
exclude credentials from the Docker build context, and use BuildKit secret
mounts for build-time authentication. The
[operational safety rules](resources/boost/skills/laravel-best-practices-overlay/rules/operational-safety.md#scan-for-secrets-before-committing-and-publishing)
cover history/layer coverage, safe handling of findings, and credential
rotation. This is a recommendation, not an installed hook or workflow, and
does not authorise an AI agent to inspect credentials or raw scan findings.

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
