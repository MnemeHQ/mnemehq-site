#!/usr/bin/env python3
"""Validate Mneme's public agent-discovery chain.

The local contract ties together the website's canonical version manifest,
AI Catalog, Agent Skill index/digest, Decision MCP skill, runtime-generated
tool catalog, llms.txt, and MCP documentation.

With --online it also verifies the external sources of package/discovery
truth: PyPI, the core repository's server.json, and the official MCP Registry.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

VERSION_MANIFEST = ROOT / "scripts" / "core_version.json"
AI_CATALOG = SITE / ".well-known" / "ai-catalog.json"
SKILLS_INDEX = SITE / ".well-known" / "agent-skills" / "index.json"
DECISION_SKILL = SITE / ".well-known" / "agent-skills" / "mneme-decision-mcp" / "SKILL.md"
TOOL_CATALOG = SITE / ".well-known" / "mcp" / "decision-tools.json"
LLMS = SITE / "llms.txt"
MCP_DOCS = SITE / "docs" / "mcp" / "index.html"
HOMEPAGE = SITE / "index.html"
HTACCESS = SITE / ".htaccess"

BASE = "https://mnemehq.com"
REGISTRY_NAME = "io.github.MnemeHQ/mneme"
REGISTRY_SEARCH_URL = (
    "https://registry.modelcontextprotocol.io/v0.1/servers?"
    "search=io.github.MnemeHQ%2Fmneme"
)
CORE_SERVER_JSON_URL = "https://raw.githubusercontent.com/MnemeHQ/mneme/main/server.json"
PYPI_URL = "https://pypi.org/pypi/mneme-hq/json"

EXPECTED_TOOLS = (
    "decision.propose",
    "decision.propose_batch",
    "decision.get",
    "decision.search",
    "decision.applicable_to",
    "decision.trace",
)

REQUIRED_AI_ENTRIES = {
    "urn:air:mnemehq.com:skills:index": (
        "application/agent-skills+json",
        "https://mnemehq.com/.well-known/agent-skills/index.json",
    ),
    "urn:air:mnemehq.com:skill:decision-mcp": (
        "application/agent-skills+md",
        "https://mnemehq.com/.well-known/agent-skills/mneme-decision-mcp/SKILL.md",
    ),
    "urn:air:mnemehq.com:integrate": (
        "text/html",
        "https://mnemehq.com/integrations/",
    ),
    "urn:air:mnemehq.com:mcp:decision-tools": (
        "application/json",
        "https://mnemehq.com/.well-known/mcp/decision-tools.json",
    ),
    "urn:air:mnemehq.com:docs:mcp": (
        "text/html",
        "https://mnemehq.com/docs/mcp/",
    ),
    "urn:air:mnemehq.com:index:llms": (
        "text/markdown",
        "https://mnemehq.com/llms.txt",
    ),
}

REQUIRED_LLMS_URLS = (
    "https://mnemehq.com/.well-known/ai-catalog.json",
    "https://mnemehq.com/integrations/",
    "https://mnemehq.com/.well-known/agent-skills/index.json",
    "https://mnemehq.com/.well-known/agent-skills/mneme-decision-mcp/SKILL.md",
    "https://mnemehq.com/.well-known/mcp/decision-tools.json",
    REGISTRY_SEARCH_URL,
    "https://github.com/MnemeHQ/mneme/blob/main/server.json",
)

# Mneme HQ ships on PyPI only. These npm packages belong to an unrelated
# project and have been misattributed to Mneme by external scanners; they must
# never appear in our discovery content.
# llms.txt is a navigation index; agent tooling recommends keeping it within
# 30,000 characters. Annotated page lists live in llms-full.txt.
LLMS_MAX_CHARS = 30_000
PYPI_PROJECT_URL = "https://pypi.org/project/mneme-hq/"
NO_NPM_STATEMENT = "Mneme HQ does not currently publish official npm packages"
STDIO_ONLY_STATEMENT = "local and stdio-only"
UNOWNED_NPM_PACKAGES = (
    "@mnemehq/sdk",
    "@mnemehq/mcp-server",
    "@mnemehq/distiller-claude",
)
DISCOVERY_CONTENT = (
    AI_CATALOG,
    SKILLS_INDEX,
    DECISION_SKILL,
    TOOL_CATALOG,
    LLMS,
    SITE / "llms-full.txt",
    MCP_DOCS,
)


class Contract:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.checks = 0

    def require(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            self.failures.append(message)

    def equal(self, actual: Any, expected: Any, label: str) -> None:
        self.require(actual == expected, f"{label}: expected {expected!r}, found {actual!r}")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def expected_version() -> str:
    manifest = load_json(VERSION_MANIFEST)
    if manifest.get("package") != "mneme-hq":
        raise ValueError(f"{VERSION_MANIFEST} package must be mneme-hq")
    version = manifest.get("minimum_version")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError(f"{VERSION_MANIFEST} minimum_version must use X.Y.Z")
    return version


def site_path_for_url(url: str) -> Path | None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.netloc != "mnemehq.com" or parsed.query or parsed.fragment:
        return None
    path = parsed.path
    if path.endswith("/"):
        return SITE / path.lstrip("/") / "index.html"
    return SITE / path.lstrip("/")


def parse_skill_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def check_server_metadata(c: Contract, payload: dict[str, Any], version: str, label: str) -> None:
    c.equal(payload.get("name"), REGISTRY_NAME, f"{label} server name")
    c.equal(payload.get("version"), version, f"{label} server version")
    c.equal(payload.get("websiteUrl"), "https://mnemehq.com/integrations/mcp/", f"{label} websiteUrl")

    packages = payload.get("packages")
    c.require(isinstance(packages, list), f"{label} packages must be a list")
    if not isinstance(packages, list):
        return
    matching = [
        item for item in packages
        if isinstance(item, dict)
        and item.get("registryType") == "pypi"
        and item.get("identifier") == "mneme-hq"
    ]
    c.equal(len(matching), 1, f"{label} must expose exactly one mneme-hq PyPI package")
    if len(matching) != 1:
        return

    package = matching[0]
    c.equal(package.get("version"), version, f"{label} package version")
    transport = package.get("transport")
    c.equal(
        transport.get("type") if isinstance(transport, dict) else None,
        "stdio",
        f"{label} transport",
    )

    runtime_args = package.get("runtimeArguments")
    c.require(isinstance(runtime_args, list), f"{label} runtimeArguments must be a list")
    if isinstance(runtime_args, list):
        from_values = [
            arg.get("value")
            for arg in runtime_args
            if isinstance(arg, dict)
            and arg.get("type") == "named"
            and arg.get("name") == "--from"
        ]
        c.equal(from_values, [f"mneme-hq[mcp]=={version}"], f"{label} --from package selector")

    package_args = package.get("packageArguments")
    c.require(isinstance(package_args, list), f"{label} packageArguments must be a list")
    if isinstance(package_args, list):
        positional = [
            arg.get("value")
            for arg in package_args
            if isinstance(arg, dict) and arg.get("type") == "positional"
        ]
        c.equal(positional, ["mneme", "decision-mcp"], f"{label} package arguments")


def check_local(c: Contract, version: str) -> None:
    ai = load_json(AI_CATALOG)
    c.equal(ai.get("specVersion"), "1.0", "AI Catalog specVersion")
    host = ai.get("host") if isinstance(ai.get("host"), dict) else {}
    c.equal(host.get("displayName"), "Mneme HQ", "AI Catalog host displayName")
    c.equal(host.get("documentationUrl"), "https://mnemehq.com/docs/", "AI Catalog documentationUrl")

    entries = ai.get("entries")
    c.require(isinstance(entries, list), "AI Catalog entries must be a list")
    if isinstance(entries, list):
        ids = [entry.get("identifier") for entry in entries if isinstance(entry, dict)]
        urls = [entry.get("url") for entry in entries if isinstance(entry, dict)]
        c.equal(len(ids), len(set(ids)), "AI Catalog identifiers must be unique")
        c.equal(len(urls), len(set(urls)), "AI Catalog URLs must be unique")
        by_id = {
            entry.get("identifier"): entry
            for entry in entries
            if isinstance(entry, dict) and isinstance(entry.get("identifier"), str)
        }
        for identifier, (expected_type, expected_url) in REQUIRED_AI_ENTRIES.items():
            entry = by_id.get(identifier)
            c.require(isinstance(entry, dict), f"AI Catalog missing {identifier}")
            if not isinstance(entry, dict):
                continue
            c.equal(entry.get("type"), expected_type, f"{identifier} type")
            c.equal(entry.get("url"), expected_url, f"{identifier} URL")
            path = site_path_for_url(expected_url)
            c.require(path is not None and path.is_file(), f"{identifier} target is not a deployed site file: {expected_url}")

    index = load_json(SKILLS_INDEX)
    c.equal(
        index.get("$schema"),
        "https://schemas.agentskills.io/discovery/0.2.0/schema.json",
        "Agent Skills schema",
    )
    skills = index.get("skills")
    c.require(isinstance(skills, list), "Agent Skills index skills must be a list")
    target_skill: dict[str, Any] | None = None
    if isinstance(skills, list):
        names = [s.get("name") for s in skills if isinstance(s, dict)]
        c.equal(len(names), len(set(names)), "Agent Skill names must be unique")
        matches = [s for s in skills if isinstance(s, dict) and s.get("name") == "mneme-decision-mcp"]
        c.equal(len(matches), 1, "Agent Skills index must contain exactly one mneme-decision-mcp skill")
        if len(matches) == 1:
            target_skill = matches[0]

    skill_bytes = DECISION_SKILL.read_bytes()
    skill_text = skill_bytes.decode("utf-8")
    skill_frontmatter = parse_skill_frontmatter(skill_text)
    c.equal(skill_frontmatter.get("name"), "mneme-decision-mcp", "Decision MCP skill frontmatter name")
    c.require(bool(skill_frontmatter.get("description")), "Decision MCP skill frontmatter description is required")

    if target_skill is not None:
        c.equal(target_skill.get("type"), "skill-md", "Decision MCP skill type")
        c.equal(
            target_skill.get("url"),
            "/.well-known/agent-skills/mneme-decision-mcp/SKILL.md",
            "Decision MCP skill URL",
        )
        digest = "sha256:" + hashlib.sha256(skill_bytes).hexdigest()
        c.equal(target_skill.get("digest"), digest, "Decision MCP skill digest")

    skill_versions = set(re.findall(r"mneme-hq\[mcp\]==(\d+\.\d+\.\d+)", skill_text))
    c.equal(skill_versions, {version}, "Decision MCP skill current package version")
    for tool in EXPECTED_TOOLS:
        c.require(f"`{tool}`" in skill_text, f"Decision MCP skill missing tool {tool}")
    c.require(REGISTRY_SEARCH_URL in skill_text, "Decision MCP skill missing official Registry URL")
    c.require(
        "https://github.com/MnemeHQ/mneme/blob/main/server.json" in skill_text,
        "Decision MCP skill missing canonical server.json URL",
    )

    tools = load_json(TOOL_CATALOG)
    c.equal(tools.get("schema"), "mneme.mcp-tool-catalog/v1", "tool catalog schema")
    generated = tools.get("generatedFrom") if isinstance(tools.get("generatedFrom"), dict) else {}
    c.equal(generated.get("distribution"), "mneme-hq", "tool catalog distribution")
    c.equal(generated.get("version"), version, "tool catalog version")
    c.equal(generated.get("transport"), "stdio", "tool catalog transport")
    c.equal(generated.get("protocolSource"), "MCP tools/list", "tool catalog protocol source")
    tool_items = tools.get("tools")
    c.require(isinstance(tool_items, list), "tool catalog tools must be a list")
    if isinstance(tool_items, list):
        names = tuple(item.get("name") for item in tool_items if isinstance(item, dict))
        c.equal(names, EXPECTED_TOOLS, "tool catalog frozen tool order")
        for item in tool_items:
            if not isinstance(item, dict):
                continue
            name = item.get("name", "<unknown>")
            c.require(bool(item.get("description")), f"{name} missing description")
            c.require(isinstance(item.get("inputSchema"), dict), f"{name} missing inputSchema")
            c.require(isinstance(item.get("outputSchema"), dict), f"{name} missing outputSchema")
            c.require(isinstance(item.get("annotations"), dict), f"{name} missing annotations")
            c.require(isinstance(item.get("exampleArguments"), dict), f"{name} missing exampleArguments")

    authority = tools.get("authorityBoundary") if isinstance(tools.get("authorityBoundary"), dict) else {}
    c.equal(authority.get("proposalToolsAreNonAuthoritative"), True, "tool catalog proposal authority")
    c.equal(authority.get("acceptRejectActivateSupersedeViaMcp"), False, "tool catalog authority mutations")
    c.equal(authority.get("enforcementViaMcp"), False, "tool catalog enforcement authority")
    c.equal(authority.get("humanAuthoritySurface"), "Mneme CLI", "tool catalog human authority surface")

    llms_text = LLMS.read_text(encoding="utf-8")
    for url in REQUIRED_LLMS_URLS:
        c.require(url in llms_text, f"llms.txt missing discovery URL: {url}")

    c.require(
        len(llms_text) <= LLMS_MAX_CHARS,
        f"llms.txt is {len(llms_text)} characters; keep the navigation index within {LLMS_MAX_CHARS} "
        "(annotated page lists belong in llms-full.txt)",
    )
    c.require(f"{BASE}/llms-full.txt" in llms_text, "llms.txt must link the annotated index in llms-full.txt")
    c.require(PYPI_PROJECT_URL in llms_text, "llms.txt missing official PyPI project URL")
    c.require("pip install mneme-hq" in llms_text, "llms.txt missing official install command")
    c.require(NO_NPM_STATEMENT in llms_text, "llms.txt missing no-official-npm-packages statement")
    c.require(f"`{REGISTRY_NAME}`" in llms_text, "llms.txt missing official MCP Registry identity")
    c.require(STDIO_ONLY_STATEMENT in llms_text, "llms.txt missing local stdio-only MCP statement")

    integrate = by_id.get("urn:air:mnemehq.com:integrate") if isinstance(entries, list) else None
    integrate_description = integrate.get("description", "") if isinstance(integrate, dict) else ""
    c.require("mneme-hq on PyPI" in integrate_description, "AI Catalog integrate entry missing official PyPI identity")
    c.require(NO_NPM_STATEMENT in integrate_description, "AI Catalog integrate entry missing no-official-npm-packages statement")

    for path in DISCOVERY_CONTENT:
        content = path.read_text(encoding="utf-8").lower()
        for package in UNOWNED_NPM_PACKAGES:
            c.require(
                package not in content,
                f"{path.relative_to(ROOT).as_posix()} names unowned npm package {package}",
            )

    docs_text = MCP_DOCS.read_text(encoding="utf-8")
    c.require(
        "/.well-known/mcp/decision-tools.json" in docs_text,
        "MCP docs missing machine-readable tool catalog link",
    )
    docs_versions = set(re.findall(r"mneme-hq\[mcp\]==(\d+\.\d+\.\d+)", docs_text))
    c.equal(docs_versions, {version}, "MCP docs current package version")

    for label, html in (
        ("homepage", HOMEPAGE.read_text(encoding="utf-8")),
        ("MCP docs", docs_text),
    ):
        c.require(
            'rel="ai-catalog"' in html and 'href="/.well-known/ai-catalog.json"' in html,
            f"{label} must advertise the AI Catalog",
        )

    htaccess_text = HTACCESS.read_text(encoding="utf-8")
    c.require(
        r"RewriteRule ^\.well-known/ard\.json$ /.well-known/ai-catalog.json [L]" in htaccess_text,
        ".htaccess must serve the AI Catalog at the canonical ARD path /.well-known/ard.json",
    )
    c.require("decision-tools\\.json" in htaccess_text, ".htaccess discovery cache/CORS matcher must include decision-tools.json")


def fetch_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "mnemehq-agent-discovery-ci/1.0",
        },
    )
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except (OSError, ValueError, urllib.error.HTTPError) as exc:
            last_error = exc
            if attempt < 3:
                time.sleep(float(attempt))
    assert last_error is not None
    raise RuntimeError(f"failed to fetch {url}: {last_error}") from last_error


def check_online(c: Contract, version: str) -> None:
    pypi = fetch_json(PYPI_URL)
    info = pypi.get("info") if isinstance(pypi.get("info"), dict) else {}
    c.equal(info.get("name"), "mneme-hq", "PyPI package name")
    c.equal(info.get("version"), version, "PyPI latest version vs site current stable")

    core_server = fetch_json(CORE_SERVER_JSON_URL)
    check_server_metadata(c, core_server, version, "core server.json")

    encoded_name = urllib.parse.quote(REGISTRY_NAME, safe="")
    registry_url = (
        "https://registry.modelcontextprotocol.io/v0.1/servers/"
        f"{encoded_name}/versions/latest"
    )
    registry_payload = fetch_json(registry_url)
    registry_server = registry_payload.get("server")
    if not isinstance(registry_server, dict):
        registry_server = registry_payload
    check_server_metadata(c, registry_server, version, "official MCP Registry")

    metadata = registry_payload.get("_meta")
    c.require(isinstance(metadata, dict), "official MCP Registry response missing _meta")
    if isinstance(metadata, dict):
        official = metadata.get("io.modelcontextprotocol.registry/official")
        c.require(isinstance(official, dict), "official MCP Registry response missing official metadata")
        if isinstance(official, dict):
            c.equal(official.get("status"), "active", "official MCP Registry status")
            if "isLatest" in official:
                c.equal(official.get("isLatest"), True, "official MCP Registry latest flag")

    # The Registry and source metadata must agree on the installation contract.
    for field in ("name", "version", "websiteUrl", "packages"):
        c.equal(registry_server.get(field), core_server.get(field), f"Registry/core agreement for {field}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--online",
        action="store_true",
        help="also verify PyPI, core server.json, and the official MCP Registry",
    )
    args = parser.parse_args(argv)

    try:
        version = expected_version()
        contract = Contract()
        check_local(contract, version)
        if args.online:
            check_online(contract, version)
    except Exception as exc:
        print(f"agent-discovery: ERROR: {exc}", file=sys.stderr)
        return 2

    if contract.failures:
        print(f"agent-discovery: FAIL ({len(contract.failures)} failure(s), {contract.checks} checks)")
        for failure in contract.failures:
            print(f"  - {failure}")
        return 1

    mode = "local + online" if args.online else "local"
    print(
        f"agent-discovery: PASS ({contract.checks} checks, {mode}, "
        f"mneme-hq {version})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
