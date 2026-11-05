# Secret scanner selection and controlled execution

Read alongside [operational safety](operational-safety.md). These procedures are
for a human owner or a controlled CI runner. They do not authorise an agent to
scan protected inputs or read findings. Use one suitable scanner per project;
retain an existing equivalent that meets the same checks.

## Decision and synthetic evidence (2026-11-05)

Retain **Gitleaks 8.30.1** as the baseline recommendation for projects without
an existing scanner; **Betterleaks 1.10.0** is a supported alternative after
project-specific evaluation. This small corpus does not justify a universal
migration: Betterleaks improves short-password/archive coverage but introduces
a prose false positive, and neither default detects our Laravel app key.
Add reviewed application-specific rules and re-run the corpus before adoption.
Do not install both as a routine requirement.

The reproducible [native benchmark](../../../../../examples/safety/verify.py)
creates its own temporary Laravel-shaped files and Git repository. No issued
credentials or real data are used. On macOS arm64, official release binaries
with embedded default rules produced:

| Synthetic fixture / intended classification | Gitleaks 8.30.1 | Betterleaks 1.10.0 |
| --- | --- | --- |
| Fabricated GitHub-shaped token in `.env` | Detected | Detected |
| Same token in `bootstrap/cache/config.php` | Detected | Detected |
| Same token in `storage/logs/laravel.log` | Detected | Detected |
| Base64 32-byte Laravel `APP_KEY` (secret) | Missed | Missed |
| Short `DB_PASSWORD` (secret) | Missed | Detected |
| Explicit placeholder (benign) | Clean | Clean |
| Prose assigned to password (benign demonstration) | Clean | False positive |
| Token-shaped test dummy (benign by construction) | False positive | False positive |
| Name, email, customer ID without credentials | Clean (PII gap) | Clean (PII gap) |
| Token inside ZIP, default archive settings | Missed | Detected |

The dummy result is expected for a format detector; it cannot establish whether
a credential was issued. No provider validation was used. The ZIP difference
reflects defaults, not an inability to configure Gitleaks archive traversal.
This is a coverage probe, not a performance benchmark or statistical accuracy
estimate. The PII row is not a secret-scanner false negative; see the separate
[PII practice](pii-handling.md).

Both native binaries detected staged additions and the introducing commit
range, passed a removal-only range, and still detected the removed token in
full history. Both passed clean cases and failed invalid config/revision cases.
Gitleaks initially returned zero for a non-repository Git target; the wrapper
now rejects that target and treats error-level diagnostics as failure even
when a process returns zero. Native JSON/stdout/stderr with `--redact=100`
contained no fabricated token in the tested case. This tests that value only:
paths, authors, surrounding text and other PII may remain in reports.

Release archive SHA-256 values were checked against upstream checksum files:

- `gitleaks_8.30.1_darwin_arm64.tar.gz`: `b40ab0ae55c505963e365f271a8d3846efbc170aa17f2607f13df610a9aeb6a5`
- `betterleaks_1.10.0_darwin_arm64.tar.gz`: `91eaea97709d3308c7712574a56260539c65fbd0672711537aa68d566ea630b3`

