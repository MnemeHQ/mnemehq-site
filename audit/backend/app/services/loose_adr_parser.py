"""
Loose ADR Parser — Extract architectural intent from non-Mneme ADR formats.

This parser handles common ADR formats that don't follow Mneme's canonical
ADR-*.md + YAML frontmatter convention. It extracts architectural intent
without inventing enforceable rules.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class LooseADRDecision:
    """A candidate architectural decision extracted from a loose ADR format."""
    title: str
    decision_text: str
    rationale: str = ""
    source_path: str = ""
    source_lines: str = ""
    confidence: float = 0.5  # Conservative confidence for extracted intent


# Directories where loose ADRs might be found
LOOSE_ADR_DIRS = [
    "docs/adr/",
    "adr/",
    ".adr/",
    "docs/decisions/",
    "docs/architecture/decisions/",
    "docs/architecture/adr/",
    "architecture/decisions/",
    "decisions/",
]

# File patterns that might be ADRs (but not index/template files)
ADR_FILE_PATTERNS = [
    r"^\d{4}[-_].*\.md$",           # 0001-something.md, 0001_something.md
    r"^adr[-_]\d+.*\.md$",          # adr-001.md, adr_001.md
    r"^ADR[-_]\d+.*\.md$",          # ADR-001.md, ADR_001.md
]

# Files to skip (not ADR decisions)
SKIP_FILES = {
    "index.md",
    "readme.md",
    "template.md",
}

# Supported decision headings — EXACT match (case-insensitive), not prefix
VALID_DECISION_HEADINGS = {
    "decision",
    "decision outcome",
    "outcome",
    "chosen option",
    "accepted decision",
}

# Context/rationale headings
VALID_RATIONALE_HEADINGS = {
    "context",
    "background",
    "rationale",
    "motivation",
    "reasoning",
}

# Status headings
VALID_STATUS_HEADINGS = {
    "status",
    "state",
}

# Headings that terminate a decision section but are NOT decision headings
TERMINATING_HEADINGS = VALID_RATIONALE_HEADINGS | VALID_STATUS_HEADINGS


def _normalize_heading(line: str) -> str:
    """Extract and normalize heading text from a markdown heading line."""
    stripped = line.strip()
    match = re.match(r"^#+\s*(.+)$", stripped)
    if not match:
        return ""
    return match.group(1).strip().lower()


def is_adr_candidate(file_path: Path, repo_root: Path) -> bool:
    """
    Check if a file is a potential loose ADR candidate.
    
    Returns True if:
    - File is in a recognized ADR directory
    - File matches ADR filename patterns
    - Is not a known index/template file
    """
    # Check if in a recognized ADR directory
    try:
        relative_path = file_path.relative_to(repo_root)
    except ValueError:
        return False
    relative_str = str(relative_path).replace("\\", "/")
    
    # Normalize LOOSE_ADR_DIRS for cross-platform comparison
    normalized_dirs = [d.replace("/", "/").rstrip("/") + "/" for d in LOOSE_ADR_DIRS]
    in_adr_dir = any(relative_str.startswith(d) for d in normalized_dirs)
    if not in_adr_dir:
        return False
    
    # Check filename patterns
    filename = file_path.name.lower()
    if filename in SKIP_FILES:
        return False
    
    # Check if filename matches ADR patterns
    for pattern in ADR_FILE_PATTERNS:
        if re.match(pattern, file_path.name, re.IGNORECASE):
            # Skip if this is a canonical Mneme ADR (already handled by Mneme import)
            if _has_mneme_frontmatter(file_path):
                return False
            return True
    
    return False


def _has_mneme_frontmatter(file_path: Path) -> bool:
    """
    Check if a file has Mneme-style YAML frontmatter (canonical ADR format).
    
    Canonical Mneme ADRs have YAML frontmatter with at least 'id' and 'status' fields.
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    
    # Check for YAML frontmatter (starts with ---)
    if not content.startswith("---"):
        return False
    
    # Find the end of frontmatter
    end_idx = content.find("---", 3)
    if end_idx == -1:
        return False
    
    frontmatter = content[3:end_idx]
    # Check for required Mneme ADR fields
    has_id = re.search(r"^\s*id\s*:", frontmatter, re.MULTILINE | re.IGNORECASE)
    has_status = re.search(r"^\s*status\s*:", frontmatter, re.MULTILINE | re.IGNORECASE)
    
    return bool(has_id and has_status)


