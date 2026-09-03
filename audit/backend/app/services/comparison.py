"""
Comparison engine for Mneme Audit M1 with P1.2 Architecture Protection.

Compares two immutable audit snapshots to produce a deterministic diff:
improved, regressed, unchanged, added, removed, uncomparable.

For P1.2, comparison is based on ProtectionClassification:
- Protected > Mneme-ready > Requires modelling > Guidance

Cross-version comparison (M0.1 vs P1.2) returns uncomparable with explicit reason.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from uuid import UUID


class ComparisonState(str, Enum):
    """Result of comparing a decision/control between two audits."""
    IMPROVED = "improved"
    REGRESSED = "regressed"
    UNCHANGED = "unchanged"
    ADDED = "added"
    REMOVED = "removed"
    UNCOMPARABLE = "uncomparable"


class SchemaCompatibility(str, Enum):
    """Schema compatibility between two audits."""
    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class DecisionComparison:
    """Comparison result for a single decision/control."""
    # Stable identity for the decision (not array position)
    decision_key: str
    baseline_decision: Optional[dict] = None
    current_decision: Optional[dict] = None
    state: ComparisonState = ComparisonState.UNCOMPARABLE
    details: dict = field(default_factory=dict)


@dataclass(frozen=True)
class AuditComparison:
    """Complete comparison between baseline and current audit."""
    baseline_audit_id: UUID
    current_audit_id: UUID
    baseline_commit_sha: str
    current_commit_sha: str
    baseline_mneme_version: str
    current_mneme_version: str
    baseline_schema_version: int
    current_schema_version: int
    baseline_schema: str  # e.g., "legacy/v1" or "mneme.audit/v1"
    current_schema: str
    schema_compatibility: SchemaCompatibility
    decisions: list[DecisionComparison] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)
    baseline_summary: Optional[dict] = None
    current_summary: Optional[dict] = None
    current_protection_delta: Optional[float] = None
    identified_mneme_potential_delta: Optional[float] = None

    def __post_init__(self):
        """Serialize semantics from this engine, including canonical scores."""
        counts = {state.value: 0 for state in ComparisonState}
        for d in self.decisions:
            counts[d.state.value] += 1
        object.__setattr__(self, "summary", counts)
        if self.baseline_schema == self.current_schema == "mneme.audit/v1":
            for metric, output in (
                ("current_protection", "current_protection_delta"),
                ("identified_mneme_potential", "identified_mneme_potential_delta"),
            ):
                before = (self.baseline_summary or {}).get(metric)
                after = (self.current_summary or {}).get(metric)
                if isinstance(before, (int, float)) and isinstance(after, (int, float)):
                    object.__setattr__(self, output, after - before)

    @property
    def has_uncomparable(self) -> bool:
        """Whether any decisions are uncomparable (schema mismatch)."""
        return any(d.state == ComparisonState.UNCOMPARABLE for d in self.decisions)


# P1.2 Protection Classification order (higher = more protected)
P12_PROTECTION_ORDER = {
    "Protected": 3,
    "Mneme-ready": 2,
    "Requires modelling": 1,
    "Guidance": 0,
}

# Legacy M0.1 Governability order
LEGACY_GOVERNABILITY_ORDER = {
    "guidance": 0,
    "partial": 1,
    "enforceable": 2,
}

# Schema identifiers
LEGACY_SCHEMA = "legacy/v1"
P12_SCHEMA = "mneme.audit/v1"


class ComparisonEngine:
    """
    Compares two audit results using stable decision identities.

    Comparison unit is a stable decision/control identity (decision.id),
    not array position or presentation text.

    For P1.2, compares ProtectionClassification with explicit ordering.
    Cross-version comparisons (legacy vs P1.2) return UNCOMPARABLE.
    """

    def __init__(self):
        pass

    def compare(
        self,
        baseline_result: dict,
        current_result: dict,
        baseline_audit_id: UUID,
        current_audit_id: UUID,
        baseline_commit_sha: str,
        current_commit_sha: str,
        baseline_mneme_version: str,
        current_mneme_version: str,
        baseline_schema_version: int,
        current_schema_version: int,
    ) -> AuditComparison:
        """
        Compare two audit results.

        Args:
            baseline_result: The baseline audit's result_payload
            current_result: The current audit's result_payload
            ... provenance metadata

        Returns:
            AuditComparison with per-decision diff and summary
        """
        # Determine schema identifiers
        baseline_schema = self._detect_schema(baseline_result, baseline_schema_version)
        current_schema = self._detect_schema(current_result, current_schema_version)

        # Check schema compatibility
        schema_compatibility = self._check_schema_compatibility(baseline_schema, current_schema)

        # Extract decisions by stable ID
        baseline_decisions = self._extract_decisions(baseline_result, baseline_schema)
        current_decisions = self._extract_decisions(current_result, current_schema)

        all_keys = set(baseline_decisions.keys()) | set(current_decisions.keys())

        comparisons = []

        for key in sorted(all_keys):
            base_dec = baseline_decisions.get(key)
            curr_dec = current_decisions.get(key)

            if schema_compatibility == SchemaCompatibility.INCOMPATIBLE:
                # Cross-version comparison - all decisions are uncomparable
                comparisons.append(DecisionComparison(
                    decision_key=key,
                    baseline_decision=base_dec,
                    current_decision=curr_dec,
                    state=ComparisonState.UNCOMPARABLE,
                    details={
                        "reason": f"Schema mismatch: baseline={baseline_schema}, current={current_schema}",
                        "baseline_classification": self._get_classification(base_dec, baseline_schema) if base_dec else None,
                        "current_classification": self._get_classification(curr_dec, current_schema) if curr_dec else None,
                    },
                ))
            else:
                # Same schema - normal comparison logic
                if base_dec is None:
                    # Added in current
                    comparisons.append(DecisionComparison(
                        decision_key=key,
                        current_decision=curr_dec,
                        state=ComparisonState.ADDED,
                        details={"added_at_commit": current_commit_sha, "schema": current_schema},
                    ))
                elif curr_dec is None:
                    # Removed in current
                    comparisons.append(DecisionComparison(
                        decision_key=key,
                        baseline_decision=base_dec,
                        state=ComparisonState.REMOVED,
                        details={"removed_at_commit": current_commit_sha, "schema": baseline_schema},
                    ))
                else:
                    # Both exist - compare classification
                    state = self._compare_classification(
                        base_dec, curr_dec, baseline_schema
                    )
                    comparisons.append(DecisionComparison(
                        decision_key=key,
                        baseline_decision=base_dec,
                        current_decision=curr_dec,
                        state=state,
                        details={
                            "baseline_classification": self._get_classification(base_dec, baseline_schema),
                            "current_classification": self._get_classification(curr_dec, current_schema),
                        },
                    ))

        return AuditComparison(
            baseline_audit_id=baseline_audit_id,
            current_audit_id=current_audit_id,
            baseline_commit_sha=baseline_commit_sha,
            current_commit_sha=current_commit_sha,
            baseline_mneme_version=baseline_mneme_version,
            current_mneme_version=current_mneme_version,
            baseline_schema_version=baseline_schema_version,
            current_schema_version=current_schema_version,
            baseline_schema=baseline_schema,
            current_schema=current_schema,
            schema_compatibility=schema_compatibility,
            decisions=comparisons,
            baseline_summary=baseline_result.get("summary"),
            current_summary=current_result.get("summary"),
        )

    def _detect_schema(self, result: dict, schema_version: int) -> str:
        """Detect the audit schema from result payload."""
        # P1.2 audits have explicit schema field
        if result.get("schema") == P12_SCHEMA:
            return P12_SCHEMA
        # Legacy audits have legacy fields in decisions or summary
        decisions = result.get("decisions", [])
        if decisions and "governability" in decisions[0]:
            return LEGACY_SCHEMA
        if "coverage" in result.get("summary", {}):
            return LEGACY_SCHEMA
        # Default to P1.2 for schema_version >= 1 with new format
        return P12_SCHEMA

    def _check_schema_compatibility(self, baseline_schema: str, current_schema: str) -> SchemaCompatibility:
        """Check if two schemas are compatible for comparison."""
        if baseline_schema == current_schema:
            return SchemaCompatibility.COMPATIBLE
        return SchemaCompatibility.INCOMPATIBLE

    def _extract_decisions(self, result: dict, schema: str) -> dict[str, dict]:
        """Extract decisions keyed by stable ID."""
        decisions = result.get("decisions", [])
        return {d["id"]: d for d in decisions if "id" in d}

    def _get_classification(self, decision: dict, schema: str) -> str:
        """Get the classification from a decision based on schema."""
        if schema == P12_SCHEMA:
            return decision.get("protection_classification", "Guidance")
        else:
            return decision.get("governability", "guidance")

    def _compare_classification(self, baseline_dec: dict, current_dec: dict, schema: str) -> ComparisonState:
        """Compare two decisions' classifications."""
        if schema == P12_SCHEMA:
            base_class = baseline_dec.get("protection_classification", "Guidance")
            curr_class = current_dec.get("protection_classification", "Guidance")
            order = P12_PROTECTION_ORDER
        else:
            base_class = baseline_dec.get("governability", "guidance")
            curr_class = current_dec.get("governability", "guidance")
            order = LEGACY_GOVERNABILITY_ORDER

        base_score = order.get(base_class, 0)
        curr_score = order.get(curr_class, 0)

        if curr_score > base_score:
            return ComparisonState.IMPROVED
        elif curr_score < base_score:
            return ComparisonState.REGRESSED
        else:
            return ComparisonState.UNCHANGED


# Singleton instance
comparison_engine = ComparisonEngine()
