# CLAUDE.md - Project Instructions for AI Assistants

## Architecture
- Follow ADR-001: Use PostgreSQL, never SQLite in production
- Follow ADR-002: Use uv for package management
- Follow ADR-003: Respect service boundaries

## Code Style
- Use type hints everywhere
- Prefer composition over inheritance
- Write tests for new functionality

## Security
- Never commit secrets or API keys
- Use environment variables for configuration