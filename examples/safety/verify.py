#!/usr/bin/env python3
"""Native, synthetic-only benchmark. No repository or user inputs are scanned."""
import argparse
import base64
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import zipfile
from scan import scan

# Fabricated, never issued by a provider. Generated here so normal repository
# scans do not need broad exceptions for deliberately token-shaped fixtures.
TOKEN = "ghp_" + "aB3dE5fG7hI9jK1mN3pQ5rS7tU9vW1xY3zA5"
APP_KEY = base64.b64encode(bytes(range(32))).decode()
CASES = {
    "env-token": (".env", "GITHUB_TOKEN=" + TOKEN, True),
    "cached-config": ("bootstrap/cache/config.php", "<?php return ['token' => '" + TOKEN + "'];", True),
    "log-token": ("storage/logs/laravel.log", "Authorization: " + TOKEN, True),
    "app-key": (".env", "APP_KEY=base64:" + APP_KEY, True),
    "db-password": (".env", "DB_PASSWORD=short-pass", True),
    "placeholder": (".env.example", "GITHUB_TOKEN=<configured-locally>", False),
    "natural-language": ("config/demo.php", "<?php $password = 'this is a friendly demonstration sentence';", False),
    "dummy-token": ("tests/Fixtures/provider.txt", TOKEN, False),
    "pii-only": ("storage/logs/laravel.log", "Customer: Ada Example, ada@example.test, CUST-000042", False),
}


def run(binary, scanner, root, mode="dir", revision=None):
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        status = scan(scanner, binary, mode, root, revision)
    assert TOKEN not in output.getvalue() and APP_KEY not in output.getvalue()
    return status


def verify(scanner, binary):
    with tempfile.TemporaryDirectory(prefix="synthetic-only-") as temp:
        root = Path(temp)
        for label, (name, content, expected) in CASES.items():
            target = root / label
            path = target / name
            path.parent.mkdir(parents=True)
            path.write_text(content + "\n")
            status = run(binary, scanner, target)
            detected = label in {"env-token", "cached-config", "log-token", "dummy-token"}
            if scanner == "betterleaks" and label in {"db-password", "natural-language"}:
                detected = True
            assert status == int(detected), "pinned synthetic coverage changed; review the decision record"
            print(f"{scanner}: {label}: {'detected' if status else 'not detected'}; expected-secret={expected}")
        archived = root / "archive"
        archived.mkdir()
        with zipfile.ZipFile(archived / "export.zip", "w") as archive:
            archive.writestr(".env", "GITHUB_TOKEN=" + TOKEN)
        archive_status = run(binary, scanner, archived)
        assert archive_status == int(scanner == "betterleaks")
        print(f"{scanner}: archive: {'detected' if archive_status else 'not detected'}")
        # Inspect native redacted JSON only for data generated above. Never
        # publish scanner reports, excerpts, paths, or exception messages.
        report = root / "report.json"
        config = root / "rules.toml"
        config.write_text('[extend]\nuseDefault = true\n')
        env = {"PATH": "/usr/bin:/bin", "HOME": temp, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
        result = subprocess.run([binary, "dir", str(root / "env-token"), "--config", str(config),
                                 "--redact=100", "--report-format=json", "--report-path", str(report)],
                                cwd=temp, env=env, capture_output=True, timeout=90)
        assert result.returncode == 1
        data = report.read_bytes()
        assert json.loads(data) and TOKEN.encode() not in data + result.stdout + result.stderr
        # Malformed configuration must be a native scanner error, not clean.
        config.write_text("[[broken")
        invalid = subprocess.run([binary, "dir", str(root / "placeholder"), "--config", str(config)],
                                 cwd=temp, env=env, capture_output=True, timeout=90)
        assert invalid.returncode != 0
        assert run(binary, scanner, root / "absent") == 2
        assert run(binary, scanner, root / "placeholder", "history") == 2
        assert run(str(root / "missing-binary"), scanner, root) == 2
        other_scanner = "betterleaks" if scanner == "gitleaks" else "gitleaks"
        assert run(binary, other_scanner, root) == 2
        # Real Git index and commits: staged secret, removal, range vs history.
        repo = root / "repo"
        repo.mkdir()
        def git(*args):
            r = subprocess.run(["/usr/bin/git", "-C", str(repo), *args], env=env,
                               capture_output=True, timeout=20)
            assert r.returncode == 0, "synthetic Git setup failed"
            return r.stdout.decode().strip()
        git("init", "-q")
        git("config", "user.name", "Synthetic Test")
        git("config", "user.email", "test@example.test")
        (repo / "README").write_text("Synthetic only\n")
        git("add", ".")
        git("commit", "-qm", "clean")
        clean = git("rev-parse", "HEAD")
        (repo / "fixture.txt").write_text(TOKEN + "\n")
        assert run(binary, scanner, repo, "staged") == 0
        git("add", ".")
        assert run(binary, scanner, repo, "staged") == 1
        git("commit", "-qm", "synthetic finding")
        secret = git("rev-parse", "HEAD")
        assert run(binary, scanner, repo, "range", clean + ".." + secret) == 1
        git("rm", "-q", "fixture.txt")
        git("commit", "-qm", "remove fixture")
        removed = git("rev-parse", "HEAD")
        assert run(binary, scanner, repo, "staged") == 0
        assert run(binary, scanner, repo, "dir") == 0
        assert run(binary, scanner, repo, "range", secret + ".." + removed) == 0
        assert run(binary, scanner, repo, "history") == 1
        assert run(binary, scanner, repo, "range", "0" * 40 + ".." + removed) == 2
        assert run(binary, scanner, repo, "range", "invalid") == 2
        print(f"{scanner}: redaction, staged/range/history and error assertions passed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gitleaks")
    parser.add_argument("betterleaks")
    args = parser.parse_args()
    verify("gitleaks", str(Path(args.gitleaks).resolve()))
    verify("betterleaks", str(Path(args.betterleaks).resolve()))
