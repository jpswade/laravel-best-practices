#!/usr/bin/env python3
"""Synthetic Git syntax checks; --codex also exercises the installed sandbox.
No fixtures are read from the application or home directory.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / 'tests/host-controls/cases.json').read_text())
PATHS = {prefix + path: kind == 'deny' for prefix in ('', 'packages/demo/')
         for kind, paths in CASES.items() for path in paths}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='lbp-patterns-') as directory:
        root = Path(directory).resolve()
        for path in PATHS:
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text('SYNTHETIC FIXTURE ONLY\n')
        env = dict(os.environ, GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
        subprocess.run(['git', 'init', '-q', str(root)], env=env, check=True)
        templates = [ROOT / '.aiignore'] + [ROOT / 'resources/host-controls' / name
                     for name in ('cursorignore', 'aiexclude', 'geminiignore')]
        for template in templates:
            (root / '.gitignore').write_text(template.read_text())
            result = subprocess.run(['git', '-C', str(root), 'check-ignore', '--no-index', '--stdin'],
                                    input='\n'.join(PATHS)+'\n', text=True, capture_output=True, env=env)
            if result.returncode not in (0, 1):
                raise RuntimeError(result.stderr)
            actual = set(result.stdout.splitlines())
            assert actual == {p for p, deny in PATHS.items() if deny}, template
            print(f'PASS {template.name}: {len(PATHS)} Git syntax cases (not host enforcement)')
        if args.codex:
            # Pass a unique explicit profile to the native sandbox. No model/auth needed.
            import tomllib
            fragment = tomllib.loads((ROOT / 'resources/host-controls/codex-permissions.example.toml').read_text())
            rules = fragment['permissions']['project']['filesystem'][':workspace_roots']
            command = ['codex', 'sandbox', '-C', str(root), '-P', 'lbp-synthetic-check',
                       '-c', 'permissions.lbp-synthetic-check.extends=":workspace"',
                       '-c', 'permissions.lbp-synthetic-check.network.enabled=false']
            table = ', '.join(json.dumps(pattern) + '=' + json.dumps(access)
                              for pattern, access in rules.items())
            command += ['-c', 'permissions.lbp-synthetic-check.filesystem={":workspace_roots"={' + table + '}}']
            # Native command checks access, without printing even synthetic file contents.
            (root / 'probe.py').write_text('''import json, pathlib
cases = json.loads(pathlib.Path("cases.json").read_text())
for name, denied in cases.items():
    try:
        pathlib.Path(name).read_bytes()
        blocked = False
    except PermissionError:
        blocked = True
    assert blocked == denied, (name, denied, blocked)
print("PASS Codex sandbox: %d synthetic file reads" % len(cases))
''')
            (root / 'cases.json').write_text(json.dumps(PATHS))
            subprocess.run(command + ['--', '/usr/bin/python3', str(root / 'probe.py')], check=True)


if __name__ == '__main__':
    main()
