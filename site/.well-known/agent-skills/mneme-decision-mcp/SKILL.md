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

For the current stable release:

```bash
uvx --from "mneme-hq[mcp]==0.9.2" mneme decision-mcp
```

To expose a canonical ADR corpus and durable proposal store from the repository root:

```bash
uvx --from "mneme-hq[mcp]==0.9.2" mneme decision-mcp \
  --adr-dir docs/adr \
  --proposals .mneme/decision_proposals.json
```

If `uvx` is unavailable:

```bash
pipx install "mneme-hq[mcp]==0.9.2"
mneme decision-mcp --adr-dir docs/adr --proposals .mneme/decision_proposals.json
```

## MCP host configuration

For a host that launches local stdio servers, use the equivalent process contract:

```json
{
  "mcpServers": {
    "mneme": {
      "command": "uvx",
      "args": [
        "--from", "mneme-hq[mcp]==0.9.2",
        "mneme", "decision-mcp",
        "--adr-dir", "docs/adr",
        "--proposals", ".mneme/decision_proposals.json"
      ]
    }
  }
}
```

Only include `--adr-dir` when it points to a schema-valid Mneme ADR corpus. Invalid or ambiguous canonical ADR state fails closed at startup.

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
