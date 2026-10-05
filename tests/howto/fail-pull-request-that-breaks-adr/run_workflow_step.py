"""Run one `run:` step from the workflow file under bash, as the runner would.

Lets the fixture execute the exact script the guide publishes, instead of a
copy that could drift from it.
"""
import os
import subprocess
import sys

import yaml

workflow = yaml.safe_load(open(".github/workflows/mneme-decisions.yml", encoding="utf-8"))
step = next(s for s in workflow["jobs"]["mneme"]["steps"] if s.get("name") == sys.argv[1])
env = {**os.environ, **{k: v for k, v in step.get("env", {}).items() if "${{" not in str(v)}}
env.update(dict(a.split("=", 1) for a in sys.argv[2:]))
sys.exit(subprocess.run(["bash", "-c", step["run"]], env=env).returncode)
