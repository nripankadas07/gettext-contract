from gettext_contract import audit, parse, brace_contract, percent_contract, main
from pathlib import Path
import tempfile
import unittest


class Contracts(unittest.TestCase):
    def check(self, body):
        return audit(parse(body))

    def test_brace_reorder_escape_nested(self):
        self.assertEqual(brace_contract('{name} {{ok}} {amount:.2f}'), brace_contract('{amount:.2f} {name} {{bon}}'))
        self.assertNotEqual(brace_contract('{a:{width}}'), brace_contract('{a:{size}}'))
        with self.assertRaises(ValueError):
            brace_contract('{} {0}')

    def test_context_multiline_and_mismatch(self):
        po = '#, python-brace-format\nmsgctxt "menu"\nmsgid "Hello "\n"{name}"\nmsgstr "Bonjour {nom}"\n'
        out = self.check(po)
        self.assertEqual(out['findings'][0]['kind'], 'placeholder-mismatch')
        self.assertEqual(out['findings'][0]['context'], 'menu')

    def test_percent_named_reorder_and_type(self):
        self.assertEqual(percent_contract('%(a)s %(b)d %%'), percent_contract('%(b)d %(a)s'))
        self.assertNotEqual(percent_contract('%s %d'), percent_contract('%d %s'))
        with self.assertRaises(ValueError):
            percent_contract('%(a)s %s')

    def test_plurals_and_metadata(self):
        po = 'msgid ""\nmsgstr "Plural-Forms: nplurals=2; plural=(n != 1);\\n"\n\n#, python-format\nmsgid "%d file"\nmsgid_plural "%d files"\nmsgstr[0] "%d fichier"\nmsgstr[1] "%d fichiers"\n'
        self.assertEqual(self.check(po)['checked_translations'], 2)
        self.assertEqual(self.check(po)['findings'], [])
        self.assertEqual(self.check(po.replace('msgstr[1]', 'msgstr[2]'))['findings'][0]['kind'], 'plural-shape')

    def test_untranslated_fuzzy_unsupported_visible(self):
        for flag, value, kind in [('python-format', '', 'untranslated'), ('fuzzy, python-format', '%s', 'fuzzy'), ('c-format', '%s', 'unsupported-format')]:
            out = self.check(f'#, {flag}\nmsgid "%s"\nmsgstr "{value}"\n')
            self.assertEqual(out['findings'][0]['kind'], kind)

    def test_unflagged_not_claimed_checked(self):
        out = self.check('msgid "{x}"\nmsgstr "{y}"\n')
        self.assertEqual(out['checked_translations'], 0)
        self.assertEqual(out['unflagged_translations'], 1)

    def test_duplicates_malformed_and_format(self):
        for po in ['msgid "x"\nmsgstr "a"\n\nmsgid "x"\nmsgstr "b"', 'msgid "unterminated', 'msgstr "no source"']:
            with self.assertRaises((ValueError, SyntaxError)):
                parse(po)
        out = self.check('#, python-brace-format\nmsgid "{x}"\nmsgstr "{x"')
        self.assertEqual(out['findings'][0]['kind'], 'invalid-format')

    def test_cli_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'bad.po'
            path.write_text('#, python-brace-format\nmsgid "{name}"\nmsgstr "{nom}"')
            self.assertEqual(main([str(path)]), 1)
            path.write_bytes(b'\xff')
            self.assertEqual(main([str(path)]), 2)


if __name__ == '__main__':
    unittest.main()
