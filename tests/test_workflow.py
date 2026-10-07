"""Evaluate the deployment contract, not whitespace or YAML source lines.

The workflow uses JSON syntax, a YAML subset accepted by GitHub Actions.
These local checks do not replace a successful GitHub Actions run.
"""
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def permits(condition, ref, event):
    values = {'ref': ref, 'event_name': event}
    results = []
    for clause in condition.split('&&'):
        match = re.fullmatch(r"\s*github\.(ref|event_name)\s*(==|!=)\s*'([^']+)'\s*", clause)
        if not match:
            raise AssertionError(f'Unreviewed deployment condition: {clause}')
        field, operator, expected = match.groups()
        results.append((values[field] == expected) if operator == '==' else (values[field] != expected))
    return all(results)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        path = ROOT / '.github/workflows/pages.yml'
        self.assertTrue(path.is_file(), 'Pages workflow is not implemented')
        self.flow = json.loads(path.read_text())

    def test_only_main_may_publish(self):
        gate = self.flow['jobs']['deploy']['if']
        for ref, event, expected in [
            ('refs/heads/main', 'push', True),
            ('refs/heads/main', 'workflow_dispatch', True),
            ('refs/heads/main', 'pull_request', False),
            ('refs/pull/1/merge', 'pull_request', False),
            ('refs/heads/feature', 'workflow_dispatch', False),
            ('refs/heads/feature', 'push', False),
        ]:
            with self.subTest(ref=ref, event=event):
                self.assertEqual(expected, permits(gate, ref, event))

    def test_no_privileged_pr_trigger(self):
        events = self.flow['on']
        self.assertNotIn('pull_request_target', events)
        self.assertEqual(['main'], events['push']['branches'])
        self.assertIn('pull_request', events)
        self.assertIn('workflow_dispatch', events)

    def test_validation_gates_deployment(self):
        self.assertEqual('validate', self.flow['jobs']['deploy']['needs'])
        steps = self.flow['jobs']['validate']['steps']
        runs = [step['run'] for step in steps if 'run' in step]
        self.assertIn('python3 -m unittest discover -s tests -v', runs)
        self.assertIn('python3 scripts/validate_site.py site', runs)
        self.assertFalse(any(step.get('continue-on-error') for step in steps))

    def test_only_site_is_uploaded(self):
        steps = self.flow['jobs']['deploy']['steps']
        upload = [s for s in steps if s.get('uses', '').startswith('actions/upload-pages-artifact@')]
        self.assertEqual(1, len(upload))
        artifact = (ROOT / upload[0]['with']['path']).resolve()
        self.assertEqual(ROOT / 'site', artifact)
        self.assertTrue((artifact / 'app-ads.txt').is_file())
        self.assertFalse((artifact / 'docs').exists())
        self.assertFalse((artifact / '.git').exists())

    def test_write_permissions_restricted_to_deploy(self):
        self.assertEqual({'contents': 'read'}, self.flow['permissions'])
        self.assertNotIn('permissions', self.flow['jobs']['validate'])
        deploy = self.flow['jobs']['deploy']
        self.assertEqual({'contents': 'read', 'pages': 'write', 'id-token': 'write'}, deploy['permissions'])
        self.assertEqual('github-pages', deploy['environment']['name'])
        self.assertFalse(deploy['concurrency']['cancel-in-progress'])


if __name__ == '__main__':
    unittest.main()
