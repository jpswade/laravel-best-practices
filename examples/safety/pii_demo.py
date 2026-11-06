#!/usr/bin/env python3
"""Synthetic evaluation of deliberately limited rules, NOT a PII sanitizer."""
import re

RULES = {
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "CUSTOMER_ID": re.compile(r"\bCUST-\d{6}\b"),
}
# Expected labels describe the synthetic scenario, not whether the literal is
# a real person's information. No real customer data is accepted by this demo.
CASES = [
    ("export-email", "ada@example.test", {"EMAIL"}, {"EMAIL"}),
    ("support-customer", "Please help CUST-000042", {"CUSTOMER_ID"}, {"CUSTOMER_ID"}),
    ("public-mailbox", "Public contact: help@example.test", set(), {"EMAIL"}),
    ("product-code", "Product SKU CUST-000042", set(), {"CUSTOMER_ID"}),
    ("obfuscated-email", "ada [at] example [dot] test", {"EMAIL"}, set()),
    ("free-text-name", "Patient Ada Example", {"PERSON"}, set()),
    ("other-language", "患者：山田架空", {"PERSON"}, set()),
    ("clean", "The job completed", set(), set()),
]

if __name__ == "__main__":
    for label, text, expected, observed in CASES:
        found = {entity for entity, pattern in RULES.items() if pattern.search(text)}
        assert found == observed, "synthetic recognizer regression"
        redacted = text
        for pattern in RULES.values():
            redacted = pattern.sub("<removed>", redacted)
        for pattern in RULES.values():
            assert not pattern.search(redacted)
        # Emit only labels/counts. A successful replacement assertion still
        # leaves the missed names/obfuscations untouched; never publish text.
        print(f"{label}: TP={len(expected & found)} FP={len(found - expected)} FN={len(expected - found)}")
