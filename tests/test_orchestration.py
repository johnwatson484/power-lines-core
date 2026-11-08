import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class OrchestrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.core = self.root / 'power-lines-core'
        self.core.mkdir()
        source = Path(__file__).resolve().parents[1]
        for name in ('install', 'build', 'start', 'stop', 'open', 'data-service-run'):
            shutil.copy2(source / name, self.core / name)
        self.log = self.root / 'calls'
        stub = self.root / 'stub'
        stub.write_text('#!/usr/bin/env python3\nimport json, os, sys\n'
                        'with open(os.environ["CALL_LOG"], "a") as f: '
                        'f.write(json.dumps([os.path.abspath(sys.argv[0]), os.path.basename(sys.argv[0]), *sys.argv[1:]]) + "\\n")\n')
        stub.chmod(0o755)
        tools = self.root / 'tools'
        tools.mkdir()
        for name in ('dotnet', 'docker', 'code', 'git'):
            (tools / name).symlink_to(stub)
        for name in ('power-lines-web', 'power-lines-data-service'):
            repo = self.root / name
            (repo / 'scripts').mkdir(parents=True)
            (repo / '.env.example').write_text('EXAMPLE=yes\n')
            for script in ('services-up', 'services-down', 'run-service'):
                (repo / 'scripts' / script).symlink_to(stub)
        self.env = dict(os.environ, PATH=str(tools) + os.pathsep + os.environ['PATH'], CALL_LOG=str(self.log))

    def run_script(self, name, *args, check=True):
        return subprocess.run([str(self.core / name), *args], cwd='/tmp', env=self.env,
                              capture_output=True, text=True, check=check)

    def calls(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def test_native_start_runs_repositories_sequentially_without_imports(self):
        self.run_script('start')
        self.assertEqual([row[1] for row in self.calls()], ['services-up', 'services-up'])
        self.assertEqual([Path(row[0]).parents[1].name for row in self.calls()],
                         ['power-lines-web', 'power-lines-data-service'])

    def test_docker_start_runs_web_only_after_dependencies(self):
        self.run_script('start', '--docker')
        self.assertEqual([row[1] for row in self.calls()], ['services-up', 'services-up', 'docker'])
        self.assertEqual(self.calls()[-1][2:], ['compose', '--profile', 'app', 'up', '-d', '--build', 'power-lines-web'])

    def test_import_arguments_are_forwarded_without_splitting(self):
        self.run_script('data-service-run', '--docker', '--results', 'argument with spaces')
        self.assertEqual(self.calls()[0][1:], ['run-service', '--docker', '--results', 'argument with spaces'])

    def test_build_modes_and_argument_forwarding(self):
        self.run_script('build', '--configuration', 'Release')
        self.assertTrue(all(row[1:] == ['dotnet', 'build', '--configuration', 'Release'] for row in self.calls()))
        self.log.unlink()
        self.run_script('build', '--docker', '--no-cache')
        self.assertTrue(all(row[1:] == ['docker', 'compose', '--profile', 'app', 'build', '--no-cache'] for row in self.calls()))

    def test_install_preserves_existing_environment(self):
        existing = self.root / 'power-lines-web' / '.env'
        existing.write_text('KEEP=yes\n')
        self.run_script('install')
        self.assertEqual(existing.read_text(), 'KEEP=yes\n')
        self.assertEqual((self.root / 'power-lines-data-service' / '.env').read_text(), 'EXAMPLE=yes\n')
        self.assertEqual([row[1] for row in self.calls()], ['dotnet', 'dotnet'])

    def test_stop_retains_data_and_forwards_options(self):
        self.run_script('stop', '--docker', '--timeout', '3')
        self.assertEqual([row[1] for row in self.calls()], ['docker', 'services-down', 'services-down'])
        self.assertTrue(all(row[-2:] == ['--timeout', '3'] for row in self.calls()))
        self.assertNotIn('--volumes', str(self.calls()))

    def test_open_uses_workspace_from_any_directory(self):
        self.run_script('open', '--new-window')
        self.assertEqual(self.calls()[0][1:], ['code', str(self.core / 'power-lines.code-workspace'), '--new-window'])

    def test_invalid_start_arguments_do_not_start_anything(self):
        self.assertNotEqual(self.run_script('start', '--unknown', check=False).returncode, 0)
        self.assertEqual(self.calls(), [])

    def test_workspace_references_and_dependency_order(self):
        workspace = json.loads((Path(__file__).resolve().parents[1] / 'power-lines.code-workspace').read_text())
        self.assertEqual({f['name'] for f in workspace['folders']}, {'power-lines-core', 'power-lines-web', 'power-lines-data-service'})
        tasks = {task['label']: task for task in workspace['tasks']['tasks']}
        for task in tasks.values():
            for dependency in task.get('dependsOn', []):
                self.assertIn(dependency, tasks)
        self.assertEqual(tasks['Local: Start all']['dependsOrder'], 'sequence')
        self.assertEqual(tasks['Local: Start all']['dependsOn'][0], 'Local: Dependencies')
