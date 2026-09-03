"""
Lifecycle state machine for Mneme Audit M1.

Monotonic transitions: ephemeral → saved → pilot
No reverse transitions, no deletion workflow in M1.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from app.db.models import ProjectLifecycle


class LifecycleTransitionError(ValueError):
    """Raised when an invalid lifecycle transition is attempted."""
    pass


# Valid transitions (from -> allowed to states)
VALID_TRANSITIONS: dict[ProjectLifecycle, set[ProjectLifecycle]] = {
    ProjectLifecycle.EPHEMERAL: {ProjectLifecycle.SAVED},
    ProjectLifecycle.SAVED: {ProjectLifecycle.PILOT},
    ProjectLifecycle.PILOT: set(),  # Terminal in M1
}


@dataclass(frozen=True)
class TransitionResult:
    """Result of a lifecycle transition."""
    from_state: ProjectLifecycle
    to_state: ProjectLifecycle
    success: bool
    error: str | None = None


def can_transition(from_state: ProjectLifecycle, to_state: ProjectLifecycle) -> bool:
    """Check if a transition is valid."""
    return to_state in VALID_TRANSITIONS.get(from_state, set())


def transition(
    current_state: ProjectLifecycle,
    target_state: ProjectLifecycle,
) -> TransitionResult:
    """
    Attempt a lifecycle transition.

    Returns TransitionResult with success status.
    Does not mutate state - caller must apply the transition.
    """
    if current_state == target_state:
        return TransitionResult(
            from_state=current_state,
            to_state=target_state,
            success=True,
            error=None,
        )

    if not can_transition(current_state, target_state):
        return TransitionResult(
            from_state=current_state,
            to_state=target_state,
            success=False,
            error=f"Invalid lifecycle transition: {current_state.value} → {target_state.value}. "
                  f"Valid transitions from {current_state.value}: "
                  f"{[s.value for s in VALID_TRANSITIONS.get(current_state, set())]}",
        )

    return TransitionResult(
        from_state=current_state,
        to_state=target_state,
        success=True,
        error=None,
    )


def get_valid_transitions(state: ProjectLifecycle) -> list[ProjectLifecycle]:
    """Get all valid target states from the current state."""
    return list(VALID_TRANSITIONS.get(state, set()))


def is_terminal(state: ProjectLifecycle) -> bool:
    """Check if a state is terminal (no outgoing transitions)."""
    return len(VALID_TRANSITIONS.get(state, set())) == 0