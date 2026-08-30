"""
Loose ADR Parser — Extract architectural intent from non-Mneme ADR formats.

This parser handles common ADR formats that don't follow Mneme's canonical
ADR-*.md + YAML frontmatter convention. It extracts architectural intent
without inventing enforceable rules.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
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
    r"^adr[-_]\d+.*\.md$",          # adr-001.md, adr_001.md
]

# Files to skip (not ADR decisions)
SKIP_FILES = {
    "index.md",
    "README.md",
    "README.md",
    "template.md",
    "TEMPLATE.md",
    "template.md",
    "readme.md",
    "README.md",
}

# Heading patterns that indicate a decision
DECISION_HEADING_PATTERNS = [
    r"^##?\s*(Decision|Decision Outcome|Outcome|Chosen Option|Accepted Decision)",
    r"^##?\s*(Decision|Outcome|Chosen Option)",
]

# Context/rationale headings
RATIONALE_HEADING_PATTERNS = [
    r"^##?\s*(Context|Background|Rationale|Motivation|Reasoning)",
    r"^##?\s*(Context|Background|Rationale)",
]

# Status/Status heading patterns
STATUS_HEADING_PATTERNS = [
    r"^##?\s*(Status|State)",
]


def is_adr_candidate(file_path: Path, repo_root: Path) -> bool:
    """
    Check if a file is a potential loose ADR candidate.
    
    Returns True if:
    - File is in a recognized ADR directory
    - File matches ADR filename patterns
    - Is not a known index/template file
    """
    # Check if in a recognized ADR directory
    relative_path = file_path.relative_to(repo_root) if file_path.is_absolute() else file_path
    relative_str = str(relative_path).replace("\\", "/")
    
    in_adr_dir = any(relative_str.startswith(d.rstrip("/") + "/") for d in LOOSE_ADR_DIRS)
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
    
    # Check if this looks like an ADR (has decision-related headings)
    has_decision_heading = False
    for line in lines:
        for pattern in DECISION_HEADING_PATTERNS:
            if re.match(pattern, line.strip(), re.IGNORECASE):
                has_decision_heading = True
                break
        if has_decision_heading:
            break
    
    if not has_decision_heading:
        return None
    
    # Skip if it's a template or index file
    filename_lower = Path(relative_to=repo_root, other=file_path).name.lower() if file_path.is_absolute() else file_path.name.lower()
    if filename_lower in SKIP_FILES:
        return None
    
    # Parse the document structure
    title = ""
    decision_text = ""
    rationale = ""
    
    # Extract title from first heading
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    
    # Parse sections
    current_section = ""
    current_content = []
    
    for line in lines:
        line_stripped = line.strip()
        
        # Check for decision heading
        is_decision_heading = False
        for pattern in DECISION_HEADING_PATTERNS:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                is_decision_heading = True
                break
        
        # Check for rationale/context heading
        is_rationale_heading = False
        for pattern in RATIONALE_HEADING_PATTERNS:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                is_rationale_heading = True
                break
        
        # Check for status heading
        is_status_heading = False
        for pattern in STATUS_HEADING_PATTERNS:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                is_status_heading = True
                break
        
        if is_decision_heading and not current_section:
            # Start collecting decision text
            current_section = "decision"
            continue
        elif is_rationale_heading:
            if current_section == "decision":
                decision_text = "\n".join(current_content).strip()
            current_section = "rationale"
            current_content = []
            continue
        elif is_status_heading:
            if current_section == "rationale":
                rationale = "\n".join(current_content).strip()
            current_section = "status"
            current_content = []
            continue
        elif line.startswith("##") and current_section:
            # Another heading - end current section
            if current_section == "decision":
                decision_text = "\n".join(current_content).strip()
            elif current_section == "rationale":
                rationale = "\n".join(current_content).strip()
            current_section = ""
            current_content = []
            continue
        
        if current_section:
            current_content.append(line)
    
    # Handle remaining content
    if current_section == "decision":
        decision_text = "\n".join(current_content).strip()
    elif current_section == "rationale":
        rationale = "\n".join(current_content).strip()
    
    # Fallback: if no structured decision found but we have a decision heading,
    # use the whole document
    if not decision_text and has_decision_heading:
        decision_text = content[:2000]
    
    if not decision_text:
        return None
    
    # Get relative path and source lines
    try:
        rel_path = file_path.relative_to(repo_root)
    except Exception:
        rel_path = file_path
    
    # Determine source lines (approximate)
    source_lines = "1-" + str(min(len(lines), 100))
    
    # Generate title from filename if no title found
    title = title or file_path.stem.replace("_", " ").replace("-", " ").title()
    
    return LooseADRDecision(
        title=title,
        decision_text=decision_text[:2000],  # Limit size
        rationale=rationale[:2000],
        source_path=str(file_path.relative_to(repo_root)) if file_path.is_absolute() else str(file_path),
        source_lines="1-" + str(min(len(lines), 100)),
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