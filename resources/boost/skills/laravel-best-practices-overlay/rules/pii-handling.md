# Personal data before agent context

Secret scanning detects credential patterns; it does not establish the absence
of personal data. PII review is a distinct practice for production exports,
logs, support transcripts, screenshots, fixtures and any data supplied to an
agent. Names, addresses, contact details, account/customer identifiers, health
information and combinations of seemingly innocuous attributes can identify
people without containing credentials.

Prefer synthetic data created for the task. Do not open protected originals to
see whether they contain PII. Detection/redaction is not proof that data is
safe, nor permission for an agent to inspect it. The credential boundary in
[operational safety](operational-safety.md) still applies. A request to debug a
customer issue does not authorise reading exports, logs or transcripts.

## Controlled preprocessing, when genuinely needed

Have an authorised data owner minimise fields and records before data reaches
the agent. Keep source data and intermediate results in an approved environment
with restricted access and retention. Remove unnecessary identifiers and free
text; preserve referential structure with synthetic replacements when useful.
Pseudonymised identifiers and lookup tables remain sensitive. Review the
result for context-based identification and credentials before releasing only
the minimum approved example. Never paste raw detections into chat or tickets.

[Presidio](https://presidio.dataprivacystack.org/) is an optional preprocessing
candidate, not a required package dependency or an agent-side permission to
read data. Its text analyzers combine recognizers and NLP; image workflows need
separate OCR/redaction. Evaluate the selected deployment with a labelled
synthetic corpus before using protected data:

- Pin the analyzer, anonymizer, models and image/OCR dependencies in controlled
  tooling; review their licenses and maintenance separately. No runtime PHP
  dependency is added here.
- Define application-specific entities such as customer IDs, internal account
  formats and sensitive domain terms. Use [custom recognizers](https://presidio.dataprivacystack.org/tutorial/02_regex/)
  and representative context, not just generic email/phone recognition.
- Select supported languages/models and thresholds explicitly; measure false
  positives and false negatives per entity and language. A lower threshold can
  over-redact; a higher threshold can miss people. Retest after model changes.
- Review output before release. Test nested export fields, multiline logs,
  quoted support messages, attachments, image regions and OCR misses. Screenshots
  can retain names in pixels/metadata even when a text detector reports clean.
- Publish only aggregate evaluation counts and synthetic case labels. Keep raw
  text, offsets, mappings, reports and screenshots restricted; do not enable
  remote services without separate data-transfer authorisation.

## Executed synthetic examples

[pii_demo.py](../../../../../examples/safety/pii_demo.py) is a deterministic
standard-library demonstration, **not Presidio and not a production sanitizer**.
It accepts no input files. It tests an email regex and a custom `CUST-` customer
ID recognizer, performs replacement assertions internally and emits only case
labels and TP/FP/FN counts. Observed results on 2026-11-05:

- Export email and support customer ID: one expected detection each (2 TP).
- Public contact mailbox and a product SKU resembling a customer ID: one false
  positive each (2 FP); context determines whether a match is personal data.
- Obfuscated email, free-text patient name and Japanese name: one false negative
  each (3 FN). Successful replacement of recognised matches leaves these intact.
- Clean operational message: no detections.

The [native secret-scanner benchmark](secret-scanning.md) also passed the
synthetic name/email/customer-ID log without findings in both tools. That is
why secret scanning cannot substitute for PII review. These narrow examples
make no claim about Presidio's accuracy. A project adopting Presidio must run
its own pinned analyzer/models against these and expanded cases; Presidio was
not installed or benchmarked for this package recommendation.

## Composes with Boost

- [Operational safety](operational-safety.md) governs access before processing; this practice governs minimisation and review before agent context.
