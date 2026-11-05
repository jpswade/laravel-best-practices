#!/usr/bin/env python3
"""Exercise vendor:publish in a NEW disposable Laravel application, never a real app.
Install this package through a Composer path repository first. All target files
must be absent; the test refuses existing targets before making changes.
"""
import argparse
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FILES = {'pint': ('pint.json', ROOT / 'pint.json'),
         'phpstan': ('phpstan.neon.dist', ROOT / 'phpstan.neon.dist'),
         'aiignore': ('.aiignore', ROOT / '.aiignore')}
FILES.update({name: ('.'+name, ROOT / 'resources/host-controls' / name)
              for name in ('cursorignore', 'aiexclude', 'geminiignore')})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--disposable-app', required=True, type=Path)
    app = parser.parse_args().disposable_app.resolve()
    assert (app / 'artisan').is_file(), 'Expected a disposable Laravel application'
    assert all(not (app / target).exists() for target, _ in FILES.values()), 'Refusing existing target files'

    def publish(tag):
        subprocess.run(['php', 'artisan', 'vendor:publish', '--tag=laravel-best-practices-'+tag,
                        '--no-interaction'], cwd=app, check=True, capture_output=True)

    try:
        # Boot/discover must not publish anything automatically.
        subprocess.run(['php', 'artisan', 'package:discover', '--no-interaction'], cwd=app,
                       check=True, capture_output=True)
        assert all(not (app / target).exists() for target, _ in FILES.values())
        for tag, (target, source) in FILES.items():
            publish(tag)
            assert (app / target).read_bytes() == source.read_bytes(), tag
            assert all(not (app / other).exists() for other, _ in FILES.values() if other != target), tag
            (app / target).write_text('SYNTHETIC EXISTING PROJECT PROTECTION\n')
            publish(tag)
            assert (app / target).read_text() == 'SYNTHETIC EXISTING PROJECT PROTECTION\n', tag
            (app / target).unlink()
            print(f'PASS {tag}: exact copy, isolated tag, existing file preserved')
        publish('all')
        for tag, (target, source) in FILES.items():
            if tag in ('pint', 'phpstan', 'aiignore'):
                assert (app / target).read_bytes() == source.read_bytes(), tag
                (app / target).write_text('SYNTHETIC EXISTING PROJECT PROTECTION\n')
            else:
                assert not (app / target).exists(), tag
        publish('all')
        for tag in ('pint', 'phpstan', 'aiignore'):
            assert (app / FILES[tag][0]).read_text() == 'SYNTHETIC EXISTING PROJECT PROTECTION\n'
        assert not (app / '.claude/settings.json').exists()
        assert not (app / '.codex/config.toml').exists()
        print('PASS all: legacy three files only; existing files preserved; no permission settings published')
    finally:
        for target, _ in FILES.values():
            (app / target).unlink(missing_ok=True)


if __name__ == '__main__':
    main()
