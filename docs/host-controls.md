# Optional host controls

These templates implement the package's conservative sensitive-path policy.
They do not detect secrets by content. `.env.example` and `.env.testing` remain
excluded, including nested copies. Keep project-specific exclusions too.

## Publish and merge

Run only the tag for the host you use:

```sh
php artisan vendor:publish --tag=laravel-best-practices-cursorignore
php artisan vendor:publish --tag=laravel-best-practices-aiexclude
php artisan vendor:publish --tag=laravel-best-practices-geminiignore
```

These publish `.cursorignore`, `.aiexclude`, and `.geminiignore`, respectively,
at the application root. Normal publishing skips existing destination files;
it does **not** merge updates into them. Do not force replacement. Compare the
corresponding file in `vendor/jpswade/laravel-best-practices/resources/host-controls/`
and manually merge missing exclusions into the existing file. Preserve local
protections, review negations (`!`) and ordering, and test the merged result.
A later negation can undo an earlier exclusion. Back up existing configuration
before editing; review the diff before activating it.

The existing `laravel-best-practices-aiignore`, `-pint`, and `-phpstan` tags are
unchanged. `laravel-best-practices-all` still publishes **only** `.aiignore`,
`pint.json`, and `phpstan.neon.dist`. Installation alone publishes nothing.
Avoid provider-wide or unfiltered publishing when you only want one host.
No tag publishes Claude or Codex settings.

## Host activation and pattern semantics

Official documentation checked **2026-11-05**; rolling host documentation is
not a promise of compatibility with every historical release.

