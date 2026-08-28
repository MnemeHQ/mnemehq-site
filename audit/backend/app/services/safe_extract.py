"""
Safe extraction utilities for hostile repository input.

All repo ingestion (git clone, ZIP extract) goes through these functions.
They enforce size limits, path validation, binary detection, and cleanup.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Optional
from git import Repo, GitCommandError

# Hard limits for repository ingestion
MAX_REPO_SIZE_BYTES = 50 * 1024 * 1024      # 50 MB total
MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024       # 2 MB per file
MAX_FILE_COUNT = 5000                       # max files to process
MAX_ZIP_RATIO = 100                         # max uncompressed/compressed ratio (zip bomb)
CLONE_TIMEOUT_SECONDS = 30                  # git clone timeout
READ_CHUNK_SIZE = 8192                      # bounded reads

# Unix file type constants for symlink detection in ZIP external_attr
# external_attr is (mode << 16) | attrs, where mode is standard stat mode
S_IFMT = 0o170000
S_IFLNK = 0o120000


class SafeExtractionError(Exception):
    """Raised when repository extraction fails safety checks."""
    pass


def _is_binary(content: bytes) -> bool:
    """Heuristic: file is binary if it contains null bytes or high non-ASCII ratio."""
    if b"\x00" in content[:READ_CHUNK_SIZE]:
        return True
    sample = content[:READ_CHUNK_SIZE]
    if not sample:
        return False
    non_ascii = sum(1 for b in sample if b > 127)
    return (non_ascii / len(sample)) > 0.3


def _is_absolute_path(filename: str) -> bool:
    """Check if a ZIP member filename is an absolute path."""
    # POSIX absolute paths start with /
    # Windows absolute paths start with drive letter + : or \\
    if filename.startswith("/"):
        return True
    if len(filename) >= 2 and filename[1] == ":":
        return True
    if filename.startswith("\\\\"):
        return True
    return False


def _is_symlink(member: zipfile.ZipInfo) -> bool:
    """Check if a ZIP member is a symlink via external_attr (Unix mode bits)."""
    # external_attr upper 16 bits contain the Unix mode
    mode = (member.external_attr >> 16) & 0xFFFF
    return (mode & S_IFMT) == S_IFLNK


def _validate_zip_member(member: zipfile.ZipInfo, base_path: Path) -> Path:
    """
    Validate a ZIP member path and return the resolved safe destination.
    
    Prevents:
    - Absolute paths
    - Path traversal (..)
    - Symlink escapes
    """
    # Check for absolute paths
    if _is_absolute_path(member.filename):
        raise SafeExtractionError(f"ZIP contains absolute path: {member.filename}")
    
    # Reject symlinks entirely
    if _is_symlink(member):
        raise SafeExtractionError(f"ZIP contains symlink (rejected): {member.filename}")
    
    try:
        resolved = (base_path / member.filename).resolve()
    except Exception as e:
        raise SafeExtractionError(f"Invalid path in ZIP: {member.filename}") from e
    
    # Ensure resolved path stays within base_path
    try:
        resolved.relative_to(base_path.resolve())
    except ValueError:
        raise SafeExtractionError(f"Path traversal attempt: {member.filename}")
    
    return resolved


def safe_extract_zip(zip_path: str, dest_dir: Optional[Path] = None) -> Path:
    """
    Safely extract a ZIP file with all hostile-input protections.
    """
    zip_path = Path(zip_path)
    if not zip_path.exists():
        raise SafeExtractionError(f"ZIP file not found: {zip_path}")
    
    zip_size = zip_path.stat().st_size
    if zip_size > MAX_REPO_SIZE_BYTES:
        raise SafeExtractionError(f"ZIP file too large: {zip_size} bytes (max {MAX_REPO_SIZE_BYTES})")
    
    if dest_dir is None:
        dest_dir = Path(tempfile.mkdtemp(prefix="mneme-audit-zip-"))
    else:
        dest_dir = Path(dest_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
    
    dest_dir = dest_dir.resolve()
    
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            members = zip_ref.infolist()
            
            if len(members) > MAX_FILE_COUNT:
                raise SafeExtractionError(f"ZIP contains too many files: {len(members)} (max {MAX_FILE_COUNT})")
            
            total_uncompressed = sum(m.file_size for m in members)
            if zip_size > 0 and total_uncompressed / zip_size > MAX_ZIP_RATIO:
                raise SafeExtractionError(f"Suspected zip bomb: ratio {total_uncompressed/zip_size:.1f}")
            
            # Also enforce absolute uncompressed size limit
            if total_uncompressed > MAX_REPO_SIZE_BYTES:
                raise SafeExtractionError(f"ZIP uncompressed size too large: {total_uncompressed} bytes (max {MAX_REPO_SIZE_BYTES})")
            
            extracted_count = 0
            for member in members:
                if member.is_dir():
                    continue
                
                safe_path = _validate_zip_member(member, dest_dir)
                safe_path.parent.mkdir(parents=True, exist_ok=True)
                
                with zip_ref.open(member) as source:
                    if member.compress_size > MAX_FILE_SIZE_BYTES:
                        raise SafeExtractionError(
                            f"Compressed file too large: {member.filename} ({member.compress_size} bytes)"
                        )
                    
                    written = 0
                    with open(safe_path, "wb") as target:
                        while True:
                            chunk = source.read(READ_CHUNK_SIZE)
                            if not chunk:
                                break
                            written += len(chunk)
                            if written > MAX_FILE_SIZE_BYTES:
                                raise SafeExtractionError(
                                    f"Uncompressed file too large: {member.filename} ({written} bytes)"
                                )
                            target.write(chunk)
                
                try:
                    sample = safe_path.read_bytes()[:READ_CHUNK_SIZE]
                    if _is_binary(sample):
                        safe_path.unlink(missing_ok=True)
                        continue
                except Exception:
                    pass
                
                extracted_count += 1
            
            return dest_dir
    
    except SafeExtractionError:
        shutil.rmtree(dest_dir, ignore_errors=True)
        raise
    except Exception as e:
        shutil.rmtree(dest_dir, ignore_errors=True)
        raise SafeExtractionError(f"ZIP extraction failed: {e}") from e


def safe_clone_repo(repo_url: str, dest_dir: Optional[Path] = None, depth: int = 1) -> Path:
    """
    Safely clone a Git repository with timeout and size limits.
    
    Uses `git clone` subprocess with timeout for reliable timeout enforcement,
    since GitPython's clone_from doesn't support timeout directly.
    """
    if dest_dir is None:
        dest_dir = Path(tempfile.mkdtemp(prefix="mneme-audit-git-"))
    else:
        dest_dir = Path(dest_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
    
    dest_dir = dest_dir.resolve()
    
    try:
        # Use subprocess with timeout for reliable timeout enforcement
        # GitPython's clone_from doesn't expose timeout parameter
        cmd = [
            "git", "clone",
            "--depth", str(depth),
            "--single-branch",
            repo_url,
            str(dest_dir),
        ]
        env = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        
        result = subprocess.run(
            cmd,
            env=env,
            timeout=CLONE_TIMEOUT_SECONDS,
            capture_output=True,
            text=True,
        )
        
        if result.returncode != 0:
            raise SafeExtractionError(f"Git clone failed: {result.stderr}")
        
        # Verify repo size after clone and check for symlinks
        total_size = 0
        file_count = 0
        for root, dirs, files in os.walk(dest_dir):
            if ".git" in root.split(os.sep):
                continue
            for f in files:
                fp = Path(root) / f
                try:
                    # Check for symlinks
                    if fp.is_symlink():
                        raise SafeExtractionError(f"Repository contains symlink (rejected): {fp}")
                    total_size += fp.stat().st_size
                    file_count += 1
                    if total_size > MAX_REPO_SIZE_BYTES:
                        raise SafeExtractionError(f"Repository too large: {total_size} bytes (max {MAX_REPO_SIZE_BYTES})")
                    if file_count > MAX_FILE_COUNT:
                        raise SafeExtractionError(f"Repository has too many files: {file_count} (max {MAX_FILE_COUNT})")
                except OSError:
                    pass
        
        return dest_dir
    
    except subprocess.TimeoutExpired:
        shutil.rmtree(dest_dir, ignore_errors=True)
        raise SafeExtractionError(f"Git clone timed out after {CLONE_TIMEOUT_SECONDS} seconds")
    except SafeExtractionError:
        shutil.rmtree(dest_dir, ignore_errors=True)
        raise
    except subprocess.CalledProcessError as e:
        shutil.rmtree(dest_dir, ignore_errors=True)
        raise SafeExtractionError(f"Git clone failed: {e.stderr}") from e
    except Exception as e:
        shutil.rmtree(dest_dir, ignore_errors=True)
        raise SafeExtractionError(f"Repository clone failed: {e}") from e


def safe_local_path(local_path: str) -> Path:
    """Validate and resolve a local repository path."""
    path = Path(local_path).resolve()
    
    if not path.exists():
        raise SafeExtractionError(f"Local path does not exist: {local_path}")
    
    if not path.is_dir():
        raise SafeExtractionError(f"Local path is not a directory: {local_path}")
    
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for f in files:
            if f.startswith("."):
                continue
            fp = Path(root) / f
            try:
                total_size += fp.stat().st_size
                file_count += 1
                if total_size > MAX_REPO_SIZE_BYTES:
                    raise SafeExtractionError(f"Repository too large: {total_size} bytes")
                if file_count > MAX_FILE_COUNT:
                    raise SafeExtractionError(f"Too many files: {file_count}")
            except OSError:
                pass
    
    return path


def cleanup_temp_dir(path: Path) -> None:
    """Safely remove a temporary directory."""
    try:
        if path and path.exists():
            shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass