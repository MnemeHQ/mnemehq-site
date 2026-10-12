---
name: mneme-decision-mcp
description: Install and configure Mneme's local Decision MCP server when an agent or developer needs to query architectural decisions, find applicable decision context, trace decision lineage, or submit non-authoritative decision proposals without giving the MCP client authority to accept or enforce them.
---

# Mneme Decision MCP

Use this skill when a repository has or wants Mneme decision state exposed to an MCP-capable coding agent.

## Authority boundary

Mneme's released Decision MCP is local and stdio-only. It does not expose a hosted HTTP or SSE endpoint. The MCP surface can read decision state and submit proposals, but it cannot accept, reject, activate, supersede, bypass, or enforce decisions. Human authority remains outside MCP.

## Install and start

Prefer the official MCP Registry metadata as the source of package and version truth:

- Registry API: https://registry.modelcontextprotocol.io/v0.1/servers?search=io.github.MnemeHQ%2Fmneme
- Canonical server metadata: https://github.com/MnemeHQ/mneme/blob/main/server.json

The server reads canonical decisions from the Decision Index in project memory (`--memory`, default `.mneme/project_memory.json`). It exits with code 2 if that file is missing or has no `decision_index` section. Memory created by `mneme init` or `mneme setup` on 0.10.0 is ready. Memory written by 0.9.x must be migrated first: run the preview, show it to the user, and apply only with their approval:

```bash
uvx --from "mneme-hq[mcp]==0.10.0" mneme decision-index migrate --memory .mneme/project_memory.json
uvx --from "mneme-hq[mcp]==0.10.0" mneme decision-index migrate --memory .mneme/project_memory.json --apply
```

Before applying, every process that writes the memory file (CI jobs, hooks, other installs) must run 0.10.0. A 0.9.2 or earlier writer on migrated memory succeeds silently and leaves a file 0.10.0 refuses to read.

For the current stable release, from the repository root:

```bash
uvx --from "mneme-hq[mcp]==0.10.0" mneme decision-mcp \
  --memory .mneme/project_memory.json \
  --proposals .mneme/decision_proposals.json
```

If `uvx` is unavailable:

```bash
pipx install "mneme-hq[mcp]==0.10.0"
mneme decision-mcp --memory .mneme/project_memory.json --proposals .mneme/decision_proposals.json
```

## MCP host configuration

For a host that launches local stdio servers, use the equivalent process contract:

```json
{
  "mcpServers": {
    "mneme": {
      "command": "uvx",
      "args": [
        "--from", "mneme-hq[mcp]==0.10.0",
        "mneme", "decision-mcp",
        "--memory", ".mneme/project_memory.json",
        "--proposals", ".mneme/decision_proposals.json"
      ]
    }
  }
}
```

`--adr-dir docs/adr` is optional: it validates that ADR corpus at startup and fails closed if it is invalid or ambiguous, but it never changes what the server reads. To bring ADR edits into the Decision Index, run `mneme adr import docs/adr --memory .mneme/project_memory.json --apply --update-existing`; a running server sees the change on its next read.

## Tool surface

The released surface contains exactly six tools:

- `decision.propose`
- `decision.propose_batch`
- `decision.get`
- `decision.search`
- `decision.applicable_to`
- `decision.trace`

Use the read tools to retrieve or trace decision state. Use proposal tools only to create non-authoritative candidates. Do not infer enforcement or acceptance authority from an MCP response.

## Canonical references

- MCP operator reference: https://mnemehq.com/docs/mcp/
- MCP integration guide: https://mnemehq.com/integrations/mcp/
- Mneme source: https://github.com/MnemeHQ/mneme
