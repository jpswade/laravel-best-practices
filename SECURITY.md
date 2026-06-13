# Security Policy

## Supported versions

Security fixes are applied to the latest tagged release on the `main` branch. Older tags are not patched; please upgrade to the latest release.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security problems.

Preferred channel: [GitHub private vulnerability reporting](https://github.com/jpswade/laravel-best-practices/security/advisories/new) on this repository.

When reporting, please include:

- A description of the issue and the conditions under which it triggers.
- Affected version(s) or commit SHA, where known.
- A minimal reproduction (or proof-of-concept) if you have one.
- Any suggested mitigation, if you have one.

You should expect an acknowledgement within **5 working days**. We will keep you updated as we investigate and prepare a fix; coordinated disclosure is appreciated until a patched release is available.

## Scope

This package is a development-time Composer dependency that ships Markdown guidance, a Pint config, and a PHPStan config. It registers a no-op service provider whose only job is to expose `vendor:publish` tags. It contains no runtime request-handling code, no database access, and no network I/O.

In practice, the relevant security surface is therefore:

- **Supply chain** — the `composer.json` constraints and the contents of any tagged release.
- **CI configuration** — the GitHub Actions workflows in `.github/workflows/`.
- **Published guidance** — the Markdown files under `resources/boost/skills/` that are read by AI coding assistants in consumer projects.

Reports outside this scope (for example, vulnerabilities in Laravel itself, in Boost, or in a consumer's application) should go to the relevant upstream project.
