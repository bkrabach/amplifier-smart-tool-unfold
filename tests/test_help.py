"""CLI help is a skill at every entry point and remains safe offline."""

import inspect
import json
import subprocess
import sys

from unfold.capability_help import CAPABILITY_HELP
from unfold.lib import Unfold
from unfold.operations import CAPABILITIES


def test_all_help_without_runtime(tmp_path):
    # A single fresh process exercises parser dispatch without a provider or store.
    code = """
import contextlib, io, sys
from unfold import cli
from unfold.capability_help import CAPABILITY_HELP, COMMAND_HELP

def forbidden(*args, **kwargs):
    raise AssertionError("Help attempted to initialize runtime")
cli.Unfold.__init__ = forbidden
for command in [[], *[[n] for n in COMMAND_HELP], *[["call", n] for n in CAPABILITY_HELP]]:
    for flag in ["--help", "-h"]:
        sys.argv = ["unfold", "--library", "/unused", *command, flag]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            try:
                cli.main()
            except SystemExit as exc:
                assert exc.code == 0, (command, flag, exc.code)
        text = output.getvalue()
        assert text.strip(), command
        if flag == "--help":
            assert '<skill_content name="unfold' in text, command
            if command:
                for section in ["## When to use", "## Arguments", "## Example", "## Result", "## Constraints and recovery"]:
                    assert section in text, (command, section)
        else:
            assert "usage:" in text and "<skill_content" not in text, command
assert not any(m.startswith("amplifier") for m in sys.modules)
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=30,
        env={"PATH": str(tmp_path), "HOME": str(tmp_path)},
    )
    assert result.returncode == 0, result.stderr
    assert not (tmp_path / ".local").exists()


def test_capability_examples_match_public_arguments():
    assert set(CAPABILITY_HELP) == set(CAPABILITIES)
    for name, (_, example, _, _) in CAPABILITY_HELP.items():
        method = getattr(Unfold, CAPABILITIES[name])
        inspect.signature(method).bind(None, **json.loads(json.dumps(example)))


def test_unknown_capability_help_is_bad_invocation():
    result = subprocess.run(
        [sys.executable, "-m", "unfold", "call", "not-a-capability", "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 2
    assert "Unknown capability" in result.stderr
