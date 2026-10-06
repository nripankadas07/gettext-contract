# gettext-contract

Checks declared Python percent/brace contracts, plural shapes, fuzzy and untranslated entries.

Built for localization release engineers reviewing UTF-8 Python-format PO catalogs. A translated placeholder, conversion or plural shape can break a released message. Review needs a small, offline, machine-readable contract report.

## Quickstart

Python 3.11 or later. No runtime dependencies, service account or API key.
Clone the public source, create an isolated environment and install:

```sh
git clone https://github.com/nripankadas07/gettext-contract.git
cd gettext-contract
python -m venv .venv
. .venv/bin/activate
python -m pip install .
gettext-contract example.po
```

Expected synthetic demo outcome: 3 checked translations, zero findings. JSON goes to stdout.
Use `--help` for options. On Windows, activate with `.venv\Scripts\activate`.
Windows is not locally validated in this launch; remote CI covers Linux Python 3.11/3.12/3.13.

## Contract

Preserve context and multiline identity, permit named-field reordering, catch missing/type/spec changes, validate plural indexes, expose fuzzy/untranslated/unsupported entries, and reject malformed catalogs.

Exit 0 means the supported input has no gated finding; 1 means a finding or gate failure;
2 means malformed or unsupported input/coverage. Read the JSON counts and limitations
before interpreting a zero result as comprehensive validation.

## Limitations

UTF-8 and quoted PO syntax compatible with Python string literals only; entries require blank separators. Only python-format and python-brace-format are validated. Unflagged strings are counted separately, not claimed safe. Source singular/plural contracts must match; exact types/specs/counts are conservative and can require human review. This is not a complete GNU PO parser, grammar checker or translation platform. No plural-expression evaluation. Obsolete entries are ignored. Catalogs are limited to 10 MB.

## Verify and contribute

```sh
python -m unittest -v
python -m compileall -q gettext_contract.py
python -m pip install build
python -m build
```

The tests exercise successful behavior and meaningful failure cases. See
[validation](VALIDATION.md), [research](RESEARCH.md), [contribution guidance](CONTRIBUTING.md)
and [security guidance](SECURITY.md). Open a reproducible issue with a synthetic fixture;
do not post private exports or credentials. MIT licensed; implementation is original,
with no competitor code or prose copied.
