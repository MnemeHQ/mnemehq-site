"""Tests for check_stale_mcp_claims.py: pre-0.10.0 MCP storage claims stay gone."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_stale_mcp_claims as gate  # noqa: E402


def _site(tmp_path: Path, rel: str, text: str) -> Path:
    path = tmp_path / "site" / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_flags_a_stale_claim_with_file_and_line(tmp_path):
    _site(tmp_path, "docs/mcp/index.html", "<p>ok</p>\n<p>Canonical reads are optional.</p>\n")
    hits = gate.find_hits(tmp_path)
    assert hits == ["site/docs/mcp/index.html:2: Canonical reads are optional"]


def test_matching_ignores_case(tmp_path):
    _site(tmp_path, "llms.txt", "you can RUN WITH PROPOSALS ONLY\n")
    assert len(gate.find_hits(tmp_path)) == 1


def test_scans_templates_and_skill_files(tmp_path):
    tpl = tmp_path / "templates" / "howto" / "guide.html"
    tpl.parent.mkdir(parents=True)
    tpl.write_text("leave it out to run with proposals only\n", encoding="utf-8")
    _site(tmp_path, ".well-known/agent-skills/x/SKILL.md", "a proposal-store-only server\n")
    assert len(gate.find_hits(tmp_path)) == 2


def test_clean_tree_has_no_hits(tmp_path):
    _site(tmp_path, "docs/mcp/index.html", "<p>The server reads the Decision Index.</p>\n")
    assert gate.find_hits(tmp_path) == []


def test_main_exit_codes(tmp_path):
    _site(tmp_path, "docs/index.html", "fine\n")
    assert gate.main(["--root", str(tmp_path)]) == 0
    _site(tmp_path, "docs/cli/index.html", "Known limitations in 0.9.0\n")
    assert gate.main(["--root", str(tmp_path)]) == 1
