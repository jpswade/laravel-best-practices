#!/usr/bin/env python3
"""Controlled-runner example; never authorizes an agent to scan protected inputs."""
import argparse
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

PINS = {"gitleaks": "8.30.1", "betterleaks": "1.10.0"}


def scan(scanner, binary, mode, target, revision=None):
    # No inherited scanner config, validation toggles, credentials, Git config,
    # or repository-controlled executable/configuration. Provision binary first.
    with tempfile.TemporaryDirectory(prefix="secret-scan-") as private:
        env = {"PATH": "/usr/bin:/bin", "HOME": private,
               "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
        config = Path(private) / "rules.toml"
        config.write_text('[extend]\nuseDefault = true\n')
        try:
            binary = str(Path(binary).resolve(strict=True))
            version = subprocess.run([binary, "version"], env=env, cwd=private,
                                     capture_output=True, timeout=10)
            if version.returncode or version.stdout.decode().strip().removeprefix("v") != PINS[scanner]:
                print("ERROR: provision the documented pinned scanner version.")
                return 2
            target = Path(target).resolve(strict=True)
            if not target.is_dir():
                raise ValueError()
            args = [binary, "dir" if mode == "dir" else "git", str(target),
                    "--config", str(config), "--gitleaks-ignore-path", private,
                    "--ignore-gitleaks-allow", "--redact=100", "--no-banner",
                    "--exit-code=42", "--timeout=60", "--log-level=error"]
            if scanner == "betterleaks":
                args += ["--validation=false"]
            if mode == "staged":
                args += ["--pre-commit", "--staged"]
            elif mode == "history":
                args += ["--log-opts=--all"]
            elif mode == "range":
                if not revision or not re.fullmatch(r"[0-9a-f]{40}\.\.[0-9a-f]{40}", revision):
                    raise ValueError()
                args += ["--log-opts=" + revision]
            if mode != "dir":
                probe = subprocess.run(["/usr/bin/git", "-C", str(target), "rev-parse", "--git-dir"],
                                       env=env, capture_output=True, timeout=10)
                if probe.returncode:
                    raise ValueError()
            result = subprocess.run(args, env=env, cwd=private,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                    timeout=90)
            # Some scanner source errors have returned zero. At error log level,
            # any diagnostic is a failure even if the process claims success.
            if result.stderr:
                print("ERROR: scanner diagnostic; owner must inspect privately for source/configuration failures before retrying.")
                return 2
        except (OSError, ValueError, subprocess.TimeoutExpired, UnicodeError):
            print("ERROR: check binary/target provisioning, full commit SHAs and runner timeout; retry in the controlled runner.")
            return 2
        if result.returncode == 0:
            print("PASS: no findings in the requested scope; this is not proof of safety.")
            return 0
        if result.returncode == 42:
            print("BLOCKED: findings require owner triage in the controlled environment.")
            return 1
        print("ERROR: scanner failed; check repository access, fetched revisions and reviewed config in the controlled runner. Do not paste raw diagnostics.")
        return 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scanner", choices=PINS)
    parser.add_argument("binary", help="absolute path to a verified pinned binary")
    parser.add_argument("mode", choices=["dir", "staged", "range", "history"])
    parser.add_argument("target")
    parser.add_argument("--revision", help="full base SHA..full head SHA")
    args = parser.parse_args()
    sys.exit(scan(args.scanner, args.binary, args.mode, args.target, args.revision))
