"""Audit declared Python formatting contracts in UTF-8 gettext PO catalogs."""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import json
from pathlib import Path
import re
import string
import sys

MAX_BYTES = 10_000_000
FIELD = re.compile(r'^(msgctxt|msgid_plural|msgid|msgstr(?:\[\d+\])?)\s+(".*")$')
PERCENT = re.compile(r'%(?:\(([^)]+)\))?([-+#0 ]*)(\*|\d+)?(?:\.(\*|\d+))?([hlL])?([diouxXeEfFgGcrsa%])')


def parse(text: str) -> list[dict]:
    entries, fields, flags, current, start = [], {}, set(), None, 0

    def flush():
        nonlocal fields, flags, current
        if fields:
            if 'msgid' not in fields:
                raise ValueError(f'line {start}: entry lacks msgid')
            entries.append({'line': start, 'fields': fields, 'flags': flags})
        fields, flags, current = {}, set(), None

    for number, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            flush()
        elif line.startswith('#~'):
            if fields:
                flush()
        elif line.startswith('#,'):
            flags.update(x.strip() for x in line[2:].split(','))
        elif line.startswith('#'):
            continue
        else:
            match = FIELD.fullmatch(line)
            if match:
                key, quoted = match.groups()
                if key in fields:
                    raise ValueError(f'line {number}: duplicate field; separate PO entries with blank lines')
                current = key
                if not fields:
                    start = number
                value = ast.literal_eval(quoted)
                if not isinstance(value, str):
                    raise ValueError(f'line {number}: expected quoted string')
                fields[key] = value
            elif line.startswith('"') and current:
                value = ast.literal_eval(line)
                if not isinstance(value, str):
                    raise ValueError(f'line {number}: expected string continuation')
                fields[current] += value
            else:
                raise ValueError(f'line {number}: unsupported PO syntax')
    flush()
    seen = set()
    for entry in entries:
        f = entry['fields']
        key = (f.get('msgctxt', ''), f['msgid'])
        if key in seen:
            raise ValueError('duplicate context/msgid identity')
        seen.add(key)
    return entries


def brace_contract(text: str) -> Counter:
    result = Counter()
    automatic = 0
    positional_mode = None

    def walk(value, depth=0):
        nonlocal automatic, positional_mode
        if depth > 8:
            raise ValueError('brace nesting exceeds 8')
        for _, field, spec, conversion in string.Formatter().parse(value):
            if field is None:
                continue
            if field == '':
                if positional_mode == 'manual':
                    raise ValueError('mixed automatic and explicit positional brace fields')
                positional_mode = 'automatic'
                field = str(automatic)
                automatic += 1
            elif re.match(r'^\d+(?:$|[.\[])', field):
                if positional_mode == 'automatic':
                    raise ValueError('mixed automatic and explicit positional brace fields')
                positional_mode = 'manual'
            if conversion not in {None, 's', 'r', 'a'}:
                raise ValueError('unsupported brace conversion')
            # Exact field/conversion/spec preserves type/precision contracts. A
            # translated format spec is conservatively considered a change.
            result[(field, conversion or '', spec)] += 1
            if '{' in spec:
                walk(spec, depth + 1)
    walk(text)
    return result


def percent_contract(text: str) -> tuple:
    named, positional, position, mode = Counter(), [], 0, None
    while position < len(text):
        percent = text.find('%', position)
        if percent < 0:
            break
        match = PERCENT.match(text, percent)
        if not match:
            raise ValueError('malformed or unsupported Python percent formatting')
        name, flags, width, precision, length, kind = match.groups()
        position = match.end()
        if kind == '%':
            if name or flags or width or precision or length:
                raise ValueError('unsupported decorated percent escape')
            continue
        this_mode = 'named' if name else 'positional'
        if mode and this_mode != mode:
            raise ValueError('mixed named and positional percent fields')
        mode = this_mode
        signature = (kind, width or '', precision or '', length or '')
        if name:
            if width == '*' or precision == '*':
                raise ValueError('dynamic width not supported with named fields')
            named[(name, *signature)] += 1
        else:
            positional.append(signature)
    return tuple(sorted(named.items())), tuple(positional)


def audit(entries: list[dict]) -> dict:
    findings, checked, skipped = [], 0, 0
    header = next((e['fields'].get('msgstr', '') for e in entries if e['fields']['msgid'] == ''), '')
    plural_match = re.search(r'(?im)^Plural-Forms:\s*nplurals\s*=\s*(\d+)\s*;', header)
    nplurals = int(plural_match[1]) if plural_match else None
    if nplurals is not None and not 1 <= nplurals <= 20:
        raise ValueError('nplurals must be between 1 and 20')
    for entry in entries:
        f, flags, line = entry['fields'], entry['flags'], entry['line']
        if f['msgid'] == '':
            continue
        issue = {'line': line, 'context': f.get('msgctxt', ''), 'msgid': f['msgid']}
        if 'fuzzy' in flags:
            findings.append({**issue, 'kind': 'fuzzy', 'detail': 'translation requires review'})
            continue
        modes = flags & {'python-format', 'python-brace-format'}
        unsupported = {x for x in flags if x.endswith('-format') and not x.startswith('no-') and x not in modes}
        if unsupported or len(modes) > 1:
            findings.append({**issue, 'kind': 'unsupported-format', 'detail': ', '.join(sorted(unsupported or modes))})
            continue
        plural = 'msgid_plural' in f
        translated = {k: v for k, v in f.items() if k.startswith('msgstr')}
        expected = {f'msgstr[{i}]' for i in range(nplurals or 0)} if plural else {'msgstr'}
        if (plural and nplurals is None) or set(translated) != expected:
            findings.append({**issue, 'kind': 'plural-shape', 'detail': 'translation fields do not match declared nplurals/singular shape'})
            continue
        for key, value in sorted(translated.items()):
            if not value:
                findings.append({**issue, 'kind': 'untranslated', 'detail': key})
                continue
            if not modes:
                skipped += 1
                continue
            check = brace_contract if 'python-brace-format' in modes else percent_contract
            try:
                contract = check(f['msgid'])
                if plural and check(f['msgid_plural']) != contract:
                    findings.append({**issue, 'kind': 'source-contract', 'detail': 'singular/plural source contracts differ'})
                    break
                checked += 1
                if check(value) != contract:
                    findings.append({**issue, 'kind': 'placeholder-mismatch', 'detail': key})
            except ValueError as exc:
                findings.append({**issue, 'kind': 'invalid-format', 'detail': str(exc)})
    return {'schema': 1, 'checked_translations': checked, 'unflagged_translations': skipped, 'findings': findings}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('catalog', type=Path)
    args = parser.parse_args(argv)
    try:
        with args.catalog.open('rb') as handle:
            data = handle.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError('catalog exceeds 10 MB')
        report = audit(parse(data.decode('utf-8-sig')))
        print(json.dumps(report, indent=2, ensure_ascii=True))
        return int(bool(report['findings']))
    except (OSError, ValueError, SyntaxError, RecursionError) as exc:
        print(f'gettext-contract: invalid input: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
