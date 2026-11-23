"""Write .codex/hooks.json for Mneme's Codex CLI hook.

Run it from your repository root with the Python interpreter that has
mneme-hq installed. It fills in that interpreter's path and the hook file's path.
"""
import json
import pathlib
import sys

import mneme.integrations.codex_cli.hook as hook

command = f'"{sys.executable}" "{hook.__file__}"'


def entry(timeout, matcher=None):
    item = {"hooks": [{"type": "command", "command": command, "timeout": timeout}]}
    return [{"matcher": matcher, **item}] if matcher else [item]


config = {"hooks": {
    "SessionStart": entry(60, "startup|resume"),
    "PreToolUse": entry(30, "^apply_patch$"),
    "Stop": entry(60),
}}
out = pathlib.Path(".codex") / "hooks.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
print(f"Wrote {out}")
print(f"Hook command: {command}")
