# Research and project brief

Observed: 2026-10-06T06:12:37.248955+00:00 UTC, exact query `gettext language:Python`, sorted by stars descending.
[Search receipt](https://api.github.com/search/repositories?q=gettext%20language%3APython&sort=stars&order=desc&per_page=10). Only the first ten results were inspected;
this is not an exhaustive worldwide ranking. WeblateOrg/weblate is the highest-star
relevant comparable found in this query. Comparables can serve broader/different workflows.

| Repository | Observed stars | Repository pushed UTC | License metadata |
|---|---:|---|---|
| [WeblateOrg/weblate](https://github.com/WeblateOrg/weblate) | 6106 | 2026-10-06T05:05:02Z | GPL-3.0 |
| [python-babel/babel](https://github.com/python-babel/babel) | 1469 | 2026-09-22T10:44:15Z | BSD-3-Clause |
| [mbi/django-rosetta](https://github.com/mbi/django-rosetta) | 1154 | 2026-07-30T09:05:25Z | MIT |

Pushed timestamps are evidence of repository activity, not proof of response/support quality.
Commit observations for the original research are in [machine-readable evidence](research.json).
Latest PR activity can be dependency automation rather than substantive maintenance.

## User, need and smallest useful capability

Localization release engineers reviewing UTF-8 Python-format PO catalogs. A translated placeholder, conversion or plural shape can break a released message. Review needs a small, offline, machine-readable contract report. Checks declared Python percent/brace contracts, plural shapes, fuzzy and untranslated entries.

Read Babel messages/checkers.py and current documentation. Inspected latest issues/PRs in all three comparables; no verified request for this exact new tool. Demand is inferred from release review, not attributed to those reporters.

## Fair feature comparison

Babel already validates Python percent formats and plural counts. Weblate is a broader translation platform; Rosetta integrates PO editing in Django. This tool offers a small standalone report with exact conservative brace/percent contracts, not missing functionality claimed across those products.

Our install path is a source clone plus Python pip install, with no runtime third-party
dependencies. Alternatives have their documented Go/Node/Python/Rust, hosted platform or
calendar-server workflows; their setup was reviewed in current documentation, not timed.
Our example and failure checks are runnable. Our supported input surface and support are
smaller; mature alternatives have broader documentation, integrations and maintenance history.
License metadata is reported, not legal compatibility advice; no code was reused.

No equivalent cross-tool workload was measured. No speed, reliability or global ranking
superiority is claimed. Synthetic fixtures prove only our documented behavior. Negative
results and unsupported configurations are in [validation](VALIDATION.md).

## Distinctness and discovery

Compared all five candidate briefs with 138 existing README/description briefs.
Existing trace/report/diff tools do not make these five one product: their users, accepted
input contracts and working algorithms differ. The archive-preflight idea was rejected
because it overlapped the existing wheel/path safety tools. gettext and Python localization topics; a reproducible failing PO example in this repository.

Acceptance criteria: Preserve context and multiline identity, permit named-field reordering, catch missing/type/spec changes, validate plural indexes, expose fuzzy/untranslated/unsupported entries, and reject malformed catalogs.
