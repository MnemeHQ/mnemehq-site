"""
Safe extraction utilities for hostile repository input.

All repo ingestion (git clone, ZIP extract) goes through these functions.
They enforce size limits, path validation, binary detection, and cleanup.
"""
from __future__ import annotations

import os
import shutil
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


def _validate_zip_member(member: zipfile.ZipInfo, base_path: Path) -> Path:
    """
    Validate a ZIP member path and return the resolved safe destination.
    
    Prevents:
    - Absolute paths
    - Path traversal (..)
    - Symlink escapes
    """
    if member.is_absolute():
        raise SafeExtractionError(f"ZIP contains absolute path: {member.filename}")
    
    try:
        resolved = (base_path / member.filename).resolve()
    except Exception as e:
        raise SafeExtractionError(f"Invalid path in ZIP: {member.filename}") from e
    
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
    """
    if dest_dir is None:
        dest_dir = Path(tempfile.mkdtemp(prefix="mneme-audit-git-"))
    else:
        dest_dir = Path(dest_dir)
        dest_dir.mkdir(parents=True, exist_ok=True)
    
    dest_dir = dest_dir.resolve()
    
    try:
        Repo.clone_from(
            repo_url,
            dest_dir,
            depth=depth,
            single_branch=True,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
        
        total_size = 0
        file_count = 0
        for root, dirs, files in os.walk(dest_dir):
            if ".git" in root.split(os.sep):
                continue
            for f in files:
                fp = Path(root) / f
                try:
                    total_size += fp.stat().st_size
                    file_count += 1
                    if total_size > MAX_REPO_SIZE_BYTES:
                        raise SafeExtractionError(f"Repository too large: {total_size} bytes (max {MAX_REPO_SIZE_BYTES})")
                    if file_count > MAX_FILE_COUNT:
                        raise SafeExtractionError(f"Repository has too many files: {file_count} (max {MAX_FILE_COUNT})")
                except OSError:
                    pass
        
        return dest_dir
    
    except GitCommandError as e:
        shutil.rmtree(dest_dir, ignore_errors=True)
        raise SafeExtractionError(f"Git clone failed: {e}") from e
    except SafeExtractionError:
        shutil.rmtree(dest_dir, ignore_errors=True)
        raise
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