- **Cursor:** place `.cursorignore` at the project root. It uses gitignore
  syntax for Agent/Tab/context references. Terminal and MCP access are outside
  this protection. Parent-file discovery requires the Hierarchical Cursor
  Ignore setting. Check indexing/ignore settings and test a new session.
  [Official Cursor documentation](https://cursor.com/docs/reference/ignore-file).
- **Gemini Code Assist:** `.aiexclude` uses gitignore syntax. VS Code's Context
  Exclusion File setting defaults to this name; verify it has not been changed.
  `.aiexclude` takes precedence over conflicting `.gitignore` directives.
  This covers supported context features, not arbitrary filesystem access.
  JetBrains does not support configuring these exclusion settings; IDE/agent
  modes must be verified separately.
  [Official Code Assist documentation](https://docs.cloud.google.com/gemini/docs/codeassist/create-aiexclude-file).
- **Gemini CLI:** put `.geminiignore` at the project root and restart the
  session after edits. Its documented gitignore conventions include comments,
  globs, directory suffixes, root anchoring, and negation. Only tools that
  respect the file filter are covered, including `@` attachment. Shell and
  MCP reads are not universally fenced by this file.
  [Official Gemini CLI documentation](https://geminicli.com/docs/cli/gemini-ignore/).

For these gitignore-style templates, a bare filename pattern matches at any
depth; `/name` anchors at the root; `directory/` matches directories; and
`**/bootstrap/cache/config.php*` covers root and nested Laravel applications.
`*` does not cross directory separators. These distinctions follow the
[Git pattern specification](https://git-scm.com/docs/gitignore).
The three labelled files intentionally start with the same patterns because
these hosts document this common subset. They remain independent files so a
host-specific correction need not change other hosts. Shared behavioral cases,
not a generator or equality assertion, keep the intended coverage aligned.

## Merge permission examples

Examples live in `resources/host-controls/` and are **fragments**, not complete
settings files. Review them alongside existing permissions and organizational
policy. Do not copy them over a settings file. Keep equivalent existing tools
and protections; these examples do not require a particular integration.

### Claude Code

Merge the entries from `claude-permissions.example.json` into the existing
`permissions.deny` array in project `.claude/settings.json`, retaining all
other fields and rules. The `Read` patterns begin with `/` to anchor to the
project settings source and use `**` for nested paths. Home-relative entries
illustrate outside-workspace protection; add other credential stores locally.
Do not relocate these project-anchored rules into user settings unchanged.

Inspect `/permissions` in a fresh session. Read denies cover built-in file
reads and recognized Bash file commands, but arbitrary subprocesses can read
indirectly. Review Bash, PowerShell, MCP permissions and sandbox controls
separately. A read deny is not an edit deny; add `Edit` restrictions if needed.
The installed 2.1.318 CLI was identified, but live permission enforcement was
not exercised: no authenticated/model session or private account inputs were
used. No older-version minimum is asserted.
[Official Claude permission semantics](https://code.claude.com/docs/en/permissions).

### Codex

Merge `codex-permissions.example.toml` into an existing selected permission
profile, replacing `project` with its name. Merge keys into existing TOML
tables; duplicate table declarations are invalid. Preserve other filesystem,
network, and approval restrictions. Select the profile with `default_permissions`
or `--permission-profile`; the fragment deliberately does not change selection.
For a new profile, explicitly choose a baseline such as `extends = ":workspace"`.

Beta profiles do not compose with legacy `sandbox_mode` settings or `--sandbox`;
verify the effective configuration. Workspace-relative deny globs cover local
sandboxed commands. Home-path examples require local adaptation; MCP,
connectors, browsers, cloud execution, and unsandboxed approvals are separate.
On Linux/WSL/Windows, glob matches are snapshotted at process startup; newly
created matches may remain accessible until a new process starts. Unbounded
`**` can require `glob_scan_max_depth`; choose and test a sufficient depth.
Only macOS enforcement was tested here. Do not infer other-platform enforcement.
[Official Codex permission profiles](https://learn.chatgpt.com/docs/permissions).

## Verification record

Observed on **2026-11-05**, macOS **26.5 arm64**, PHP **8.3.30**, Composer
**2.10.3**, Git **2.46.0**, Node **18.20.8** (Gemini core module execution only,
not a claim that this Node version supports the full Gemini CLI).
All file contents were synthetic. No real credential values were inspected.

- **Git reference engine:** 86 paths per template, including compatibility
  `.aiignore`; 344 checks passed. Every case runs at root and under
  `packages/demo/`. Denied categories include environments, auth stores, keys,
  logs, dumps, runtime data, and cached Laravel config. Positive controls
  include application source and `bootstrap/cache/packages.php`.
- **Gemini CLI core 0.67.0:** actual `FileDiscoveryService.shouldIgnoreFile`
  and batch `filterFiles` passed all 86 cases with Git filtering disabled.
  Disabling Gemini filtering allowed the synthetic `.env` control. This is
  observed discovery-engine filtering, not a model session, terminal, MCP,
  or IDE enforcement test.
- **Codex CLI 0.166.0:** native `codex sandbox` on macOS passed 86 actual
  Python file-open attempts, with the example's workspace rules in an explicit
  test profile extending `:workspace`. Denied reads raised permission errors;
  allowed controls remained readable. No model or authentication was needed.
  Home-path rules, symlink escapes, other tools and platforms were not tested.
- **Laravel 13.40.0 disposable application:** Composer path installation and
  package discovery passed. Each of six individual tags copied exact bytes,
  published no unrelated target, and preserved existing sentinel contents on
  a second publish. `all` copied only the legacy three files and preserved
  existing files. No Claude/Codex settings were published.
- **Unavailable/unverified:** Cursor IDE was absent (the launcher reported no
  installation); Gemini Code Assist IDE integration was unavailable. Their
  patterns have official-doc and Git syntax coverage only. Claude's native
  permission evaluator was not independently exposed by this test setup.
  Windows/Linux, full Gemini CLI sessions and other Laravel versions were not
  run locally. Repository CI remains responsible for its PHP/Laravel matrix.

### Reproduce without private inputs

```sh
python3 scripts/verify_host_patterns.py
# Optional: installed Codex supporting beta permission profiles (Python 3.11+)
python3 scripts/verify_host_patterns.py --codex

# Install host test tooling outside the package; it adds no runtime dependency.
npm install --prefix /tmp/lbp-host-tools --ignore-scripts @google/gemini-cli-core@0.67.0
node scripts/verify_gemini_patterns.mjs /tmp/lbp-host-tools/node_modules/@google/gemini-cli-core
composer validate --strict --no-check-publish
composer validate:skills
```

Use a new temporary directory for the publishing test. Create a Laravel app
with `composer create-project laravel/laravel <temporary-app> --no-scripts`,
using an empty temporary `COMPOSER_HOME`. Register this checkout as a Composer
`path` repository and require `jpswade/laravel-best-practices:@dev` with
`--no-scripts`. Then run:

```sh
python3 scripts/verify_publishing.py --disposable-app <temporary-app>
```

The test refuses existing destination files and cleans up its own published
fixtures. It invokes actual Artisan commands, not a mocked provider. Never
point it at an application containing private data. For each unavailable host,
repeat these shared paths in a synthetic workspace, verify a denied attachment
and an allowed control in the active tool, and record version/settings/surface
before relying on deployment. Filename filters cannot replace an isolated
environment without real credentials.
