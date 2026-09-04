"""Opt-in combined preview. This module performs no provisioning or migration."""
import os
from pathlib import Path, PurePosixPath

from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from sqlalchemy.engine import make_url

PREVIEW_DATABASE = 'mneme_audit_preview'
RUNTIME_USER = 'mneme_audit_preview_runtime'
MIGRATOR_USER = 'mneme_audit_preview_migrator'


def require_preview_database(expected_user=RUNTIME_USER):
    """Fail before importing the API/creating engines. Never print credentials.

    This protects against misconfiguration, not database authorization attacks.
    The DBA permission gate and isolated IAM identity remain mandatory.
    """
    try:
        url = make_url(os.environ.get('DATABASE_URL', ''))
        valid = (url.drivername == 'postgresql+asyncpg'
                 and url.database == PREVIEW_DATABASE
                 and url.username == expected_user and bool(url.password))
    except Exception:
        valid = False
    if not valid:
        raise RuntimeError('Preview requires its explicit restricted preview database credential.') from None
    if os.environ.get('DB_ECHO', 'false').lower() != 'false':
        raise RuntimeError('Preview requires DB_ECHO=false.')
    return url


class PreviewSite(StaticFiles):
    """Serve marketing plus clean workspace deep links, never API fallbacks."""

    async def get_response(self, path, scope):
        path = path.replace('\\', '/')
        try:
            response = await super().get_response(path, scope)
        except HTTPException as error:
            if error.status_code != 404:
                raise
            response = None
        if response is None or response.status_code == 404:
            route = PurePosixPath(path)
            if path.startswith('audit/workspace/') and not route.suffix and '..' not in route.parts:
                return await super().get_response('audit/workspace/index.html', scope)
            if response is None:
                raise HTTPException(status_code=404)
        return response


def create_preview_app():
    require_preview_database()
    site = Path(os.environ.get('AUDIT_SITE_ROOT', '/app/site'))
    if not (site / 'audit/workspace/index.html').is_file():
        raise RuntimeError('Combined preview workspace assets are missing.')
    from app.main import app
    app.mount('/', PreviewSite(directory=str(site), html=True), name='preview-site')
    return app