Fetch the exact assets from the [Gitleaks release](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1)
or [Betterleaks release](https://github.com/betterleaks/betterleaks/releases/tag/v1.10.0),
verify checksums before extraction/execution, and pin the platform-specific
hash in the project's trusted CI provisioning. These hashes cover arm64 macOS
only; select and verify the matching release asset for Linux CI. Avoid `latest`,
unreviewed installer scripts, and binaries/config supplied by an untrusted PR.

### Maintenance, licensing and integration

[Gitleaks upstream](https://github.com/gitleaks/gitleaks) now describes the
project as feature complete with future security patches only. Assign an owner
to review security releases and detection gaps; this is not a promise of future
rule coverage. [Betterleaks v1 documentation](https://github.com/betterleaks/betterleaks/blob/v1.10.0/README.md)
describes a v1 maintenance line; its main branch develops v2 with different
commands. Re-evaluate releases and migration costs before changing the pin.
The shared original maintainer and newer features alone do not prove quality.

Both tested CLIs have MIT licenses ([Gitleaks](https://github.com/gitleaks/gitleaks/blob/v8.30.1/LICENSE),
[Betterleaks](https://github.com/betterleaks/betterleaks/blob/v1.10.0/LICENSE)).
The separate [Gitleaks Action](https://github.com/gitleaks/gitleaks-action)
has licensing requirements for organisation use; do not conflate that with the
CLI license. Direct CLI integration avoids depending on that Action. Review
licenses for chosen wrappers, images and future versions separately.

## Executable example and verification

The [controlled runner example](../../../../../examples/safety/scan.py) uses
Python 3.9+ standard library only, checks the exact version, supplies a trusted
embedded-default configuration, ignores source-controlled suppression files
and inline allow comments, removes inherited environment configuration, and
explicitly disables Betterleaks validation. It outputs fixed status messages
only: exit 0 means no findings in scope, 1 blocks on findings, 2 blocks on setup,
scanner errors or timeout. It emits no report and discards scanner output;
never upload raw diagnostics as a CI artifact. All nonzero statuses must block
required CI, without `continue-on-error` or `|| true`.

Provision both binaries only for this comparison; replace the two absolute
paths below with their verified locations. Run from the package root:

```sh
python3 examples/safety/verify.py /opt/scanners/gitleaks /opt/scanners/betterleaks
python3 examples/safety/pii_demo.py
composer validate:skills
```

In an explicitly authorised controlled job, invoke the wrapper with the chosen
scanner name, verified binary path, mode and target directory. Supported modes
are `staged` (native Git index scan), `range` (requires `--revision` containing
full `baseSHA..headSHA`), `history` (all available refs), and `dir` (filesystem).
Use staged checks in developer hooks; required CI scans the actual merge-base
to proposed head range with both commits fetched. Periodically scan full
history with all relevant refs fetched; reject shallow/incomplete checkouts in
that job. A passing narrow range does not clear old or deleted secrets.

Run on isolated, trusted runner infrastructure without production credentials,
untrusted hooks, external diff helpers or executable PR configuration. Restrict
network egress during scanning. The wrapper is an example, not a sandbox.
For reviewed exceptions, adapt its trusted configuration in the controlled
runner: specify rule/path scope, rationale, owner and expiry, and verify a real
synthetic detection still blocks. Never blanket-ignore `.env`, logs or fixtures.

Errors require owner investigation of provisioning, access, configuration,
revision availability or resource limits, then a rerun. If details are needed,
a human may collect diagnostics within an access-controlled environment with
short retention; provide the agent only a sanitised error category. Redaction
is not permission to publish JSON/SARIF, filenames, excerpts or author metadata.

Credential validation makes provider requests and can transmit findings;
revocation changes live credentials. Both are **separate, explicitly authorised
operations**, outside routine scanning. Keep validation off, never add debug
HTTP output, and do not infer permission from a request to scan. Let the
credential owner coordinate revocation/rotation and incident response.

## Container boundary

Neither tested CLI exposes a native image scan command. Running a scanner
inside Docker scans only its mounted inputs; a directory scan of an extracted
final filesystem does not inspect removed layers, image configuration,
intermediate builds or caches. No image coverage is claimed by this benchmark.
Do not apply Betterleaks v2 container claims to the tested v1 binary. Follow the
[image/build-context procedure](operational-safety.md#scan-for-secrets-before-committing-and-publishing)
and verify the chosen image-capable tool against synthetic layer/config/cache
fixtures before relying on it. No scanner result replaces owner-led rotation.

## Composes with Boost

- [Operational safety](operational-safety.md) adds the credential boundary to Boost's development workflows.
