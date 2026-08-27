import os
import re

integration_map = {
    "adr-import": ("ADRs", "Turn the ADRs already sitting in your docs/ into enforceable AI coding guardrails"),
    "antigravity": ("Google Antigravity", "A shipped native adapter enforces Mneme's architectural decision corpus inside Google Antigravity"),
    "claude-agent-sdk": ("Claude Agent SDK", "Govern architectural constraints in Claude Agent SDK workflows"),
    "claude-code": ("Claude Code", "Claude Code governance via PreToolUse hooks - Mneme HQ intercepts Edit and Write calls"),
    "codex-cli": ("Codex CLI", "A shipped native integration enforces Mneme's decision corpus in OpenAI Codex CLI"),
    "cursor": ("Cursor", "Cursor governance for AI-assisted teams - Mneme HQ holds the structured decision corpus"),
    "github-actions": ("GitHub Actions", "GitHub Actions AI governance - Run Mneme HQ's enforcement checks against every PR diff"),
    "gitlab": ("GitLab", "Run Mneme HQ's checks in your GitLab CI pipeline - Block merge requests that violate architectural decisions"),
    "hermes": ("Hermes Agent", "Context injection and pre-tool enforcement for supported mutations in Hermes Agent"),
    "jetbrains": ("JetBrains IDEs", "Mneme HQ's decision corpus is the constraint layer for JetBrains AI Assistant across IntelliJ, PyCharm, and WebStorm"),
    "langchain-langgraph": ("LangChain/LangGraph", "Native agent middleware injects Mneme's architectural decisions before model calls and governs supported write_file and edit_file mutations"),
    "microsoft-agent-forge": ("Microsoft Agent Forge", "Mneme adds deterministic architectural governance and verification before autonomous changes propagate downstream"),
    "opencode": ("OpenCode", "OpenCode runs an open-source coding agent with a plugin system of execution and session hooks - Mneme integration is experimental"),
    "perplexity": ("Perplexity", "Perplexity helps teams understand why - Mneme helps teams preserve what must remain true - Research-to-enforcement workflow"),
    "vscode": ("VS Code", "VS Code is the host for Claude Code and Copilot - Mneme HQ's PreToolUse hooks govern every Edit, Write, and MultiEdit in Claude Code sessions automatically"),
    "warp": ("Warp", "Warp orchestrates Agent Mode and autonomous execution in the terminal - Governance applies through underlying supported agent hooks or a CI gate on the resulting diff"),
    "copilot": ("Copilot", "GitHub Copilot generates code in VS Code and JetBrains - Mneme HQ is the architectural constraint layer above it - a structured decision corpus for AI tools"),
    "paperclip": ("Paperclip", "Paperclip drives Claude Code - Mneme's existing hook enforcement applies unchanged under both Paperclip transports (CLI and ACP) - No adapter required"),
}

base = r'C:\dev\mnemehq-site\site/integrations'

for dirname in sorted(os.listdir(base)):
    idx_path = os.path.join(base, dirname, "index.html")
    if not os.path.exists(idx_path):
        continue
    
    with open(idx_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    name, desc = integration_map.get(dirname, (dirname, ""))
    
    # Update og:title
    content = re.sub(
        r'<meta property="og:title" content="[^"]*"',
        f'<meta property="og:title" content="Mneme HQ + {name}: Architectural Governance"',
        content
    )
    
    # Update og:description
    content = re.sub(
        r'<meta property="og:description" content="[^"]*"',
        f'<meta property="og:description" content="{desc}"',
        content
    )
    
    # Update meta name="description"
    content = re.sub(
        r'<meta name="description" content="[^"]*"',
        f'<meta name="description" content="{desc}"',
        content
    )
    
    # Update twitter:title
    content = re.sub(
        r'<meta name="twitter:title" content="[^"]*"',
        f'<meta name="twitter:title" content="Mneme HQ + {name}: Architectural Governance"',
        content
    )
    
    # Update twitter:description
    content = re.sub(
        r'<meta name="twitter:description" content="[^"]*"',
        f'<meta name="twitter:description" content="{desc}"',
        content
    )
    
    with open(idx_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated: {dirname}")

print("\nDone updating all integration pages.")