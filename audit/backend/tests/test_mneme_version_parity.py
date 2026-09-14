"""Engine dependency parity guard (P0: prod ran 0.6.0 vs the supported 0.7.0).

The server's Docker image installs the Mneme engine from the dynamic floor
in audit/backend/requirements.txt. Production must never silently run an
engine older than the released semantics the site depends on, and the
exact resolved version must be observable everywhere.

This test pins:
- the declared dependency is a dynamic floor (`mneme-hq>=X.Y.Z`), never a
  manually maintained exact pin (the `==` failure mode itself);
- the floor is not below the version whose public semantics the backend
  now requires (0.8.0: ADR-026 tier semantics + ADR-028 public
  assess_decision_intent);
- the RESOLVED runtime version (importlib.metadata) satisfies the floor
  and agrees with the package's own `__version__`.

The published-release drift check (floor satisfiable, resolved version
recorded) runs as a separate CI step
(scripts/check_mneme_version_parity.py) because it needs network access
to PyPI and a fully installed backend environment.
"""
import re
from importlib.metadata import version as installed_version
from pathlib import Path

import mneme

REQUIREMENTS = Path(__file__).parents[1] / "requirements.txt"

# Minimum engine semantics the backend requires: ADR-026 tier semantics and
# the ADR-028 public decision-intent API. Raise deliberately, never below.
MIN_MNEME_HQ_FLOOR = (0, 8, 0)


def mneme_hq_requirement() -> str:
    text = REQUIREMENTS.read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("mneme-hq"):
            return stripped
    raise AssertionError("requirements.txt has no mneme-hq requirement")


def parse_version(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", value))


def test_engine_dependency_is_a_dynamic_floor_not_an_exact_pin():
    requirement = mneme_hq_requirement()
    assert re.fullmatch(r"mneme-hq>=\d+(?:\.\d+)*", requirement), (
        f"mneme-hq must be declared as a dynamic floor (mneme-hq>=X.Y.Z) "
        f"so a new engine release cannot be missed; found {requirement!r}. "
        f"An exact '==' pin is how production silently stayed on 0.6.0."
    )


def test_engine_floor_is_not_below_the_required_semantics():
    requirement = mneme_hq_requirement()
    floor = parse_version(requirement.split(">=", 1)[1])
    assert floor >= MIN_MNEME_HQ_FLOOR, (
        f"backend floor {requirement} is below the released semantics the "
        f"backend depends on (mneme-hq>={'.'.join(map(str, MIN_MNEME_HQ_FLOOR))})"
    )


def test_resolved_engine_version_satisfies_the_floor():
    floor = parse_version(mneme_hq_requirement().split(">=", 1)[1])
    resolved = installed_version("mneme-hq")
    assert parse_version(resolved) >= floor, (
        f"resolved mneme-hq {resolved} is below the declared floor "
        f"{'.'.join(map(str, floor))}"
    )


def test_resolved_engine_version_is_observable_and_consistent():
    """The runtime reports one version everywhere: distribution metadata,
    package __version__, and (via the Audit response) mneme_version."""
    resolved = installed_version("mneme-hq")
    assert resolved == mneme.__version__, (
        f"distribution metadata ({resolved}) disagrees with mneme.__version__ "
        f"({mneme.__version__}); an editable/local-checkout shadow may be in "
        f"the import path"
    )
    from mneme.enforcer import assess_decision_intent

    assert assess_decision_intent("The system must reject invalid input.").intent == "prescriptive"
