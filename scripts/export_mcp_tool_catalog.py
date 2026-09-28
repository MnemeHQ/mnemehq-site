#!/usr/bin/env python3
"""Export Mneme's released Decision MCP tools/list contract for the public site.

The artifact is generated from the installed, released mneme-hq[mcp]
runtime, not from hand-maintained website copy. scripts/core_version.json
selects the exact public release the website documents.

Usage:
    python scripts/export_mcp_tool_catalog.py
    python scripts/export_mcp_tool_catalog.py --check
    python scripts/export_mcp_tool_catalog.py --output /tmp/decision-tools.json
"""
from __future__ import annotations

import argparse
import asyncio
import importlib.metadata
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION_MANIFEST = ROOT / "scripts" / "core_version.json"
TARGET = ROOT / "site" / ".well-known" / "mcp" / "decision-tools.json"

EXAMPLE_ARGUMENTS: dict[str, dict[str, Any]] = {
    "decision.propose": {
        "candidate": {
            "title": "Keep service storage behind the repository boundary",
            "statement": "Application services must access persistence through the repository layer.",
            "rationale": "Preserve the approved storage boundary across agent-generated changes.",
            "provenance": {
                "producer_name": "example-agent",
                "producer_type": "agent",
                "source_reference": "example-session-001",
                "source_version": "1",
                "repository_locator": "src/service.py",
                "origin_classification": "ai_generated",
            },
            "scope_hints": ["service", "storage"],
            "architecture_context": {"component": "service"},
            "related_decision_ids": [],
        }
    },
    "decision.propose_batch": {
        "candidates": [
            {
                "title": "Keep API handlers thin",
                "statement": "API handlers delegate domain work to application services.",
                "rationale": "Preserve separation between transport and domain behavior.",
                "scope_hints": ["api"],
                "architecture_context": {"component": "api"},
                "related_decision_ids": [],
            },
            {
                "title": "Keep persistence behind repositories",
                "statement": "Domain services do not call database clients directly.",
                "rationale": "Preserve the repository boundary.",
                "scope_hints": ["storage"],
                "architecture_context": {"component": "domain"},
                "related_decision_ids": [],
            },
        ],
        "shared_provenance": {
            "producer_name": "example-agent",
            "producer_type": "agent",
            "source_reference": "example-session-002",
            "source_version": "1",
            "repository_locator": "src/",
            "origin_classification": "ai_generated",
        },
    },
    "decision.get": {"record_id": "ADR-001"},
    "decision.search": {
        "query": "storage",
        "canonical_lifecycle_status": "active",
    },
    "decision.applicable_to": {
        "context": ["storage", "service"],
        "paths": ["src/service.py"],
    },
    "decision.trace": {"record_id": "ADR-001"},
}


def _expected_version() -> str:
    payload = json.loads(VERSION_MANIFEST.read_text(encoding="utf-8"))
    if payload.get("package") != "mneme-hq":
        raise RuntimeError(f"unexpected package in {VERSION_MANIFEST}")
    version = payload.get("minimum_version")
    if not isinstance(version, str) or not version:
        raise RuntimeError(f"missing minimum_version in {VERSION_MANIFEST}")
    return version


def _jsonable(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json", by_alias=True, exclude_none=True)
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


async def _catalog() -> dict[str, Any]:
    expected = _expected_version()
    resolved = importlib.metadata.version("mneme-hq")
    if resolved != expected:
        raise RuntimeError(
            f"installed mneme-hq {resolved} does not match site core version {expected}; "
            "install the exact version from scripts/core_version.json"
        )

    from mcp import Client
    from mneme.decision_mcp import (
        APPROVED_TOOLS,
        SERVER_NAME,
        SERVER_VERSION,
        build_server_from_parts,
    )
    from mneme.decision_proposal_store import InMemoryDecisionProposalStore

    server = build_server_from_parts(InMemoryDecisionProposalStore())
    async with Client(server) as client:
        listed = await client.list_tools()
        by_name = {tool.name: tool for tool in listed.tools}
        if set(by_name) != set(APPROVED_TOOLS):
            raise RuntimeError(
                "Decision MCP tools/list drift: "
                f"expected {list(APPROVED_TOOLS)!r}, got {sorted(by_name)!r}"
            )

        tools: list[dict[str, Any]] = []
        for name in APPROVED_TOOLS:
            tool = by_name[name]
            example = EXAMPLE_ARGUMENTS[name]

            properties = (tool.input_schema or {}).get("properties", {})
            unknown_example_keys = sorted(set(example) - set(properties))
            if unknown_example_keys:
                raise RuntimeError(
                    f"{name} example uses unknown top-level keys: {unknown_example_keys}"
                )

            required = set((tool.input_schema or {}).get("required", []))
            missing_required = sorted(required - set(example))
            if missing_required:
                raise RuntimeError(
                    f"{name} example omits required top-level keys: {missing_required}"
                )

            example_result = await client.call_tool(name, example)
            if getattr(example_result, "is_error", False):
                raise RuntimeError(f"{name} public example is rejected by the released runtime")

            tools.append(
                {
                    "name": tool.name,
                    "title": getattr(tool, "title", None),
                    "description": tool.description or "",
                    "inputSchema": _jsonable(tool.input_schema),
                    "outputSchema": _jsonable(getattr(tool, "output_schema", None)),
                    "annotations": _jsonable(tool.annotations),
                    "exampleArguments": example,
                }
            )

    return {
        "schema": "mneme.mcp-tool-catalog/v1",
        "generatedFrom": {
            "distribution": "mneme-hq",
            "version": resolved,
            "serverName": SERVER_NAME,
            "serverVersion": SERVER_VERSION,
            "transport": "stdio",
            "protocolSource": "MCP tools/list",
        },
        "authorityBoundary": {
            "proposalToolsAreNonAuthoritative": True,
            "acceptRejectActivateSupersedeViaMcp": False,
            "enforcementViaMcp": False,
            "humanAuthoritySurface": "Mneme CLI",
        },
        "tools": tools,
    }


def render() -> str:
    return json.dumps(
        asyncio.run(_catalog()),
        indent=2,
        ensure_ascii=False,
    ) + "\n"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the published artifact differs from the released runtime")
    parser.add_argument("--output", type=Path, help="write a generated copy to this path instead of the canonical site path")
    args = parser.parse_args(argv)

    if args.check and args.output:
        parser.error("--check and --output are mutually exclusive")

    try:
        rendered = render()
    except Exception as exc:
        print(f"mcp-tool-catalog: ERROR: {exc}", file=sys.stderr)
        return 2

    if args.check:
        if not TARGET.exists():
            print(f"mcp-tool-catalog: FAIL: missing {TARGET.relative_to(ROOT)}")
            return 1
        current = TARGET.read_text(encoding="utf-8")
        if current != rendered:
            print(
                "mcp-tool-catalog: FAIL: published artifact differs from "
                f"mneme-hq=={_expected_version()} tools/list; regenerate with "
                "python scripts/export_mcp_tool_catalog.py"
            )
            return 1
        print(
            "mcp-tool-catalog: PASS: "
            f"{TARGET.relative_to(ROOT)} matches mneme-hq=={_expected_version()}"
        )
        return 0

    target = args.output if args.output is not None else TARGET
    _write(target, rendered)
    print(f"mcp-tool-catalog: wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