def extract_loose_adr(file_path: Path, repo_root: Path) -> Optional[LooseADRDecision]:
    """
    Extract a loose ADR decision from a Markdown file.
    
    Returns a LooseADRDecision if the file contains recognizable
    architectural decision content, None otherwise.
    """
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    
    if not content.strip():
        return None
    
    # Skip binary files
    if "\x00" in content[:1024]:
        return None
    
    lines = content.split("\n")
    if not lines:
        return None
    
    # Check if this looks like an ADR (has at least one valid decision heading)
    has_valid_decision_heading = False
    for line in lines:
        heading = _normalize_heading(line)
        if heading in VALID_DECISION_HEADINGS:
            has_valid_decision_heading = True
            break
    
    if not has_valid_decision_heading:
        return None
    
    # Skip if it's a template or index file
    filename_lower = file_path.name.lower()
    if filename_lower in SKIP_FILES:
        return None
    
    # Parse the document structure
    title = ""
    decision_text = ""
    rationale = ""
    
    # Extract title from first heading that doesn't look like a filename
    for line in lines:
        if line.startswith("# "):
            candidate = line[2:].strip()
            # Skip headings that look like filenames (end with .md, contain dashes/underscores like a slug)
            if not (candidate.endswith(".md") or 
                    (candidate.lower().replace(" ", "-") == file_path.stem.lower())):
                title = candidate
                break
    # Fallback: if all # headings look like filenames, use the first one anyway
    if not title:
        for line in lines:
            if line.startswith("# "):
                title = line[2:].strip()
                break
    
    # Parse sections - track line numbers for provenance
    current_section = ""  # "decision", "rationale", "status", or ""
    current_content = []
    decision_start_line = 0
    decision_end_line = 0
    
    for i, line in enumerate(lines, start=1):
        line_stripped = line.strip()
        heading = _normalize_heading(line)
        
        is_valid_decision_heading = heading in VALID_DECISION_HEADINGS
        is_valid_rationale_heading = heading in VALID_RATIONALE_HEADINGS
        is_valid_status_heading = heading in VALID_STATUS_HEADINGS
        is_any_heading = line.startswith("#")
        
        if is_valid_decision_heading:
            # New valid decision heading found - finalize any previous section
            if current_section == "rationale":
                rationale = "\n".join(current_content).strip()
            elif current_section == "decision":
                decision_text = "\n".join(current_content).strip()
                decision_end_line = i - 1
            elif current_section == "status":
                pass  # status section, just finalize
            
            # Start NEW decision section - reset BOTH start and end
            current_section = "decision"
            current_content = []
            decision_start_line = i + 1  # Body starts after heading
            decision_end_line = 0  # Reset end line for new section
            continue
        
        elif is_valid_rationale_heading:
            if current_section == "decision":
                decision_text = "\n".join(current_content).strip()
                decision_end_line = i - 1
            elif current_section == "rationale":
                rationale = "\n".join(current_content).strip()
            current_section = "rationale"
            current_content = []
            continue
        
        elif is_valid_status_heading:
            if current_section == "rationale":
                rationale = "\n".join(current_content).strip()
            elif current_section == "decision":
                decision_text = "\n".join(current_content).strip()
                decision_end_line = i - 1
            current_section = "status"
            current_content = []
            continue
        
        elif is_any_heading and current_section:
            # Another heading terminates current section
            if current_section == "decision":
                decision_text = "\n".join(current_content).strip()
                decision_end_line = i - 1
            elif current_section == "rationale":
                rationale = "\n".join(current_content).strip()
            elif current_section == "status":
                pass
            current_section = ""
            current_content = []
            continue
        
        if current_section:
            if current_section == "decision" and decision_start_line == 0:
                decision_start_line = i
            current_content.append(line)
    
    # Handle remaining content at EOF
    if current_section == "decision":
        decision_text = "\n".join(current_content).strip()
        if not decision_end_line:
            decision_end_line = len(lines)
    elif current_section == "rationale":
        rationale = "\n".join(current_content).strip()
    
    if not decision_text:
        return None
    
    # Get relative path
    try:
        rel_path = file_path.relative_to(repo_root)
    except Exception:
        rel_path = file_path
    
    # Determine source lines for the decision section
    # Only use exact range if both start and end are established and valid
    if decision_start_line and decision_end_line and decision_end_line >= decision_start_line:
        source_lines = f"{decision_start_line}-{decision_end_line}"
    else:
        # Cannot establish exact range - return unknown rather than fabricated precision
        source_lines = "unknown"
    
    # Generate title from filename if no title found
    title = title or file_path.stem.replace("_", " ").replace("-", " ").title()
    
    return LooseADRDecision(
        title=title,
        decision_text=decision_text[:2000],  # Limit size
        rationale=rationale[:2000],
        source_path=str(rel_path),
        source_lines=source_lines,
        confidence=0.5,
    )


def find_loose_adrs(repo_path: Path) -> list[LooseADRDecision]:
    """
    Find all loose ADRs in a repository.
    
    Returns a list of LooseADRDecision objects for files that appear
    to be ADRs but don't follow Mneme's canonical format.
    """
    loose_adrs = []
    
    repo_path = Path(repo_path).resolve()
    
    for adr_dir in LOOSE_ADR_DIRS:
        adr_path = repo_path / adr_dir
        if not adr_path.exists() or not adr_path.is_dir():
            continue
        
        for file_path in adr_path.rglob("*.md"):
            if not file_path.is_file():
                continue
            
            # Check if this is a candidate
            if not is_adr_candidate(file_path, repo_path):
                continue
            
            adr = extract_loose_adr(file_path, repo_path)
            if adr:
                loose_adrs.append(adr)
    
    return loose_adrs