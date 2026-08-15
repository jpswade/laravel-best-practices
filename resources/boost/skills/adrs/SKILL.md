---
name: adrs
description: >-
  Record and maintain Architecture Decision Records in docs/adr/ using Nygard's
  Context, Decision, Consequences format plus an index. Use when writing or
  updating an ADR, superseding a decision, recording a hard-to-reverse
  architecture or product-architecture choice, or when a design session settles
  one.
license: MIT
metadata:
  author: jpswade
when_to_use:
  - The user asks to write, update, or supersede an Architecture Decision Record.
  - A hard-to-reverse architecture or product-architecture choice is being made (schema, module boundaries, tenancy, external integrations, lock-in).
  - A design session has settled a decision that would surprise a future reader without context.
when_not_to_use:
  - Routine implementation, bug fixes, or choices already obvious from framework or platform defaults.
  - Local capability details (page behaviour, field lists) that belong in a feature doc.
  - Glossary or ubiquitous-language updates — those belong in CONTEXT.md via domain-modeling.
  - Work still being designed — keep that in working notes until a decision is actually made.
---

# Architecture Decision Records

ADRs are the durable record of **why**. Feature or capability docs describe **what**. Plans, prototypes, and issue notes are working notes — not the long-term record.

Use [Michael Nygard's template](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions): Context, Decision, Consequences. Not a one-paragraph stub. If `docs/adr/` already exists, match its numbering, index, and density.

System-wide ADRs live in `docs/adr/`. In a multi-context repo (`CONTEXT-MAP.md` at the root), context-specific decisions live next to that context's `CONTEXT.md`. Create the directory lazily when the first ADR is needed.

## When to write one

All three must be true:

1. **Hard to reverse** — schema, module boundaries, tenancy, external integrations, lock-in
2. **Surprising without context** — a future reader will wonder why it was done this way
3. **A real trade-off** — genuine alternatives, picked for specific reasons

Write **at decision time**. Do not wait until after implementation.

Skip: routine implementation, bug fixes, and choices already obvious from framework or platform defaults.

### Belongs elsewhere

| Kind of choice | Put it here |
|----------------|-------------|
| Cross-cutting or foundational (modules, tenancy, integration patterns) | **ADR** in `docs/adr/` (or the context's `docs/adr/`) |
| Local to one capability (page behaviour, field list) | That feature's docs |
| Glossary / ubiquitous language | `CONTEXT.md` via domain-modeling — never implementation |
| Still being designed | Working notes (plans, scratch issues) — wherever this repo already keeps them |
| Explicit no-s for a feature's scope | Feature doc **and** an ADR if the no is architectural |

If another skill or ticket asks for an ADR outline, write the full Nygard record and link it from the source.

## Before writing

1. Read `docs/adr/README.md` (create a simple index if none exists) and any ADRs that touch the same area.
2. If the new choice **contradicts** an existing ADR, do not silently override — **supersede** it (below) or surface the conflict and stop.
3. Scan the target `docs/adr/` for the highest `NNNN` and increment by one. Numbering is global within that directory; an index may group thematically (numbers will interleave).
4. Confirm it is one decision. Split if two independent choices are being smuggled together.

## File and shape

`docs/adr/NNNN-kebab-slug.md`

```markdown
# ADR-NNNN: Short title of the decision

**Date:** YYYY-MM-DD
**Status:** Accepted
**Supersedes:** [ADR-NNNN](NNNN-slug.md)   ← only when replacing an earlier decision

## Context

Forces at play — technical, product, or organisational. Cite related ADRs.
What would go wrong if we did not decide?

## Decision

What we chose. Explicit no-s are as valuable as yes-s.
Use a table or numbered rules when the choice is a mapping or a set of constraints.

## Consequences

**Positive** / **Negative** / **Neutral** when outcomes are mixed.
A short paragraph is fine when the consequence is mainly a module seam or implementation pointer.
```

Status values: `Proposed` · `Accepted` · `Superseded by [ADR-NNNN](…)` · `Deprecated`.

Ship as **Accepted** once the decision is made. Use **Proposed** only while it is still being debated in-tree.

## After writing

1. Add a row to the matching thematic group in `docs/adr/README.md`. Add a group if the area is genuinely new. If there is no README yet, create one with a short intro and an index table.
2. Link from the originating issue, feature doc, or plan if that is how the decision was reached.
3. If glossary terms crystallised, update `CONTEXT.md` separately (domain-modeling) — do not turn the ADR into a glossary.

## Superseding

1. New ADR: `**Supersedes:** [ADR-NNNN](NNNN-slug.md)` plus a parenthetical of *what* is replaced (not every rule in the old file).
2. Old ADR: `**Status:** Superseded by [ADR-NNNN](NNNN-slug.md) …`. Keep the body; note which rules still stand.
3. Index: annotate the old row; list the new ADR in the right group.

## Style

- One decision per file. Match the repository's existing prose (language, spelling, tone).
- Cross-link related ADRs and feature docs. Do not duplicate a feature spec.
- Internal planning language is fine in ADRs; do not leak it into user-facing copy.
- No PII, credentials, or secrets — synthetic examples only.

## Density

Match neighbouring ADRs in the same directory:

- Mixed outcomes → Positive / Negative / Neutral subsections
- A tight seam or single constraint → a short Consequences paragraph
- Mappings and rule-sets → a table or numbered list in Decision
